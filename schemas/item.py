from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    item_type: str = Field(min_length=1, max_length=50)


class ItemRead(BaseModel):
    id: int
    name: str
    item_type: str

    model_config = ConfigDict(from_attributes=True)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    item_type: str | None = Field(default=None, min_length=1, max_length=50)
