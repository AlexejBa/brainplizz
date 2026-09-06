from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question


class QuestionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, question: Question) -> Question:
        self.session.add(question)
        self.session.commit()
        self.session.refresh(question)

        return question

    def get_by_id(self, question_id: UUID) -> Question | None:
        statement = select(Question).where(
            Question.id == question_id
        )

        return self.session.scalar(statement)

    def get_all(self) -> list[Question]:
        statement = select(Question)

        return list(
            self.session.scalars(statement).all()
        )

    def delete(self, question: Question) -> None:
        self.session.delete(question)
        self.session.commit()