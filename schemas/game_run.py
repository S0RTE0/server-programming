from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GameRunCreate(BaseModel):
    player_id: UUID
    score: int = Field(default=0, ge=0)
    waves_cleared: int = Field(default=0, ge=0)
    survival_time_sec: int = Field(default=0, ge=0)


class GameRunRead(BaseModel):
    id: UUID
    player_id: UUID
    score: int
    waves_cleared: int
    survival_time_sec: int
    played_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameRunUpdate(BaseModel):
    player_id: UUID | None = None
    score: int | None = Field(default=None, ge=0)
    waves_cleared: int | None = Field(default=None, ge=0)
    survival_time_sec: int | None = Field(default=None, ge=0)
