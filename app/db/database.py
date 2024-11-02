# app/db/database.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

# Create database URL
DATABASE_URL = "sqlite:///./sql_app.db"

# Create engine with proper SQLite configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool,  # Helps prevent threading issues
    echo=False,  # Set to True to see SQL queries
)


# Initialize database
def init_db():
    """Initialize the database, creating all tables."""
    # Import all models that inherit from SQLModel
    from app.models.models import DBProfile  # Make sure to import all your models

    SQLModel.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Create a new database session and close it after use.
    Yields:
        Session: SQLModel database session
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
