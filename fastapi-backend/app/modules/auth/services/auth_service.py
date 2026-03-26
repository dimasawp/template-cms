from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.modules.auth.schemas.auth_schema import TokenResponse
from app.exceptions import UnauthorizedException, ForbiddenException, NotFoundException


class AuthService:

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Incorrect username or password")
        if not user.is_active:
            raise ForbiddenException("User account is inactive")
        return user

    @staticmethod
    def create_tokens(user_id: int) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(data={"sub": str(user_id)}),
            refresh_token=create_refresh_token(data={"sub": str(user_id)}),
            token_type="bearer",
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token")

        try:
            user_id = int(payload.get("sub"))
        except (ValueError, TypeError):
            raise UnauthorizedException("Invalid token payload")

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        return AuthService.create_tokens(user_id)

    @staticmethod
    def get_user_info(db: Session, user_id: int) -> dict:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")

        role = db.query(Role).filter(Role.id == user.role_id).first()
        permissions = [p.name for p in role.permissions] if role else []

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role_name": role.name if role else None,
            "permissions": permissions,
            "is_active": user.is_active,
        }
