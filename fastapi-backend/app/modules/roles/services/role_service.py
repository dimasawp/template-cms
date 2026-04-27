from sqlalchemy.orm import Session

from app.modules._base.service import BaseService
from app.modules.roles.repositories.role_repository import RoleRepository
from app.modules.roles.models.role_model import Role
from app.modules.audit.services.audit_service import AuditService
from app.exceptions import NotFoundException, ConflictException, BadRequestException
from fastapi import Request


class RoleService(BaseService):
    repository = RoleRepository

    @classmethod
    def to_response(cls, role: Role, db: Session) -> dict:
        user_count = RoleRepository.get_user_count(db, role.id)
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "permissions": [
                {"id": p.id, "name": p.name, "description": p.description}
                for p in role.permissions
            ],
            "permission_count": len(role.permissions),
            "user_count": user_count,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None,
        }

    @classmethod
    def create_role(cls, db: Session, data, actor_id: int = None, request: Request = None) -> Role:
        if RoleRepository.get_by_name(db, data.name):
            raise ConflictException("Role name already exists")

        role = Role(
            name=data.name, 
            description=data.description,
            is_active=getattr(data, "is_active", True)
        )
        if data.permission_ids:
            role.permissions = RoleRepository.get_permissions_by_ids(db, data.permission_ids)

        db.add(role)
        db.commit()
        db.refresh(role)

        # Audit Log
        AuditService.log(
            db, actor_id, "CREATE", "ROLES", 
            item_id=str(role.id), 
            description=f"Created role: {role.name}",
            payload_after=cls.to_response(role, db),
            request=request
        )

        return role

    @classmethod
    def update_role(cls, db: Session, role_id: int, data, actor_id: int = None, request: Request = None) -> Role:
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise NotFoundException("Role not found")

        payload_before = cls.to_response(role, db)

        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.is_active is not None:
            role.is_active = data.is_active
        if data.permission_ids is not None:
            role.permissions = RoleRepository.get_permissions_by_ids(db, data.permission_ids)

        db.commit()
        db.refresh(role)

        # Audit Log
        AuditService.log(
            db, actor_id, "UPDATE", "ROLES", 
            item_id=str(role.id), 
            description=f"Updated role: {role.name}",
            payload_before=payload_before,
            payload_after=cls.to_response(role, db),
            request=request
        )

        return role

    @classmethod
    def delete_role(cls, db: Session, role_id: int, actor_id: int = None, request: Request = None) -> None:
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise NotFoundException("Role not found")

        payload_before = cls.to_response(role, db)
        role_name = role.name

        user_count = RoleRepository.get_user_count(db, role_id)
        if user_count > 0:
            raise BadRequestException(f"Cannot delete role with {user_count} assigned user(s)")

        db.delete(role)
        db.commit()

        # Audit Log
        AuditService.log(
            db, actor_id, "DELETE", "ROLES", 
            item_id=str(role_id), 
            description=f"Deleted role: {role_name}",
            payload_before=payload_before,
            request=request
        )
