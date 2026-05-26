from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.modules.categories.schemas.category_schema import CategoryResponse

class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    category_id: Optional[int] = None
    content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_published: bool = True

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    category_id: Optional[int] = None
    content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
