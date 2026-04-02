from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base
from app.modules.users.models.user_model import User  # Ensure User is in registry


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    
    # storage_mode determines which provider was used:
    # 'local_project' | 'local_system' | 'cloud'
    storage_mode = Column(String(50), nullable=False, default="local_project")
    
    # For extra metadata (e.g. S3 bucket, etc.)
    provider_metadata = Column(String(1000), nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="media_files")

    def __repr__(self):
        return f"<Media {self.filename} ({self.storage_mode})>"
