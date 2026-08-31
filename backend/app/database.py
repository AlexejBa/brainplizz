from sqlalchemy import create_engine


DATABASE_URL = "postgresql+psycopg://brainplizz:brainplizz_password@localhost:5433/brainplizz"

engine = create_engine(DATABASE_URL)


def check_database_connection():
    try:
        with engine.connect():
            print("Подключение к PostgreSQL успешно!")
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")