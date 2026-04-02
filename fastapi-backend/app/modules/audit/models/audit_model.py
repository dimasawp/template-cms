from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)
    item_id = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Store JSON payloads for "Before" and "After" states
    payload_before = Column(JSON, nullable=True)
    payload_after = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.module} by User {self.user_id}>"
