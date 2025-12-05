from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.participants import join_trip_by_code
from pydantic import BaseModel

router = APIRouter(prefix="/trips", tags=["participants"])

class JoinRequest(BaseModel):
    join_code: str

@router.post("/join")
def join_trip(request: JoinRequest, db: Session = Depends(get_db)):
    try:
        result = join_trip_by_code(db, user_id=2, join_code=request.join_code)
        return {"status": "Присоединился", "data": result}
    except ValueError as e:
        raise HTTPException(400, str(e))
