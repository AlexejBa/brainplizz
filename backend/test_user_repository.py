from app.database import SessionLocal
from app.repositories.user_repository import UserRepository


session = SessionLocal()

try:
    repository = UserRepository(session)

    user = repository.get_by_email("test@example.com")

    if user:
        repository.delete(user)
        print("Тестовый пользователь удалён!")
    else:
        print("Тестовый пользователь не найден.")

finally:
    session.close()