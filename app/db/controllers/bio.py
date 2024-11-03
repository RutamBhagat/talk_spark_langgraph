# controllers/bio.py
from typing import Optional, Dict, Any
from app.db.database import get_db
from app.models.models import DBProfile


def get_user_by_profile_url(profile_url: str) -> Optional[DBProfile]:
    """
    Retrieve a user from the database based on their profile URL.
    """
    with get_db() as db:
        return db.query(DBProfile).filter(DBProfile.url == profile_url).first()


def save_new_user(url: str, person: str, scrapped_data: Dict[str, Any]) -> DBProfile:
    """
    Save a new user profile in the database.
    """
    with get_db() as db:
        # Check if user exists
        user = db.query(DBProfile).filter(DBProfile.url == url).first()
        if user:
            return user

        # Create new user profile
        user = DBProfile(url=url, person=person, scrapped_data=scrapped_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def update_user_bio(profile_url: str, bio: Dict[str, Any]) -> Optional[DBProfile]:
    """
    Update the bio of an existing user profile.
    """
    with get_db() as db:
        user = db.query(DBProfile).filter(DBProfile.url == profile_url).first()
        if user:
            user.bio = bio
            db.commit()
            db.refresh(user)
        return user
