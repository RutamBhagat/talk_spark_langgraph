# controllers/bio.py
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import DBProfile


def get_user_by_profile_url(profile_url: str) -> Optional[DBProfile]:
    """
    Retrieve a user from the database based on their profile URL.

    Args:
        profile_url (str): The URL of the user profile.

    Returns:
        Optional[DBProfile]: The user profile if found, else None.
    """
    with get_db() as db:
        return db.query(DBProfile).filter(DBProfile.url == profile_url).first()


def save_new_user(url: str, person: str, scrapped_data: Dict[str, Any]) -> DBProfile:
    """
    Save a new user profile in the database.

    Args:
        url (str): The URL of the user profile.
        person (str): Name of the person.
        scrapped_data (Dict[str, Any]): The scraped profile data.

    Returns:
        DBProfile: The saved user profile.
    """
    with get_db() as db:
        # Check if user exists
        user = get_user_by_profile_url(url)
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

    Args:
        profile_url (str): The URL of the user profile.
        bio (Dict[str, Any]): The new bio data.

    Returns:
        Optional[DBProfile]: The updated user profile if found.
    """
    with get_db() as db:
        user = db.query(DBProfile).filter(DBProfile.url == profile_url).first()
        if user:
            user.bio = bio
            db.commit()
            db.refresh(user)
        return user


# Updated scrape_profile function
async def scrape_profile(
    profile_url: str, person_name: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch and cache profile data.

    Args:
        profile_url (str): URL of the profile to scrape.
        person_name (str): Name of the person.

    Returns:
        Optional[Dict[str, Any]]: The scraped profile data.
    """
    import requests

    # Check cache first
    user = get_user_by_profile_url(profile_url)
    if user and user.scrapped_data:
        return user.scrapped_data

    # Fetch new data
    try:
        request_url = f"https://r.jina.ai/{profile_url}"
        response = requests.get(request_url)
        response.raise_for_status()

        scraped_data = {"raw_content": response.text}

        # Save to database
        save_new_user(url=profile_url, person=person_name, scrapped_data=scraped_data)

        return scraped_data

    except Exception as e:
        print(f"Error scraping profile: {str(e)}")
        return None
