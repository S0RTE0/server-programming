import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.item import ItemCreate, ItemRead, ItemUpdate
from services.items import ItemService, get_item_service
from utils.security import AccessTokenDepend, AdminDepend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["Items"])

ItemServiceDepend = Annotated[ItemService, Depends(get_item_service)]


@router.get(path="/", response_model=list[ItemRead])
async def get_items(item_service: ItemServiceDepend):
    try:
        return await item_service.get_all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get items")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get items",
        ) from exc


@router.get(path="/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, item_service: ItemServiceDepend):
    try:
        item = await item_service.get_by_id(item_id=item_id)

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
async def create_item(
    item_data: ItemCreate,
    item_service: ItemServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        return await item_service.create(data=item_data)
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
    item_service: ItemServiceDepend,
    _token: AccessTokenDepend,
):
    try:
        item = await item_service.update(item_id=item_id, data=item_update)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        return item
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
async def delete_item(
    item_id: int,
    item_service: ItemServiceDepend,
    _admin: AdminDepend,
):
    try:
        deleted = await item_service.delete(item_id=item_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        return
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete item with id %d", item_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        ) from exc
