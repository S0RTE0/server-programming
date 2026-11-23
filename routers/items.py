import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.db import get_db
from models.item import Item
from schemas.item import ItemCreate, ItemRead, ItemUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["Items"])

SessionDepend = Annotated[AsyncSession, Depends(get_db)]


@router.get(path="/", response_model=list[ItemRead])
async def get_items(session: SessionDepend):
    try:
        result = await session.execute(select(Item))
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get items")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get items",
        ) from exc


@router.get(path="/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, session: SessionDepend):
    try:
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalars().first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        return item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get item with id %d", item_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get item",
        ) from exc


@router.post(
    path="/",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(item_data: ItemCreate, session: SessionDepend):
    try:
        new_item = Item(**item_data.model_dump())
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create item")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create item",
        ) from exc


@router.put(path="/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    session: SessionDepend,
):
    try:
        result = await session.execute(select(Item).where(Item.id == item_id))
        existing_item = result.scalars().first()

        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        for field, value in item_update.model_dump(exclude_unset=True).items():
            setattr(existing_item, field, value)

        session.add(existing_item)
        await session.commit()
        await session.refresh(existing_item)
        return existing_item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update item with id %d", item_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update item",
        ) from exc


@router.delete(
    path="/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_item(item_id: int, session: SessionDepend):
    try:
        result = await session.execute(select(Item).where(Item.id == item_id))
        existing_item = result.scalars().first()

        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        await session.delete(existing_item)
        await session.commit()
        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete item with id %d", item_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        ) from exc
