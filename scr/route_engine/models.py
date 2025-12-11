# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Preferences(BaseModel):
    city: str
    interests: List[str]
    budget: str = "средний"
    pace: str = "умеренный"
    duration: str = "1 день"
    activity_level: str = "средний"
    group: str = "соло"
    days: Optional[int] = Field(default=1, description="Количество дней маршрута")

class RouteResponse(BaseModel):
    route: List[Dict[str, Any]]
    summary: str
    estimated_cost: str
    reasoning: str
    tips: List[str]
    map_config: Optional[Dict[str, Any]] = None