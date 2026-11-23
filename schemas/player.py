from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PlayerCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    total_coins: int = Field(default=0, ge=0)


class PlayerRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    total_coins: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlayerUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    total_coins: int | None = Field(default=None, ge=0)
