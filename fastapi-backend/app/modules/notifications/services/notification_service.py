from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.modules._base.service import BaseService
from app.modules.notifications.repositories.notification_repository import NotificationRepository
from app.modules.notifications.models.notification_model import AuditLog
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


class AuditService:

    @staticmethod
    def log_action(
        db: Session,
        *,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        detail: Optional[str] = None,
        actor: User,
        request: Optional[Request] = None,
    ):
        ip = request.client.host if request and request.client else None
        entry = AuditLog(
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id else None,
            detail=detail,
            actor_id=actor.id,
            ip_address=ip,
        )
        db.add(entry)
