from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models import Item
from schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[Item]:
        result = await self.db.execute(select(Item))
        return result.scalars().all()

    async def get_by_id(self, item_id: int) -> Item | None:
        result = await self.db.execute(select(Item).where(Item.id == item_id))
        return result.scalars().first()

    async def create(self, data: ItemCreate) -> Item:
        new_item = Item(**data.model_dump())
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def update(self, item_id: int, data: ItemUpdate) -> Item | None:
        item = await self.get_by_id(item_id)
        if not item:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)

        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item_id: int) -> bool:
        item = await self.get_by_id(item_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True


async def get_item_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemService:
    return ItemService(db)
