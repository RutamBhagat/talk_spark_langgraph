from typing import Any, Dict, List, Optional, TypedDict, Tuple
from langchain_community.tools import TavilySearchResults
from app.graph.state import GraphState
from app.graph.utils.scrape_profile import scrape_profile


class SearchResult(TypedDict):
    """Type definition for search results"""

    url: str
    content: str


class ProfileData(TypedDict):
    """Type definition for profile data"""

    profile_url: str
    scrapped_data: Optional[Dict[str, Any]]
    person: Optional[str]


def extract_profile_scrapped_data(
    state: GraphState, search_results: List[SearchResult]
) -> GraphState:
    """
    Extract profile data from search results and update state

    Args:
        state: Current graph state
        search_results: List of search results to process

    Returns:
        Updated graph state with scrapped data and URL
    """
    if not search_results:
        return state

    # Combine all content
    state.scrapped_data = " ".join(
        result.get("content", "") for result in search_results
    )

    # Set URL from first result if available
    if search_results[0].get("url"):
        state.url = search_results[0]["url"]

    return state


async def search_profile(
    state: GraphState, max_search_results: int = 5
) -> List[SearchResult]:
    """
    Search for a person's profile on a specific platform

    Args:
        state: Current graph state containing person info
        max_search_results: Maximum number of search results to return

    Returns:
        List of search results
    """
    if not state.person:
        return []

    web_search_tool = TavilySearchResults(max_results=max_search_results)
    results = await web_search_tool.ainvoke({"query": state.person})

    return results if results else []


async def process_profiles(state: GraphState) -> GraphState:
    """
    Process profiles for a given person and update state

    Args:
        state: Current graph state
        max_search_results: Maximum number of search results to process

    Returns:
        Updated graph state with profile data
    """
    max_search_results: int = 5
    try:
        # Search for profiles
        search_results = await search_profile(state, max_search_results)

        # Extract data and update state
        state = extract_profile_scrapped_data(state, search_results)

        # Scrape profile if URL was found
        if state.url and state.url != "no_url_found":
            state.scrapped_data += await scrape_profile(state.url, person=state.person)

        return state

    except Exception as e:
        # Log error if needed
        state.error = str(e)
        return state
