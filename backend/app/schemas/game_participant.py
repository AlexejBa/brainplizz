from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JoinRoomRequest(BaseModel):

    code: str = Field(
        min_length=6,
        max_length=6
    )


class GameParticipantResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    username: str
    room_id: UUID
    score: int
    is_ready: bool