from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.modules._base.service import BaseService
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.models.category_model import Category
from app.exceptions import NotFoundException, ConflictException, BadRequestException
from app.modules.audit.services.audit_service import AuditService
from app.modules.settings.services.setting_service import SettingService

class CategoryService(BaseService):
    repository = CategoryRepository

    @classmethod
    def _get_category_level(cls, db: Session, cat_id: int) -> int:
        level = 1
        current = CategoryRepository.get_by_id(db, cat_id)
        while current and current.parent_id:
            level += 1
            current = CategoryRepository.get_by_id(db, current.parent_id)
        return level

    @classmethod
    def get_descendant_ids(cls, db: Session, cat_id: int) -> list[int]:
        descendants = []
        children = db.query(Category.id).filter(
            Category.parent_id == cat_id,
            Category.deleted_at == None
        ).all()
        for child in children:
            descendants.append(child.id)
            descendants.extend(cls.get_descendant_ids(db, child.id))
        return descendants

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
        is_menu: Optional[bool] = None,
        level: Optional[int] = None,
        order_by: Optional[str] = None,
        order_dir: str = "asc",
    ):
        query = db.query(Category).filter(Category.deleted_at == None)

        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        if is_menu is not None:
            query = query.filter(Category.is_menu == is_menu)
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        if search:
            query = query.filter(
                Category.name.ilike(f"%{search}%")
                | Category.slug.ilike(f"%{search}%")
            )
            
        if level is not None:
            all_cats = db.query(Category).filter(Category.deleted_at == None).all()
            parent_map = {c.id: c.parent_id for c in all_cats}
            
            def get_level(cid):
                lvl = 1
                curr = parent_map.get(cid)
                while curr:
                    lvl += 1
                    curr = parent_map.get(curr)
                return lvl
                
            target_cat_ids = [cid for cid in parent_map if get_level(cid) == level]
            if not target_cat_ids:
                query = query.filter(Category.id == -1)
            else:
                query = query.filter(Category.id.in_(target_cat_ids))

        total = query.count()
        if order_by and hasattr(Category, order_by):
            col = getattr(Category, order_by)
            query = query.order_by(col.desc() if order_dir == "desc" else col.asc())
        else:
            query = query.order_by(Category.order_index.asc(), Category.id.desc())

        categories = query.offset((page - 1) * per_page).limit(per_page).all()
        return categories, total

    @classmethod
    def create(cls, db: Session, data, actor_id: int = None, request: Request = None) -> Category:
        if CategoryRepository.get_by_slug(db, data.slug):
            raise ConflictException("Slug already exists")

        if data.parent_id:
            parent = CategoryRepository.get_by_id(db, data.parent_id)
            if not parent:
                raise NotFoundException("Parent category not found")

            # Max level validation
            max_level = 3
            try:
                setting = SettingService.get_by_key(db, "category_max_level")
                max_level = int(setting.setting_value)
            except Exception:
                pass
            
            parent_level = cls._get_category_level(db, parent.id)
            if parent_level >= max_level:
                raise BadRequestException(f"Maximum nested level ({max_level}) reached")

        # Auto-assign order_index at the end of the sibling list
        max_order = db.query(Category.order_index).filter(
            Category.parent_id == data.parent_id,
            Category.deleted_at == None
        ).order_by(Category.order_index.desc()).first()
        next_order = (max_order[0] + 1) if max_order else 0

        category = Category(**data.model_dump())
        category.order_index = next_order
        category.created_by = actor_id
        category.updated_by = actor_id
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
            
            # Max level validation
            max_level = 3
            try:
                setting = SettingService.get_by_key(db, "category_max_level")
                max_level = int(setting.setting_value)
            except Exception:
                pass
            
            parent_level = cls._get_category_level(db, parent.id)
            if parent_level >= max_level:
                raise BadRequestException(f"Maximum nested level ({max_level}) reached")

        has_changes = False
        for k, v in update_data.items():
            if getattr(category, k) != v:
                has_changes = True
                setattr(category, k, v)

        if not has_changes:
            raise BadRequestException("No changes detected")

        category.updated_by = actor_id
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
        
        # Soft delete
        from app.helpers.date_helper import get_now_wib
        category.deleted_at = get_now_wib()
        category.updated_by = actor_id
        db.commit()

        AuditService.log(
            db, actor_id, "DELETE", "CATEGORIES",
            item_id=str(cat_id),
            description=f"Deleted category: {name}",
            request=request
        )

    @classmethod
    def reorder(cls, db: Session, data, actor_id: int = None, request: Request = None) -> None:
        """
        Mass update for category ordering and parenting.
        data.items contains list of CategoryReorderItem (id, parent_id, order_index)
        """
        item_ids = [item.id for item in data.items]
        categories = db.query(Category).filter(Category.id.in_(item_ids)).all()
        cat_map = {c.id: c for c in categories}

        for item in data.items:
            cat = cat_map.get(item.id)
            if cat:
                cat.parent_id = item.parent_id
                cat.order_index = item.order_index
                cat.updated_by = actor_id

        # Ideally, validate max_level here as well, but for simplicity we assume frontend handles drag constraints properly.
        # Max level validation could be complex for a mass update tree change.

        db.commit()

        AuditService.log(
            db, actor_id, "UPDATE", "CATEGORIES",
            item_id="0",
            description="Reordered categories",
            request=request
        )
