from langgraph.graph import END, StateGraph
from dotenv import load_dotenv, find_dotenv
from app.graph.state import GraphState
from app.graph.nodes import generate, process_profiles
from app.graph.consts import WEB_SEARCH, GENERATE

# Load environment variables
_ = load_dotenv(find_dotenv())


def save_graph_visualization(graph: StateGraph, filename: str = "graph.png") -> None:
    """Save graph visualization to file."""
    with open(filename, "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())


def should_continue(state: GraphState) -> bool:
    url = state.url
    if url is None:
        return "NO_URL_FOUND"
    return "URL_FOUND"


def build_graph() -> StateGraph:
    """Construct and compile the state graph."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node(WEB_SEARCH, process_profiles)
    workflow.add_node(GENERATE, generate)

    # Set entry point
    workflow.set_entry_point(WEB_SEARCH)

    # Add conditional edges
    workflow.add_conditional_edges(
        WEB_SEARCH,
        should_continue,
        path_map={"NO_URL_FOUND": END, "URL_FOUND": GENERATE},
    )
    workflow.add_edge(GENERATE, END)

    return workflow.compile()


# Build and compile the graph
graph = build_graph()

save_graph_visualization(graph)
