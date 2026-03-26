"""
Base service class.

Provides a thin layer over BaseRepository.
Subclass and override for custom business logic.

    class UserService(BaseService):
        repository = UserRepository
"""

from typing import Type, Optional, Any, Dict
from sqlalchemy.orm import Session
from app.modules._base.repository import BaseRepository


class BaseService:
    repository: Type[BaseRepository] = None

    @classmethod
    def create(cls, db: Session, data: dict) -> Any:
        return cls.repository.create(db, data)

    @classmethod
    def get_by_id(cls, db: Session, record_id: int) -> Optional[Any]:
        return cls.repository.get_by_id(db, record_id)

    @classmethod
    def get_all(cls, db: Session, **kwargs):
        return cls.repository.get_all(db, **kwargs)

    @classmethod
    def update(cls, db: Session, record_id: int, data: dict) -> Optional[Any]:
        return cls.repository.update(db, record_id, data)

    @classmethod
    def delete(cls, db: Session, record_id: int) -> bool:
        return cls.repository.delete(db, record_id)
