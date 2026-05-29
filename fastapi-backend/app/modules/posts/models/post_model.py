from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Rich text content (Jodit Editor)
    content = Column(Text, nullable=True)
    
    # Thumbnail image URL/path
    thumbnail = Column(String(500), nullable=True)
    
    # Additional dynamic content blocks (iframes, etc.) stored as JSON array
    additional_contents = Column(JSON, nullable=True)
    
    # Post status: DRAFT, PUBLISHED, ARCHIVED
    status = Column(String(20), default="DRAFT", nullable=False, index=True)
    
    # Actor tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
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
    author = relationship("User", foreign_keys=[created_by])
    editor = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<Post {self.title}>"
