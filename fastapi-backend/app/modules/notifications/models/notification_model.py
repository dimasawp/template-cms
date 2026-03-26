import enum
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False, nullable=False)
    link = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<Notification {self.id} for user {self.user_id}>"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True, index=True, autoincrement=True,
    )
    action = Column(String(50), nullable=False, index=True)
    resource = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(50), nullable=True)
    detail = Column(Text, nullable=True)
    actor_id = Column(Integer, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource}:{self.resource_id}>"
