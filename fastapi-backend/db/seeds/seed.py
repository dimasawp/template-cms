"""
Database seeder.

Usage:
    python -m db.seeds.seed            # sync mode (default, safe)
    python -m db.seeds.seed --sync     # explicit sync
    python -m db.seeds.seed --reset    # reset (dev only, drops tables)
    python -m db.seeds.seed --reset --force   # skip confirmation
"""

import argparse
import sys

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.roles.models.role_model import Role, Permission
from app.modules.users.models.user_model import User
from app.modules.settings.models.setting_model import Setting
from app.core.security import get_password_hash
from app.core.config import settings

from db.seeds.data import (
    SEED_ROLES,
    SEED_PERMISSIONS,
    ALL_PERMISSION_NAMES,
    SEED_ROLE_PERMISSIONS,
    SEED_USERS,
    SEED_SETTINGS,
)
from db.seeds import upsert_by_name, add_missing_permissions, confirm_or_abort


# ==================== ROLES ====================

def seed_roles(db: Session):
    for data in SEED_ROLES:
        upsert_by_name(db, Role, data["name"], {"description": data["description"]})
    print("[OK] Roles synced")


# ==================== PERMISSIONS ====================

def seed_permissions(db: Session):
    for data in SEED_PERMISSIONS:
        upsert_by_name(db, Permission, data["name"], {"description": data["description"]})
    print("[OK] Permissions synced")


# ==================== ROLE-PERMISSION MAPPING ====================

def seed_role_permissions(db: Session):
    all_perms = db.query(Permission).all()
    all_perms_by_name = {p.name: p for p in all_perms}

    for role_name, perm_names in SEED_ROLE_PERMISSIONS.items():
        role = db.query(Role).filter_by(name=role_name).first()
        if not role:
            print(f"[SKIP] Role '{role_name}' not found, skipping permissions")
            continue

        if perm_names == "*":
            target_perms = all_perms
        else:
            target_perms = [all_perms_by_name[n] for n in perm_names if n in all_perms_by_name]

        add_missing_permissions(db, role, target_perms)
        print(f"[OK] Role '{role_name}' permissions synced")


# ==================== USERS ====================

def seed_users(db: Session):
    for u in SEED_USERS:
        existing = db.query(User).filter_by(username=u["username"]).first()
        if existing:
            print(f"[SKIP] User '{u['username']}' already exists")
            continue
        role = db.query(Role).filter_by(name=u["role"]).first()
        if not role:
            print(f"[SKIP] Role '{u['role']}' not found, cannot create user '{u['username']}'")
            continue
        db.add(User(
            username=u["username"],
            email=u["email"],
            full_name=u["full_name"],
            password_hash=get_password_hash(u["password"]),
            role_id=role.id,
            is_active=True,
        ))
        print(f"[OK] User '{u['username']}' created")


# ==================== SETTINGS ====================

def seed_settings(db: Session):
    for s in SEED_SETTINGS:
        existing = db.query(Setting).filter_by(setting_key=s["setting_key"]).first()
        if existing:
            print(f"[SKIP] Setting '{s['setting_key']}' already exists (value kept)")
            continue
        db.add(Setting(
            setting_key=s["setting_key"],
            setting_value=s["setting_value"],
            description=s["description"],
        ))
        print(f"[OK] Setting '{s['setting_key']}' created")
    print("[OK] Settings synced")


# ==================== MODEL IMPORTS ====================

def _import_models():
    """Import all models so Base.metadata is fully populated."""
    import app.modules.users.models.user_model               # noqa: F401
    import app.modules.roles.models.role_model                # noqa: F401
    import app.modules.notifications.models.notification_model  # noqa: F401
    import app.modules.media.models.media_model               # noqa: F401
    import app.modules.audit.models.audit_model               # noqa: F401
    import app.modules.auth.models.session_model              # noqa: F401
    import app.modules.settings.models.setting_model          # noqa: F401
    import app.modules.users.models.password_reset_model      # noqa: F401
    import app.modules.categories.models.category_model       # noqa: F401
    import app.modules.posts.models.post_model                # noqa: F401
    import app.modules.captcha.models.captcha_model          # noqa: F401


# ==================== DROP & CREATE ====================

def _reset_database():
    """Drop all tables and recreate them. Only for development."""
    from app.core.database import engine, Base

    print("[RESET] Dropping all tables...")
    with engine.begin() as conn:
        if engine.dialect.name == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        elif engine.dialect.name == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = OFF;"))

        Base.metadata.drop_all(bind=conn)

        if engine.dialect.name == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        elif engine.dialect.name == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = ON;"))
    print("[OK] All tables dropped\n")

    print("[RESET] Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables ready\n")


# ==================== RUNNER ====================

def run(mode: str = "sync", force: bool = False):
    _import_models()
    from app.core.database import SessionLocal

    print(f"\n{'='*50}")
    print(f"  DATABASE SEEDER  (ENV={settings.ENV}, mode={mode})")
    print(f"{'='*50}\n")

    if mode == "reset":
        if settings.ENV == "production" and not force:
            print("[ABORT] Cannot reset database in production mode. Use --force to override.\n")
            sys.exit(1)

        if not force:
            print("  WARNING: This will DELETE ALL DATA and re-insert seeds!")
            if not confirm_or_abort("Are you sure you want to proceed?"):
                print("[ABORT] Reset cancelled.\n")
                return

        _reset_database()

    db = SessionLocal()
    try:
        seed_roles(db)
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_users(db)
        seed_settings(db)
        db.commit()
        print(f"\n{'='*50}")
        print(f"  ✅  SEEDING COMPLETED SUCCESSFULLY (mode={mode})")
        print(f"{'='*50}\n")
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database seeder")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sync", action="store_true", help="Sync seed data only (default)")
    group.add_argument("--reset", action="store_true", help="Drop all tables and reseed (dev only)")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    args = parser.parse_args()

    mode = "reset" if args.reset else "sync"
    run(mode=mode, force=args.force)
