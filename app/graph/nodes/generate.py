from typing import Any, Dict, Optional
from dataclasses import dataclass
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.db.controllers.linkedin_bio import get_user_by_linkedin_url, update_user_bio
from app.graph.chains.generation import generation_chain
from app.graph.state import GraphState

# Configure structured logging
logger = structlog.get_logger()


@dataclass
class UserBioData:
    """
    Data class representing user biographical data.

    Attributes:
        person (str): Name of the person
        bio (Dict[str, Any]): Biographical information
        scrapped_data (Dict[str, Any]): Raw data scraped from LinkedIn
    """

    person: str
    bio: Dict[str, Any]
    scrapped_data: Dict[str, Any]


class BioGenerator:
    """
    A class to handle biography generation and caching for LinkedIn profiles.
    """

    def __init__(self):
        """Initialize the BioGenerator with a logger."""
        self.logger = logger.bind(module="bio_generator")

    async def _generate_bio(
        self, person: str, scrapped_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a biography using the generation chain.

        Args:
            person (str): Name of the person
            scrapped_data (Dict[str, Any]): Scraped LinkedIn data

        Returns:
            Dict[str, Any]: Generated biography

        Raises:
            ValueError: If generation fails
        """
        try:
            bio_response = await generation_chain.ainvoke(
                {"person": person, "scrapped_data": scrapped_data}
            )
            return bio_response.dict()
        except Exception as e:
            self.logger.error("bio_generation_failed", person=person, error=str(e))
            raise ValueError(f"Failed to generate biography: {str(e)}")

    def _get_cached_bio(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached biography from database.

        Args:
            linkedin_url (str): LinkedIn profile URL

        Returns:
            Optional[Dict[str, Any]]: Cached biography if exists, None otherwise
        """
        try:
            user = get_user_by_linkedin_url(linkedin_url)
            return user.bio if user and user.bio else None
        except Exception as e:
            self.logger.error(
                "cache_retrieval_failed", linkedin_url=linkedin_url, error=str(e)
            )
            return None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _update_bio_cache(self, linkedin_url: str, bio: Dict[str, Any]) -> None:
        """
        Update biography cache in database with retry logic.

        Args:
            linkedin_url (str): LinkedIn profile URL
            bio (Dict[str, Any]): Biography to cache

        Raises:
            ValueError: If update fails after retries
        """
        try:
            update_user_bio(linkedin_url=linkedin_url, bio=bio)
            self.logger.info("bio_cache_updated", linkedin_url=linkedin_url)
        except Exception as e:
            self.logger.error(
                "cache_update_failed", linkedin_url=linkedin_url, error=str(e)
            )
            raise ValueError(f"Failed to update bio cache: {str(e)}")

    async def process_bio(self, state: GraphState) -> UserBioData:
        """
        Process biography generation request, using cache when available.

        Args:
            state (GraphState): Current state containing person information

        Returns:
            UserBioData: Generated or cached biographical data

        Raises:
            ValueError: If processing fails
        """
        self.logger.info(
            "processing_bio_request",
            person=state.person,
            linkedin_url=state.linkedin_url,
        )

        # Check cache first
        cached_bio = self._get_cached_bio(state.linkedin_url)
        if cached_bio:
            self.logger.info("using_cached_bio", person=state.person)
            return UserBioData(
                person=state.person, bio=cached_bio, scrapped_data=state.scrapped_data
            )

        # Generate new bio
        self.logger.info("generating_new_bio", person=state.person)
        try:
            bio = await self._generate_bio(state.person, state.scrapped_data)
            await self._update_bio_cache(state.linkedin_url, bio)

            return UserBioData(
                person=state.person, bio=bio, scrapped_data=state.scrapped_data
            )
        except Exception as e:
            self.logger.error(
                "bio_processing_failed", person=state.person, error=str(e)
            )
            raise


async def generate(state: GraphState) -> Dict[str, Any]:
    """
    Generate or retrieve biography for a LinkedIn profile.

    Args:
        state (GraphState): Current state containing person information

    Returns:
        Dict[str, Any]: Dictionary containing person info, biography, and scraped data
    """
    bio_generator = BioGenerator()
    result = await bio_generator.process_bio(state)
    return {
        "person": result.person,
        "bio": result.bio,
        "scrapped_data": result.scrapped_data,
    }
