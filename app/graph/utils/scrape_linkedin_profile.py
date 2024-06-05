import os
import requests


def scrape_linkedin_profile(linkedin_url: str):
    """
    Scrape information from LinkedIn profiles,
    Manually scrape the information from LinkedIn profile
    """
    print("Linkedin URL: ", linkedin_url)

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

    return data
