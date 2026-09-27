from app.database import SessionLocal
from app.models.question import Question


QUESTIONS = [
    {
        "text": "Какой язык программирования используется в серверной части BrainPlizz?",
        "answer_1": "Java",
        "answer_2": "Python",
        "answer_3": "C++",
        "answer_4": "PHP",
        "correct_answer": 2,
    },
    {
        "text": "Какой фреймворк используется в серверной части BrainPlizz?",
        "answer_1": "Django",
        "answer_2": "FastAPI",
        "answer_3": "Flask",
        "answer_4": "Laravel",
        "correct_answer": 2,
    },
]


def seed_questions():
    db = SessionLocal()

    try:
        existing_question = db.query(Question).first()

        if existing_question:
            print("Вопросы уже существуют. Seed не требуется.")
            return

        for question_data in QUESTIONS:
            question = Question(**question_data)
            db.add(question)

        db.commit()

        print(f"Добавлено вопросов: {len(QUESTIONS)}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()