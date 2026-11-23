from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RunItemCreate(BaseModel):
    run_id: UUID
    item_id: int = Field(gt=0)
    level: int = Field(default=1, ge=1)


class RunItemRead(BaseModel):
    run_id: UUID
    item_id: int
    level: int

    model_config = ConfigDict(from_attributes=True)


class RunItemUpdate(BaseModel):
    level: int | None = Field(default=None, ge=1)
