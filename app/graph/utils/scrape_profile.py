import asyncio
import aiohttp
from typing import Optional
from functools import partial
from app.db.controllers.bio import get_user_by_profile_url, save_new_user


async def scrape_profile(profile_url: str, person: str) -> str:
    """
    Fetch raw markdown data from a profile (wikipedia.org, etc.) by appending the URL with Jina's fetcher.
    Uses asyncio for HTTP requests and handles database operations in the event loop.
    """
    # Run database check in the event loop
    loop = asyncio.get_running_loop()
    user = await loop.run_in_executor(None, get_user_by_profile_url, profile_url)

    if user:
        return user.scrapped_data

    print("Fetching profile in markdown format...")
    request_url = f"https://r.jina.ai/{profile_url}"

    # Fetch markdown data asynchronously
    async with aiohttp.ClientSession() as session:
        async with session.get(request_url) as response:
            response.raise_for_status()
            markdown_data = await response.text()

    # Run database save in the event loop
    user = await loop.run_in_executor(
        None,
        partial(
            save_new_user, url=profile_url, person=person, scrapped_data=markdown_data
        ),
    )

    return user.scrapped_data
