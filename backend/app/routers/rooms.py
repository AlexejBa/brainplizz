from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db
from app.models.game_room import GameRoom
from app.repositories.game_room_repository import GameRoomRepository
from app.schemas.game_room import CreateRoomRequest, GameRoomResponse
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
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = GameRoomRepository(db)

    code = generate_room_code()

    while repository.get_by_code(code):
        code = generate_room_code()

    room = GameRoom(
        code=code,
        host_id=user_id
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