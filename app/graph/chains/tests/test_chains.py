from pprint import pprint

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # Do not move this below other app. imports

from app.graph.chains.generation import generation_chain


def test_generation_chain() -> None:
    question = "LangChain Expression Language?"
    # generation = generation_chain.invoke({"context": docs, "question": question})
    # pprint(generation)
