from sqlalchemy.orm import Session
from database.models.models import Place, Trip

def get_places_by_trip(db: Session, trip_id: int):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return []
    return db.query(Place).filter(Place.city_id == trip.city_id).limit(10).all()