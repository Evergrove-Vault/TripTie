from fastapi import FastAPI, HTTPException
from typing import List
import json
import time

from models import Preferences, RouteResponse
from prompts import SYSTEM_PROMPT, build_user_prompt
from llm_client import call_llm
from cache import get_cached, make_cache_key, set_cached

app = FastAPI(title="Нижегородский Route Generator", version="1.0")

@app.get("/")
async def root():
    return {"message": "Генератор маршрутов по Нижнему Новгороду", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nnovgorod-route-engine"}

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
        
        # Генерация промпта
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
                result = create_fallback_route(preferences)
            
            # Проверяем что в маршруте есть Нижний Новгород
            if not is_nnovgorod_route(result):
                result = create_fallback_route(preferences)
            
            # Кэшируем
            set_cached(cache_key, result)
            
            return RouteResponse(**result)
            
        except json.JSONDecodeError as e:
            result = create_fallback_route(preferences)
            return RouteResponse(**result)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

def create_fallback_route(preferences: Preferences) -> dict:
    """Создаёт гарантированный маршрут по Нижнему Новгороду"""
    days = preferences.days or 1
    interests = preferences.interests or []
    
    base_route = [
        {"time": "10:00", "place": "Нижегородский кремль", "description": "Экскурсия по историческому центру города"},
        {"time": "12:00", "place": "Чкаловская лестница", "description": "Спуск/подъём по самой длинной лестнице в России"},
        {"time": "14:00", "place": "Большая Покровская улица", "description": "Обед и прогулка по главной пешеходной улице"},
    ]
    
    if days > 1:
        base_route.extend([
            {"time": "10:00", "place": "Рождественская улица", "description": "Прогулка по историческому району с купеческими домами"},
            {"time": "13:00", "place": "Набережная Федоровского", "description": "Лучший вид на слияние Оки и Волги, фотосессия"},
            {"time": "16:00", "place": "Канатная дорога", "description": "Переезд через Волгу с панорамным видом на город"},
        ])
    
    return {
        "route": base_route,
        "summary": f"Классический маршрут по Нижнему Новгороду на {days} день(дней)",
        "estimated_cost": f"{3000 * days} руб на человека",
        "reasoning": "Выбраны главные достопримечательности Нижнего Новгорода",
        "tips": ["Удобная обувь обязательна - город холмистый", "Попробуйте нижегородские пряники"]
    }

def is_nnovgorod_route(route_data: dict) -> bool:
    """Проверяет что маршрут действительно для Нижнего Новгорода"""
    route_text = json.dumps(route_data, ensure_ascii=False).lower()
    nnov_keywords = ["нижний", "новгород", "н.новг", "кремль", "чкаловск", "покровск"]
    return any(keyword in route_text for keyword in nnov_keywords)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
