from sqlalchemy.orm import Session
from database.models.models import Trip
import uuid

def create_trip(db: Session, trip_data: dict):
    db_trip = Trip(
        creator_id=1,  # TODO: заменим на current_user.id
        join_code=uuid.uuid4().hex[:10].upper(),
        **trip_data
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip