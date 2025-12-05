from sqlalchemy.orm import Session
from database.models.models import Place

def get_places_by_trip(db: Session, trip_id: int):
    trip = db.execute(
        "SELECT city_id FROM trips WHERE id = :id", {"id": trip_id}
    ).fetchone()
    if not trip:
        return []
    return db.query(Place).filter(Place.city_id == trip.city_id).limit(10).all()
