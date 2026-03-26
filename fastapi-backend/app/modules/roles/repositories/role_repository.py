from sqlalchemy.orm import Session
from sqlalchemy import func

from app.modules._base.repository import BaseRepository
from app.modules.roles.models.role_model import Role, Permission
from app.modules.users.models.user_model import User


class RoleRepository(BaseRepository):
    model = Role
    search_fields = ["name"]

    @classmethod
    def get_by_name(cls, db: Session, name: str):
        return db.query(Role).filter(Role.name == name).first()

    @classmethod
    def get_user_count(cls, db: Session, role_id: int) -> int:
        return db.query(func.count(User.id)).filter(User.role_id == role_id).scalar()

    @classmethod
    def get_all_permissions(cls, db: Session):
        return db.query(Permission).order_by(Permission.name).all()

    @classmethod
    def get_permissions_by_ids(cls, db: Session, ids: list):
        return db.query(Permission).filter(Permission.id.in_(ids)).all()
