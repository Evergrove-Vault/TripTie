from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.places import get_places_by_trip
from ..schemas import Place

router = APIRouter(prefix="/trips/{trip_id}/places", tags=["places"])

@router.get("/", response_model=list[Place])
def get_places(trip_id: int, db: Session = Depends(get_db)):
    return get_places_by_trip(db, trip_id)

@router.get("/route")
def get_route(trip_id: int, db: Session = Depends(get_db)):
    places = get_places_by_trip(db, trip_id)
    return [
        {"name": p.name, "lat": float(p.latitude), "lng": float(p.longitude)}
        for p in places if p.latitude and p.longitude
    ]