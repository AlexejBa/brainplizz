from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class GameAnswer(Base):
    __tablename__ = "game_answers"

    __table_args__ = (UniqueConstraint(
        "participant_id",
        "question_id",
        name="uq_game_answer_participant_question"),
    )
    
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    participant_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_participants.id"),
        nullable=False
    )

    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False
    )

    selected_answer: Mapped[int] = mapped_column(
        nullable=False
    )

    is_correct: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    answered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )