"""
FastAPI dependencies for authentication & authorisation.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role, Permission


# ── Security Scheme ─────────────────────────────────────────────────
# OAuth2PasswordBearer powers both:
#   1. Swagger UI "Authorize" dialog (username + password form)
#   2. Standard Bearer token usage from frontend / Postman

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/swagger-login",
    auto_error=False,
)


# ── Current User (JWT) ──────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    return user


# ── Super-Admin Guard ────────────────────────────────────────────────

def get_current_superadmin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if not role or role.name != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super-admin access required")
    return current_user


# ── Permission Checker (factory) ─────────────────────────────────────

def check_permission(permission_name: str):
    def _checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        role = db.query(Role).filter(Role.id == current_user.role_id).first()
        has_perm = (
            db.query(Permission)
            .join(Role.permissions)
            .filter(Role.id == role.id, Permission.name == permission_name)
            .first()
        )
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_name} required",
            )
        return current_user

    return _checker
