from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.modules.auth.schemas.auth_schema import LoginRequest, RefreshTokenRequest
from app.modules.auth.services.auth_service import AuthService
from app.helpers.response import success_response
from app.exceptions import handle_errors, UnauthorizedException, ForbiddenException


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ==================== ENDPOINTS ====================

@router.post("/login")
@handle_errors
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return JWT tokens (for frontend / API clients)."""
    user = AuthService.authenticate_user(db, request.username, request.password)
    tokens = AuthService.create_tokens(user.id)
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

    tokens = AuthService.create_tokens(user.id)
    # OAuth2 spec requires exactly these fields at the top level
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
@handle_errors
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    tokens = AuthService.refresh_access_token(db, request.refresh_token)
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
async def logout(current_user: User = Depends(get_current_user)):
    """Logout — client should delete the stored token."""
    return success_response(message="Logout successful. Please delete token from client.")
