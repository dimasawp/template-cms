from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_superadmin, require_roles, check_permission
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.modules.auth.schemas.auth_schema import (
    LoginRequest, RefreshTokenRequest, ProfileUpdateRequest, ChangePasswordRequest, BulkRevokeRequest,
    RegisterRequest
)
from app.modules.auth.services.auth_service import AuthService
from app.helpers.response import success_response
from app.helpers.file_handler import save_file
from app.exceptions import handle_errors, UnauthorizedException, ForbiddenException
from app.modules.audit.services.audit_service import AuditService


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ==================== ENDPOINTS ====================

@router.post("/register")
@handle_errors
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Self-registration for new users."""
    user = AuthService.register_user(
        db, payload.username, payload.email, payload.full_name, payload.password
    )
    return success_response(
        data={"id": user.id, "username": user.username},
        message="Registration successful. Please login."
    )

@router.post("/login")
@handle_errors
async def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate and return JWT tokens (for frontend / API clients)."""
    user = AuthService.authenticate_user(db, payload.username, payload.password)
    
    # Check for maintenance mode. Only super_admins can login during maintenance.
    from app.modules.settings.models.setting_model import Setting
    from datetime import datetime
    
    s_rows = db.query(Setting).filter(Setting.setting_key.in_(["maintenance_mode", "maintenance_scheduled_at"])).all()
    s_dict = {s.setting_key: s.setting_value for s in s_rows}
    
    is_m_active = s_dict.get("maintenance_mode") == "true"
    scheduled_at = s_dict.get("maintenance_scheduled_at")
    
    should_block = is_m_active
    if is_m_active and scheduled_at:
        try:
            target_dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
            if datetime.now(target_dt.tzinfo) < target_dt:
                should_block = False
        except: pass

    if should_block:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role or role.name != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System is under maintenance. Only administrators can access."
            )

    tokens = AuthService.create_tokens(user.id, request, db)

    # Log activity
    AuditService.log(
        db=db, user_id=user.id, action="LOGIN", module="AUTH",
        item_id=str(user.id), description=f"User {user.username} logged in",
        request=request
    )

    return success_response(
        data={
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
        },
        message="Login successful",
    )


@router.post("/swagger-login", include_in_schema=True)
@handle_errors
async def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 Password Flow — used by Swagger UI 'Authorize' button.
    Restricted to super_admin role only.
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    # Check super_admin role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role or role.name != "super_admin":
        raise ForbiddenException("Swagger access is restricted to super administrators")

    # Pass dummy request for Swagger login or actual request
    # Since swagger_login doesn't have request injected, let's inject it
    tokens = AuthService.create_tokens(user.id, None, db)
    # OAuth2 spec requires exactly these fields at the top level
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
@handle_errors
async def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    tokens = AuthService.refresh_access_token(db, payload.refresh_token)
    return success_response(
        data={
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
        },
        message="Token refreshed successfully",
    )


@router.get("/me")
@handle_errors
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the authenticated user's profile + permissions."""
    info = AuthService.get_user_info(db, current_user.id)
    return success_response(data=info, message="User information retrieved")


@router.post("/logout")
@handle_errors
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logout — revoke session in DB and signal client to delete token."""
    # Get sid from request.state set by get_current_user dependency
    sid = getattr(request.state, "sid", None)
    
    if sid:
        try:
            AuthService.revoke_session(db, sid)
        except:
            pass # Already revoked or not found

    return success_response(message="Logout successful. Please delete token from client.")


# ── Session Management (Super Admin only) ───────────────────────────

@router.get("/sessions")
@handle_errors
async def get_active_sessions(
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("sessions.view")),
):
    """List all active user sessions (refresh tokens)."""
    sessions = AuthService.get_all_sessions(db)
    data = [
        {
            "id": s.id,
            "user_id": s.user_id,
            "username": s.user.username,
            "full_name": s.user.full_name,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "expires_at": s.expires_at.isoformat(),
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]
    return success_response(data=data, message="Active sessions retrieved")


@router.delete("/sessions/{session_id}")
@handle_errors
async def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission("sessions.delete"))
):
    """Admin feature: kill a specific user session."""
    AuthService.revoke_session(db, session_id)
    return success_response(message="Session revoked successfully")


@router.post("/sessions/bulk-revoke")
@handle_errors
async def bulk_revoke_sessions(
    payload: BulkRevokeRequest,
    db: Session = Depends(get_db),
    _=Depends(check_permission("sessions.delete"))
):
    """Admin feature: kill multiple user sessions."""
    AuthService.bulk_revoke_sessions(db, payload.session_ids)
    return success_response(message=f"{len(payload.session_ids)} sessions revoked successfully")


# ── Profile Management (Authenticated Users) ───────────────────────

@router.put("/me")
@handle_errors
async def update_my_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update authenticated user's profile (name & email)."""
    user = AuthService.update_user_profile(
        db, current_user.id, username=payload.username, full_name=payload.full_name, email=payload.email
    )
    return success_response(
        data={"username": user.username, "full_name": user.full_name, "email": user.email},
        message="Profile updated successfully"
    )


@router.put("/change-password")
@handle_errors
async def change_my_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change authenticated user's password."""
    AuthService.change_user_password(
        db, current_user.id, payload.old_password, payload.new_password
    )
    return success_response(message="Password changed successfully")


@router.post("/avatar")
@handle_errors
async def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and set profile picture."""
    path = save_file(file, sub_dir="avatars")
    AuthService.update_avatar(db, current_user.id, path)
    return success_response(data={"avatar": path}, message="Avatar uploaded successfully")
