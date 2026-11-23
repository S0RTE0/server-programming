import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models.player import Player
from schemas.player import PlayerCreate, PlayerRead, PlayerUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/players", tags=["Players"])

SessionDepend = Annotated[AsyncSession, Depends(get_db)]


@router.get(path="/", response_model=list[PlayerRead])
async def get_players(session: SessionDepend):
    try:
        result = await session.execute(select(Player))
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get players")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get players",
        ) from exc


@router.get(path="/{player_id}", response_model=PlayerRead)
async def get_player(player_id: UUID, session: SessionDepend):
    try:
        result = await session.execute(select(Player).where(Player.id == player_id))
        player = result.scalars().first()

        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )

        return player
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get player with id %s", player_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get player",
        ) from exc


@router.post(
    path="/",
    response_model=PlayerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_player(player_data: PlayerCreate, session: SessionDepend):
    try:
        new_player = Player(**player_data.model_dump())
        session.add(new_player)
        await session.commit()
        await session.refresh(new_player)
        return new_player
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create player")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create player",
        ) from exc


@router.put(path="/{player_id}", response_model=PlayerRead)
async def update_player(
    player_id: UUID,
    player_update: PlayerUpdate,
    session: SessionDepend,
):
    try:
        result = await session.execute(select(Player).where(Player.id == player_id))
        existing_player = result.scalars().first()

        if not existing_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )

        for field, value in player_update.model_dump(exclude_unset=True).items():
            setattr(existing_player, field, value)

        session.add(existing_player)
        await session.commit()
        await session.refresh(existing_player)
        return existing_player
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update player with id %s", player_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update player",
        ) from exc


@router.delete(
    path="/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_player(player_id: UUID, session: SessionDepend):
    try:
        result = await session.execute(select(Player).where(Player.id == player_id))
        existing_player = result.scalars().first()

        if not existing_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )

        await session.delete(existing_player)
        await session.commit()
        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete player with id %s", player_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete player",
        ) from exc
