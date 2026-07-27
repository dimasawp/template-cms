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
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        category_level: Optional[int] = None,
        order_by: Optional[str] = None,
        order_dir: str = "asc",
    ):
        query = db.query(Post).filter(Post.deleted_at == None)

        if status is not None:
            query = query.filter(Post.status == status)
            
        if category_id is not None:
            from app.modules.categories.services.category_service import CategoryService
            descendant_ids = CategoryService.get_descendant_ids(db, category_id)
            query = query.filter(Post.category_id.in_([category_id] + descendant_ids))
            
        if category_level is not None:
            from app.modules.categories.models.category_model import Category
            all_cats = db.query(Category).filter(Category.deleted_at == None).all()
            parent_map = {c.id: c.parent_id for c in all_cats}
            
            def get_level(cid):
                lvl = 1
                curr = parent_map.get(cid)
                while curr:
                    lvl += 1
                    curr = parent_map.get(curr)
                return lvl
                
            target_cat_ids = [cid for cid in parent_map if get_level(cid) == category_level]
            if not target_cat_ids:
                query = query.filter(Post.category_id == -1)
            else:
                query = query.filter(Post.category_id.in_(target_cat_ids))

        if search:
            query = query.filter(
                Post.title.ilike(f"%{search}%")
                | Post.slug.ilike(f"%{search}%")
            )

        total = query.count()
        if order_by and hasattr(Post, order_by):
            col = getattr(Post, order_by)
            query = query.order_by(col.desc() if order_dir == "desc" else col.asc())
        else:
            query = query.order_by(Post.id.desc())

        posts = query.offset((page - 1) * per_page).limit(per_page).all()
        return posts, total

    @classmethod
    def create(cls, db: Session, data, actor_id: int = None, request: Request = None) -> Post:
        original_slug = data.slug
        counter = 1
        while PostRepository.get_by_slug(db, data.slug):
            data.slug = f"{original_slug}-{counter}"
            counter += 1

        if data.category_id:
            cat = CategoryRepository.get_by_id(db, data.category_id)
            if not cat:
                raise NotFoundException("Category not found")

        post_data = data.model_dump()
        
        # Serialize additional_contents blocks to dicts for JSON storage
        if post_data.get("additional_contents"):
            post_data["additional_contents"] = [
                block if isinstance(block, dict) else block.model_dump()
                for block in post_data["additional_contents"]
            ]
        
        post = Post(**post_data)
        post.created_by = actor_id
        post.updated_by = actor_id
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
            original_slug = update_data["slug"]
            counter = 1
            while PostRepository.get_by_slug(db, update_data["slug"]):
                update_data["slug"] = f"{original_slug}-{counter}"
                counter += 1

        if "category_id" in update_data and update_data["category_id"] is not None:
            cat = CategoryRepository.get_by_id(db, update_data["category_id"])
            if not cat:
                raise NotFoundException("Category not found")

        # Serialize additional_contents blocks to dicts for JSON storage
        if "additional_contents" in update_data and update_data["additional_contents"]:
            update_data["additional_contents"] = [
                block if isinstance(block, dict) else block.model_dump()
                for block in update_data["additional_contents"]
            ]

        has_changes = False
        for k, v in update_data.items():
            current_val = getattr(post, k)
            # Use str comparison for enum-like values
            if str(current_val) != str(v) if isinstance(v, str) and isinstance(current_val, str) else current_val != v:
                has_changes = True
                setattr(post, k, v)

        if not has_changes:
            raise BadRequestException("No changes detected")

        post.updated_by = actor_id
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
        
        # Soft delete
        from app.helpers.date_helper import get_now_wib
        post.deleted_at = get_now_wib()
        post.updated_by = actor_id
        db.commit()

        AuditService.log(
            db, actor_id, "DELETE", "POSTS",
            item_id=str(post_id),
            description=f"Deleted post: {title}",
            request=request
        )
