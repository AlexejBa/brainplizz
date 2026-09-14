from uuid import UUID

from app.services.game_manager import GameManager
from app.websocket_manager import ConnectionManager


connection_manager = ConnectionManager()


async def on_game_finished(
    room_id: UUID
) -> None:

    from app.services.game_finish_service import (
        finish_game_by_timeout
    )

    await finish_game_by_timeout(
        room_id=room_id,
        game_manager=game_manager,
        connection_manager=connection_manager
    )


game_manager = GameManager(
    connection_manager=connection_manager,
    on_game_finished=on_game_finished
)