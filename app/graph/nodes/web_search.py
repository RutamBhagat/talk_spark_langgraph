import re
from typing import Any, Dict
from dotenv import load_dotenv, find_dotenv
from langchain_community.tools.tavily_search.tool import TavilySearchResults

load_dotenv(find_dotenv())
from app.graph.state import GraphState

web_search_tool = TavilySearchResults(max_results=3)


def web_search(state: GraphState) -> Dict[str, Any]:
    print("Searching the web for linkedin url...")
    person = state.person
    tavily_results = web_search_tool.invoke(
        {"query": f"provide {person} LinkedIn URL only"}
    )

    linkedin_url = find_linkedin_url(tavily_results)

    return {"linkedin_url": linkedin_url}


def find_linkedin_url(tavily_results):
    linkedin_url_pattern = r"https://www.linkedin.com/in/[\w-]+/?$"

    for result in tavily_results:
        if isinstance(result, dict) and "url" in result:
            url = result["url"]
            if re.match(linkedin_url_pattern, url):
                return url

    return "no_url_found"


if __name__ == "__main__":

    class AgentState:
        def __init__(
            self, person="", documents=[], generation="", linkedin_url="", bio={}
        ):
            self.person = person
            self.generation = generation
            self.bio = bio
            self.documents = documents
            self.linkedin_url = linkedin_url

    state = AgentState(person="Andrew NG")
    res = web_search(state=state)
    print("Result: ", res)
