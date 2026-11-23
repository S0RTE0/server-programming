from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models import RunItem
from schemas.run_item import RunItemCreate, RunItemUpdate


class RunItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[RunItem]:
        result = await self.db.execute(select(RunItem))
        return result.scalars().all()

    async def get_by_id(self, run_id: UUID, item_id: int) -> RunItem | None:
        result = await self.db.execute(
            select(RunItem).where(
                RunItem.run_id == run_id,
                RunItem.item_id == item_id,
            )
        )
        return result.scalars().first()

    async def create(self, data: RunItemCreate) -> RunItem:
        new_run_item = RunItem(**data.model_dump())
        self.db.add(new_run_item)
        await self.db.commit()
        await self.db.refresh(new_run_item)
        return new_run_item

    async def update(
        self, run_id: UUID, item_id: int, data: RunItemUpdate
    ) -> RunItem | None:
        run_item = await self.get_by_id(run_id, item_id)
        if not run_item:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(run_item, field, value)

        self.db.add(run_item)
        await self.db.commit()
        await self.db.refresh(run_item)
        return run_item

    async def delete(self, run_id: UUID, item_id: int) -> bool:
        run_item = await self.get_by_id(run_id, item_id)
        if not run_item:
            return False

        await self.db.delete(run_item)
        await self.db.commit()
        return True


async def get_run_item_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RunItemService:
    return RunItemService(db)
