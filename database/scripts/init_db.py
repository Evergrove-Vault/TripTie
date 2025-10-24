import sys
import os

# Добавляем корень проекта в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
database_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(database_dir)
sys.path.insert(0, project_root)

from database.config.database import engine, Base, SessionLocal
from database.models.models import User, City, Activity
from sqlalchemy import inspect

def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)
    print("Все таблицы созданы успешно!")

def seed_initial_data():
    """Наполняет БД начальными данными (только если их нет)"""
    db = SessionLocal()
    
    try:
        # Проверяем есть ли уже данные в таблицах
        inspector = inspect(engine)
        
        # Проверяем активности
        if db.query(Activity).count() == 0:
            activities = [
                Activity(name="art", description="Музеи, галереи, искусство"),
                Activity(name="food", description="Рестораны, кафе, местная кухня"),
                Activity(name="nature", description="Парки, природа, походы"),
                Activity(name="nightlife", description="Бары, клубы, вечерние развлечения"),
                Activity(name="shopping", description="Магазины, рынки, шопинг"),
                Activity(name="history", description="Исторические места, архитектура"),
                Activity(name="adventure", description="Экстрим, спорт, приключения"),
                Activity(name="relax", description="Спа, отдых, пляжи")
            ]
            
            for activity in activities:
                db.add(activity)
            print("Активности добавлены")
        else:
            print("Активности уже существуют, пропускаем")
        
        # Проверяем города
        if db.query(City).count() == 0:
            russian_cities = [
                City(name="Москва", country_code="RU", latitude=55.7558, longitude=37.6176),
                City(name="Санкт-Петербург", country_code="RU", latitude=59.9343, longitude=30.3351),
                City(name="Казань", country_code="RU", latitude=55.7964, longitude=49.1089),
                City(name="Екатеринбург", country_code="RU", latitude=56.8389, longitude=60.6057),
                City(name="Нижний Новгород", country_code="RU", latitude=56.3269, longitude=44.0075),
                City(name="Новосибирск", country_code="RU", latitude=55.0084, longitude=82.9357),
                City(name="Сочи", country_code="RU", latitude=43.5855, longitude=39.7231),
                City(name="Владивосток", country_code="RU", latitude=43.1155, longitude=131.8855),
            ]
            
            for city in russian_cities:
                db.add(city)
            print("Города добавлены")
        else:
            print("ℹГорода уже существуют, пропускаем")
        
        db.commit()
        print("Начальные данные проверены/добавлены!")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при добавлении данных: {e}")
    finally:
        db.close()

def check_database_status():
    """Показывает текущее состояние БД"""
    db = SessionLocal()
    try:
        print("\nТекущее состояние БД:")
        print(f"   - Таблиц: {len(Base.metadata.tables)}")
        print(f"   - Активностей: {db.query(Activity).count()}")
        print(f"   - Городов: {db.query(City).count()}")
        print(f"   - Пользователей: {db.query(User).count()}")
    except Exception as e:
        print(f"Ошибка при проверке статуса: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Запуск инициализации БД...")
    create_tables()
    seed_initial_data()
    check_database_status()
    print("Инициализация БД завершена!")