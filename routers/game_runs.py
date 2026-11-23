import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.game_run import GameRunCreate, GameRunRead, GameRunUpdate
from services.game_runs import GameRunService, get_game_run_service
from utils.security import AccessTokenDepend, AdminDepend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game-runs", tags=["GameRuns"])

GameRunServiceDepend = Annotated[GameRunService, Depends(get_game_run_service)]


@router.get(path="/", response_model=list[GameRunRead])
async def get_game_runs(game_run_service: GameRunServiceDepend):
    try:
        return await game_run_service.get_all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get game runs")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get game runs",
        ) from exc


@router.get(path="/{run_id}", response_model=GameRunRead)
async def get_game_run(run_id: UUID, game_run_service: GameRunServiceDepend):
    try:
        game_run = await game_run_service.get_by_id(run_id=run_id)

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
async def create_game_run(
    run_data: GameRunCreate,
    game_run_service: GameRunServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        return await game_run_service.create(data=run_data)
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
    game_run_service: GameRunServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        game_run = await game_run_service.update(run_id=run_id, data=run_update)

        if not game_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GameRun not found",
            )

        return game_run
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
async def delete_game_run(
    run_id: UUID,
    game_run_service: GameRunServiceDepend,
    _admin: AdminDepend,
):
    try:
        deleted = await game_run_service.delete(run_id=run_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GameRun not found",
            )

        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete game run with id %s", run_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete game run",
        ) from exc
