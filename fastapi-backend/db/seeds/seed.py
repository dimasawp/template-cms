from sqlalchemy.orm import Session
from app.modules.roles.models.role_model import Role, Permission
from app.modules.users.models.user_model import User
from app.modules.settings.models.setting_model import Setting
from app.core.security import get_password_hash


# ==================== ROLES ====================

def seed_roles(db: Session):
    roles = [
        {"id": 1, "name": "super_admin", "description": "Full system access"},
        {"id": 2, "name": "admin", "description": "Administrative access"},
    ]
    for data in roles:
        if not db.query(Role).filter_by(name=data["name"]).first():
            db.add(Role(**data))
    print("[OK] Roles seeded")


# ==================== PERMISSIONS ====================

def seed_permissions(db: Session):
    permissions = [
        {"id": 1,  "name": "users.view",    "description": "View users"},
        {"id": 2,  "name": "users.create",  "description": "Create users"},
        {"id": 3,  "name": "users.update",  "description": "Update users"},
        {"id": 4,  "name": "users.delete",  "description": "Delete users"},
        {"id": 5,  "name": "roles.view",    "description": "View roles"},
        {"id": 6,  "name": "roles.create",  "description": "Create roles"},
        {"id": 7,  "name": "roles.update",  "description": "Update roles"},
        {"id": 8,  "name": "roles.delete",  "description": "Delete roles"},
        {"id": 9,  "name": "audit.view",    "description": "View audit logs"},
        {"id": 10, "name": "notifications.view", "description": "View notifications"},
        {"id": 11, "name": "settings.view",   "description": "View settings"},
        {"id": 12, "name": "settings.update", "description": "Update settings"},
        {"id": 13, "name": "sessions.view",   "description": "View active sessions"},
        {"id": 14, "name": "sessions.delete", "description": "Revoke sessions (kick)"},
        {"id": 15, "name": "categories.view",   "description": "View categories"},
        {"id": 16, "name": "categories.create", "description": "Create categories"},
        {"id": 17, "name": "categories.update", "description": "Update categories"},
        {"id": 18, "name": "categories.delete", "description": "Delete categories"},
        {"id": 19, "name": "posts.view",      "description": "View posts"},
        {"id": 20, "name": "posts.create",    "description": "Create posts"},
        {"id": 21, "name": "posts.update",    "description": "Update posts"},
        {"id": 22, "name": "posts.delete",    "description": "Delete posts"},
        {"id": 23, "name": "media.view",      "description": "View media files"},
        {"id": 24, "name": "media.create",    "description": "Upload media files"},
        {"id": 25, "name": "media.update",    "description": "Update media files"},
        {"id": 26, "name": "media.delete",    "description": "Delete media files"},
    ]
    for data in permissions:
        if not db.query(Permission).filter_by(name=data["name"]).first():
            db.add(Permission(**data))
    print("[OK] Permissions seeded")


# ==================== ROLE-PERMISSION MAPPING ====================

def seed_role_permissions(db: Session):
    all_perms = db.query(Permission).all()

    # Super Admin: ALL permissions
    sa = db.query(Role).filter_by(name="super_admin").first()
    if sa:
        sa.permissions = []
        db.flush()
        sa.permissions = all_perms
        print("[OK] Super Admin → all permissions")

    # Admin: All except roles.delete and settings.update
    admin = db.query(Role).filter_by(name="admin").first()
    if admin:
        admin.permissions = [
            p for p in all_perms
            if p.name not in ("roles.delete", "settings.update")
        ]
        print("[OK] Admin → restricted permissions")

    print("[OK] Role-permissions assigned")


# ==================== USERS ====================

def seed_users(db: Session):
    # 1. Super Admin account
    if not db.query(User).filter_by(username="superadmin").first():
        sa_role = db.query(Role).filter_by(name="super_admin").first()
        db.add(User(
            username="superadmin",
            email="superadmin@example.com",
            full_name="Super Administrator",
            password_hash=get_password_hash("admin123"),
            role_id=sa_role.id,
            is_active=True,
        ))
        print("[OK] Super Admin created  →  superadmin / admin123")
    else:
        print("[SKIP] Super Admin already exists")

    # 2. Admin account
    if not db.query(User).filter_by(username="admin").first():
        admin_role = db.query(Role).filter_by(name="admin").first()
        db.add(User(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            password_hash=get_password_hash("admin123"),
            role_id=admin_role.id,
            is_active=True,
        ))
        print("[OK] Admin created        →  admin / admin123")
    else:
        print("[SKIP] Admin already exists")


# ==================== SETTINGS ====================

def seed_settings(db: Session):
    settings_data = [
        {"setting_key": "app_name", "setting_value": "CMS Template", "description": "Application Name"},
        {"setting_key": "maintenance_mode", "setting_value": "false", "description": "Maintenance Mode Toggle"},
        {"setting_key": "registration_enabled", "setting_value": "true", "description": "Allow user self-registration"},
    ]
    for data in settings_data:
        if not db.query(Setting).filter_by(setting_key=data["setting_key"]).first():
            db.add(Setting(**data))
    print("[OK] Settings seeded")


# ==================== RUNNER ====================

def run():
    from app.core.database import SessionLocal, engine, Base
    from app.core.config import settings
    from sqlalchemy import text

    # Import all models so Base.metadata knows every table
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

    print(f"\n{'='*50}")
    print(f"  DATABASE SEEDER  (ENV={settings.ENV})")
    print(f"{'='*50}\n")

    # Non-production: wipe & recreate for clean sequential IDs
    if settings.ENV != "production":
        print("[SEED] Resetting database (truncate all)...")
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
        print("[OK] All tables dropped — auto-increments reset\n")

    print("[SEED] Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables ready\n")

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
        print("  ✅  SEEDING COMPLETED SUCCESSFULLY")
        print(f"{'='*50}\n")
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
