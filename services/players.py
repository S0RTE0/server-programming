from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models import Player
from schemas.player import PlayerCreate, PlayerUpdate


class PlayerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[Player]:
        result = await self.db.execute(select(Player))
        return result.scalars().all()

    async def get_by_id(self, player_id: UUID) -> Player | None:
        result = await self.db.execute(select(Player).where(Player.id == player_id))
        return result.scalars().first()

    async def create(self, data: PlayerCreate) -> Player:
        new_player = Player(**data.model_dump())
        self.db.add(new_player)
        await self.db.commit()
        await self.db.refresh(new_player)
        return new_player

    async def update(self, player_id: UUID, data: PlayerUpdate) -> Player | None:
        player = await self.get_by_id(player_id)
        if not player:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(player, field, value)

        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player

    async def delete(self, player_id: UUID) -> bool:
        player = await self.get_by_id(player_id)
        if not player:
            return False

        await self.db.delete(player)
        await self.db.commit()
        return True


async def get_player_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlayerService:
    return PlayerService(db)
