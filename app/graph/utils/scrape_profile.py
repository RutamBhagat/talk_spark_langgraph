import asyncio
import aiohttp
import re
from typing import Optional
from functools import partial
from app.db.controllers.bio import get_user_by_profile_url, save_new_user


def clean_markdown(markdown_content: str) -> str:
    """
    Clean markdown content by removing unnecessary elements while preserving core information.
    """
    # Remove HTML tags
    content = re.sub(r"<[^>]+>", "", markdown_content)

    # Remove markdown links but keep link text
    content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)

    # Remove reference-style links
    content = re.sub(r"\[\^?\d+\](?:\[[^\]]*\]|\([^\)]*\))?", "", content)

    # Remove URLs
    content = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        content,
    )

    # Remove markdown tables
    content = re.sub(r"\|[^\n]*\|", "", content)
    content = re.sub(r"[-|]+\s*\n", "", content)

    # Remove footnotes
    content = re.sub(r"^\[\^[^\]]*\]:[^\n]*$", "", content, flags=re.MULTILINE)

    # Remove image markdown
    content = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", content)

    # Remove emphasis markers but keep the text
    content = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", content)

    # Remove heading markers
    content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)

    # Clean up any remaining artifacts
    content = re.sub(r"\s+", " ", content)  # Collapse multiple spaces
    content = re.sub(r"\n\s*\n", "\n\n", content)  # Normalize line breaks
    content = re.sub(r"^\s+|\s+$", "", content, flags=re.MULTILINE)  # Trim lines

    # Final cleanup
    cleaned_paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    return "\n\n".join(cleaned_paragraphs)


async def scrape_profile(profile_url: str, person: str) -> str:
    """
    Fetch and clean markdown data from a profile using Jina's fetcher.
    Uses asyncio for HTTP requests and handles database operations asynchronously.

    Args:
        profile_url (str): URL of the profile to scrape
        person (str): Name of the person whose profile is being scraped

    Returns:
        str: Cleaned markdown content with unnecessary elements removed
    """
    # Check if the profile already exists in the database
    user = get_user_by_profile_url(profile_url)
    if user:
        return clean_markdown(user.scrapped_data)

    print("Fetching profile in markdown format...")
    request_url = f"https://r.jina.ai/{profile_url}"

    # Fetch markdown data asynchronously
    async with aiohttp.ClientSession() as session:
        async with session.get(request_url) as response:
            response.raise_for_status()
            markdown_data = await response.text()

    # Clean the markdown data
    cleaned_data = clean_markdown(markdown_data)

    # Save the new profile in the database
    save_new_user(url=profile_url, person=person, scrapped_data=cleaned_data)

    return cleaned_data
