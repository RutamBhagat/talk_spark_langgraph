# app/db/database.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)


def init_db():
    """Initialize the database, creating all tables."""
    from app.models.models import DBProfile

    SQLModel.metadata.create_all(bind=engine)


@contextmanager
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
