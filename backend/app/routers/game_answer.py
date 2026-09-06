from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db
from app.models.game_answer import GameAnswer

from app.repositories.game_answer_repository import GameAnswerRepository
from app.repositories.game_participant_repository import GameParticipantRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.game_answer import (
    GameAnswerResponse,
    GameStatisticsResponse,
    GameResultResponse,
    SubmitAnswerRequest
)
from app.models.game_room import GameRoom
from app.repositories.game_room_repository import GameRoomRepository
from app.schemas.question import GameQuestionResponse

router = APIRouter(
    prefix="/game",
    tags=["Game"]
)


@router.post(
    "/answers",
    response_model=GameAnswerResponse,
    status_code=201
)
def submit_answer(
    data: SubmitAnswerRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    answer_repository = GameAnswerRepository(db)
    participant_repository = GameParticipantRepository(db)
    question_repository = QuestionRepository(db)
    room_repository = GameRoomRepository(db)

    participant = participant_repository.get_by_id(
        data.participant_id
    )

    if not participant:
        raise HTTPException(
            status_code=404,
            detail="Участник не найден"
        )

    if participant.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете отвечать от имени другого участника"
        )

    question = question_repository.get_by_id(
        data.question_id
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Вопрос не найден"
        )

    existing_answer = (
        answer_repository.get_by_participant_and_question(
            participant_id=data.participant_id,
            question_id=data.question_id
        )
    )

    if existing_answer:
        raise HTTPException(
            status_code=409,
            detail="Вы уже отвечали на этот вопрос"
        )

    is_correct = (
        data.selected_answer == question.correct_answer
    )

    score = 100 if is_correct else 0

    answer = GameAnswer(
        participant_id=data.participant_id,
        question_id=data.question_id,
        selected_answer=data.selected_answer,
        is_correct=is_correct,
        score=score
    )

    created_answer = answer_repository.create(answer)

    participant.score += score

    participant_repository.update(participant)

    room = room_repository.get_by_id(
        participant.room_id
    )

    participants = participant_repository.get_by_room(
        participant.room_id
    )

    questions = question_repository.get_all()

    answers = answer_repository.get_by_room(
        participant.room_id
    )

    required_answers = len(participants) * len(questions)

    if len(answers) >= required_answers:
        room.status = "finished"
        room_repository.update(room)

    return created_answer

@router.get(
    "/rooms/{room_id}/question",
    response_model=GameQuestionResponse
)
def get_current_question(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    room_repository = GameRoomRepository(db)
    participant_repository = GameParticipantRepository(db)
    question_repository = QuestionRepository(db)
    answer_repository = GameAnswerRepository(db)

    room = room_repository.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    if room.status != "playing":
        raise HTTPException(
            status_code=400,
            detail="Игра ещё не началась"
        )

    participant = participant_repository.get_by_user_and_room(
        user_id=user_id,
        room_id=room_id
    )

    if not participant:
        raise HTTPException(
            status_code=403,
            detail="Вы не являетесь участником этой комнаты"
        )

    questions = question_repository.get_all()

    if not questions:
        raise HTTPException(
            status_code=404,
            detail="Вопросы для игры не найдены"
        )

    answers = answer_repository.get_by_participant(
        participant.id
    )

    answered_question_ids = {
        answer.question_id
        for answer in answers
    }

    for question in questions:
        if question.id not in answered_question_ids:
            return question

    raise HTTPException(
        status_code=404,
        detail="Все вопросы уже пройдены"
    )

@router.get(
    "/participants/{participant_id}/statistics",
    response_model=GameStatisticsResponse
)
def get_game_statistics(
    participant_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    participant_repository = GameParticipantRepository(db)
    answer_repository = GameAnswerRepository(db)

    participant = participant_repository.get_by_id(
        participant_id
    )

    if not participant:
        raise HTTPException(
            status_code=404,
            detail="Участник не найден"
        )

    if participant.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете просматривать статистику другого участника"
        )

    answered_count = answer_repository.get_answered_count(
        participant_id
    )

    correct_count = answer_repository.get_correct_count(
        participant_id
    )

    return GameStatisticsResponse(
        participant_id=participant.id,
        score=participant.score,
        answered_count=answered_count,
        correct_count=correct_count
    )

@router.post(
    "/rooms/{room_id}/finish",
    response_model=GameResultResponse
)
def finish_game(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    room_repository = GameRoomRepository(db)
    participant_repository = GameParticipantRepository(db)
    question_repository = QuestionRepository(db)
    answer_repository = GameAnswerRepository(db)

    room = room_repository.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    if room.status != "playing":
        raise HTTPException(
            status_code=400,
            detail="Игра не находится в активном состоянии"
        )

    current_participant = participant_repository.get_by_user_and_room(
        user_id=user_id,
        room_id=room_id
    )

    if not current_participant:
        raise HTTPException(
            status_code=403,
            detail="Вы не являетесь участником этой комнаты"
        )

    questions = question_repository.get_all()

    if not questions:
        raise HTTPException(
            status_code=404,
            detail="Вопросы для игры не найдены"
        )

    answers = answer_repository.get_by_participant(
        current_participant.id
    )

    if len(answers) < len(questions):
        raise HTTPException(
            status_code=400,
            detail="Вы ещё не ответили на все вопросы"
        )

    room.status = "finished"
    room_repository.update(room)

    participants = participant_repository.get_by_room(room_id)

    result_participants = []

    for participant in participants:
        participant_answers = answer_repository.get_by_participant(
            participant.id
        )

        answered_count = len(participant_answers)

        correct_count = sum(
            1
            for answer in participant_answers
            if answer.is_correct
        )

        result_participants.append(
            {
                "participant_id": participant.id,
                "user_id": participant.user_id,
                "score": participant.score,
                "answered_count": answered_count,
                "correct_count": correct_count,
                "place": 0
            }
        )

    result_participants.sort(
        key=lambda participant: participant["score"],
        reverse=True
    )

    for index, participant in enumerate(
        result_participants,
        start=1
    ):
        participant["place"] = index

    winner_id = None

    if result_participants:
        winner_id = result_participants[0]["participant_id"]

    return GameResultResponse(
        room_id=room.id,
        status=room.status.value,
        winner_id=winner_id,
        participants=result_participants
    )