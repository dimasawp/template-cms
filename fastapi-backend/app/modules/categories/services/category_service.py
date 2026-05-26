from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.modules._base.service import BaseService
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.models.category_model import Category
from app.exceptions import NotFoundException, ConflictException, BadRequestException
from app.modules.audit.services.audit_service import AuditService

class CategoryService(BaseService):
    repository = CategoryRepository

    @classmethod
    def get_all(
        cls,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[int] = None,
    ):
        query = db.query(Category)

        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        if search:
            query = query.filter(
                Category.name.ilike(f"%{search}%")
                | Category.slug.ilike(f"%{search}%")
            )

        total = query.count()
        categories = query.order_by(Category.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return categories, total

    @classmethod
    def create(cls, db: Session, data, actor_id: int = None, request: Request = None) -> Category:
        if CategoryRepository.get_by_slug(db, data.slug):
            raise ConflictException("Slug already exists")

        if data.parent_id:
            parent = CategoryRepository.get_by_id(db, data.parent_id)
            if not parent:
                raise NotFoundException("Parent category not found")

        category = Category(**data.model_dump())
        db.add(category)
        db.commit()
        db.refresh(category)

        AuditService.log(
            db, actor_id, "CREATE", "CATEGORIES",
            item_id=str(category.id),
            description=f"Created category: {category.name}",
            request=request
        )
        return category

    @classmethod
    def update(cls, db: Session, cat_id: int, data, actor_id: int = None, request: Request = None) -> Category:
        category = CategoryRepository.get_by_id(db, cat_id)
        if not category:
            raise NotFoundException("Category not found")

        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data and update_data["slug"] != category.slug:
            if CategoryRepository.get_by_slug(db, update_data["slug"]):
                raise ConflictException("Slug already exists")

        if "parent_id" in update_data and update_data["parent_id"] is not None:
            if update_data["parent_id"] == cat_id:
                raise BadRequestException("Category cannot be its own parent")
            parent = CategoryRepository.get_by_id(db, update_data["parent_id"])
            if not parent:
                raise NotFoundException("Parent category not found")

        has_changes = False
        for k, v in update_data.items():
            if getattr(category, k) != v:
                has_changes = True
                setattr(category, k, v)

        if not has_changes:
            raise BadRequestException("No changes detected")

        db.commit()
        db.refresh(category)

        AuditService.log(
            db, actor_id, "UPDATE", "CATEGORIES",
            item_id=str(category.id),
            description=f"Updated category: {category.name}",
            request=request
        )
        return category

    @classmethod
    def delete(cls, db: Session, cat_id: int, actor_id: int = None, request: Request = None) -> None:
        category = CategoryRepository.get_by_id(db, cat_id)
        if not category:
            raise NotFoundException("Category not found")
        
        name = category.name
        db.delete(category)
        db.commit()

        AuditService.log(
            db, actor_id, "DELETE", "CATEGORIES",
            item_id=str(cat_id),
            description=f"Deleted category: {name}",
            request=request
        )
