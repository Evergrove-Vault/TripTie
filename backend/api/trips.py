from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.trips import create_trip, get_user_trips
from ..schemas import TripCreate, Trip
from database.models.models import Trip as TripModel
import traceback

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=Trip)
def create_trip_api(
    trip: TripCreate,
    user_id: int = Query(1, description="ID пользователя (временно, в будущем из JWT)"),
    db: Session = Depends(get_db)
):
    try:
        trip_data = trip.model_dump(exclude_none=True)
        trip_data['creator_id'] = user_id
        return create_trip(db, trip_data)
    except ValueError as e:
        # Ошибка валидации (например, пользователь не найден)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Ошибка при создании поездки: {str(e)}")
        print(f"Трассировка: {error_trace}")
        # Извлекаем понятное сообщение об ошибке
        error_message = str(e)
        if "ForeignKeyViolation" in error_message or "foreign key" in error_message.lower():
            if "creator_id" in error_message:
                error_message = f"Пользователь с ID {user_id} не найден в базе данных"
            elif "city_id" in error_message:
                error_message = f"Город с указанным ID не найден в базе данных"
        raise HTTPException(status_code=400, detail=error_message)

@router.get("/", response_model=list[Trip])
def get_trips(
    user_id: int = Query(None, description="ID пользователя (опционально, для фильтрации)"),
    db: Session = Depends(get_db)
):
    if user_id:
        # Возвращаем поездки конкретного пользователя
        return get_user_trips(db, user_id)
    else:
        # Возвращаем все поездки (для совместимости)
        return db.query(TripModel).limit(5).all()
