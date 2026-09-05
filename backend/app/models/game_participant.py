from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class GameParticipant(Base):
    __tablename__ = "game_participants"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_rooms.id"),
        nullable=False
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    is_ready: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )