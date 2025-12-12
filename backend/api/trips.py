from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.trips import create_trip, get_user_trips
from ..schemas import TripCreate, Trip
from database.models.models import Trip as TripModel

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=Trip)
def create_trip_api(
    trip: TripCreate,
    user_id: int = Query(1, description="ID пользователя (временно, в будущем из JWT)"),
    db: Session = Depends(get_db)
):
    trip_data = trip.model_dump()
    trip_data['creator_id'] = user_id
    return create_trip(db, trip_data)

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
