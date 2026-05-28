import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./f1_historical.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    driver_id_str = Column(String, unique=True, index=True)  # e.g., 'leclerc'
    code = Column(String, index=True)  # e.g., 'LEC'
    first_name = Column(String)
    last_name = Column(String)
    nationality = Column(String)

class RaceResult(Base):
    __tablename__ = "race_results"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, index=True)
    round = Column(Integer, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    position = Column(Integer)
    points = Column(Float)
    time_seconds = Column(Float)

def init_db():
    Base.metadata.create_all(bind=engine)
