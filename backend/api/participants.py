from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DatabaseError, SQLAlchemyError, IntegrityError
from ..database import get_db
from ..crud.participants import join_trip_by_code
from pydantic import BaseModel

router = APIRouter(prefix="/trips", tags=["participants"])

class JoinRequest(BaseModel):
    join_code: str

@router.post("/join")
def join_trip(request: JoinRequest, db: Session = Depends(get_db)):
    try:
        result = join_trip_by_code(db, user_id=2, join_code=request.join_code)
        return {"status": "Присоединился", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        # Ошибка уникального ключа (дубликат)
        error_msg = str(e).split('\n')[0]
        raise HTTPException(
            status_code=400,
            detail="Вы уже являетесь участником этой поездки"
        )
    except (OperationalError, DatabaseError) as e:
        error_msg = str(e).split('\n')[0]
        # Проверяем тип ошибки для более понятного сообщения
        if "unique constraint" in error_msg.lower() or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Вы уже являетесь участником этой поездки"
            )
        raise HTTPException(
            status_code=503,
            detail=f"Ошибка базы данных: {error_msg}"
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    except Exception as e:
        # Для отладки показываем полную ошибку
        import traceback
        error_detail = f"{str(e)}\n\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при присоединении к поездке: {error_detail}"
        )
