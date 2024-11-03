from typing import Optional

from pydantic import BaseModel, Field

from app.graph.chains.generation import BioGeneration


class GraphState(BaseModel):
    """Represents the state of our graph.

    Attributes:
        person: The name of the person to generate a bio for.
        url: The URL of the person.
        bio: An optional BioGeneration object containing the generated bio.
        scrapped_data: An optional dictionary containing the scraped data.
    """

    person: str = Field(..., description="The person to generate a bio for")
    url: str = Field(..., description="Profile URL")
    bio: Optional[BioGeneration] = None
    scrapped_data: Optional[str] = None
