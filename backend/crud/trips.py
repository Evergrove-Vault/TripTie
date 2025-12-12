from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_
from database.models.models import Trip, trip_members, User
import uuid
from datetime import datetime

def get_user_trips(db: Session, user_id: int):
    """
    Получает все поездки пользователя: где он создатель или участник.
    """
    # Поездки, где пользователь создатель
    created_trips = db.query(Trip).filter(Trip.creator_id == user_id).all()
    
    # Поездки, где пользователь участник
    member_trips_stmt = select(trip_members.c.trip_id).where(trip_members.c.user_id == user_id)
    member_trip_ids = [row[0] for row in db.execute(member_trips_stmt).fetchall()]
    member_trips = db.query(Trip).filter(Trip.id.in_(member_trip_ids)).all() if member_trip_ids else []
    
    # Объединяем и убираем дубликаты
    all_trips = {trip.id: trip for trip in created_trips + member_trips}
    return list(all_trips.values())

def create_trip(db: Session, trip_data: dict):
    # Преобразуем строки дат в объекты date, если они переданы
    trip_data_copy = trip_data.copy()
    
    def parse_date(date_str: str):
        """Парсит дату в различных форматах"""
        formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Не удалось распарсить дату: {date_str}")
    
    if 'start_date' in trip_data_copy and trip_data_copy['start_date']:
        if isinstance(trip_data_copy['start_date'], str) and trip_data_copy['start_date'].strip():
            try:
                trip_data_copy['start_date'] = parse_date(trip_data_copy['start_date'])
            except ValueError as e:
                # Если не удалось распарсить, удаляем поле
                trip_data_copy.pop('start_date', None)
    if 'end_date' in trip_data_copy and trip_data_copy['end_date']:
        if isinstance(trip_data_copy['end_date'], str) and trip_data_copy['end_date'].strip():
            try:
                trip_data_copy['end_date'] = parse_date(trip_data_copy['end_date'])
            except ValueError as e:
                # Если не удалось распарсить, удаляем поле
                trip_data_copy.pop('end_date', None)
    
    # creator_id должен быть передан в trip_data
    if 'creator_id' not in trip_data_copy:
        trip_data_copy['creator_id'] = 1  # Fallback для совместимости
    
    creator_id = trip_data_copy['creator_id']
    
    # Проверяем, что пользователь существует
    user = db.query(User).filter(User.id == creator_id).first()
    if not user:
        raise ValueError(f"Пользователь с ID {creator_id} не найден в базе данных")
    
    db_trip = Trip(
        join_code=uuid.uuid4().hex[:10].upper(),
        **trip_data_copy
    )
    db.add(db_trip)
    db.flush()  # Получаем ID поездки без коммита
    
    # Автоматически добавляем создателя в участники поездки
    try:
        db.execute(
            trip_members.insert().values(
                trip_id=db_trip.id,
                user_id=creator_id,
                joined_at=datetime.utcnow()
            )
        )
    except Exception:
        # Если уже добавлен (не должно произойти, но на всякий случай)
        pass
    
    db.commit()
    db.refresh(db_trip)
    return db_trip
