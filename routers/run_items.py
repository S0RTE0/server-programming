import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.run_item import RunItemCreate, RunItemRead, RunItemUpdate
from services.run_items import RunItemService, get_run_item_service
from utils.security import AccessTokenDepend, AdminDepend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run-items", tags=["RunItems"])

RunItemServiceDepend = Annotated[RunItemService, Depends(get_run_item_service)]


@router.get(path="/", response_model=list[RunItemRead])
async def get_run_items(run_item_service: RunItemServiceDepend):
    try:
        return await run_item_service.get_all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get run items")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get run items",
        ) from exc


@router.get(path="/{run_id}/{item_id}", response_model=RunItemRead)
async def get_run_item(
    run_id: UUID,
    item_id: int,
    run_item_service: RunItemServiceDepend,
):
    try:
        run_item = await run_item_service.get_by_id(run_id=run_id, item_id=item_id)

        if not run_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RunItem not found",
            )

        return run_item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to get run item with run_id %s and item_id %d", run_id, item_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get run item",
        ) from exc


@router.post(
    path="/",
    response_model=RunItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_run_item(
    run_item_data: RunItemCreate,
    run_item_service: RunItemServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        return await run_item_service.create(data=run_item_data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create run item")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create run item",
        ) from exc


@router.put(path="/{run_id}/{item_id}", response_model=RunItemRead)
async def update_run_item(
    run_id: UUID,
    item_id: int,
    run_item_update: RunItemUpdate,
    run_item_service: RunItemServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        run_item = await run_item_service.update(
            run_id=run_id, item_id=item_id, data=run_item_update
        )

        if not run_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RunItem not found",
            )

        return run_item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to update run item with run_id %s and item_id %d", run_id, item_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update run item",
        ) from exc


@router.delete(
    path="/{run_id}/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_run_item(
    run_id: UUID,
    item_id: int,
    run_item_service: RunItemServiceDepend,
    _admin: AdminDepend,
):
    try:
        deleted = await run_item_service.delete(run_id=run_id, item_id=item_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RunItem not found",
            )

        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to delete run item with run_id %s and item_id %d", run_id, item_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete run item",
        ) from exc
