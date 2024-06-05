from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI


class BioGeneration(BaseModel):
    """Bio generated of the person from linkedin_url and scrapped data"""

    summary: str = Field(description="Summary of the person")
    interesting_facts: List[str] = Field(
        description="Two interesting facts about the person"
    )
    topics_of_interest: str = Field(description="Topic that may interest the person")
    ice_breakers: List[str] = Field(
        description="Two creative ice breakers to start a conversation with the person"
    )


llm = ChatOpenAI(temperature=0)

structured_llm_response = llm.with_structured_output(BioGeneration)

system = """<FILL>"""

generation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "List of scrapped_data: \n\n {scrapped_data}",
        ),
    ]
)

generation_chain: RunnableSequence = generation_prompt | structured_llm_response
