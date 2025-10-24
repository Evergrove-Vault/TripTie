import sys
import os
import hashlib

# Добавляем корень проекта в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
database_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(database_dir)
sys.path.insert(0, project_root)

from database.config.database import SessionLocal
from database.models.models import User

def simple_hash_password(password: str) -> str:
    """Простое хеширование пароля (для тестовых данных)"""
    # Обрезаем пароль до 72 символов если нужно
    if len(password) > 72:
        password = password[:72]
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """Создает тестовых пользователей (только если их нет)"""
    db = SessionLocal()
    
    try:
        # Проверяем есть ли уже тестовые пользователи
        existing_users = db.query(User).filter(
            User.username.in_(["test_user", "alex_traveler", "maria_explorer"])
        ).count()
        
        if existing_users > 0:
            print("Тестовые пользователи уже существуют")
            # Покажем существующих
            users = db.query(User).filter(
                User.username.in_(["test_user", "alex_traveler", "maria_explorer"])
            ).all()
            print("Существующие тестовые пользователи:")
            for user in users:
                print(f"{user.username} ({user.email})")
            return
        
        # Создаем тестовых пользователей
        users = [
            User(
                username="test_user",
                email="test@example.com", 
                password_hash=simple_hash_password("test123")
            ),
            User(
                username="alex_traveler",
                email="alex@example.com",
                password_hash=simple_hash_password("password123")
            ),
            User(
                username="maria_explorer", 
                email="maria@example.com",
                password_hash=simple_hash_password("password123")
            )
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        
        print("Тестовые пользователи созданы:")
        print(f"test_user / test123")
        print(f"alex_traveler / password123") 
        print(f"maria_explorer / password123")
        
        # Покажем созданных пользователей
        created_users = db.query(User).all()
        print(f"\nВсего пользователей в БД: {len(created_users)}")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании тестовых пользователей: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_existing_users():
    """Показывает существующих пользователей"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if users:
            print("\nСуществующие пользователи в БД:")
            for user in users:
                print(f"{user.username} ({user.email}) - создан: {user.created_at}")
        else:
            print("В БД пока нет пользователей")
    except Exception as e:
        print(f"Ошибка при проверке пользователей: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Создание тестовых пользователей...")
    check_existing_users()
    create_test_users()