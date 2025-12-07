from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from database.models.models import Trip, trip_members, User
from datetime import datetime

def join_trip_by_code(db: Session, user_id: int, join_code: str):
    # Найти поездку по join_code
    trip = db.query(Trip).filter(Trip.join_code == join_code).first()
    if not trip:
        raise ValueError("Поездка с таким кодом не найдена")
    
    # Проверить, существует ли пользователь
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Пользователь не найден")
    
    # Проверить, не является ли пользователь уже участником
    stmt = select(trip_members).where(
        and_(
            trip_members.c.trip_id == trip.id,
            trip_members.c.user_id == user_id
        )
    )
    existing = db.execute(stmt).first()
    if existing:
        raise ValueError("Вы уже являетесь участником этой поездки")
    
    # Добавить пользователя в поездку
    try:
        stmt = trip_members.insert().values(
            trip_id=trip.id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.execute(stmt)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Если все равно возникает ошибка уникальности (на случай race condition)
        raise ValueError("Вы уже являетесь участником этой поездки")
    
    return {"trip_id": trip.id}
