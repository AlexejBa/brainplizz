from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db
from app.models.question import Question
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import (
    CreateQuestionRequest,
    QuestionResponse
)


router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=201
)
def create_question(
    data: CreateQuestionRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = QuestionRepository(db)

    question = Question(
        text=data.text,
        answer_1=data.answer_1,
        answer_2=data.answer_2,
        answer_3=data.answer_3,
        answer_4=data.answer_4,
        correct_answer=data.correct_answer
    )

    created_question = repository.create(question)

    return created_question


@router.get(
    "",
    response_model=list[QuestionResponse]
)
def get_questions(
    db: Session = Depends(get_db)
):
    repository = QuestionRepository(db)

    return repository.get_all()


@router.get(
    "/{question_id}",
    response_model=QuestionResponse
)
def get_question(
    question_id: UUID,
    db: Session = Depends(get_db)
):
    repository = QuestionRepository(db)

    question = repository.get_by_id(question_id)

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Вопрос не найден"
        )

    return question


@router.delete(
    "/{question_id}",
    status_code=204
)
def delete_question(
    question_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = QuestionRepository(db)

    question = repository.get_by_id(question_id)

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Вопрос не найден"
        )

    repository.delete(question)