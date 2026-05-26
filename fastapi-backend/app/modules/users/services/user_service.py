from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.modules.audit.services.audit_service import AuditService

from app.modules._base.service import BaseService
from app.modules.users.repositories.user_repository import UserRepository
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.core.security import get_password_hash, verify_password
from app.exceptions import NotFoundException, ConflictException, BadRequestException


class UserService(BaseService):
    repository = UserRepository

    @classmethod
    def get_all_users(
        cls,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        order_by: Optional[str] = None,
        order_dir: str = "asc",
    ):
        query = db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role_id is not None:
            query = query.filter(User.role_id == role_id)
        if search:
            query = query.filter(
                User.username.ilike(f"%{search}%")
                | User.full_name.ilike(f"%{search}%")
                | User.email.ilike(f"%{search}%")
            )

        total = query.count()
        if order_by and hasattr(User, order_by):
            col = getattr(User, order_by)
            query = query.order_by(col.desc() if order_dir == "desc" else col.asc())
        else:
            query = query.order_by(User.id.desc())

        users = query.offset((page - 1) * per_page).limit(per_page).all()
        return users, total

    @classmethod
    def create_user(cls, db: Session, data, actor_id: int = None, request: Request = None) -> User:
        if UserRepository.get_by_username(db, data.username):
            raise ConflictException("Username already exists")

        user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            password_hash=get_password_hash(data.password),
            role_id=data.role_id,
            is_active=data.is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Audit Log
        AuditService.log(
            db, actor_id, "CREATE", "USERS", 
            item_id=str(user.id), 
            description=f"Created user: {user.username}",
            payload_after=cls.to_response(user, db),
            request=request
        )

        return user

    @classmethod
    def update_user(cls, db: Session, user_id: int, data, actor_id: int = None, request: Request = None) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")

        payload_before = cls.to_response(user, db)
        update_data = data.model_dump(exclude_unset=True)
        
        # Check for last super_admin if attempting to deactivate or change role
        role = db.query(Role).filter(Role.id == user.role_id).first()
        is_super_admin = role and role.name == "super_admin"
        
        attempting_deactivation = "is_active" in update_data and update_data["is_active"] is False
        attempting_role_change = "role_id" in update_data and update_data["role_id"] != user.role_id

        if is_super_admin and (attempting_deactivation or attempting_role_change):
            active_sa_count = db.query(User).join(Role).filter(Role.name == "super_admin", User.is_active == True).count()
            if active_sa_count <= 1:
                raise ConflictException("Cannot deactivate or change the role of the last active super_admin")

        has_changes = False
        if "password" in update_data:
            user.password_hash = get_password_hash(update_data.pop("password"))
            has_changes = True
            
        for k, v in update_data.items():
            if getattr(user, k) != v:
                has_changes = True
                setattr(user, k, v)
                
        if not has_changes:
            raise BadRequestException("No changes detected")

        db.commit()
        db.refresh(user)

        # Audit Log
        AuditService.log(
            db, actor_id, "UPDATE", "USERS", 
            item_id=str(user.id), 
            description=f"Updated user: {user.username}",
            payload_before=payload_before,
            payload_after=cls.to_response(user, db),
            request=request
        )

        return user

    @classmethod
    def delete_user(cls, db: Session, user_id: int, actor_id: int = None, request: Request = None) -> None:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
            
        payload_before = cls.to_response(user, db)
        username = user.username

        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role and role.name == "super_admin" and user.is_active:
            active_sa_count = db.query(User).join(Role).filter(Role.name == "super_admin", User.is_active == True).count()
            if active_sa_count <= 1:
                raise ConflictException("Cannot delete the last active super_admin")
                
        db.delete(user)
        db.commit()

        # Audit Log
        AuditService.log(
            db, actor_id, "DELETE", "USERS", 
            item_id=str(user_id), 
            description=f"Deleted user: {username}",
            payload_before=payload_before,
            request=request
        )

    @classmethod
    def reset_password(cls, db: Session, user_id: int, new_password: str, actor_id: int = None, request: Request = None) -> None:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        user.password_hash = get_password_hash(new_password)
        db.commit()

        # Audit Log
        AuditService.log(
            db, actor_id, "RESET_PASSWORD", "USERS", 
            item_id=str(user.id), 
            description=f"Reset password for user: {user.username}",
            request=request
        )

    @classmethod
    def change_password(cls, db: Session, user: User, old_password: str, new_password: str, request: Request = None) -> None:
        if not verify_password(old_password, user.password_hash):
            raise BadRequestException("Old password is incorrect")
        user.password_hash = get_password_hash(new_password)
        db.commit()

        # Audit Log
        AuditService.log(
            db, user.id, "CHANGE_PASSWORD", "AUTH", 
            item_id=str(user.id), 
            description=f"User changed their own password",
            request=request
        )

    @classmethod
    def to_response(cls, user: User, db: Session) -> dict:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role_id": user.role_id,
            "role_name": role.name if role else None,
            "avatar": user.avatar,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    @classmethod
    def to_list_item(cls, user: User, db: Session) -> dict:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role_id": user.role_id,
            "role_name": role.name if role else None,
            "avatar": user.avatar,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
