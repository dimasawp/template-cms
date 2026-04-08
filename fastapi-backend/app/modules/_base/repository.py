"""
Base repository with generic CRUD operations.

Subclass and set ``model`` to get instant CRUD with pagination,
search, and filtering.

    class UserRepository(BaseRepository):
        model = User
        search_fields = ["username", "email", "full_name"]
"""

from typing import Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import Base


class BaseRepository:
    model: Type[Base] = None
    search_fields: List[str] = []

    @classmethod
    def create(cls, db: Session, data: dict) -> Any:
        obj = cls.model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def get_by_id(cls, db: Session, record_id: int) -> Optional[Any]:
        query = db.query(cls.model).filter(cls.model.id == record_id)
        if hasattr(cls.model, "deleted_at"):
            query = query.filter(cls.model.deleted_at == None)
        return query.first()

    @classmethod
    def get_all(
        cls,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_dir: str = "asc",
    ):
        query = db.query(cls.model)

        if hasattr(cls.model, "deleted_at"):
            query = query.filter(cls.model.deleted_at == None)
        if filters:
            for col, val in filters.items():
                if val is not None and hasattr(cls.model, col):
                    query = query.filter(getattr(cls.model, col) == val)

        if search and cls.search_fields:
            conditions = [
                getattr(cls.model, f).ilike(f"%{search}%")
                for f in cls.search_fields
                if hasattr(cls.model, f)
            ]
            if conditions:
                query = query.filter(or_(*conditions))

        total = query.count()

        if order_by and hasattr(cls.model, order_by):
            col = getattr(cls.model, order_by)
            query = query.order_by(col.desc() if order_dir == "desc" else col.asc())
        elif hasattr(cls.model, "id"):
            query = query.order_by(cls.model.id.desc())

        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    @classmethod
    def update(cls, db: Session, record_id: int, data: dict) -> Optional[Any]:
        obj = cls.get_by_id(db, record_id)
        if obj is None:
            return None
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def delete(cls, db: Session, record_id: int) -> bool:
        obj = cls.get_by_id(db, record_id)
        if obj is None:
            return False
        
        if hasattr(obj, "deleted_at"):
            from app.helpers.date_helper import get_now_wib
            obj.deleted_at = get_now_wib()
        else:
            db.delete(obj)
            
        db.commit()
        return True

    @classmethod
    def hard_delete(cls, db: Session, record_id: int) -> bool:
        obj = db.query(cls.model).filter(cls.model.id == record_id).first()
        if obj is None:
            return False
        db.delete(obj)
        db.commit()
        return True
