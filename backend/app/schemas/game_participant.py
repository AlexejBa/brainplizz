from uuid import UUID

from pydantic import BaseModel, Field


class JoinRoomRequest(BaseModel):
    code: str = Field(
        min_length=6,
        max_length=6
    )


class GameParticipantResponse(BaseModel):
    id: UUID
    user_id: UUID
    room_id: UUID
    score: int
    is_ready: bool