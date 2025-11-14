from fastapi import FastAPI
from .api import participants, places, votes  # Импортируем роутеры

app = FastAPI(title="TripTie API", version="0.1.0")

# Подключаем роутеры
app.include_router(participants.router, prefix="/api", tags=["participants"])
app.include_router(places.router, prefix="/api", tags=["places"])
app.include_router(votes.router, prefix="/api", tags=["votes"])

@app.get("/")
def root():
    return {"message": "Welcome to TripTie API"}