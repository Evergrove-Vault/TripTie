from database.config.database import engine, SessionLocal, Base
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
