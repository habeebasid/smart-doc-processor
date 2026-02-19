from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.database import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (set False in production)
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Function to create all tables
def init_db():
    """Creates all tables in the database"""
    Base.metadata.create_all(bind=engine)


# Dependency for FastAPI routes
def get_db():
    """Provides database session to routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
