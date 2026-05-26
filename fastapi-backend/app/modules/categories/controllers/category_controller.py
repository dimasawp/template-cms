from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.modules.users.models.user_model import User
from app.modules.categories.schemas.category_schema import (
    CategoryCreate, CategoryUpdate, CategoryResponse
)
from app.modules.categories.services.category_service import CategoryService
from app.helpers.response import success_response, paginated_response
from app.exceptions import handle_errors, NotFoundException
from app.modules.categories.repositories.category_repository import CategoryRepository

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

@router.get("")
@handle_errors
async def get_all_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    parent_id: Optional[int] = Query(None),
    order_by: Optional[str] = Query(None),
    order_dir: str = Query("asc"),
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("categories.view")),
):
    categories, total = CategoryService.get_all(
        db, page=page, per_page=per_page, search=search,
        is_active=is_active, parent_id=parent_id,
        order_by=order_by, order_dir=order_dir
    )
    # Using CategoryResponse for serialization
    items = [CategoryResponse.model_validate(c).model_dump() for c in categories]
    return paginated_response(items, total, page, per_page)


@router.get("/{cat_id}")
@handle_errors
async def get_category(
    cat_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("categories.view")),
):
    category = CategoryRepository.get_by_id(db, cat_id)
    if not category:
        raise NotFoundException("Category not found")
    return success_response(data=CategoryResponse.model_validate(category).model_dump())


@router.post("")
@handle_errors
async def create_category(
    data: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("categories.create")),
):
    category = CategoryService.create(db, data, actor_id=current_user.id, request=request)
    return success_response(data=CategoryResponse.model_validate(category).model_dump(), message="Category created", code=201)


@router.put("/{cat_id}")
@handle_errors
async def update_category(
    cat_id: int,
    data: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("categories.update")),
):
    category = CategoryService.update(db, cat_id, data, actor_id=current_user.id, request=request)
    return success_response(data=CategoryResponse.model_validate(category).model_dump(), message="Category updated")


@router.delete("/{cat_id}")
@handle_errors
async def delete_category(
    cat_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("categories.delete")),
):
    CategoryService.delete(db, cat_id, actor_id=current_user.id, request=request)
    return success_response(message="Category deleted")
