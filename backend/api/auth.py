from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DatabaseError, SQLAlchemyError
from ..database import get_db
from ..schemas import UserCreate, UserResponse, UserLogin
from ..crud.auth import create_user, check_user_exists, get_user_by_username, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # 1. Проверить, нет ли уже такого пользователя
        db_user = check_user_exists(db, username=user.username, email=user.email)
        
        if db_user:
            raise HTTPException(status_code=400, detail="Email или username уже заняты")
        
        # 2. Создать нового пользователя
        db_user = create_user(db, user)
        
        # 3. Вернуть ответ
        return db_user
    except HTTPException:
        # Перебрасываем HTTPException как есть
        raise
    except ValueError as e:
        # Ошибки валидации (например, проблемы с паролем)
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка валидации данных: {str(e)}"
        )
    except (OperationalError, DatabaseError) as e:
        # Ошибки подключения или работы с БД
        error_msg = str(e).split('\n')[0]  # Берем первую строку ошибки
        # Упрощаем сообщение об ошибке для пользователя
        if "could not translate host name" in error_msg or "could not connect" in error_msg.lower():
            user_message = "База данных недоступна. Проверьте, что БД запущена (docker-compose up или другой способ)."
        else:
            user_message = f"Ошибка подключения к базе данных: {error_msg}"
        
        raise HTTPException(
            status_code=503,
            detail=user_message
        )
    except SQLAlchemyError as e:
        # Другие ошибки SQLAlchemy
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    except Exception as e:
        # Прочие неожиданные ошибки
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при регистрации: {str(e)}"
        )

@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Авторизация пользователя по username и password.
    Возвращает данные пользователя при успешной авторизации.
    """
    try:
        # 1. Найти пользователя по username
        db_user = get_user_by_username(db, username=credentials.username)
        
        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Неверное имя пользователя или пароль"
            )
        
        # 2. Проверить пароль
        if not verify_password(credentials.password, db_user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Неверное имя пользователя или пароль"
            )
        
        # 3. Возвратить данные пользователя
        return db_user
        
    except HTTPException:
        # Перебрасываем HTTPException как есть
        raise
    except (OperationalError, DatabaseError) as e:
        # Ошибки подключения или работы с БД
        error_msg = str(e).split('\n')[0]
        if "could not translate host name" in error_msg or "could not connect" in error_msg.lower():
            user_message = "База данных недоступна. Проверьте, что БД запущена (docker-compose up или другой способ)."
        else:
            user_message = f"Ошибка подключения к базе данных: {error_msg}"
        
        raise HTTPException(
            status_code=503,
            detail=user_message
        )
    except SQLAlchemyError as e:
        # Другие ошибки SQLAlchemy
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    except Exception as e:
        # Прочие неожиданные ошибки
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при авторизации: {str(e)}"
        )
