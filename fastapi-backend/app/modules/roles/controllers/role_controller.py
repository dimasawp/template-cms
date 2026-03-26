from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.modules.users.models.user_model import User
from app.modules.roles.schemas.role_schema import RoleCreate, RoleUpdate
from app.modules.roles.services.role_service import RoleService
from app.modules.roles.repositories.role_repository import RoleRepository
from app.helpers.response import success_response, paginated_response
from app.exceptions import handle_errors, NotFoundException


router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


# ==================== ENDPOINTS ====================

@router.get("")
@handle_errors
async def get_all_roles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by role name"),
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("roles.view")),
):
    """List roles with pagination."""
    roles, total = RoleRepository.get_all(db, page=page, per_page=per_page, search=search)
    items = [RoleService.to_response(r, db) for r in roles]
    return paginated_response(items, total, page, per_page)


@router.get("/permissions")
@handle_errors
async def get_all_permissions(
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("roles.view")),
):
    """Return all available permissions (for the permission matrix UI)."""
    perms = RoleRepository.get_all_permissions(db)
    data = [{"id": p.id, "name": p.name, "description": p.description} for p in perms]
    return success_response(data=data)


@router.get("/{role_id}")
@handle_errors
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("roles.view")),
):
    """Get single role by ID."""
    role = RoleRepository.get_by_id(db, role_id)
    if not role:
        raise NotFoundException("Role not found")
    return success_response(data=RoleService.to_response(role, db))


@router.post("")
@handle_errors
async def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("roles.create")),
):
    """Create a new role."""
    role = RoleService.create_role(db, data)
    return success_response(data=RoleService.to_response(role, db), message="Role created", code=201)


@router.put("/{role_id}")
@handle_errors
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("roles.update")),
):
    """Update an existing role."""
    role = RoleService.update_role(db, role_id, data)
    return success_response(data=RoleService.to_response(role, db), message="Role updated")


@router.delete("/{role_id}")
@handle_errors
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _u: User = Depends(check_permission("roles.delete")),
):
    """Delete a role."""
    RoleService.delete_role(db, role_id)
    return success_response(message="Role deleted")
