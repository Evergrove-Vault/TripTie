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
