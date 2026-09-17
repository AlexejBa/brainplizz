from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.game_room import GameRoomStatus
from app.repositories.game_answer_repository import (
    GameAnswerRepository
)

from app.repositories.game_participant_repository import (
    GameParticipantRepository
)

from app.repositories.game_room_repository import GameRoomRepository
from app.repositories.question_repository import (
    QuestionRepository
)
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
        answer_repository = GameAnswerRepository(db)
        question_repository = QuestionRepository(db)

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

        if room.status == GameRoomStatus.PLAYING:
            current_question_id = game_manager.current_question(
                room_id
            )

            if current_question_id:
                remaining_seconds = game_manager.get_remaining_time(
                    room_id=room_id,
                    seconds=30
                )

                existing_answer = (
                    answer_repository.get_by_participant_and_question(
                        participant_id=participant.id,
                        question_id=current_question_id
                    )
                )

                selected_answer = (
                    existing_answer.selected_answer
                    if existing_answer
                    else None
                )

                current_question = question_repository.get_by_id(
                    current_question_id
                )

                correct_answer = (
                    current_question.correct_answer
                    if current_question
                    else None
                )

                game = game_manager.get_game(room_id)

                question_finished = (
                    game.question_finished
                    if game
                    else False
                )

                await connection_manager.send_to_user(
                    room_id=room_id,
                    user_id=user_id,
                    message={
                        "type": "current_question",
                        "room_id": str(room_id),
                        "question_id": str(current_question_id),
                        "remaining_seconds": remaining_seconds,
                        "selected_answer": selected_answer,
                        "correct_answer": correct_answer,
                        "question_finished": question_finished
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

            message_type = message.get("type")
            print(
                f"WEBSOCKET MESSAGE: "
                f"room={room_id}, "
                f"user={user_id}, "
                f"type={message_type}, "
                f"message={message}"
            )

            if message_type == "next_question":

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"получено сообщение от user={user_id}"
                )

                db.expire_all()
                current_room = room_repository.get_by_id(
                    room_id
                )
                print(
                    f"NEXT QUESTION DEBUG: "
                    f"room_found={current_room is not None}"
                )

                if not current_room:
                    await connection_manager.send_to_user(
                        room_id=room_id,
                        user_id=user_id,
                        message={
                            "type": "error",
                            "message": "Игровая комната не найдена"
                        }
                    )
                    continue

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"host_id={current_room.host_id}, "
                    f"user_id={user_id}"
                )

                if current_room.host_id != user_id:
                    await connection_manager.send_to_user(
                        room_id=room_id,
                        user_id=user_id,
                        message={
                            "type": "error",
                            "message": (
                                "Только хост может перейти "
                                "к следующему вопросу"
                            )
                        }
                    )
                    continue

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"room_status={current_room.status}"
                )

                if current_room.status != GameRoomStatus.PLAYING:
                    await connection_manager.send_to_user(
                        room_id=room_id,
                        user_id=user_id,
                        message={
                            "type": "error",
                            "message": (
                                "Игра не находится "
                                "в активном состоянии"
                            )
                        }
                    )
                    continue

                game = game_manager.get_game(
                    room_id
                )
                print(
                    f"NEXT QUESTION DEBUG: "
                    f"game_found={game is not None}"
                )

                if not game:
                    await connection_manager.send_to_user(
                        room_id=room_id,
                        user_id=user_id,
                        message={
                            "type": "error",
                            "message": "Состояние игры не найдено"
                        }
                    )
                    continue

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"question_finished={game.question_finished}"
                )

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"current_question_index="
                    f"{game.current_question_index}, "
                    f"total_questions="
                    f"{len(game.question_ids)}"
                )

                if not game.question_finished:
                    await connection_manager.send_to_user(
                        room_id=room_id,
                        user_id=user_id,
                        message={
                            "type": "error",
                            "message": (
                                "Текущий вопрос ещё не завершён"
                            )
                        }
                    )
                    continue


                is_last = game_manager.is_last_question(
                    room_id
                )

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"is_last_question={is_last}"
                )

                if is_last:
                    current_room.status = GameRoomStatus.FINISHED

                    room_repository.update(
                        current_room
                    )

                    await connection_manager.broadcast(
                        room_id=room_id,
                        message={
                            "type": "game_finished",
                            "room_id": str(room_id)
                        }
                    )

                    game_manager.remove_game(
                        room_id
                    )

                    continue

                print(
                    "NEXT QUESTION DEBUG: "
                    "переходим к следующему вопросу"
                )


                next_question_id = game_manager.next_question(
                    room_id
                )

                print(
                    f"NEXT QUESTION DEBUG: "
                    f"next_question_id={next_question_id}"
                )

                if not next_question_id:
                    await connection_manager.send_to_user(
                        room_id=room_id,
                        user_id=user_id,
                        message={
                            "type": "error",
                            "message": (
                                "Не удалось перейти "
                                "к следующему вопросу"
                            )
                        }
                    )
                    continue

                game = game_manager.get_game(
                    room_id
                )

                if not game:
                    continue

                game_manager.start_question_timer(
                    room_id=room_id,
                    seconds=30
                )

                await connection_manager.broadcast(
                    room_id=room_id,
                    message={
                        "type": "next_question",
                        "room_id": str(room_id),
                        "question_id": str(next_question_id),
                        "question_number": (
                            game.current_question_index + 1
                        ),
                        "total_questions": len(
                            game.question_ids
                        )
                    }
                )

                continue

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