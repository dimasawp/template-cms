"""
FastAPI dependencies for authentication & authorisation.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, decode_token_lenient
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role, Permission
from app.modules.auth.models.session_model import UserSession
from app.modules.settings.models.setting_model import Setting


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
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_logout = request.url.path.endswith("/auth/logout") or request.url.path.endswith("/auth/logout/")
    
    # Use lenient decoding for logout to handle expired tokens
    payload = decode_token_lenient(token) if is_logout else decode_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        user_id = int(payload.get("sub"))
        sid = payload.get("sid")
        # Store sid in request state so controllers can use it without re-decoding
        if sid:
            request.state.sid = sid
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    # ── FAST-TRACK FOR LOGOUT ──
    # If logging out, we skip further checks (session existence, maintenance mode).
    if request.url.path.endswith("/auth/logout") or request.url.path.endswith("/auth/logout/"):
        return user

    # Real-time Session Validation (Instant Kick)
    sid = payload.get("sid")
    if sid:
        session = db.query(UserSession).filter(UserSession.id == sid, UserSession.user_id == user_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Session has been revoked or expired"
            )

    # ── Maintenance Mode Check ──
    m_mode = db.query(Setting).filter(Setting.setting_key == "maintenance_mode").first()
    if m_mode and m_mode.setting_value == "true":
        # Check if the user is a super_admin
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role or role.name != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System is under maintenance. Only administrators can access."
            )

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

def require_roles(allowed_roles: list[str]):
    """FastAPI dependence: block unless user has one of these roles."""
    def _role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        # Check role name
        role = db.query(Role).filter(Role.id == current_user.role_id).first()
        if not role or role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: One of these roles required: {allowed_roles}",
            )
        return current_user
    return _role_checker
