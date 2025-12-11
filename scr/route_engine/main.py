from fastapi import FastAPI, HTTPException
from typing import List
import json
import time
import re

from models import Preferences, RouteResponse
from prompts import SYSTEM_PROMPT, build_user_prompt
from llm_client import call_llm
from cache import get_cached, make_cache_key, set_cached
from coordinates_nnov_extended import get_nnov_coordinates

app = FastAPI(title="Нижегородский Route Generator", version="1.0")

@app.get("/")
async def root():
    return {"message": "Генератор маршрутов по Нижнему Новгороду", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nnovgorod-route-engine"}

@app.get("/test-coordinates/{place_name}")
async def test_coordinates(place_name: str):
    """Тестовый endpoint для проверки координат"""
    from coordinates_nnov_extended import NOVGOROD_COORDINATES
    coords = get_nnov_coordinates(place_name)
    return {
        "place": place_name,
        "coordinates": coords,
        "all_matches": [p for p in NOVGOROD_COORDINATES.keys() if place_name.lower() in p.lower()]
    }

@app.post("/generate-route", response_model=RouteResponse)
async def generate_route(preferences: Preferences):
    """
    Генерирует маршрут ТОЛЬКО для Нижнего Новгорода
    """
    # Нормализуем название города
    city_input = preferences.city.strip().lower()
    
    # Все возможные написания Нижнего Новгорода
    nnov_variants = [
        "нижний новгород",
        "н.новгород", 
        "ннов",
        "нижний",
        "н.новг",
        "нижнем новгороде",
        "нижнем",
        "nnovgorod",
        "nizhny novgorod"
    ]
    
    # Проверяем все варианты
    is_nnovgorod = any(variant in city_input for variant in nnov_variants)
    
    if not is_nnovgorod:
        raise HTTPException(
            status_code=400, 
            detail=f"Этот сервис работает только для Нижнего Новгорода. Вы указали: '{preferences.city}'. Пожалуйста, укажите 'Нижний Новгород'."
        )
    
    # Принудительно устанавливаем правильное название
    preferences.city = "Нижний Новгород"
    
    try:
        # Кэширование
        pref_dict = preferences.dict()
        cache_key = make_cache_key(pref_dict)
        cached = get_cached(cache_key)
        if cached:
            print("Используем кэшированный результат")
            return RouteResponse(**cached)
        
        # Генерация промпта с явным указанием дней
        user_prompt = build_user_prompt(pref_dict)
        
        # Вызов LLM
        success, content = call_llm(SYSTEM_PROMPT, user_prompt)
        
        if not success:
            raise HTTPException(status_code=500, detail=content)
        
        # Парсинг JSON
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                result = json.loads(json_str)
            else:
                # Фолбэк если не нашли JSON
                print("Не найден JSON, использую запасной маршрут")
                result = create_fallback_route(preferences)
            
            # Проверяем что в маршруте есть Нижний Новгород
            if not is_nnovgorod_route(result):
                print("Маршрут не для НН, использую запасной")
                result = create_fallback_route(preferences)
            
            # После успешного парсинга
            if result and "route" in result:
                # Сохраняем оригинальный ответ (обрезанный для экономии места)
                result["llm_raw_response"] = content[:500] + ("..." if len(content) > 500 else "")

            # Определяем количество дней (из duration или days)
            days_requested = get_days_count(preferences)
            
            # Применяем распределение по дням
            result = distribute_by_days(result, days_requested)
            
            # Добавляем координаты и структуру
            if "route" in result and isinstance(result["route"], list):
                enhanced_route = []
                for i, item in enumerate(result["route"]):
                    # Определяем день - используем day из результата или вычисляем
                    day_number = item.get("day", (i // 4) + 1)
                    # Обрезаем day_number если больше запрошенных дней
                    day_number = min(day_number, days_requested)
                    
                    # Вычисляем порядок в дне
                    points_in_day = [p for p in enhanced_route if p.get("day") == day_number]
                    order_in_day = len(points_in_day) + 1
                    
                    # Получаем координаты
                    coords = get_nnov_coordinates(item.get("place", ""))
                    
                    enhanced_item = {
                        **item,
                        "coordinates": coords,
                        "day": day_number,
                        "order": order_in_day,
                        "id": f"day{day_number}_point{order_in_day}"
                    }
                    enhanced_route.append(enhanced_item)
                
                # Добавляем информацию для карты
                result["route"] = enhanced_route
                result["map_config"] = {
                    "center": {"lat": 56.3269, "lon": 44.0065},
                    "zoom": 13,
                    "bounds": {
                        "north": 56.3500,
                        "south": 56.2300,
                        "east": 44.0500,
                        "west": 43.7800
                    }
                }
            
            # Обновляем summary с правильным количеством дней
            if "summary" in result:
                result["summary"] = result["summary"].replace("1 день", f"{days_requested} дней")
                if "день" in result["summary"].lower() and str(days_requested) not in result["summary"]:
                    result["summary"] = f"Маршрут по Нижнему Новгороду на {days_requested} дней"
            
            # Кэшируем
            set_cached(cache_key, result)
            
            return RouteResponse(**result)
          
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            result = create_fallback_route(preferences)
            return RouteResponse(**result)
            
    except Exception as e:
        print(f"Общая ошибка: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации маршрута: {str(e)}")

def get_days_count(preferences: Preferences) -> int:
    """Определяет количество дней из preferences"""
    # Сначала пробуем получить из поля days
    if preferences.days and preferences.days > 0:
        return preferences.days
    
    # Если нет, пробуем извлечь из duration строки
    if preferences.duration:
        # Извлекаем число из строки "5 дней", "3 дня" и т.д.
        match = re.search(r'(\d+)\s*(?:дн|ден|day|days)', preferences.duration.lower())
        if match:
            return int(match.group(1))
    
    # Если ничего не нашли, проверяем duration на ключевые слова
    duration_lower = preferences.duration.lower() if preferences.duration else ""
    if "недел" in duration_lower:
        return 7
    elif "месяц" in duration_lower:
        return 30
    elif "два дня" in duration_lower or "2 дня" in duration_lower:
        return 2
    elif "три дня" in duration_lower or "3 дня" in duration_lower:
        return 3
    
    # По умолчанию 1 день
    return 1

def create_fallback_route(preferences: Preferences) -> dict:
    """Создаёт гарантированный маршрут по Нижнему Новгороду с координатами"""
    from coordinates_nnov_extended import get_nnov_coordinates
    
    days_requested = get_days_count(preferences)
    
    # Полный список достопримечательностей с днями
    all_attractions = [
        # День 1 - Исторический центр
        {"time": "10:00", "place": "Нижегородский кремль", "description": "Экскурсия по историческому центру города", "day": 1},
        {"time": "12:00", "place": "Чкаловская лестница", "description": "Спуск/подъём по самой длинной лестнице в России", "day": 1},
        {"time": "14:00", "place": "Большая Покровская улица", "description": "Обед и прогулка по главной пешеходной улице", "day": 1},
        {"time": "16:00", "place": "Площадь Минина и Пожарского", "description": "Центральная площадь города", "day": 1},
        
        # День 2 - История и архитектура
        {"time": "10:00", "place": "Рождественская улица", "description": "Прогулка по историческому району с купеческими домами", "day": 2},
        {"time": "12:00", "place": "Набережная Федоровского", "description": "Лучший вид на слияние Оки и Волги, фотосессия", "day": 2},
        {"time": "14:00", "place": "Печерский монастырь", "description": "Древний монастырь с богатой историей", "day": 2},
        {"time": "16:00", "place": "Собор Александра Невского", "description": "Красивый собор на Стрелке Волги и Оки", "day": 2},
        
        # День 3 - Культура и музеи
        {"time": "10:00", "place": "Художественный музей", "description": "Коллекция русского искусства", "day": 3},
        {"time": "13:00", "place": "Музей истории ГАЗ", "description": "История автомобилестроения", "day": 3},
        {"time": "15:00", "place": "Театр драмы", "description": "Посещение одного из старейших театров России", "day": 3},
        {"time": "19:00", "place": "Ужин в ресторане", "description": "Ужин в одном из ресторанов на Рождественской", "day": 3},
        
        # День 4 - Природа и парки (если нужно больше дней)
        {"time": "10:00", "place": "Парк Швейцария", "description": "Крупнейший парк города с аттракционами", "day": 4},
        {"time": "14:00", "place": "Канатная дорога", "description": "Переезд через Волгу с панорамным видом на город", "day": 4},
        {"time": "16:00", "place": "Парк Победы", "description": "Мемориальный комплекс", "day": 4},
        {"time": "18:00", "place": "Вечерняя прогулка по набережной", "description": "Прогулка по Верхне-Волжской набережной", "day": 4},
        
        # День 5 - Современность
        {"time": "10:00", "place": "Нижегородская ярмарка", "description": "Исторический выставочный комплекс", "day": 5},
        {"time": "13:00", "place": "Стадион Нижний Новгород", "description": "Современный стадион чемпионата мира", "day": 5},
        {"time": "15:00", "place": "Торговые центры", "description": "Шоппинг в современных торговых центрах", "day": 5},
        {"time": "19:00", "place": "Прощальный ужин", "description": "Ужин в ресторане с видом на город", "day": 5},
    ]
    
    # Выбираем только нужное количество дней
    max_points = min(days_requested * 4, len(all_attractions))
    route = [point for point in all_attractions if point["day"] <= days_requested]
    
    # Добавляем координаты, order, id и map_config
    enhanced_route = []
    for i, item in enumerate(route[:max_points]):
        coords = get_nnov_coordinates(item.get("place", ""))
        
        day_number = item["day"]
        order_in_day = len([p for p in enhanced_route if p["day"] == day_number]) + 1
        
        enhanced_route.append({
            **item,
            "coordinates": coords,
            "order": order_in_day,
            "id": f"day{day_number}_point{order_in_day}"
        })
    
    return {
        "route": enhanced_route,
        "summary": f"Классический маршрут по Нижнему Новгороду на {days_requested} дней",
        "estimated_cost": f"{3000 * days_requested} руб на человека",
        "reasoning": f"Выбраны главные достопримечательности Нижнего Новгорода, распределённые по {days_requested} дням",
        "tips": [
            "Удобная обувь обязательна - город холмистый",
            "Попробуйте нижегородские пряники",
            f"Распределите {days_requested} дней так: день 1-центр, день 2-история, и т.д.",
            "Используйте общественный транспорт для перемещения между районами"
        ],
        "map_config": {
            "center": {"lat": 56.3269, "lon": 44.0065},
            "zoom": 13,
            "bounds": {
                "north": 56.3500,
                "south": 56.2300,
                "east": 44.0500,
                "west": 43.7800
            }
        }
    }

def distribute_by_days(route_data: dict, days_requested: int) -> dict:
    """
    Принудительно распределяет точки по дням, если LLM этого не сделал
    """
    if "route" not in route_data:
        return route_data
    
    route = route_data["route"]
    
    if days_requested <= 1:
        # Если 1 день, просто добавляем day=1 ко всем точкам
        for point in route:
            if "day" not in point:
                point["day"] = 1
        return route_data
    
    # Проверяем, есть ли уже информация о днях
    has_days = any("day" in point for point in route)
    
    if not has_days:
        # Распределяем точки по дням равномерно
        points_per_day = max(3, len(route) // days_requested)
        
        for i, point in enumerate(route):
            day_number = min((i // points_per_day) + 1, days_requested)
            point["day"] = day_number
    
    # Проверяем распределение по дням
    days_with_points = set()
    for point in route:
        if "day" in point:
            days_with_points.add(point["day"])
    
    # Если какие-то дни остались без точек, перераспределяем
    if len(days_with_points) < days_requested:
        # Сортируем точки по текущим дням
        route.sort(key=lambda x: x.get("day", 1))
        
        # Перераспределяем равномерно
        for i, point in enumerate(route):
            day_number = min((i // (len(route) // days_requested)) + 1, days_requested)
            point["day"] = day_number
    
    return route_data

def is_nnovgorod_route(route_data: dict) -> bool:
    """Проверяет что маршрут действительно для Нижнего Новгорода"""
    route_text = json.dumps(route_data, ensure_ascii=False).lower()
    nnov_keywords = ["нижний", "новгород", "н.новг", "кремль", "чкаловск", "покровск", "нижегород"]
    return any(keyword in route_text for keyword in nnov_keywords)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)