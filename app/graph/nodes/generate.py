from typing import Any, Dict
from app.graph.chains.generation import generation_chain
from app.graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("Generating answer...")
    person = state.person
    scrapped_data = state.scrapped_data
    bio = generation_chain.invoke({"person": person, "question": person})
    return {
        "scrapped_data": scrapped_data,
        "bio": bio,
        "question": person,
    }
