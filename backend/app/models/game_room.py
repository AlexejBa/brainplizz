from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class GameRoomStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


class GameRoom(Base):
    __tablename__ = "game_rooms"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    code: Mapped[str] = mapped_column(
        String(6),
        unique=True,
        nullable=False,
        index=True
    )

    host_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    status: Mapped[GameRoomStatus] = mapped_column(
        default=GameRoomStatus.WAITING,
        nullable=False
    )

    max_players: Mapped[int] = mapped_column(
        default=8,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )