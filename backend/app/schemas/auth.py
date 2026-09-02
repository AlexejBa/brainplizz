from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime