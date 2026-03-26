from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=6)
    role_id: int
    is_active: bool = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_id: int
    role_name: str
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListItem(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_name: str
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
