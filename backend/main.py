from fastapi import FastAPI
from .api import trips, auth, participants, places, votes

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TripTie API",
    description="MVP бэкенд для планирования совместных поездок",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем все роутеры
app.include_router(trips.router)
app.include_router(auth.router)
app.include_router(participants.router)
app.include_router(places.router)
# app.include_router(votes.router)

@app.get("/")
def home():
    return {
        "status": " API работает",
        "docs": "/docs",
        "team": ["Ира — БД", "Ilyana — auth + trips", "Alina — participants + places + votes"]
    }

@app.get("/health")
def health_check():
    from .database import check_db_connection
    
    db_connected, db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "backend": "FastAPI",
        "database": {
            "type": "PostgreSQL",
            "status": db_status,
            "connected": db_connected
        }
    }