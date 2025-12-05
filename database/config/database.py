import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
import time

# Для Docker используем hostname "db" вместо "localhost"
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://travel_user:password@db:5432/travel_ml"
)

# Функция для проверки подключения к БД
def wait_for_db():
    """Ждет пока БД будет доступна"""
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()