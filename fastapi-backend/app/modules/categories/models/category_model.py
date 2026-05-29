from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Display ordering within same parent
    order_index = Column(Integer, default=0, nullable=False)
    
    # Show as standalone menu in sidebar
    is_menu = Column(Boolean, default=False, nullable=False)
    
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
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="category")
    author = relationship("User", foreign_keys=[created_by])
    editor = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<Category {self.name}>"
