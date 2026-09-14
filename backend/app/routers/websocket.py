from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.game_participant_repository import (
    GameParticipantRepository
)
from app.repositories.game_room_repository import GameRoomRepository
from app.game_state import (
    connection_manager,
    game_manager
)


router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"]
)


@router.websocket("/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: UUID
):
    db: Session = SessionLocal()

    user_id = None

    try:
        user_id_param = websocket.query_params.get("user_id")

        if not user_id_param:
            await websocket.close(code=4001)
            return

        user_id = UUID(user_id_param)

        room_repository = GameRoomRepository(db)
        participant_repository = GameParticipantRepository(db)

        room = room_repository.get_by_id(room_id)

        if not room:
            await websocket.close(code=4004)
            return

        participant = (
            participant_repository.get_by_user_and_room(
                user_id=user_id,
                room_id=room_id
            )
        )

        if not participant:
            await websocket.close(code=4003)
            return

        await connection_manager.connect(
            room_id=room_id,
            user_id=user_id,
            websocket=websocket
        )

        await connection_manager.send_to_user(
            room_id=room_id,
            user_id=user_id,
            message={
                "type": "connected",
                "room_id": str(room_id),
                "user_id": str(user_id)
            }
        )

        if room.status == "playing":
            current_question_id = game_manager.current_question(
                room_id
            )

            if current_question_id:
                remaining_seconds = game_manager.get_remaining_time(
                    room_id=room_id,
                    seconds=30
                )

                await connection_manager.send_to_user(
                    room_id=room_id,
                    user_id=user_id,
                    message={
                        "type": "current_question",
                        "room_id": str(room_id),
                        "question_id": str(current_question_id),
                        "remaining_seconds": remaining_seconds
                    }
                )



        await connection_manager.broadcast(
            room_id=room_id,
            message={
                "type": "player_connected",
                "user_id": str(user_id)
            }
        )
        
        await connection_manager.broadcast(
            room_id=room_id,
            message={
                "type": "presence_updated",
                "connected_user_ids": [
                    str(connected_user_id)
                    for connected_user_id
                    in connection_manager.get_connected_user_ids(room_id)
                ]
            }
        )

        while True:
            message = await websocket.receive_json()

            await connection_manager.broadcast(
                room_id=room_id,
                message={
                    "type": "message",
                    "user_id": str(user_id),
                    "data": message
                }
            )

    except WebSocketDisconnect:
        if user_id is not None:
            connection_manager.disconnect(
                room_id=room_id,
                user_id=user_id
            )

            await connection_manager.broadcast(
                room_id=room_id,
                message={
                    "type": "player_disconnected",
                    "user_id": str(user_id)
                }
            )


            await connection_manager.broadcast(
                room_id=room_id,
                message={
                    "type": "presence_updated",
                    "connected_user_ids": [
                        str(connected_user_id)
                        for connected_user_id
                        in connection_manager.get_connected_user_ids(room_id)
                    ]
                }
            )

    finally:
        db.close()