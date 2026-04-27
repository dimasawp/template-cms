from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    is_active: bool = True
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    permissions: List[dict] = []
    user_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
