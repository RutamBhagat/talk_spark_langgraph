from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import DBUsers


def get_user_by_linkedin_url(linkedin_url: str) -> DBUsers:
    with get_db() as db:
        user = db.query(DBUsers).filter(DBUsers.linkedin_url == linkedin_url).first()
    return user


def save_new_user(linkedin_url: str = "", scrapped_data: dict = {}) -> DBUsers:
    user = get_user_by_linkedin_url(linkedin_url)
    if user:
        return user
    with get_db() as db:
        user = DBUsers(
            linkedin_url=linkedin_url,
            scrapped_data=scrapped_data,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def update_user_bio(linkedin_url: str = "", bio: dict = {}) -> DBUsers:
    user = get_user_by_linkedin_url(linkedin_url)
    if user:
        with get_db() as db:
            user.bio = bio
            db.commit()
            db.refresh(user)
    return user
