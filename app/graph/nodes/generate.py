from typing import Any, Dict
from app.db.access_layer.linkedin_bio import get_user_by_linkedin_url, update_user_bio
from app.graph.chains.generation import generation_chain
from app.graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("Generating answer...")
    person = state.person
    linkedin_url = state.linkedin_url
    scrapped_data = state.scrapped_data

    user = get_user_by_linkedin_url(linkedin_url)
    if user and user.bio:
        return {
            "person": person,
            "bio": user.bio,
            "scrapped_data": scrapped_data,
        }

    bio = generation_chain.invoke({"person": person, "scrapped_data": scrapped_data})
    print("Type of bio: ", type(bio))
    bio = bio.dict()
    update_user_bio(linkedin_url=linkedin_url, bio=bio)
    return {
        "person": person,
        "bio": bio,
        "scrapped_data": scrapped_data,
    }
