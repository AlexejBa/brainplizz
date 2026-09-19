from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db

from app.models.game_answer import GameAnswer
from app.models.game_participant import GameParticipant
from app.models.game_room import GameRoom, GameRoomStatus
from app.models.user import User

from app.game_state import connection_manager, game_manager

from app.repositories.game_answer_repository import GameAnswerRepository
from app.repositories.game_participant_repository import (
    GameParticipantRepository
)
from app.repositories.question_repository import QuestionRepository
from app.repositories.game_room_repository import GameRoomRepository

from app.schemas.game_answer import (
    GameAnswerResponse,
    GameStatisticsResponse,
    GameResultParticipant,
    GameResultResponse,
    SubmitAnswerRequest
)

from app.schemas.question import GameQuestionResponse


router = APIRouter(
    prefix="/game",
    tags=["Game"]
)


def build_game_result(
    room_id: UUID,
    db: Session
) -> GameResultResponse:
    room_statement = select(GameRoom).where(
        GameRoom.id == room_id
    )

    room = db.scalar(room_statement)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    participants_statement = (
        select(GameParticipant, User.username)
        .join(
            User,
            User.id == GameParticipant.user_id
        )
        .where(
            GameParticipant.room_id == room_id
        )
        .order_by(
            GameParticipant.score.desc()
        )
    )

    participant_rows = db.execute(
        participants_statement
    ).all()

    result_participants = []

    for place, row in enumerate(
        participant_rows,
        start=1
    ):
        participant, username = row

        answered_count_statement = select(
            func.count(GameAnswer.id)
        ).where(
            GameAnswer.participant_id == participant.id
        )

        answered_count = db.scalar(
            answered_count_statement
        ) or 0

        correct_count_statement = select(
            func.count(GameAnswer.id)
        ).where(
            GameAnswer.participant_id == participant.id,
            GameAnswer.is_correct.is_(True)
        )

        correct_count = db.scalar(
            correct_count_statement
        ) or 0

        result_participants.append(
            GameResultParticipant(
                participant_id=participant.id,
                user_id=participant.user_id,
                username=username,
                score=participant.score,
                answered_count=answered_count,
                correct_count=correct_count,
                place=place
            )
        )

    room_status = (
        room.status.value
        if hasattr(room.status, "value")
        else room.status
    )

    winner_id = None

    if (
        room_status == GameRoomStatus.FINISHED.value
        and participant_rows
    ):
        winner_id = participant_rows[0][0].user_id

    return GameResultResponse(
        room_id=room.id,
        status=room_status,
        winner_id=winner_id,
        participants=result_participants
    )


async def broadcast_question_result(
    room_id: UUID,
    question_id: UUID,
    db: Session
) -> None:
    question_repository = QuestionRepository(db)
    participant_repository = GameParticipantRepository(db)
    answer_repository = GameAnswerRepository(db)

    question = question_repository.get_by_id(question_id)

    if not question:
        return

    participants = participant_repository.get_by_room(room_id)

    for participant in participants:
        answer = (
            answer_repository.get_by_participant_and_question(
                participant_id=participant.id,
                question_id=question_id
            )
        )

        selected_answer = (
            answer.selected_answer
            if answer
            else None
        )

        await connection_manager.send_to_user(
            room_id=room_id,
            user_id=participant.user_id,
            message={
                "type": "question_result",
                "room_id": str(room_id),
                "question_id": str(question_id),
                "correct_answer": question.correct_answer,
                "selected_answer": selected_answer
            }
        )


@router.post(
    "/answers",
    response_model=GameAnswerResponse,
    status_code=201
)
async def submit_answer(
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

    room = room_repository.get_by_id(
        participant.room_id
    )

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    if room.status != GameRoomStatus.PLAYING:
        raise HTTPException(
            status_code=400,
            detail="Игра не находится в активном состоянии"
        )

    game = game_manager.get_game(
        participant.room_id
    )

    if not game:
        raise HTTPException(
            status_code=400,
            detail="Состояние игры не найдено"
        )

    if game.question_finished:
        raise HTTPException(
            status_code=400,
            detail="Вопрос уже завершён"
        )

    current_question_id = game.current_question_id

    if current_question_id != data.question_id:
        raise HTTPException(
            status_code=400,
            detail="Этот вопрос сейчас не является активным"
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

    base_score = 100 if is_correct else 0

    time_bonus = (
        game_manager.get_time_bonus(participant.room_id)
        if is_correct
        else 0
    )

    score = base_score + time_bonus

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

    game_manager.mark_answered(
        room_id=participant.room_id,
        user_id=user_id
    )

    participants = participant_repository.get_by_room(
        participant.room_id
    )

    player_ids = [
        participant.user_id
        for participant in participants
    ]

    await connection_manager.broadcast(
        room_id=participant.room_id,
        message={
            "type": "player_answered",
            "user_id": str(user_id),
            "question_id": str(data.question_id),
            "is_correct": is_correct,
            "score": score
        }
    )

    all_answered = game_manager.all_players_answered(
        room_id=participant.room_id,
        player_ids=player_ids
    )

    if all_answered:
        game.question_finished = True

        game_manager.cancel_question_timer(
            participant.room_id
        )

        await broadcast_question_result(
            room_id=participant.room_id,
            question_id=data.question_id,
            db=db
        )

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

    room = room_repository.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    if room.status != GameRoomStatus.PLAYING:
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

    game = game_manager.get_game(room_id)

    if not game:
        raise HTTPException(
            status_code=400,
            detail="Состояние игры не найдено"
        )

    current_question_id = game.current_question_id

    if not current_question_id:
        raise HTTPException(
            status_code=404,
            detail="Текущий вопрос не найден"
        )

    question = question_repository.get_by_id(
        current_question_id
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Вопрос не найден"
        )

    return question


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


@router.get(
    "/rooms/{room_id}/leaderboard",
    response_model=GameResultResponse
)
def get_room_leaderboard(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    participant_repository = GameParticipantRepository(db)

    participant = participant_repository.get_by_user_and_room(
        user_id=user_id,
        room_id=room_id
    )

    if not participant:
        raise HTTPException(
            status_code=403,
            detail="Вы не являетесь участником этой комнаты"
        )

    return build_game_result(room_id, db)


