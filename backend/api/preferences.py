from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DatabaseError, SQLAlchemyError
from ..database import get_db
from ..schemas import TripPreferencesCreate, TripPreferencesResponse, MergedTripPreferencesResponse, ParticipantPreferencesResponse
from ..crud.preferences import save_user_preferences, get_user_preferences, get_merged_preferences, get_all_participants_preferences

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.post("/", response_model=TripPreferencesResponse)
def save_preferences(
    preferences: TripPreferencesCreate,
    user_id: int = Query(..., description="ID пользователя (временно, в будущем из JWT)"),
    db: Session = Depends(get_db)
):
    """
    Сохраняет предпочтения пользователя для поездки.
    Временно user_id передается как query параметр (в будущем из JWT).
    """
    try:
        save_user_preferences(
            db=db,
            user_id=user_id,
            trip_id=preferences.trip_id,
            budget=preferences.budget,
            activity_names=preferences.activity_names
        )
        
        # Возвращаем сохраненные предпочтения
        result = get_user_preferences(db, user_id, preferences.trip_id)
        if not result:
            raise HTTPException(status_code=404, detail="Предпочтения не найдены")
        
        return TripPreferencesResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (OperationalError, DatabaseError) as e:
        error_msg = str(e).split('\n')[0]
        raise HTTPException(
            status_code=503,
            detail=f"Ошибка базы данных: {error_msg}"
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении предпочтений: {str(e)}"
        )


@router.get("/trip/{trip_id}", response_model=TripPreferencesResponse)
def get_my_preferences(
    trip_id: int,
    user_id: int = Query(..., description="ID пользователя (временно, в будущем из JWT)"),
    db: Session = Depends(get_db)
):
    """
    Получает предпочтения текущего пользователя для поездки.
    """
    try:
        result = get_user_preferences(db, user_id, trip_id)
        if not result:
            return TripPreferencesResponse(
                trip_id=trip_id,
                budget=None,
                activities=[]
            )
        return TripPreferencesResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении предпочтений: {str(e)}"
        )


@router.get("/trip/{trip_id}/merged", response_model=MergedTripPreferencesResponse)
def get_merged_preferences_for_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает объединенные предпочтения всех участников поездки.
    Объединяет бюджеты (сумма и среднее) и активности (уникальные).
    """
    try:
        result = get_merged_preferences(db, trip_id)
        return MergedTripPreferencesResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении объединенных предпочтений: {str(e)}"
        )


@router.get("/trip/{trip_id}/all", response_model=list[ParticipantPreferencesResponse])
def get_all_participants_preferences_for_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает предпочтения всех участников поездки с их именами.
    Возвращает список предпочтений каждого участника отдельно.
    """
    try:
        result = get_all_participants_preferences(db, trip_id)
        return [ParticipantPreferencesResponse(**item) for item in result]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении предпочтений участников: {str(e)}"
        )

