import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from services.players import PlayerService, get_player_service
from utils.security import AccessTokenDepend, AdminDepend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/players", tags=["Players"])

PlayerServiceDepend = Annotated[PlayerService, Depends(get_player_service)]


@router.get(path="/", response_model=list[PlayerRead])
async def get_players(player_service: PlayerServiceDepend):
    try:
        return await player_service.get_all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get players")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get players",
        ) from exc


@router.get(path="/{player_id}", response_model=PlayerRead)
async def get_player(player_id: UUID, player_service: PlayerServiceDepend):
    try:
        player = await player_service.get_by_id(player_id=player_id)

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
async def create_player(
    player_data: PlayerCreate,
    player_service: PlayerServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        return await player_service.create(data=player_data)
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
    player_service: PlayerServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        player = await player_service.update(player_id=player_id, data=player_update)

        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )

        return player
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
async def delete_player(
    player_id: UUID,
    player_service: PlayerServiceDepend,
    _admin: AdminDepend,
):
    try:
        deleted = await player_service.delete(player_id=player_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )

        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete player with id %s", player_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete player",
        ) from exc
