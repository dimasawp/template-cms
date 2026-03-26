from sqlalchemy.orm import Session
from app.modules.roles.models.role_model import Role, Permission
from app.modules.users.models.user_model import User
from app.core.security import get_password_hash


def seed_roles(db: Session):
    roles = [
        {"id": 1, "name": "super_admin", "description": "Full system access"},
        {"id": 2, "name": "admin", "description": "Administrative access"},
        {"id": 3, "name": "editor", "description": "Can create and edit content"},
        {"id": 4, "name": "viewer", "description": "Read-only access"},
    ]
    for data in roles:
        if not db.query(Role).filter_by(name=data["name"]).first():
            db.add(Role(**data))
    print("[OK] Roles seeded")


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
    ]
    for data in permissions:
        if not db.query(Permission).filter_by(name=data["name"]).first():
            db.add(Permission(**data))
    print("[OK] Permissions seeded")


def seed_role_permissions(db: Session):
    all_perms = db.query(Permission).all()

    sa = db.query(Role).filter_by(name="super_admin").first()
    if sa:
        sa.permissions = all_perms

    admin = db.query(Role).filter_by(name="admin").first()
    if admin:
        admin.permissions = [p for p in all_perms if p.name not in ("roles.delete", "settings.update")]

    editor = db.query(Role).filter_by(name="editor").first()
    if editor:
        editor.permissions = [
            p for p in all_perms
            if p.name in ("users.view", "roles.view", "audit.view", "notifications.view", "settings.view")
        ]

    viewer = db.query(Role).filter_by(name="viewer").first()
    if viewer:
        viewer.permissions = [p for p in all_perms if p.name.endswith(".view")]

    print("[OK] Role-permissions assigned")


def seed_super_admin(db: Session):
    if db.query(User).filter_by(username="superadmin").first():
        print("[INFO] Super-admin already exists")
        return

    role = db.query(Role).filter_by(name="super_admin").first()
    user = User(
        username="superadmin",
        email="admin@example.com",
        full_name="Super Administrator",
        password_hash=get_password_hash("admin123"),
        role_id=role.id,
        is_active=True,
    )
    db.add(user)
    print("[OK] Super-admin created (password: admin123)")


def run():
    from app.core.database import SessionLocal, engine, Base
    from app.core.config import settings
    import app.modules.users.models.user_model          # noqa: F401
    import app.modules.roles.models.role_model           # noqa: F401
    import app.modules.notifications.models.notification_model  # noqa: F401

    print(f"[SEED] Running seeds (ENV={settings.ENV})")
    print("[SEED] Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables ready")

    db = SessionLocal()
    try:
        seed_roles(db)
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_super_admin(db)
        db.commit()
        print("[OK] Seeding completed")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
