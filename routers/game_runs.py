import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models.game_run import GameRun
from schemas.game_run import GameRunCreate, GameRunRead, GameRunUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game-runs", tags=["GameRuns"])

SessionDepend = Annotated[AsyncSession, Depends(get_db)]


@router.get(path="/", response_model=list[GameRunRead])
async def get_game_runs(session: SessionDepend):
    try:
        result = await session.execute(select(GameRun))
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get game runs")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get game runs",
        ) from exc


@router.get(path="/{run_id}", response_model=GameRunRead)
async def get_game_run(run_id: UUID, session: SessionDepend):
    try:
        result = await session.execute(select(GameRun).where(GameRun.id == run_id))
        game_run = result.scalars().first()

        if not game_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GameRun not found",
            )

        return game_run
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get game run with id %s", run_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get game run",
        ) from exc


@router.post(
    path="/",
    response_model=GameRunRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_game_run(run_data: GameRunCreate, session: SessionDepend):
    try:
        new_run = GameRun(**run_data.model_dump())
        session.add(new_run)
        await session.commit()
        await session.refresh(new_run)
        return new_run
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create game run")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game run",
        ) from exc


@router.put(path="/{run_id}", response_model=GameRunRead)
async def update_game_run(
    run_id: UUID,
    run_update: GameRunUpdate,
    session: SessionDepend,
):
    try:
        result = await session.execute(select(GameRun).where(GameRun.id == run_id))
        existing_run = result.scalars().first()

        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GameRun not found",
            )

        for field, value in run_update.model_dump(exclude_unset=True).items():
            setattr(existing_run, field, value)

        session.add(existing_run)
        await session.commit()
        await session.refresh(existing_run)
        return existing_run
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update game run with id %s", run_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update game run",
        ) from exc


@router.delete(
    path="/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_game_run(run_id: UUID, session: SessionDepend):
    try:
        result = await session.execute(select(GameRun).where(GameRun.id == run_id))
        existing_run = result.scalars().first()

        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GameRun not found",
            )

        await session.delete(existing_run)
        await session.commit()
        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete game run with id %s", run_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete game run",
        ) from exc
