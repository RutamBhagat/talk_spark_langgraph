from typing import Any, Dict, List, Optional, TypedDict
import re
from langchain_community.tools import TavilySearchResults
from app.graph.state import GraphState
from app.graph.utils.scrape_profile import scrape_profile


class SearchResult(TypedDict):
    """Type definition for search results"""

    url: str
    title: Optional[str]
    content: Optional[str]


class ProfileData(TypedDict):
    """Type definition for profile data"""

    profile_url: str
    scrapped_data: Optional[Dict[str, Any]]
    person: Optional[str]


def validate_url(url: str, platform: str) -> bool:
    """Validate if a URL matches the expected pattern for a given platform"""
    patterns = {
        "linkedin": re.compile(r"https://(www\.|in\.)linkedin.com/in/[\w-]+/?$"),
        "x": re.compile(r"https://x.com/[\w-]+/?$"),
    }
    pattern = patterns.get(platform.lower())
    return bool(pattern and pattern.match(url)) if url else False


def extract_profile_url(search_results: List[SearchResult], platform: str) -> str:
    """Extract the first valid profile URL from search results"""
    for result in search_results:
        url = result.get("url", "")
        if validate_url(url, platform):
            return url
    return "no_url_found"


async def search_profile(
    person_name: str, platform: str, max_search_results: int = 5
) -> str:
    """Search for a person's profile on a specific platform"""
    web_search_tool = TavilySearchResults(max_results=max_search_results)
    query = f"site:{platform}.com {person_name}"
    results = await web_search_tool.ainvoke({"query": query})
    return extract_profile_url(results, platform)


async def process_profiles(
    state: GraphState, max_search_results: int = 1
) -> Dict[str, ProfileData]:
    """Process profiles for a given person and update state"""
    # Search for profiles
    linkedin_url = await search_profile(state.person, "linkedin", max_search_results)
    x_url = await search_profile(state.person, "x", max_search_results)

    # Update state with URLs
    state.linkedin_url = linkedin_url
    state.urls = [url for url in [linkedin_url, x_url] if url != "no_url_found"]

    # Fetch profile data
    linkedin_data = None
    if linkedin_url != "no_url_found":
        linkedin_data = await scrape_profile(linkedin_url, state.person)
        state.scrapped_data = linkedin_data

    x_data = None
    if x_url != "no_url_found":
        x_data = await scrape_profile(x_url, state.person)

    return {
        "LinkedIn": ProfileData(
            profile_url=linkedin_url, scrapped_data=linkedin_data, person=state.person
        ),
        "X": ProfileData(profile_url=x_url, scrapped_data=x_data, person=state.person),
    }
