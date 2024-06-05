from typing import Any, Dict
from app.db.access_layer.linkedin_bio import update_user_bio
from app.graph.chains.generation import generation_chain
from app.graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("Generating answer...")
    person = state.person
    scrapped_data = state.scrapped_data
    bio = generation_chain.invoke({"person": person, "scrapped_data": scrapped_data})
    update_user_bio(linkedin_url=person, bio=bio)
    return {
        "scrapped_data": scrapped_data,
        "bio": bio,
        "question": person,
    }
