from sqlalchemy.orm import Session
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from database.models.models import (
    UserTripPreferences, 
    Activity, 
    user_trip_activities,
    trip_members,
    Trip,
    User
)


def save_user_preferences(
    db: Session, 
    user_id: int, 
    trip_id: int, 
    budget: float = None, 
    activity_names: list[str] = None
):
    """
    Сохраняет или обновляет предпочтения пользователя для поездки.
    """
    # Проверяем, является ли пользователь участником поездки
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Поездка не найдена")
    
    # Проверяем участие пользователя
    member_check = db.execute(
        select(trip_members).where(
            and_(
                trip_members.c.trip_id == trip_id,
                trip_members.c.user_id == user_id
            )
        )
    ).first()
    
    # Если пользователь не является участником и не создатель, автоматически добавляем его
    if not member_check and trip.creator_id != user_id:
        try:
            db.execute(
                trip_members.insert().values(
                    trip_id=trip_id,
                    user_id=user_id,
                    joined_at=datetime.utcnow()
                )
            )
            db.commit()
        except IntegrityError:
            # Если уже добавлен (race condition), просто продолжаем
            db.rollback()
            pass
    
    # Находим или создаем запись предпочтений
    preferences = db.query(UserTripPreferences).filter(
        and_(
            UserTripPreferences.user_id == user_id,
            UserTripPreferences.trip_id == trip_id
        )
    ).first()
    
    if preferences:
        # Обновляем существующие предпочтения
        if budget is not None:
            preferences.budget = budget
    else:
        # Создаем новые предпочтения
        preferences = UserTripPreferences(
            user_id=user_id,
            trip_id=trip_id,
            budget=budget
        )
        db.add(preferences)
    
    # Обрабатываем активности
    if activity_names:
        # Удаляем старые связи с активностями
        db.execute(
            user_trip_activities.delete().where(
                and_(
                    user_trip_activities.c.user_id == user_id,
                    user_trip_activities.c.trip_id == trip_id
                )
            )
        )
        
        # Создаем или находим активности и связываем их
        for activity_name in activity_names:
            activity_name = activity_name.strip()
            if not activity_name:
                continue
                
            # Ищем существующую активность
            activity = db.query(Activity).filter(Activity.name == activity_name).first()
            
            if not activity:
                # Создаем новую активность
                activity = Activity(name=activity_name)
                db.add(activity)
                db.flush()  # Получаем ID новой активности
            
            # Создаем связь пользователь-поездка-активность
            db.execute(
                user_trip_activities.insert().values(
                    user_id=user_id,
                    trip_id=trip_id,
                    activity_id=activity.id
                )
            )
    
    db.commit()
    db.refresh(preferences)
    return preferences


def get_user_preferences(db: Session, user_id: int, trip_id: int):
    """
    Получает предпочтения конкретного пользователя для поездки.
    """
    preferences = db.query(UserTripPreferences).filter(
        and_(
            UserTripPreferences.user_id == user_id,
            UserTripPreferences.trip_id == trip_id
        )
    ).first()
    
    if not preferences:
        return None
    
    # Получаем активности пользователя для этой поездки
    activities = db.query(Activity).join(
        user_trip_activities,
        Activity.id == user_trip_activities.c.activity_id
    ).filter(
        and_(
            user_trip_activities.c.user_id == user_id,
            user_trip_activities.c.trip_id == trip_id
        )
    ).all()
    
    return {
        "trip_id": trip_id,
        "budget": preferences.budget,
        "activities": [a.name for a in activities]
    }


def get_merged_preferences(db: Session, trip_id: int):
    """
    Объединяет предпочтения всех участников поездки.
    Возвращает:
    - Общий бюджет (сумма)
    - Средний бюджет
    - Объединенный список всех активностей (уникальные)
    - Количество участников с предпочтениями
    """
    # Получаем всех участников поездки (включая создателя)
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Поездка не найдена")
    
    # Получаем ID всех участников
    member_ids = [trip.creator_id]
    members = db.execute(
        select(trip_members).where(trip_members.c.trip_id == trip_id)
    ).fetchall()
    member_ids.extend([m.user_id for m in members])
    member_ids = list(set(member_ids))  # Убираем дубликаты
    
    # Получаем все предпочтения участников
    all_preferences = db.query(UserTripPreferences).filter(
        and_(
            UserTripPreferences.trip_id == trip_id,
            UserTripPreferences.user_id.in_(member_ids)
        )
    ).all()
    
    # Объединяем бюджеты
    budgets = [p.budget for p in all_preferences if p.budget is not None]
    total_budget = sum(budgets) if budgets else None
    avg_budget = total_budget / len(budgets) if budgets else None
    
    # Получаем все активности всех участников
    all_activities = db.query(Activity).join(
        user_trip_activities,
        Activity.id == user_trip_activities.c.activity_id
    ).filter(
        and_(
            user_trip_activities.c.trip_id == trip_id,
            user_trip_activities.c.user_id.in_(member_ids)
        )
    ).distinct().all()
    
    unique_activities = list(set([a.name for a in all_activities]))
    
    # Общее количество участников поездки (включая создателя)
    total_participants_count = len(member_ids)
    
    return {
        "trip_id": trip_id,
        "total_budget": total_budget,
        "avg_budget": avg_budget,
        "all_activities": unique_activities,
        "participants_count": len(all_preferences),  # Количество участников с предпочтениями
        "total_participants_count": total_participants_count  # Общее количество участников
    }


def get_all_participants_preferences(db: Session, trip_id: int):
    """
    Получает предпочтения всех участников поездки с их именами.
    Возвращает список предпочтений каждого участника.
    """
    # Получаем всех участников поездки (включая создателя)
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Поездка не найдена")
    
    # Получаем ID всех участников
    member_ids = [trip.creator_id]
    members = db.execute(
        select(trip_members).where(trip_members.c.trip_id == trip_id)
    ).fetchall()
    member_ids.extend([m.user_id for m in members])
    member_ids = list(set(member_ids))  # Убираем дубликаты
    
    # Получаем всех пользователей
    users = db.query(User).filter(User.id.in_(member_ids)).all()
    user_dict = {user.id: user for user in users}
    
    # Получаем все предпочтения участников
    all_preferences = db.query(UserTripPreferences).filter(
        and_(
            UserTripPreferences.trip_id == trip_id,
            UserTripPreferences.user_id.in_(member_ids)
        )
    ).all()
    
    # Формируем результат с именами пользователей
    result = []
    for pref in all_preferences:
        user = user_dict.get(pref.user_id)
        if not user:
            continue
        
        # Получаем активности пользователя для этой поездки
        activities = db.query(Activity).join(
            user_trip_activities,
            Activity.id == user_trip_activities.c.activity_id
        ).filter(
            and_(
                user_trip_activities.c.user_id == pref.user_id,
                user_trip_activities.c.trip_id == trip_id
            )
        ).all()
        
        result.append({
            "user_id": pref.user_id,
            "username": user.username,
            "email": user.email,
            "budget": pref.budget,
            "activities": [a.name for a in activities],
            "is_creator": pref.user_id == trip.creator_id
        })
    
    return result

