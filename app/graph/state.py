from typing import Any, Dict, List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field

from app.graph.chains.generation import BioGeneration


class GraphState(BaseModel):
    """Represents the state of our graph.

    Attributes:
        person: The name of the person to generate a bio for.
        linkedin_url: The LinkedIn URL of the person.
        bio: An optional BioGeneration object containing the generated bio.
        scrapped_data: An optional dictionary containing the scraped data.
        urls: An optional list of strings containing profile URLs.
    """

    person: str = Field(..., description="The person to generate a bio for")
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    bio: Optional[BioGeneration] = None
    scrapped_data: Optional[Dict[str, Any]] = None
    urls: Optional[List[str]] = Field(default_factory=list)
