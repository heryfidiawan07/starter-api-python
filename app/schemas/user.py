from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role_id: Optional[str] = None


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    role_id: Optional[str] = None
    is_active: Optional[bool] = None


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
