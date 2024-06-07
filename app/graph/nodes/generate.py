from typing import Any, Dict
from app.db.controllers.linkedin_bio import get_user_by_linkedin_url, update_user_bio
from app.graph.chains.generation import generation_chain
from app.graph.state import GraphState


async def generate(state: GraphState) -> Dict[str, Any]:
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

    print("Generating answer...")
    bio = await generation_chain.ainvoke(
        {"person": person, "scrapped_data": scrapped_data}
    )  # this is an async function
    print("Type of bio: ", type(bio))
    bio = bio.dict()
    update_user_bio(linkedin_url=linkedin_url, bio=bio)
    return {
        "person": person,
        "bio": bio,
        "scrapped_data": scrapped_data,
    }
