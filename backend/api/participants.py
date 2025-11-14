
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, database

router = APIRouter(prefix="/trips", tags=["participants"])

@router.post("/join")
def join_trip(data: schemas.ParticipantCreate, db: Session = Depends(database.get_db)):
    trip = crud.participants.get_trip_by_join_code(db, data.join_code)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    # TODO: получить current_user.id из JWT
    result = crud.participants.create_participant(db, user_id=2, trip_id=trip.id)
    return {"trip_id": trip.id, "joined_at": result["joined_at"]}
