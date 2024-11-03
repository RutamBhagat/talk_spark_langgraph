from langgraph.graph import END, StateGraph

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

from app.graph.state import GraphState
from app.graph.nodes import generate, process_profiles
from app.graph.consts import WEB_SEARCH, GENERATE


def should_continue(state: GraphState) -> bool:
    url = state.url
    if url is None:
        return "NO_URL_FOUND"
    return "URL_FOUND"


workflow = StateGraph(GraphState)

workflow.add_node(WEB_SEARCH, process_profiles)
workflow.add_node(GENERATE, generate)

workflow.set_entry_point(WEB_SEARCH)

workflow.add_conditional_edges(
    WEB_SEARCH,
    should_continue,
    path_map={"NO_URL_FOUND": END, "URL_FOUND": GENERATE},
)
workflow.add_edge(GENERATE, END)

c_rag_app = workflow.compile()
# c_rag_app.get_graph().draw_mermaid_png(output_file_path="graph.png")
