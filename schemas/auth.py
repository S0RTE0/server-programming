from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["user", "admin"]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    role: UserRole = "user"


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
