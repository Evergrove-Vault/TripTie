from pydantic import BaseModel, Field
from typing import List, Optional

class Preferences(BaseModel):
    city: str = Field("Нижний Новгород")
    interests: List[str]
    budget: Optional[str] = "средний"
    pace: Optional[str] = "спокойный"
    duration: Optional[str] = "1 день"
    activity_level: Optional[str] = "нормально"
    group: Optional[str] = "пара"

class RouteItem(BaseModel):
    time: str
    place: str
    description: str

class RouteResponse(BaseModel):
    route: List[RouteItem]
    summary: Optional[str]
    estimated_cost: Optional[str]
    reasoning: Optional[str]
    tips: Optional[List[str]]
