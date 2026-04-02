from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: Optional[str] = None
    type: str = "info"
    link: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: Optional[str] = None
    type: str
    read_at: Optional[datetime] = None
    link: Optional[str] = None
    created_at: datetime


class NotificationBadge(BaseModel):
    unread_count: int
