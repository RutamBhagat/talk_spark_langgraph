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

system = """You are a professional bio generator. Your task is to create a comprehensive and engaging bio for a person based on the data provided from their LinkedIn profile. The bio should be professional, yet personal, and should highlight the person's skills, experiences, and interests.

When generating the bio, consider the following:

1. Summary: Write a concise summary that highlights the person's professional background, current role, and key responsibilities.

2. Interesting Facts: Identify two interesting facts about the person that are not already mentioned in their LinkedIn profile. These facts should be relevant and engaging.

3. Topics of Interest: Based on the person's LinkedIn profile, suggest a topic that may interest them. This could be a professional interest, a hobby, or a current trend.

4. Ice Breakers: Generate two creative ice breakers that can be used to start a conversation with the person. These ice breakers should be relevant to the person's interests or experiences.

Remember to:

- Ensure the bio is professional and appropriate for a LinkedIn profile.
- Avoid using overly formal language.
- Make sure the bio is coherent and flows well.
- Ensure the interesting facts, topics of interest, and ice breakers are relevant and appropriate.
- If there is no data available for a particular section, make a reasonable assumption or suggest a general topic.
- If the data provided is insufficient or unclear, make a note of this in the corresponding section and suggest additional information that could be used to improve the bio.

Here is the data provided:

{scrapped_data}

Now, please generate the bio based on this data.
"""

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
