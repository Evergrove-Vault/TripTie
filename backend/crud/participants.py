
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models

def get_trip_by_join_code(db: Session, join_code: str):
    return db.query(models.Trip).filter(models.Trip.join_code == join_code).first()

def create_participant(db: Session, user_id: int, trip_id: int):
    # Используем промежуточную таблицу trip_members
    stmt = models.trip_members.insert().values(
        trip_id=trip_id,
        user_id=user_id,
        joined_at=datetime.utcnow()
    )
    db.execute(stmt)
    db.commit()
    return {"user_id": user_id, "trip_id": trip_id, "joined_at": datetime.utcnow()}
