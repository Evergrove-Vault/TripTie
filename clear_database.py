'''
import sys
import os
sys.path.insert(0, os.getcwd())

from database.config.database import engine
from sqlalchemy import text

def reset_database():
    """Очищает все данные из таблиц (оставляет структуру)"""
    
    try:
        with engine.connect() as conn:
            # Получаем все таблицы
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                AND tablename NOT LIKE 'alembic_%'
            """))
            tables = [row[0] for row in result]
            
            print(f"Найдено таблиц: {len(tables)}")
            
            # Очищаем данные из каждой таблицы
            for table in tables:
                try:
                    conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))
                    print(f"Данные из {table} очищены")
                except Exception as e:
                    print(f"Не удалось очистить {table}: {e}")
            
            conn.commit()
            print("Все данные очищены!")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("Очистка данных из базы...")
    reset_database()
'''