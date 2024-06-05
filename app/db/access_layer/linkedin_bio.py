from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import DBUsers


def check_linkedin_url(linkedin_url: str) -> bool:
    db: Session = get_db()
    user = db.query(DBUsers).filter(DBUsers.linkedin_url == linkedin_url).first()
    return user
