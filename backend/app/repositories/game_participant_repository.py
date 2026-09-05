from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game_participant import GameParticipant


class GameParticipantRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        participant: GameParticipant
    ) -> GameParticipant:
        self.session.add(participant)
        self.session.commit()
        self.session.refresh(participant)

        return participant

    def get_by_id(
        self,
        participant_id: UUID
    ) -> GameParticipant | None:
        statement = select(GameParticipant).where(
            GameParticipant.id == participant_id
        )
        return self.session.scalar(statement)

    def get_by_user_and_room(
        self,
        user_id: UUID,
        room_id: UUID
    ) -> GameParticipant | None:
        statement = select(GameParticipant).where(
            GameParticipant.user_id == user_id,
            GameParticipant.room_id == room_id
        )
        return self.session.scalar(statement)

    def get_by_room(
        self,
        room_id: UUID
    ) -> list[GameParticipant]:
        statement = select(GameParticipant).where(
            GameParticipant.room_id == room_id
        )
        return list(self.session.scalars(statement).all())

    def update(
        self,
        participant: GameParticipant
    ) -> GameParticipant:
        self.session.commit()
        self.session.refresh(participant)

        return participant

    def delete(
        self,
        participant: GameParticipant
    ) -> None:
        self.session.delete(participant)
        self.session.commit()