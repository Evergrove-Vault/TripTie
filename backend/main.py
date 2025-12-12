from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from api import trips, auth, participants, places, votes
from database.config.database import Base, engine, SessionLocal
from database.models.models import City, User

app = FastAPI(
    title="TripTie API",
    description="MVP бэкенд для планирования совместных поездок",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB tables exist on startup (safe for SQLite/dev)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Ensure default city and user exist for demo/trial usage
        if not db.query(City).first():
            db.add(City(name="Hello Kitty City", country_code="HK"))
            db.commit()
        if not db.query(User).filter(User.id == 1).first():
            pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
            demo_user = User(
                id=1,
                username="kitty",
                email="kitty@example.com",
                password_hash=pwd.hash("kitty123"),
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()


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
    from database import check_db_connection
    
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