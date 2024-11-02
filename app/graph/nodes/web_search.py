from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass
import re
import asyncio
from urllib.parse import urlparse
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from dotenv import load_dotenv, find_dotenv
from app.graph.state import GraphState
from app.graph.utils.scrape_linkedin_profile import scrape_linkedin_profile

# Load environment variables
load_dotenv(find_dotenv())


class SearchResult(TypedDict):
    url: str
    title: Optional[str]
    content: Optional[str]


class LinkedInData(TypedDict):
    linkedin_url: str
    scrapped_data: Optional[Dict[str, Any]]


@dataclass
class AgentState:
    """
    Data class representing the state of the agent during profile search and scraping.

    Attributes:
        person (str): Name of the person to search for
        generation (str): Generated content or response
        bio (Dict[str, Any]): Biographical information
        scrapped_data (List[Any]): Raw scraped data from LinkedIn
        linkedin_url (str): LinkedIn profile URL
    """

    person: str
    generation: str = ""
    bio: Dict[str, Any] = None
    scrapped_data: List[Any] = None
    linkedin_url: str = ""

    def __post_init__(self):
        self.bio = self.bio or {}
        self.scrapped_data = self.scrapped_data or []


class LinkedInProfileFinder:
    """
    A class to handle LinkedIn profile search and data scraping operations.
    """

    def __init__(self, max_search_results: int = 5):
        """
        Initialize the LinkedIn profile finder.

        Args:
            max_search_results (int): Maximum number of search results to process
        """
        self.web_search_tool = TavilySearchResults(max_results=max_search_results)
        self.url_pattern = re.compile(r"https://(www\.|in\.)linkedin.com/in/[\w-]+/?$")

    def validate_linkedin_url(self, url: str) -> bool:
        """
        Validate if a URL is a legitimate LinkedIn profile URL.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if URL is valid LinkedIn profile URL, False otherwise
        """
        if not url:
            return False

        try:
            parsed = urlparse(url)
            return (
                parsed.netloc in ("www.linkedin.com", "linkedin.com")
                and parsed.path.startswith("/in/")
                and self.url_pattern.match(url) is not None
            )
        except Exception:
            return False

    def extract_linkedin_url(self, search_results: List[SearchResult]) -> str:
        """
        Extract LinkedIn profile URL from search results.

        Args:
            search_results (List[SearchResult]): List of search results to process

        Returns:
            str: LinkedIn profile URL if found, 'no_url_found' otherwise
        """
        for result in search_results:
            url = result.get("url", "")
            if self.validate_linkedin_url(url):
                return url
        return "no_url_found"

    async def search_profile(self, person_name: str) -> str:
        """
        Search for a person's LinkedIn profile.

        Args:
            person_name (str): Name of the person to search for

        Returns:
            str: LinkedIn profile URL if found, 'no_url_found' otherwise
        """
        try:
            results = await self.web_search_tool.ainvoke(
                {"query": f"{person_name} LinkedIn profile"}
            )
            return self.extract_linkedin_url(results)
        except Exception as e:
            raise ValueError(f"Error searching for profile: {str(e)}")

    async def fetch_profile_data(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Fetch and scrape data from a LinkedIn profile URL.

        Args:
            linkedin_url (str): LinkedIn profile URL to scrape

        Returns:
            Dict[str, Any]: Dictionary containing scraped profile data
        """
        try:
            return scrape_linkedin_profile(linkedin_url)
        except Exception as e:
            raise ValueError(f"Error scraping profile: {str(e)}")

    async def process_profile(self, state: GraphState) -> LinkedInData:
        """
        Process a LinkedIn profile search and scraping request.

        Args:
            state (GraphState): Current state containing person information

        Returns:
            LinkedInData: Dictionary containing LinkedIn URL and scraped data
        """
        linkedin_url = await self.search_profile(state.person)

        if linkedin_url == "no_url_found":
            return LinkedInData(linkedin_url=linkedin_url, scrapped_data=None)

        scrapped_data = await self.fetch_profile_data(linkedin_url)
        return LinkedInData(linkedin_url=linkedin_url, scrapped_data=scrapped_data)


async def web_search(state: GraphState) -> LinkedInData:
    """
    Search for and scrape LinkedIn profile data for a given person.

    Args:
        state (GraphState): Current state containing person information

    Returns:
        LinkedInData: Dictionary containing LinkedIn URL and scraped data
    """
    profile_finder = LinkedInProfileFinder()
    return await profile_finder.process_profile(state)


async def main():
    """
    Main function for testing the LinkedIn profile search and scraping functionality.
    """
    state = AgentState(person="Andrew NG")
    try:
        result = await web_search(state)
        print("Result:", result)
    except Exception as e:
        print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
