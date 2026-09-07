import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.websocket_manager import ConnectionManager


@dataclass
class RoomGameState:
    room_id: UUID
    question_ids: list[UUID]

    current_question_index: int = 0

    question_started_at: datetime | None = None

    answered_players: set[UUID] = field(
        default_factory=set
    )

    question_task: asyncio.Task | None = None

    @property
    def current_question_id(self) -> UUID | None:
        if self.current_question_index >= len(
            self.question_ids
        ):
            return None

        return self.question_ids[
            self.current_question_index
        ]


class GameManager:
    def __init__(
        self,
        connection_manager: ConnectionManager
    ):
        self.connection_manager = connection_manager

        self.games: dict[
            UUID,
            RoomGameState
        ] = {}

    def create_game(
        self,
        room_id: UUID,
        question_ids: list[UUID]
    ) -> RoomGameState:

        game = RoomGameState(
            room_id=room_id,
            question_ids=question_ids
        )

        self.games[room_id] = game

        return game

    def get_game(
        self,
        room_id: UUID
    ) -> RoomGameState | None:

        return self.games.get(room_id)

    def remove_game(
        self,
        room_id: UUID
    ) -> None:

        game = self.games.pop(
            room_id,
            None
        )

        if game and game.question_task:
            game.question_task.cancel()

    def mark_answered(
        self,
        room_id: UUID,
        user_id: UUID
    ) -> bool:

        game = self.get_game(room_id)

        if not game:
            return False

        if user_id in game.answered_players:
            return False

        game.answered_players.add(user_id)

        return True

    def all_players_answered(
        self,
        room_id: UUID,
        player_ids: list[UUID]
    ) -> bool:

        game = self.get_game(room_id)

        if not game:
            return False

        return all(
            player_id in game.answered_players
            for player_id in player_ids
        )

    def start_question_timer(
        self,
        room_id: UUID,
        seconds: int
    ) -> None:

        game = self.get_game(room_id)

        if not game:
            return

        if game.question_task:
            game.question_task.cancel()

        game.question_started_at = datetime.utcnow()

        game.question_task = asyncio.create_task(
            self._question_timer(
                room_id=room_id,
                seconds=seconds
            )
        )

    async def _question_timer(
        self,
        room_id: UUID,
        seconds: int
    ) -> None:

        try:
            await asyncio.sleep(seconds)

        except asyncio.CancelledError:
            return

        game = self.get_game(room_id)

        if not game:
            return

        await self.connection_manager.broadcast(
            room_id=room_id,
            message={
                "type": "question_timeout"
            }
        )

    def cancel_question_timer(
        self,
        room_id: UUID
    ) -> None:

        game = self.get_game(room_id)

        if not game:
            return

        if game.question_task:
            game.question_task.cancel()

            game.question_task = None

    def next_question(
        self,
        room_id: UUID
    ) -> UUID | None:

        game = self.get_game(room_id)

        if not game:
            return None

        self.cancel_question_timer(room_id)

        game.current_question_index += 1

        game.answered_players.clear()

        game.question_started_at = None

        return game.current_question_id

    def current_question(
        self,
        room_id: UUID
    ) -> UUID | None:

        game = self.get_game(room_id)

        if not game:
            return None

        return game.current_question_id

    def is_last_question(
        self,
        room_id: UUID
    ) -> bool:

        game = self.get_game(room_id)

        if not game:
            return False

        return (
            game.current_question_index
            >= len(game.question_ids) - 1
        )