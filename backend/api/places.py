from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models, database

router = APIRouter(prefix="/trips/{trip_id}/places", tags=["places"])

@router.post("/", response_model=schemas.Place)
def create_place(trip_id: int, place: schemas.PlaceCreate, db: Session = Depends(database.get_db)):
    db_place = models.Place(**place.model_dump())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@router.get("/", response_model=list[schemas.Place])
def read_places(trip_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Place).all()  # можно фильтровать по trip_id

@router.get("/route")
def get_route(trip_id: int, db: Session = Depends(database.get_db)):
    # Пример: просто вернуть все места в городе
    places = db.query(models.Place).all()
    return [
        {"name": p.name, "lat": float(p.latitude), "lng": float(p.longitude), "category": p.primary_category}
        for p in places
    ]
