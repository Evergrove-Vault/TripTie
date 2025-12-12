from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_
from database.models.models import Trip, trip_members, User, City
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
    if 'start_date' in trip_data_copy and trip_data_copy['start_date']:
        if isinstance(trip_data_copy['start_date'], str) and trip_data_copy['start_date'].strip():
            try:
                trip_data_copy['start_date'] = datetime.strptime(trip_data_copy['start_date'], '%Y-%m-%d').date()
            except ValueError:
                trip_data_copy['start_date'] = None
        elif not trip_data_copy['start_date']:
            trip_data_copy['start_date'] = None
    else:
        trip_data_copy['start_date'] = None
        
    if 'end_date' in trip_data_copy and trip_data_copy['end_date']:
        if isinstance(trip_data_copy['end_date'], str) and trip_data_copy['end_date'].strip():
            try:
                trip_data_copy['end_date'] = datetime.strptime(trip_data_copy['end_date'], '%Y-%m-%d').date()
            except ValueError:
                trip_data_copy['end_date'] = None
        elif not trip_data_copy['end_date']:
            trip_data_copy['end_date'] = None
    else:
        trip_data_copy['end_date'] = None
    
    # creator_id должен быть передан в trip_data
    if 'creator_id' not in trip_data_copy:
        trip_data_copy['creator_id'] = 1  # Fallback для совместимости
    
    creator_id = trip_data_copy['creator_id']
    
    # Проверяем обязательные поля
    if not trip_data_copy.get('name'):
        raise ValueError("Название поездки обязательно")
    
    if 'city_id' not in trip_data_copy or not trip_data_copy.get('city_id'):
        raise ValueError("ID города обязателен")
    
    # Проверяем существование города
    city = db.query(City).filter(City.id == trip_data_copy['city_id']).first()
    if not city:
        raise ValueError(f"Город с ID {trip_data_copy['city_id']} не найден")
    
    # Обрабатываем description - если пустая строка, делаем None
    description = trip_data_copy.get('description')
    if description == '':
        description = None
    
    # Создаем поездку с явным указанием полей
    db_trip = Trip(
        name=trip_data_copy['name'],
        description=description,
        creator_id=creator_id,
        city_id=trip_data_copy['city_id'],
        start_date=trip_data_copy.get('start_date'),
        end_date=trip_data_copy.get('end_date'),
        join_code=uuid.uuid4().hex[:10].upper()
    )
    db.add(db_trip)
    db.flush()  # Получаем ID поездки без коммита
    
    # Автоматически добавляем создателя в участники поездки
    try:
        from sqlalchemy.exc import IntegrityError
        db.execute(
            trip_members.insert().values(
                trip_id=db_trip.id,
                user_id=creator_id,
                joined_at=datetime.utcnow()
            )
        )
    except IntegrityError:
        # Если уже добавлен (не должно произойти, но на всякий случай)
        # Просто продолжаем - поездка уже создана
        pass
    except Exception as e:
        # Для других ошибок откатываем транзакцию
        db.rollback()
        raise
    
    db.commit()
    db.refresh(db_trip)
    return db_trip

def get_trip_details(db: Session, trip_id: int):
    """
    Получает детальную информацию о поездке, включая:
    - Информацию о поездке
    - Информацию о создателе
    - Информацию о городе
    - Список участников
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Поездка не найдена")
    
    # Получаем создателя
    creator = db.query(User).filter(User.id == trip.creator_id).first()
    
    # Получаем город
    city = db.query(City).filter(City.id == trip.city_id).first()
    
    # Получаем всех участников (включая создателя)
    member_ids = [trip.creator_id]
    members = db.execute(
        select(trip_members).where(trip_members.c.trip_id == trip_id)
    ).fetchall()
    member_ids.extend([m.user_id for m in members])
    member_ids = list(set(member_ids))  # Убираем дубликаты
    
    # Получаем информацию о всех участниках
    participants = db.query(User).filter(User.id.in_(member_ids)).all()
    participants_data = [
        {
            "id": p.id,
            "username": p.username,
            "email": p.email,
            "is_creator": p.id == trip.creator_id
        }
        for p in participants
    ]
    
    return {
        "id": trip.id,
        "name": trip.name,
        "description": trip.description,
        "join_code": trip.join_code,
        "start_date": trip.start_date.isoformat() if trip.start_date else None,
        "end_date": trip.end_date.isoformat() if trip.end_date else None,
        "is_completed": trip.is_completed,
        "created_at": trip.created_at.isoformat() if trip.created_at else None,
        "creator": {
            "id": creator.id if creator else None,
            "username": creator.username if creator else None,
            "email": creator.email if creator else None
        } if creator else None,
        "city": {
            "id": city.id if city else None,
            "name": city.name if city else None,
            "country_code": city.country_code if city else None
        } if city else None,
        "participants": participants_data,
        "participants_count": len(participants_data)
    }
