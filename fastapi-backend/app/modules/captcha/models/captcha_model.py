import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.core.database import Base


class CaptchaCode(Base):
    __tablename__ = "captcha_codes"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, index=True, nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)

    @classmethod
    def generate(cls, code: str, ttl_minutes: int = 5) -> "CaptchaCode":
        return cls(
            token=uuid.uuid4().hex,
            code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
            is_used=False,
            created_at=datetime.now(timezone.utc),
        )
