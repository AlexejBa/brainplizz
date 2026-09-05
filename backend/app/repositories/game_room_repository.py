from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game_room import GameRoom


class GameRoomRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, room: GameRoom) -> GameRoom:
        self.session.add(room)
        self.session.commit()
        self.session.refresh(room)

        return room

    def get_by_id(self, room_id: UUID) -> GameRoom | None:
        statement = select(GameRoom).where(GameRoom.id == room_id)
        return self.session.scalar(statement)

    def get_by_code(self, code: str) -> GameRoom | None:
        statement = select(GameRoom).where(GameRoom.code == code)
        return self.session.scalar(statement)

    def update(self, room: GameRoom) -> GameRoom:
        self.session.commit()
        self.session.refresh(room)

        return room

    def delete(self, room: GameRoom) -> None:
        self.session.delete(room)
        self.session.commit()