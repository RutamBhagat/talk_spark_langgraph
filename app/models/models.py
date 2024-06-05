from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class DBUsers(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    linkedin_url = Column(String, unique=True)
    scrapped_data = Column(JSON, nullable=True)
    bio = Column(JSON, nullable=True)
