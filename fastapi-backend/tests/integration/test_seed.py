import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.modules.roles.models.role_model import Role, Permission
from app.modules.users.models.user_model import User
from app.modules.settings.models.setting_model import Setting

from db.seeds.seed import seed_roles, seed_permissions, seed_role_permissions, seed_users, seed_settings
from db.seeds.data import SEED_PERMISSIONS, SEED_SETTINGS


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ── Sync idempotency ─────────────────────────────────────────────


class TestSeedSyncIdempotent:
    def _run_all(self, db):
        seed_roles(db)
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_users(db)
        seed_settings(db)
        db.commit()

    def test_seed_sync_adds_roles(self, db_session: Session):
        self._run_all(db_session)
        assert db_session.query(Role).count() == 2
        assert db_session.query(Role).filter_by(name="super_admin").first() is not None
        assert db_session.query(Role).filter_by(name="admin").first() is not None

    def test_seed_sync_adds_permissions(self, db_session: Session):
        self._run_all(db_session)
        assert db_session.query(Permission).count() == len(SEED_PERMISSIONS)

    def test_seed_sync_adds_settings(self, db_session: Session):
        self._run_all(db_session)
        assert db_session.query(Setting).count() == len(SEED_SETTINGS)

    def test_seed_sync_adds_users(self, db_session: Session):
        self._run_all(db_session)
        assert db_session.query(User).count() == 2

    def test_seed_sync_is_idempotent(self, db_session: Session):
        self._run_all(db_session)
        role_count = db_session.query(Role).count()
        perm_count = db_session.query(Permission).count()
        user_count = db_session.query(User).count()
        setting_count = db_session.query(Setting).count()

        self._run_all(db_session)

        assert db_session.query(Role).count() == role_count
        assert db_session.query(Permission).count() == perm_count
        assert db_session.query(User).count() == user_count
        assert db_session.query(Setting).count() == setting_count


# ── Sync does not overwrite changed settings ─────────────────────


class TestSeedSyncDoesNotOverwrite:
    def _seed_once(self, db):
        seed_roles(db)
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_users(db)
        seed_settings(db)
        db.commit()

    def test_sync_does_not_overwrite_changed_setting(self, db_session: Session):
        self._seed_once(db_session)

        setting = db_session.query(Setting).filter_by(setting_key="app_name").first()
        setting.setting_value = "My Custom App"
        db_session.commit()

        seed_settings(db_session)
        db_session.commit()

        setting = db_session.query(Setting).filter_by(setting_key="app_name").first()
        assert setting.setting_value == "My Custom App"

    def test_sync_does_not_remove_manual_permissions(self, db_session: Session):
        self._seed_once(db_session)

        role = db_session.query(Role).filter_by(name="super_admin").first()
        count_before = len(role.permissions)

        seed_role_permissions(db_session)
        db_session.commit()

        role = db_session.query(Role).filter_by(name="super_admin").first()
        assert len(role.permissions) == count_before


# ── Super admin gets all permissions ─────────────────────────────


class TestSuperAdminPermissions:
    def _seed_once(self, db):
        seed_roles(db)
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_users(db)
        db.commit()

    def test_super_admin_has_all_permissions(self, db_session: Session):
        self._seed_once(db_session)
        role = db_session.query(Role).filter_by(name="super_admin").first()
        all_perms = db_session.query(Permission).count()
        assert len(role.permissions) == all_perms


# ── Reset mode safety ────────────────────────────────────────────


class TestSeedResetSafety:
    def test_run_reset_not_implemented(self):
        from db.seeds.seed import run
        with patch("db.seeds.seed.settings.ENV", "production"):
            with pytest.raises(SystemExit):
                run(mode="reset")
