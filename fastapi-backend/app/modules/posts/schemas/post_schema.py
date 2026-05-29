from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from app.modules.categories.schemas.category_schema import CategoryResponse


class PostStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AdditionalContentBlock(BaseModel):
    """Schema for validating individual blocks inside additional_contents."""
    id: str
    type: str  # Currently only 'iframe' is allowed
    source_type: str  # 'url' or 'file'
    url: str
    title: Optional[str] = None
    order: int = 0

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed = ["iframe"]
        if v not in allowed:
            raise ValueError(f"Block type must be one of {allowed}, got '{v}'")
        return v

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        allowed = ["url", "file"]
        if v not in allowed:
            raise ValueError(f"Source type must be one of {allowed}, got '{v}'")
        return v


class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    category_id: Optional[int] = None
    content: Optional[str] = None
    thumbnail: Optional[str] = None
    additional_contents: Optional[List[AdditionalContentBlock]] = None
    status: PostStatus = PostStatus.DRAFT


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    category_id: Optional[int] = None
    content: Optional[str] = None
    thumbnail: Optional[str] = None
    additional_contents: Optional[List[AdditionalContentBlock]] = None
    status: Optional[PostStatus] = None


class AuthorSummary(BaseModel):
    id: int
    full_name: Optional[str] = None
    username: str

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    content: Optional[str] = None
    thumbnail: Optional[str] = None
    additional_contents: Optional[List[Any]] = None
    status: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    author: Optional[AuthorSummary] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
