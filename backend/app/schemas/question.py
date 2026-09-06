from uuid import UUID

from pydantic import BaseModel, Field


class CreateQuestionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

    answer_1: str = Field(min_length=1, max_length=255)
    answer_2: str = Field(min_length=1, max_length=255)
    answer_3: str = Field(min_length=1, max_length=255)
    answer_4: str = Field(min_length=1, max_length=255)

    correct_answer: int = Field(ge=1, le=4)


class QuestionResponse(BaseModel):
    id: UUID
    text: str

    answer_1: str
    answer_2: str
    answer_3: str
    answer_4: str

    correct_answer: int
class GameQuestionResponse(BaseModel):
    id: UUID
    text: str

    answer_1: str
    answer_2: str
    answer_3: str
    answer_4: str