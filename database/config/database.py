import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool
from sqlalchemy import text

def check_db_connection():
    """Проверяет подключение к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "connected"
    except OperationalError as e:
        return False, f"connection_error: {str(e)}"
    except Exception as e:
        return False, f"error: {str(e)}"

def get_database_url():
    """Безопасное получение URL базы данных"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Прямой URL из переменной окружения
    db_url = os.getenv("DATABASE_URL")
    
    if db_url:
        return db_url
    
    # Собираем URL из отдельных переменных (если настроено)
    user = os.getenv("POSTGRES_USER", "travel_user")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "travel_ml")
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

# Функция для проверки подключения к БД
def wait_for_db():
    """Ждет пока БД будет доступна"""
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            engine = create_engine(get_database_url())
            with engine.connect() as conn:
                print("✅ Database connection successful!")
                return True
        except OperationalError as e:
            if i == 0:
                print(f"⏳ Waiting for database... (attempt {i+1}/{max_retries})")
            time.sleep(retry_interval)
    
    print("❌ Failed to connect to database after retries")
    return False

# Ждем подключения к БД при импорте
if __name__ != "__main__":
    wait_for_db()

engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()