from fastapi import FastAPI
#from .api import trips, auth, participants, places, votes
from .api import participants, places
app = FastAPI(
    title="TripTie API",
    description="MVP бэкенд для планирования совместных поездок",
    version="0.1.0"
)

# Подключаем все роутеры
#app.include_router(trips.router)
#app.include_router(auth.router)
app.include_router(participants.router)
app.include_router(places.router)
#app.include_router(votes.router)

@app.get("/")
def home():
    return {
        "status": " API работает",
        "docs": "/docs",
        "team": ["Ира — БД", "Ilyana — auth + trips", "Alina — participants + places + votes"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "backend": "FastAPI", "database": "PostgreSQL"}