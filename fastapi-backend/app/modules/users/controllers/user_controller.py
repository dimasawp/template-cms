from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.modules.users.models.user_model import User
from app.modules.users.schemas.user_schema import (
    UserCreate, UserUpdate, ChangePasswordRequest, ResetPasswordRequest,
)
from app.modules.users.services.user_service import UserService
from app.helpers.response import success_response, paginated_response
from app.helpers.file_handler import save_file, delete_file
from app.exceptions import handle_errors


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# ==================== ENDPOINTS ====================

@router.get("")
@handle_errors
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by username, email, or name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    role_id: Optional[int] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.view")),
):
    """List users with pagination, search, and filters."""
    users, total = UserService.get_all_users(
        db, page=page, per_page=per_page, search=search,
        is_active=is_active, role_id=role_id,
    )
    items = [UserService.to_list_item(u, db) for u in users]
    return paginated_response(items, total, page, per_page)


@router.get("/{user_id}")
@handle_errors
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.view")),
):
    """Get single user by ID."""
    from app.modules.users.repositories.user_repository import UserRepository
    from app.exceptions import NotFoundException

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    return success_response(data=UserService.to_response(user, db))


@router.post("")
@handle_errors
async def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.create")),
):
    """Create a new user."""
    user = UserService.create_user(db, data)
    return success_response(data=UserService.to_response(user, db), message="User created", code=201)


@router.put("/{user_id}")
@handle_errors
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.update")),
):
    """Update user fields."""
    user = UserService.update_user(db, user_id, data)
    return success_response(data=UserService.to_response(user, db), message="User updated")


@router.delete("/{user_id}")
@handle_errors
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.delete")),
):
    """Delete a user."""
    UserService.delete_user(db, user_id)
    return success_response(message="User deleted")


@router.post("/{user_id}/reset-password")
@handle_errors
async def reset_password(
    user_id: int,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.update")),
):
    """Admin resets a user's password."""
    UserService.reset_password(db, user_id, data.new_password)
    return success_response(message="Password reset successfully")


@router.post("/{user_id}/avatar")
@handle_errors
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.update")),
):
    """Upload or replace user avatar."""
    from app.modules.users.repositories.user_repository import UserRepository
    from app.exceptions import NotFoundException

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    if user.avatar:
        delete_file(user.avatar)

    path = save_file(file, sub_dir="avatars")
    user.avatar = path
    db.commit()
    return success_response(data={"avatar": path}, message="Avatar uploaded")


@router.put("/me/change-password")
@handle_errors
async def change_own_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """User changes their own password."""
    UserService.change_password(db, current_user, data.old_password, data.new_password)
    return success_response(message="Password changed successfully")
