from sqlalchemy.orm import Session
from database.models.models import trip_members
from datetime import datetime

def join_trip_by_code(db: Session, user_id: int, join_code: str):
    trip = db.execute(
        "SELECT id FROM trips WHERE join_code = :code",
        {"code": join_code}
    ).fetchone()
    if not trip:
        raise ValueError("Trip not found")
    
    db.execute(
        trip_members.insert().values(
            trip_id=trip.id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
    )
    db.commit()
    return {"trip_id": trip.id}
