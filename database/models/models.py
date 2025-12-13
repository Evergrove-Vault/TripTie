from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Date, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config.database import Base

# Промежуточные таблицы
trip_members = Table(
    'trip_members',
    Base.metadata,
    Column('trip_id', Integer, ForeignKey('trips.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('joined_at', DateTime, default=func.now())
)

trip_activities = Table(
    'trip_activities',
    Base.metadata,
    Column('trip_id', Integer, ForeignKey('trips.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True)
)

place_activities = Table(
    'place_activities',
    Base.metadata,
    Column('place_id', Integer, ForeignKey('places.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    created_trips = relationship("Trip", back_populates="creator")
    trip_memberships = relationship("Trip", secondary=trip_members, back_populates="members")
    visited_places = relationship("UserVisitedPlace", back_populates="user")

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_code = Column(String(2), default="RU")
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    trips = relationship("Trip", back_populates="city")
    places = relationship("Place", back_populates="city")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    trips = relationship("Trip", secondary=trip_activities, back_populates="activities")
    places = relationship("Place", secondary=place_activities, back_populates="activities")

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_completed = Column(Boolean, default=False)
    join_code = Column(String(10), unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    creator = relationship("User", back_populates="created_trips")
    city = relationship("City", back_populates="trips")
    members = relationship("User", secondary=trip_members, back_populates="trip_memberships")
    activities = relationship("Activity", secondary=trip_activities, back_populates="trips")
    itinerary_days = relationship("ItineraryDay", back_populates="trip")
    visited_places = relationship("UserVisitedPlace", back_populates="trip")

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float)
    price_level = Column(Integer)
    website = Column(String(500))
    
    # TripAdvisor поля
    tripadvisor_id = Column(String(100), unique=True, index=True)
    tripadvisor_rating = Column(Float)
    tripadvisor_reviews_count = Column(Integer)
    primary_category = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    
    city = relationship("City", back_populates="places")
    activities = relationship("Activity", secondary=place_activities, back_populates="places")
    day_places = relationship("DayPlace", back_populates="place")
    visited_places = relationship("UserVisitedPlace", back_populates="place")

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(Date)
    notes = Column(Text)
    
    trip = relationship("Trip", back_populates="itinerary_days")
    day_places = relationship("DayPlace", back_populates="itinerary_day")

class DayPlace(Base):
    __tablename__ = "day_places"
    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("itinerary_days.id"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    order_in_route = Column(Integer, nullable=False)
    visit_time = Column(String(50))
    duration_minutes = Column(Integer)
    notes = Column(Text)
    
    itinerary_day = relationship("ItineraryDay", back_populates="day_places")
    place = relationship("Place", back_populates="day_places")

class UserVisitedPlace(Base):
    __tablename__ = "user_visited_places"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    visited_date = Column(Date, default=func.now())
    rating = Column(Integer)
    review = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="visited_places")
    trip = relationship("Trip", back_populates="visited_places")
    place = relationship("Place", back_populates="visited_places")

# Промежуточная таблица для предпочтений пользователей по активностям
user_trip_activities = Table(
    'user_trip_activities',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('trip_id', Integer, ForeignKey('trips.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

class UserTripPreferences(Base):
    __tablename__ = "user_trip_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    budget = Column(Float)  # Бюджет пользователя для поездки
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User")
    trip = relationship("Trip")
    # Убираем relationship для activities, так как связь идет через промежуточную таблицу
    # с user_id и trip_id, а не через id UserTripPreferences