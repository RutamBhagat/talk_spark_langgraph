from typing import Optional
from pydantic import BaseModel, Field


class UserBody(BaseModel):
    linkedin_url: str = Field(..., description="The user's LinkedIn URL")
    scrapped_data: Optional[dict] = Field(
        None, description="The data scraped from the user's LinkedIn profile"
    )
    bio: Optional[dict] = Field(None, description="The user's bio")
