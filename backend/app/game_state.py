from app.services.game_manager import GameManager
from app.websocket_manager import ConnectionManager


connection_manager = ConnectionManager()

game_manager = GameManager(
    connection_manager=connection_manager
)