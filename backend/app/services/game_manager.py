import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from math import ceil
from typing import Awaitable, Callable
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

    question_finished: bool = False
    finished_remaining_seconds: int | None = None

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
        connection_manager: ConnectionManager,
        on_question_finished: (
            Callable[[UUID, UUID], Awaitable[None]] | None
        ) = None
    ):
        self.connection_manager = connection_manager
        self.on_question_finished = on_question_finished

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

    def get_time_bonus(
        self,
        room_id: UUID
    ) -> int:

        game = self.get_game(room_id)

        if not game:
            return 0

        if not game.question_started_at:
            return 0

        elapsed_seconds = (
            datetime.utcnow() - game.question_started_at
        ).total_seconds()

        if elapsed_seconds <= 5:
            return 50

        if elapsed_seconds <= 10:
            return 30

        if elapsed_seconds <= 20:
            return 15

        if elapsed_seconds <= 30:
            return 5

        return 0

    def get_remaining_time(
        self,
        room_id: UUID,
        seconds: int = 30
    ) -> int:

        game = self.get_game(room_id)

        if not game:
            return 0

        if not game.question_started_at:
            return seconds

        elapsed_seconds = (
            datetime.utcnow() - game.question_started_at
        ).total_seconds()

        remaining_seconds = seconds - elapsed_seconds

        return max(
            0,
            ceil(remaining_seconds)
        )

    def remove_game(
        self,
        room_id: UUID
    ) -> None:

        game = self.games.pop(
            room_id,
            None
        )

        if not game or not game.question_task:
            return

        current_task = asyncio.current_task()

        if game.question_task is not current_task:
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
        game.question_finished = False
        game.finished_remaining_seconds = None

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

            while True:
                game = self.get_game(room_id)

                if not game:
                    return

                game.finished_remaining_seconds = self.get_remaining_time(
                    room_id=room_id,
                    seconds=seconds
                )

                if game.question_finished:
                    return

                current_question_id = game.current_question_id

                if not current_question_id:
                    return

                remaining_seconds = self.get_remaining_time(
                    room_id=room_id,
                    seconds=seconds
                )

                await self.connection_manager.broadcast(
                    room_id=room_id,
                    message={
                        "type": "timer_update",
                        "room_id": str(room_id),
                        "question_id": str(current_question_id),
                        "remaining_seconds": remaining_seconds
                    }
                )

                if remaining_seconds <= 0:
                    break

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            return

        game = self.get_game(room_id)

        if not game:
            return

        if game.question_finished:
            return

        current_question_id = game.current_question_id

        if not current_question_id:
            return

        game.question_finished = True

        await self.connection_manager.broadcast(
            room_id=room_id,
            message={
                "type": "question_timeout",
                "question_id": str(current_question_id)
            }
        )

        if self.on_question_finished:
            await self.on_question_finished(
                room_id,
                current_question_id
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

        if not game.question_finished:
            return None

        if self.is_last_question(room_id):
            return None

        self.cancel_question_timer(room_id)

        game.current_question_index += 1
        game.answered_players.clear()
        game.question_started_at = None
        game.question_finished = False

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