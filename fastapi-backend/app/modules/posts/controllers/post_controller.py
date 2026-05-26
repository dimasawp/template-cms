from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.modules.users.models.user_model import User
from app.modules.posts.schemas.post_schema import (
    PostCreate, PostUpdate, PostResponse
)
from app.modules.posts.services.post_service import PostService
from app.helpers.response import success_response, paginated_response
from app.exceptions import handle_errors, NotFoundException
from app.modules.posts.repositories.post_repository import PostRepository

router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])

@router.get("")
@handle_errors
async def get_all_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("posts.view")),
):
    posts, total = PostService.get_all(
        db, page=page, per_page=per_page, search=search,
        is_published=is_published, category_id=category_id
    )
    items = [PostResponse.model_validate(p).model_dump() for p in posts]
    return paginated_response(items, total, page, per_page)


@router.get("/{post_id}")
@handle_errors
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("posts.view")),
):
    post = PostRepository.get_by_id(db, post_id)
    if not post:
        raise NotFoundException("Post not found")
    return success_response(data=PostResponse.model_validate(post).model_dump())


@router.post("")
@handle_errors
async def create_post(
    data: PostCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("posts.create")),
):
    post = PostService.create(db, data, actor_id=current_user.id, request=request)
    return success_response(data=PostResponse.model_validate(post).model_dump(), message="Post created", code=201)


@router.put("/{post_id}")
@handle_errors
async def update_post(
    post_id: int,
    data: PostUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("posts.update")),
):
    post = PostService.update(db, post_id, data, actor_id=current_user.id, request=request)
    return success_response(data=PostResponse.model_validate(post).model_dump(), message="Post updated")


@router.delete("/{post_id}")
@handle_errors
async def delete_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("posts.delete")),
):
    PostService.delete(db, post_id, actor_id=current_user.id, request=request)
    return success_response(message="Post deleted")
