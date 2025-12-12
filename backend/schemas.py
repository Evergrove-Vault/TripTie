from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

class TripCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    city_id: int

class Trip(BaseModel):
    id: int
    name: str
    join_code: str
    creator_id: int
    city_id: int

    class Config:
        from_attributes = True
        
class ParticipantCreate(BaseModel):
    join_code: str

class PlaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city_id: int
    latitude: float
    longitude: float
    rating: Optional[float] = None
    price_level: Optional[int] = None
    website: Optional[str] = None
    tripadvisor_id: Optional[str] = None
    primary_category: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class Place(PlaceBase):
    id: int

    class Config:
        from_attributes = True

class TripPreferencesCreate(BaseModel):
    trip_id: int
    budget: Optional[float] = None
    activity_names: Optional[list[str]] = None  # Список названий активностей

class TripPreferencesResponse(BaseModel):
    trip_id: int
    budget: Optional[float] = None
    activities: list[str] = []  # Список названий активностей
    
    class Config:
        from_attributes = True

class MergedTripPreferencesResponse(BaseModel):
    trip_id: int
    total_budget: Optional[float] = None  # Сумма всех бюджетов
    avg_budget: Optional[float] = None  # Средний бюджет
    all_activities: list[str] = []  # Объединенный список всех активностей (уникальные)
    participants_count: int = 0  # Количество участников, указавших предпочтения