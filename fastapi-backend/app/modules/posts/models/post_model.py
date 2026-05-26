from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Phase 1: Simple RichText content
    content = Column(Text, nullable=True)
    
    # Optional metadata for future/advanced use cases
    meta_data = Column(JSON, nullable=True)
    
    is_published = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(),
        onupdate=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(),
        nullable=False,
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="posts")

    def __repr__(self):
        return f"<Post {self.title}>"
