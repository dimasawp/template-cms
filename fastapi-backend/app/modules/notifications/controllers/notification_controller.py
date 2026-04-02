from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models.user_model import User
from app.modules.notifications.services.notification_service import NotificationService
from app.helpers.response import success_response, paginated_response
from app.exceptions import handle_errors


router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


# ==================== ENDPOINTS ====================

@router.get("")
@handle_errors
async def get_all_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False, description="Show unread only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List notifications for the authenticated user."""
    items, total = NotificationService.get_user_notifications(
        db, current_user.id, page=page, per_page=per_page, unread_only=unread_only,
    )
    data = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "read_at": n.read_at.isoformat() if n.read_at else None,
            "link": n.link,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in items
    ]
    return paginated_response(data, total, page, per_page)


@router.get("/badge")
@handle_errors
async def get_notification_badge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return unread notification count (for the bell icon badge)."""
    count = NotificationService.get_unread_count(db, current_user.id)
    return success_response(data={"unread_count": count})


@router.put("/{notification_id}/read")
@handle_errors
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    NotificationService.mark_as_read(db, notification_id, current_user.id)
    return success_response(message="Marked as read")


@router.put("/read-all")
@handle_errors
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    count = NotificationService.mark_all_read(db, current_user.id)
    return success_response(data={"marked": count}, message="All notifications marked as read")
