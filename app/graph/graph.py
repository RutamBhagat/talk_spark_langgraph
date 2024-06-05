from dotenv import load_dotenv, find_dotenv
from langgraph.graph import END, StateGraph

from app.graph.state import GraphState
from app.graph.consts import WEB_SEARCH, GENERATE
from app.graph.nodes import generate, web_search

_ = load_dotenv(find_dotenv())


def should_continue(state: GraphState) -> bool:
    linkedin_url = state.linkedin_url
    if linkedin_url == "no_url_found":
        return "no_url_found"
    return "url_found"


workflow = StateGraph(GraphState)

workflow.add_node(WEB_SEARCH, web_search)
workflow.add_node(GENERATE, generate)

workflow.set_entry_point(WEB_SEARCH)

workflow.add_conditional_edges(
    WEB_SEARCH,
    should_continue,
    path_map={"no_url_found": END, "url_found": GENERATE},
)
workflow.add_edge(GENERATE, END)

c_rag_app = workflow.compile()
c_rag_app.get_graph().draw_mermaid_png(output_file_path="graph.png")
