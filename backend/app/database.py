from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg://brainplizz:brainplizz_password@localhost:5433/brainplizz"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def check_database_connection():
    try:
        with engine.connect():
            print("Подключение к PostgreSQL успешно!")
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")