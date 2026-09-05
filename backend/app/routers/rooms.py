from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db
from app.models.game_room import GameRoom
from app.models.game_participant import GameParticipant
from app.repositories.game_room_repository import GameRoomRepository
from app.repositories.game_participant_repository import GameParticipantRepository
from app.schemas.game_room import CreateRoomRequest, GameRoomResponse
from app.schemas.game_participant import (
    JoinRoomRequest,
    GameParticipantResponse
)
from app.utils.room_code import generate_room_code


router = APIRouter(
    prefix="/rooms",
    tags=["Game Rooms"]
)


@router.post(
    "",
    response_model=GameRoomResponse,
    status_code=201
)
def create_room(
    data: CreateRoomRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = GameRoomRepository(db)

    code = generate_room_code()

    while repository.get_by_code(code):
        code = generate_room_code()

    room = GameRoom(
        code=code,
        host_id=user_id,
        max_players=data.max_players
    )

    created_room = repository.create(room)

    return created_room


@router.get(
    "/{room_id}",
    response_model=GameRoomResponse
)
def get_room(
    room_id: UUID,
    db: Session = Depends(get_db)
):
    repository = GameRoomRepository(db)

    room = repository.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    return room


@router.post(
    "/join",
    response_model=GameParticipantResponse,
    status_code=201
)
def join_room(
    data: JoinRoomRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    room_repository = GameRoomRepository(db)
    participant_repository = GameParticipantRepository(db)

    room = room_repository.get_by_code(data.code.upper())

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    if room.status != "waiting":
        raise HTTPException(
            status_code=400,
            detail="В эту комнату нельзя присоединиться"
        )

    existing_participant = participant_repository.get_by_user_and_room(
        user_id=user_id,
        room_id=room.id
    )

    if existing_participant:
        raise HTTPException(
            status_code=409,
            detail="Вы уже находитесь в этой комнате"
        )

    participants = participant_repository.get_by_room(room.id)

    if len(participants) >= room.max_players:
        raise HTTPException(
            status_code=400,
            detail="Комната заполнена"
        )

    participant = GameParticipant(
        room_id=room.id,
        user_id=user_id
    )

    created_participant = participant_repository.create(participant)

    return created_participant

@router.get(
    "/{room_id}/participants",
    response_model=list[GameParticipantResponse]
)
def get_room_participants(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    room_repository = GameRoomRepository(db)
    participant_repository = GameParticipantRepository(db)

    room = room_repository.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
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

    participants = participant_repository.get_by_room(room_id)

    return participants

@router.post(
    "/{room_id}/ready",
    response_model=GameParticipantResponse
)
def set_ready(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    room_repository = GameRoomRepository(db)
    participant_repository = GameParticipantRepository(db)

    room = room_repository.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Игровая комната не найдена"
        )

    if room.status != "waiting":
        raise HTTPException(
            status_code=400,
            detail="Комната уже запущена"
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

    participant.is_ready = True

    updated_participant = participant_repository.update(participant)

    participants = participant_repository.get_by_room(room_id)

    all_ready = all(
        participant.is_ready
        for participant in participants
    )

    if all_ready:
        room.status = "playing"
        room_repository.update(room)

    return updated_participant

