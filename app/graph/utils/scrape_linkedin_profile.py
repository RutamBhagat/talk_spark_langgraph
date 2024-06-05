import os
import requests
from app.db.access_layer.linkedin_bio import get_user_by_linkedin_url, save_new_user


def scrape_linkedin_profile(linkedin_url: str):
    """
    Scrape information from LinkedIn profiles,
    Manually scrape the information from LinkedIn profile
    """
    # Check if user exists in the database
    user = get_user_by_linkedin_url(linkedin_url)
    if user:
        return user.scrapped_data

    print("Scraping LinkedIn profile...")
    # If user does not exist, fetch the data
    api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
    header_dic = {"Authorization": f"Bearer {os.getenv('PROXYCURL_API_KEY')}"}

    response = requests.get(
        api_endpoint,
        headers=header_dic,
        params={"url": linkedin_url},
    )

    data = response.json()

    # This is dictionary comprehension filtering out empty values and unwanted keys
    data = {
        data_key: data_value
        for data_key, data_value in data.items()
        if data_key not in ["people_also_viewed", "certifications"]
        and data_value not in ([], "", None)
    }

    # This removes the groups profile_pic_url from the data
    if data.get("groups"):
        for group_dict in data.get("groups"):
            group_dict.pop("profile_pic_url")

    # Save the new user
    user = save_new_user(linkedin_url=linkedin_url, scrapped_data=data)

    return user.scrapped_data
