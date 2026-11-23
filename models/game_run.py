import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .player import Player
    from .run_item import RunItem


class GameRun(Base):
    __tablename__ = "game_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    waves_cleared: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    survival_time_sec: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    player: Mapped[Player] = relationship(back_populates="game_runs")
    run_items: Mapped[list[RunItem]] = relationship(
        back_populates="game_run", cascade="all, delete-orphan"
    )
