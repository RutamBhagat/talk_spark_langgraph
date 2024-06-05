from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import DBUsers


db: Session = get_db()


def get_user_by_linkedin_url(linkedin_url: str) -> DBUsers:
    user = db.query(DBUsers).filter(DBUsers.linkedin_url == linkedin_url).first()
    return user


def save_new_user(linkedin_url: str = "", scrapped_data: dict = {}) -> DBUsers:
    # check if user exists
    user = get_user_by_linkedin_url(linkedin_url)
    if user:
        return user
    user = DBUsers(
        linkedin_url=linkedin_url,
        scrapped_data=scrapped_data,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# update user with new bio
def update_user_bio(linkedin_url: str = "", bio: dict = {}) -> DBUsers:
    user = get_user_by_linkedin_url(linkedin_url)
    if user:
        user.bio = bio
        db.commit()
        db.refresh(user)
        return user
