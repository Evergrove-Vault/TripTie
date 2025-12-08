from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.config.database import get_db
from crud.trips import create_trip
from schemas import TripCreate, Trip
from database.models.models import Trip as TripModel

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=Trip)
def create_trip_api(trip: TripCreate, db: Session = Depends(get_db)):
    return create_trip(db, trip.model_dump())

@router.get("/", response_model=list[Trip])
def get_trips(db: Session = Depends(get_db)):
    return db.query(TripModel).limit(5).all()