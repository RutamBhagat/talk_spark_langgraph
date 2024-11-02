import requests
from app.db.controllers.bio import get_user_by_url, save_new_user


def scrape_profile(profile_url: str) -> str:
    """
    Fetch raw markdown data from a profile (LinkedIn, X.com, etc.) by appending the URL with Jina's fetcher.
    """
    # Check if user exists in the database
    user = get_user_by_url(profile_url)
    if user:
        return user.scrapped_data

    print("Fetching profile in markdown format...")
    # Append Jina's fetcher URL to get raw markdown data
    request_url = f"https://r.jina.ai/{profile_url}"

    response = requests.get(request_url)
    response.raise_for_status()  # Raise an error if the request fails

    # Get the markdown content directly from the response
    markdown_data = response.text

    # Save the new user data to the database
    user = save_new_user(url=profile_url, scrapped_data=markdown_data)

    return user.scrapped_data
