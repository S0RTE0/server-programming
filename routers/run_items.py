import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models.run_item import RunItem
from schemas.run_item import RunItemCreate, RunItemRead, RunItemUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run-items", tags=["RunItems"])

SessionDepend = Annotated[AsyncSession, Depends(get_db)]


@router.get(path="/", response_model=list[RunItemRead])
async def get_run_items(session: SessionDepend):
    try:
        result = await session.execute(select(RunItem))
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get run items")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get run items",
        ) from exc


@router.get(path="/{run_id}/{item_id}", response_model=RunItemRead)
async def get_run_item(run_id: UUID, item_id: int, session: SessionDepend):
    try:
        result = await session.execute(
            select(RunItem).where(
                RunItem.run_id == run_id,
                RunItem.item_id == item_id,
            )
        )
        run_item = result.scalars().first()

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
async def create_run_item(run_item_data: RunItemCreate, session: SessionDepend):
    try:
        new_run_item = RunItem(**run_item_data.model_dump())
        session.add(new_run_item)
        await session.commit()
        await session.refresh(new_run_item)
        return new_run_item
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
    session: SessionDepend,
):
    try:
        result = await session.execute(
            select(RunItem).where(
                RunItem.run_id == run_id,
                RunItem.item_id == item_id,
            )
        )
        existing_run_item = result.scalars().first()

        if not existing_run_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RunItem not found",
            )

        for field, value in run_item_update.model_dump(exclude_unset=True).items():
            setattr(existing_run_item, field, value)

        session.add(existing_run_item)
        await session.commit()
        await session.refresh(existing_run_item)
        return existing_run_item
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
async def delete_run_item(run_id: UUID, item_id: int, session: SessionDepend):
    try:
        result = await session.execute(
            select(RunItem).where(
                RunItem.run_id == run_id,
                RunItem.item_id == item_id,
            )
        )
        existing_run_item = result.scalars().first()

        if not existing_run_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RunItem not found",
            )

        await session.delete(existing_run_item)
        await session.commit()
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
