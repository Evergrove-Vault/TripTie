from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.trips import get_trip_details
from ..crud.preferences import get_merged_preferences
from ..crud.route_generator import generate_route_with_llm
from database.models.models import Trip, City
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/route", tags=["route"])

@router.post("/generate/{trip_id}")
async def generate_route_for_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Генерирует маршрут для поездки на основе:
    - Города поездки
    - Объединенных предпочтений участников (активности, бюджет)
    - Дат поездки (для расчета количества дней)
    """
    try:
        # Получаем информацию о поездке
        trip_details = get_trip_details(db, trip_id)
        if not trip_details:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        # Получаем объединенные предпочтения
        merged_prefs = get_merged_preferences(db, trip_id)
        
        # Получаем город
        city_name = trip_details.get("city", {}).get("name", "Нижний Новгород")
        
        # Вычисляем количество дней
        days = 3  # Значение по умолчанию
        if trip_details.get("start_date") and trip_details.get("end_date"):
            try:
                start = datetime.fromisoformat(trip_details["start_date"])
                end = datetime.fromisoformat(trip_details["end_date"])
                calculated_days = max(1, (end - start).days + 1)
                if calculated_days > 0:
                    days = calculated_days
            except:
                pass  # Используем значение по умолчанию
        
        # Формируем интересы из активностей
        interests = merged_prefs.get("all_activities", [])
        if not interests:
            interests = ["достопримечательности", "культура", "развлечения"]
        
        # Определяем бюджет
        budget_level = "средний"
        if merged_prefs.get("avg_budget"):
            avg = merged_prefs["avg_budget"]
            if avg < 5000:
                budget_level = "низкий"
            elif avg > 20000:
                budget_level = "высокий"
        
        # Генерируем маршрут используя LLM с fallback
        route_data = generate_route_with_llm(
            city_name=city_name,
            interests=interests[:5],  # Максимум 5 интересов
            days=days,
            budget_level=budget_level,
            group="группа" if merged_prefs.get("total_participants_count", 1) > 1 else "соло"
        )
        
        return {
            "trip_id": trip_id,
            "route": route_data.get("route", []),
            "summary": route_data.get("summary", ""),
            "estimated_cost": route_data.get("estimated_cost", ""),
            "reasoning": route_data.get("reasoning", ""),
            "tips": route_data.get("tips", []),
            "map_config": route_data.get("map_config")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при генерации маршрута: {str(e)}"
        )

