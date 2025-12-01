from fastapi import APIRouter, HTTPException
from ..schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user: UserCreate):
    return {
        "message": "Пользователь создан",
        "username": user.username,
        "email": user.email
    }