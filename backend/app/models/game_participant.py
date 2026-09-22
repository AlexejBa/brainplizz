from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


class GameParticipant(Base):
    __tablename__ = "game_participants"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "room_id",
            name="uq_game_participant_user_room",
        ),
    )

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

    user = relationship("User")