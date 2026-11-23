from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .run_item import RunItem


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)

    run_items: Mapped[list[RunItem]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
