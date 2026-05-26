from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.modules._base.service import BaseService
from app.modules.posts.repositories.post_repository import PostRepository
from app.modules.posts.models.post_model import Post
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.exceptions import NotFoundException, ConflictException, BadRequestException
from app.modules.audit.services.audit_service import AuditService

class PostService(BaseService):
    repository = PostRepository

    @classmethod
    def get_all(
        cls,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        is_published: Optional[bool] = None,
        category_id: Optional[int] = None,
    ):
        query = db.query(Post)

        if is_published is not None:
            query = query.filter(Post.is_published == is_published)
        if category_id is not None:
            query = query.filter(Post.category_id == category_id)
        if search:
            query = query.filter(
                Post.title.ilike(f"%{search}%")
                | Post.slug.ilike(f"%{search}%")
            )

        total = query.count()
        posts = query.order_by(Post.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return posts, total

    @classmethod
    def create(cls, db: Session, data, actor_id: int = None, request: Request = None) -> Post:
        if PostRepository.get_by_slug(db, data.slug):
            raise ConflictException("Slug already exists")

        if data.category_id:
            cat = CategoryRepository.get_by_id(db, data.category_id)
            if not cat:
                raise NotFoundException("Category not found")

        post = Post(**data.model_dump())
        db.add(post)
        db.commit()
        db.refresh(post)

        AuditService.log(
            db, actor_id, "CREATE", "POSTS",
            item_id=str(post.id),
            description=f"Created post: {post.title}",
            request=request
        )
        return post

    @classmethod
    def update(cls, db: Session, post_id: int, data, actor_id: int = None, request: Request = None) -> Post:
        post = PostRepository.get_by_id(db, post_id)
        if not post:
            raise NotFoundException("Post not found")

        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data and update_data["slug"] != post.slug:
            if PostRepository.get_by_slug(db, update_data["slug"]):
                raise ConflictException("Slug already exists")

        if "category_id" in update_data and update_data["category_id"] is not None:
            cat = CategoryRepository.get_by_id(db, update_data["category_id"])
            if not cat:
                raise NotFoundException("Category not found")

        has_changes = False
        for k, v in update_data.items():
            if getattr(post, k) != v:
                has_changes = True
                setattr(post, k, v)

        if not has_changes:
            raise BadRequestException("No changes detected")

        db.commit()
        db.refresh(post)

        AuditService.log(
            db, actor_id, "UPDATE", "POSTS",
            item_id=str(post.id),
            description=f"Updated post: {post.title}",
            request=request
        )
        return post

    @classmethod
    def delete(cls, db: Session, post_id: int, actor_id: int = None, request: Request = None) -> None:
        post = PostRepository.get_by_id(db, post_id)
        if not post:
            raise NotFoundException("Post not found")
        
        title = post.title
        db.delete(post)
        db.commit()

        AuditService.log(
            db, actor_id, "DELETE", "POSTS",
            item_id=str(post_id),
            description=f"Deleted post: {title}",
            request=request
        )
