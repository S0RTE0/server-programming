from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models import GameRun
from schemas.game_run import GameRunCreate, GameRunUpdate


class GameRunService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[GameRun]:
        result = await self.db.execute(select(GameRun))
        return result.scalars().all()

    async def get_by_id(self, run_id: UUID) -> GameRun | None:
        result = await self.db.execute(select(GameRun).where(GameRun.id == run_id))
        return result.scalars().first()

    async def create(self, data: GameRunCreate) -> GameRun:
        new_run = GameRun(**data.model_dump())
        self.db.add(new_run)
        await self.db.commit()
        await self.db.refresh(new_run)
        return new_run

    async def update(self, run_id: UUID, data: GameRunUpdate) -> GameRun | None:
        game_run = await self.get_by_id(run_id)
        if not game_run:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(game_run, field, value)

        self.db.add(game_run)
        await self.db.commit()
        await self.db.refresh(game_run)
        return game_run

    async def delete(self, run_id: UUID) -> bool:
        game_run = await self.get_by_id(run_id)
        if not game_run:
            return False

        await self.db.delete(game_run)
        await self.db.commit()
        return True


async def get_game_run_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GameRunService:
    return GameRunService(db)
