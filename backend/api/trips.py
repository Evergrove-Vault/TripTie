from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.trips import create_trip, get_user_trips, get_trip_details
from ..schemas import TripCreate, Trip
from database.models.models import Trip as TripModel

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=Trip)
def create_trip_api(
    trip: TripCreate,
    user_id: int = Query(1, description="ID пользователя (временно, в будущем из JWT)"),
    db: Session = Depends(get_db)
):
    try:
        trip_data = trip.model_dump()
        trip_data['creator_id'] = user_id
        return create_trip(db, trip_data)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        error_detail = str(e)
        print(f"Ошибка при создании поездки: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании поездки: {error_detail}"
        )

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

@router.get("/{trip_id}/details")
def get_trip_details_api(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает детальную информацию о поездке, включая:
    - Информацию о поездке
    - Информацию о создателе
    - Информацию о городе
    - Список участников
    """
    try:
        return get_trip_details(db, trip_id)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении информации о поездке: {str(e)}"
        )
