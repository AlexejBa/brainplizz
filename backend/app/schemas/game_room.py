from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.game_room import GameRoomStatus


class CreateRoomRequest(BaseModel):
    max_players: int = Field(
        default=8,
        ge=2,
        le=20
    )


class GameRoomResponse(BaseModel):
    id: UUID
    code: str
    host_id: UUID
    status: GameRoomStatus
    max_players: int
    created_at: datetime