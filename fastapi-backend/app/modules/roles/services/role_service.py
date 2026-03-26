from sqlalchemy.orm import Session

from app.modules._base.service import BaseService
from app.modules.roles.repositories.role_repository import RoleRepository
from app.modules.roles.models.role_model import Role
from app.exceptions import NotFoundException, ConflictException, BadRequestException


class RoleService(BaseService):
    repository = RoleRepository

    @classmethod
    def to_response(cls, role: Role, db: Session) -> dict:
        user_count = RoleRepository.get_user_count(db, role.id)
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": [
                {"id": p.id, "name": p.name, "description": p.description}
                for p in role.permissions
            ],
            "user_count": user_count,
            "created_at": role.created_at.isoformat() if role.created_at else None,
        }

    @classmethod
    def create_role(cls, db: Session, data) -> Role:
        if RoleRepository.get_by_name(db, data.name):
            raise ConflictException("Role name already exists")

        role = Role(name=data.name, description=data.description)
        if data.permission_ids:
            role.permissions = RoleRepository.get_permissions_by_ids(db, data.permission_ids)

        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @classmethod
    def update_role(cls, db: Session, role_id: int, data) -> Role:
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise NotFoundException("Role not found")

        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.permission_ids is not None:
            role.permissions = RoleRepository.get_permissions_by_ids(db, data.permission_ids)

        db.commit()
        db.refresh(role)
        return role

    @classmethod
    def delete_role(cls, db: Session, role_id: int) -> None:
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise NotFoundException("Role not found")

        user_count = RoleRepository.get_user_count(db, role_id)
        if user_count > 0:
            raise BadRequestException(f"Cannot delete role with {user_count} assigned user(s)")

        db.delete(role)
        db.commit()
