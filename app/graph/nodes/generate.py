from typing import Any, Dict, Optional
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.db.controllers.bio import get_user_by_profile_url, update_user_bio
from app.graph.chains.generation import generation_chain
from app.graph.state import GraphState

# Configure structured logging
logger = structlog.get_logger()


class BioGenerator:
    """
    A class to handle bio generation and caching for LinkedIn profiles.
    """

    def __init__(self):
        """Initialize the BioGenerator with a logger."""
        self.logger = logger.bind(module="bio_generator")

    async def generate_bio(
        self, person: str, scrapped_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a bio using the generation chain.

        Args:
            person (str): Name of the person
            scrapped_data (Dict[str, Any]): Scraped LinkedIn data

        Returns:
            Dict[str, Any]: Generated bio

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
            raise ValueError(f"Failed to generate bio: {str(e)}")

    def get_bio_from_db(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve bio from database.

        Args:
            url (str): LinkedIn profile URL

        Returns:
            Optional[Dict[str, Any]]: Returns bio if exists, None otherwise
        """
        try:
            user = get_user_by_profile_url(url)
            return user.bio if user and user.bio else None
        except Exception as e:
            self.logger.error("bio_retrieval_from_db_failed", url=url, error=str(e))
            return None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def update_bio(self, url: str, bio: Dict[str, Any]) -> None:
        """
        Update bio in database with retry logic.

        Args:
            url (str): LinkedIn profile URL
            bio (Dict[str, Any]): bio to update

        Raises:
            ValueError: If update fails after retries
        """
        try:
            update_user_bio(url=url, bio=bio)
            self.logger.info("bio_updated", url=url)
        except Exception as e:
            self.logger.error("bio_update_failed", url=url, error=str(e))
            raise ValueError(f"Failed to update bio in db: {str(e)}")

    async def process_bio(self, state: GraphState):
        """
        Process bio generation request, using bio from db when available.

        Args:
            state (GraphState): Current state containing person information

        Returns:
            UserBioData: Generated or db bio data

        Raises:
            ValueError: If processing fails
        """
        self.logger.info(
            "processing_bio_request",
            person=state.person,
            url=state.url,
        )

        # Check db first
        bio = self.get_bio_from_db(state.url)
        if bio:
            self.logger.info("using_bio_from_db", person=state.person)
            state.bio = bio

        # Generate new bio
        self.logger.info("generating_new_bio", person=state.person)
        try:
            bio = await self.generate_bio(state.person, state.scrapped_data)
            await self.update_bio(state.url, bio)
            state.bio = bio
            return state
        except Exception as e:
            self.logger.error(
                "bio_processing_failed", person=state.person, error=str(e)
            )
            raise


async def generate(state: GraphState):
    """
    Generate or retrieve bio for a LinkedIn profile.

    Args:
        state (GraphState): Current state containing person information

    Returns:
        Dict[str, Any]: Dictionary containing person info, bio, and scraped data
    """
    bio_generator = BioGenerator()
    return await bio_generator.process_bio(state)
