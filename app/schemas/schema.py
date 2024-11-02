from typing import Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """
    A generic model for representing a user profile scraped from various platforms.
    """

    profile_url: str = Field(
        ..., description="The URL of the user's profile on any platform"
    )
    scrapped_data: Optional[str] = Field(
        None, description="The data scraped from the user's profile in markdown format"
    )
    bio: Optional[str] = Field(None, description="The user's bio in markdown format")
