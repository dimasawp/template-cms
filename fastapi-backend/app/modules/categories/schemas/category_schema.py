from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    is_active: bool = True
    is_menu: bool = False

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_menu: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool
    order_index: int = 0
    is_menu: bool = False
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryTreeResponse(CategoryResponse):
    children: Optional[list['CategoryTreeResponse']] = []

    class Config:
        from_attributes = True

class CategoryReorderItem(BaseModel):
    id: int
    parent_id: Optional[int] = None
    order_index: int

class CategoryReorder(BaseModel):
    items: list[CategoryReorderItem]
