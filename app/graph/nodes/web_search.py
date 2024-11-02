from typing import Dict, List, Optional, TypedDict
import re
from urllib.parse import urlparse

from langchain_community.tools import TavilySearchResults
from app.graph.state import GraphState
from app.graph.utils.scrape_linkedin_profile import scrape_profile


class SearchResult(TypedDict):
    url: str
    title: Optional[str]
    content: Optional[str]


class ProfileData(TypedDict):
    profile_url: str
    scrapped_data: Optional[str]  # Changed to `str` since data is in markdown format


class ProfileFinder:
    """Handles profile search and scraping for LinkedIn and X.com."""

    def __init__(self, max_search_results: int = 5):
        self.web_search_tool = TavilySearchResults(max_results=max_search_results)
        self.linkedin_pattern = re.compile(
            r"https://(www\.|in\.)linkedin.com/in/[\w-]+/?$"
        )
        self.x_pattern = re.compile(r"https://x.com/[\w-]+/?$")

    def validate_url(self, url: str, platform: str) -> bool:
        pattern = self.linkedin_pattern if platform == "linkedin" else self.x_pattern
        return pattern.match(url) is not None if url else False

    def extract_profile_url(
        self, search_results: List[SearchResult], platform: str
    ) -> str:
        for result in search_results:
            url = result.get("url", "")
            if self.validate_url(url, platform):
                return url
        return "no_url_found"

    async def search_profile(self, person_name: str, platform: str) -> str:
        query = f"site:{platform}.com {person_name}"
        results = await self.web_search_tool.ainvoke({"query": query})
        return self.extract_profile_url(results, platform)

    async def fetch_profile_data(self, profile_url: str) -> str:
        return scrape_profile(profile_url)

    async def process_profiles(self, state: GraphState) -> Dict[str, ProfileData]:
        linkedin_url = await self.search_profile(state.person, "linkedin")
        x_url = await self.search_profile(state.person, "x")

        linkedin_data = (
            await self.fetch_profile_data(linkedin_url)
            if linkedin_url != "no_url_found"
            else None
        )
        x_data = (
            await self.fetch_profile_data(x_url) if x_url != "no_url_found" else None
        )

        return {
            "LinkedIn": ProfileData(
                profile_url=linkedin_url, scrapped_data=linkedin_data
            ),
            "X": ProfileData(profile_url=x_url, scrapped_data=x_data),
        }
