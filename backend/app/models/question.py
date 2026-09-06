from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    answer_1: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    answer_2: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    answer_3: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    answer_4: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    correct_answer: Mapped[int] = mapped_column(
        nullable=False
    )