from pydantic import BaseModel, Field
from typing import Optional, List


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)
    captcha_token: Optional[str] = None
    captcha_answer: Optional[str] = None

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=255)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)
    captcha_token: Optional[str] = None
    captcha_answer: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserMeResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_name: str
    permissions: List[str] = []
    is_active: bool
    avatar: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class BulkRevokeRequest(BaseModel):
    session_ids: List[int]
