from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

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