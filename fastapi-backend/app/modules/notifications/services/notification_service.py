from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.modules._base.service import BaseService
from app.modules.notifications.repositories.notification_repository import NotificationRepository
from app.modules.users.models.user_model import User


class NotificationService(BaseService):
    repository = NotificationRepository

    @classmethod
    def get_user_notifications(cls, db: Session, user_id: int, **kwargs):
        return NotificationRepository.get_user_notifications(db, user_id, **kwargs)

    @classmethod
    def get_unread_count(cls, db: Session, user_id: int) -> int:
        return NotificationRepository.get_unread_count(db, user_id)

    @classmethod
    def mark_as_read(cls, db: Session, notification_id: int, user_id: int) -> bool:
        return NotificationRepository.mark_as_read(db, notification_id, user_id)

    @classmethod
    def mark_all_read(cls, db: Session, user_id: int) -> int:
        return NotificationRepository.mark_all_read(db, user_id)

