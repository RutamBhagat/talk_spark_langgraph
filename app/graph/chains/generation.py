import os
from typing import Optional
from dataclasses import dataclass
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from app.models.models import BioGeneration

# Load environment variables from .env file
load_dotenv()

# Retrieve the OPENAI_MODEL from environment variables
OPENAI_MODEL = os.getenv("OPENAI_MODEL")


@dataclass
class BioGenerationConfig:
    """Configuration for bio generation"""

    temperature: float = 0.0
    model_name: str = OPENAI_MODEL
    max_tokens: Optional[int] = None


class BioGenerationChain:
    """Chain for generating structured biographies from LinkedIn data"""

    def __init__(self, config: Optional[BioGenerationConfig] = None):
        """
        Initialize the bio generation chain with optional configuration.
        Args:
            config: Optional configuration for the generation process
        """
        self.config = config or BioGenerationConfig()
        self.llm = self._setup_llm()
        self.chain = self._build_chain()

    def _setup_llm(self) -> ChatOpenAI:
        """Configure the language model with structured output"""

        llm = ChatOpenAI(
            temperature=self.config.temperature,
            model_name=self.config.model_name,
            max_tokens=self.config.max_tokens,
        )
        return llm.with_structured_output(BioGeneration)

    def _build_chain(self) -> RunnableSequence:
        """Build the generation chain with optimized prompt"""
        system = """Professional bio generator. Create engaging LinkedIn bio from profile data.
                Generate:
                1. Summary: Current role, key achievements
                2. Facts: 2 unique professional insights
                3. Interest: Key topic for discussion
                4. Ice-breakers: 2 relevant conversation starters
                Use profile context: {scrapped_data}"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Profile data for {person}:\n{scrapped_data}"),
            ]
        )

        return prompt | self.llm

    @property
    def generation_chain(self) -> RunnableSequence:
        """Get the configured generation chain"""
        return self.chain


# Initialize the optimized chain with default config
bio_generator = BioGenerationChain()
generation_chain: RunnableSequence = bio_generator.generation_chain
