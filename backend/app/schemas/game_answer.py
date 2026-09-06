from uuid import UUID

from pydantic import BaseModel, Field


class SubmitAnswerRequest(BaseModel):
    participant_id: UUID
    question_id: UUID
    selected_answer: int = Field(ge=1, le=4)


class GameAnswerResponse(BaseModel):
    id: UUID
    participant_id: UUID
    question_id: UUID
    selected_answer: int
    is_correct: bool
    score: int

    class Config:
        from_attributes = True


class GameStatisticsResponse(BaseModel):
    participant_id: UUID
    score: int
    answered_count: int
    correct_count: int


class GameResultParticipant(BaseModel):
    participant_id: UUID
    user_id: UUID
    score: int
    answered_count: int
    correct_count: int
    place: int


class GameResultResponse(BaseModel):
    room_id: UUID
    status: str
    winner_id: UUID | None
    participants: list[GameResultParticipant]