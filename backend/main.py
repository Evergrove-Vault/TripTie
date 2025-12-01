from fastapi import FastAPI
from .api import trips

app = FastAPI(title="TripTie API")

app.include_router(trips.router)

@app.get("/")
def home():
    return {"status": " БД подключена", "try": "/docs"}
