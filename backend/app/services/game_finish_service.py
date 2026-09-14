from uuid import UUID
from typing import Any

from app.database import SessionLocal
from app.models.game_room import GameRoomStatus
from app.repositories.game_room_repository import GameRoomRepository


async def finish_game_by_timeout(
    room_id: UUID,
    game_manager: Any,
    connection_manager: Any
) -> None:

    db = SessionLocal()

    try:
        room_repository = GameRoomRepository(db)

        room = room_repository.get_by_id(room_id)

        if not room:
            print(
                f"GAME FINISH ERROR: room not found, room={room_id}"
            )
            return

        if room.status != GameRoomStatus.PLAYING:
            return

        room.status = GameRoomStatus.FINISHED

        room_repository.update(room)

        await connection_manager.broadcast(
            room_id=room_id,
            message={
                "type": "game_finished",
                "room_id": str(room_id),
                "reason": "timeout"
            }
        )

        game_manager.remove_game(room_id)

    except Exception as error:
        print(
            f"GAME FINISH ERROR: room={room_id}, error={error}"
        )

    finally:
        db.close()