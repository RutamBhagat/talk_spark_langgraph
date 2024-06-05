from dotenv import load_dotenv, find_dotenv
from langgraph.graph import END, StateGraph

from app.graph.state import GraphState
from app.graph.consts import WEB_SEARCH, GENERATE
from app.graph.nodes import generate, web_search
from app.graph.chains.hallucination_grader import hallucination_grader
from app.graph.chains.answer_grader import answer_grader

_ = load_dotenv(find_dotenv())


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("Assessing if the generation is grounded in the documents and question.")
    question = state.question
    documents = state.documents
    generation = state.generation

    is_grounded = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    ).is_grounded

    if is_grounded:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")

        is_answer_valid = answer_grader.invoke(
            {"question": question, "generation": generation}
        ).is_answer_valid

        if is_answer_valid:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


workflow = StateGraph(GraphState)

workflow.add_node(WEB_SEARCH, web_search)
workflow.add_node(GENERATE, generate)

workflow.set_entry_point(WEB_SEARCH)

# workflow.add_conditional_edges(
#     GENERATE,
#     grade_generation_grounded_in_documents_and_question,
#     path_map={"useful": END, "not useful": WEB_SEARCH, "not supported": GENERATE},
# )

workflow.add_edge(WEB_SEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

c_rag_app = workflow.compile()
c_rag_app.get_graph().draw_mermaid_png(output_file_path="graph.png")
