from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game_answer import GameAnswer
from app.models.game_participant import GameParticipant


class GameAnswerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, answer: GameAnswer) -> GameAnswer:
        self.session.add(answer)
        self.session.commit()
        self.session.refresh(answer)

        return answer

    def get_by_id(self, answer_id: UUID) -> GameAnswer | None:
        statement = select(GameAnswer).where(
            GameAnswer.id == answer_id
        )

        return self.session.scalar(statement)

    def get_by_participant_and_question(
        self,
        participant_id: UUID,
        question_id: UUID
    ) -> GameAnswer | None:
        statement = select(GameAnswer).where(
            GameAnswer.participant_id == participant_id,
            GameAnswer.question_id == question_id
        )

        return self.session.scalar(statement)

    def get_by_participant(
        self,
        participant_id: UUID
    ) -> list[GameAnswer]:
        statement = select(GameAnswer).where(
            GameAnswer.participant_id == participant_id
        )

        return list(
            self.session.scalars(statement).all()
        )

    def get_correct_count(
            self,
            participant_id: UUID
    ) -> int:
        statement = select(GameAnswer).where(
            GameAnswer.participant_id == participant_id,
            GameAnswer.is_correct == True
        )

        return len(
            self.session.scalars(statement).all()
        )

    def get_answered_count(
            self,
            participant_id: UUID
    ) -> int:
        statement = select(GameAnswer).where(
            GameAnswer.participant_id == participant_id
        )

        return len(
            self.session.scalars(statement).all()
        )

    def get_by_room(
        self,
        room_id: UUID
    ) -> list[GameAnswer]:
        statement = select(GameAnswer).join(
            GameParticipant,
            GameAnswer.participant_id == GameParticipant.id
        ).where(
            GameParticipant.room_id == room_id
        )

        return list(
            self.session.scalars(statement).all()
        )

    def delete(self, answer: GameAnswer) -> None:
        self.session.delete(answer)
        self.session.commit()