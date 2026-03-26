from sqlalchemy.orm import Session

from app.modules._base.repository import BaseRepository
from app.modules.notifications.models.notification_model import Notification


class NotificationRepository(BaseRepository):
    model = Notification

    @classmethod
    def get_user_notifications(cls, db: Session, user_id: int, *, page=1, per_page=20, unread_only=False):
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        total = query.count()
        items = (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * per_page).limit(per_page).all()
        )
        return items, total

    @classmethod
    def get_unread_count(cls, db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    @classmethod
    def mark_as_read(cls, db: Session, notification_id: int, user_id: int) -> bool:
        notif = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if not notif:
            return False
        notif.is_read = True
        db.commit()
        return True

    @classmethod
    def mark_all_read(cls, db: Session, user_id: int) -> int:
        count = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True})
        )
        db.commit()
        return count
