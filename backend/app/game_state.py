from uuid import UUID

from app.database import SessionLocal
from app.repositories.question_repository import QuestionRepository
from app.repositories.game_answer_repository import GameAnswerRepository
from app.repositories.game_participant_repository import (
    GameParticipantRepository
)
from app.services.game_manager import GameManager
from app.websocket_manager import ConnectionManager


connection_manager = ConnectionManager()


async def on_question_finished(
    room_id: UUID,
    question_id: UUID
) -> None:
    db = SessionLocal()
    print(
        f"QUESTION FINISHED CALLBACK: "
        f"room={room_id}, question={question_id}"
    )

    try:
        question_repository = QuestionRepository(db)
        game_answer_repository = GameAnswerRepository(db)
        participant_repository = GameParticipantRepository(db)

        question = question_repository.get_by_id(
            question_id
        )

        if not question:
            print(
                f"QUESTION RESULT ERROR: "
                f"question not found, question={question_id}"
            )
            return

        participants = participant_repository.get_by_room(
            room_id
        )

        for participant in participants:
            answer = (
                game_answer_repository
                .get_by_participant_and_question(
                    participant_id=participant.id,
                    question_id=question_id
                )
            )

            selected_answer = (
                answer.selected_answer
                if answer
                else None
            )
            print(
                f"QUESTION RESULT SEND: "
                f"room={room_id}, "
                f"user={participant.user_id}, "
                f"selected_answer={selected_answer}"
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

    except Exception as error:
        print(
            f"QUESTION RESULT ERROR: "
            f"room={room_id}, "
            f"question={question_id}, "
            f"error={error}"
        )

    finally:
        db.close()



game_manager = GameManager(
    connection_manager=connection_manager,
    on_question_finished=on_question_finished
)