import os
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from app.graph.graph import c_rag_app

# Configure structured logging
logger = structlog.get_logger()
load_dotenv(find_dotenv())


@dataclass
class PersonResult:
    """Stores the result of processing a person's information."""

    name: str
    bio: str
    time_taken: float
    metadata: Dict[str, Any] = None


class BatchProcessor:
    """Handles batch processing of person data, including retries, saving results, and logging."""

    def __init__(self, output_path: str = None):
        self.output_path = Path(
            output_path or os.path.join(os.environ["PYTHONPATH"], "results.md")
        )
        self.logger = logger.bind(module="batch_processor")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_response(self, person: str) -> PersonResult:
        """Get response for a single person with retry logic and error handling.

        Args:
            person (str): Name of the person to process.

        Returns:
            PersonResult: Contains processed information and metadata.
        """
        start_time = time.time()
        try:
            response = await c_rag_app.ainvoke(input={"person": person})
            time_taken = time.time() - start_time

            return PersonResult(
                name=person,
                bio=response.get("bio", "Bio not available"),
                time_taken=time_taken,
                metadata=response.get("metadata", {}),
            )
        except Exception as e:
            self.logger.error(
                "error_getting_response",
                person=person,
                error=str(e),
                time_taken=time.time() - start_time,
            )
            raise

    async def process_batch(
        self, people: List[str], batch_size: int = 3
    ) -> List[PersonResult]:
        """Process a list of people in batches to manage system load.

        Args:
            people (List[str]): List of person names to process.
            batch_size (int): Number of people to process in each batch.

        Returns:
            List[PersonResult]: Results of processed people.
        """
        results = []
        for i in range(0, len(people), batch_size):
            batch = people[i : i + batch_size]
            self.logger.info(
                "processing_batch",
                batch_number=i // batch_size + 1,
                batch_size=len(batch),
            )

            batch_results = await asyncio.gather(
                *(self.get_response(person) for person in batch), return_exceptions=True
            )

            valid_results = [
                result for result in batch_results if not isinstance(result, Exception)
            ]
            results.extend(valid_results)

            if i + batch_size < len(people):
                await asyncio.sleep(1)

        return results

    async def save_results(self, results: List[PersonResult]) -> None:
        """Save processing results to a markdown file.

        Args:
            results (List[PersonResult]): List of processed results to save.
        """
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write("# Batch Processing Results\n\n")
                for result in results:
                    f.write(f"## Person: {result.name}\n")
                    f.write(f"* Time Taken: {result.time_taken:.2f} seconds\n")
                    f.write(f"* Bio: {result.bio}\n")
                    if result.metadata:
                        f.write("\n### Additional Metadata:\n")
                        for key, value in result.metadata.items():
                            f.write(f"* {key}: {value}\n")
                    f.write("\n---\n\n")

            self.logger.info(
                "results_saved",
                file_path=str(self.output_path),
                total_results=len(results),
            )

        except Exception as e:
            self.logger.error(
                "error_saving_results", error=str(e), file_path=str(self.output_path)
            )
            raise


async def main() -> None:
    """Main function to initialize batch processing and save results."""
    people = [
        "Andrew NG",
        "Leon Noel",
        "Ankur Warikoo",
        # Add more people here
    ]

    try:
        processor = BatchProcessor()
        logger.info("starting_batch_processing", total_people=len(people))

        results = await processor.process_batch(people)
        await processor.save_results(results)

        logger.info(
            "processing_completed",
            total_processed=len(results),
            average_time=sum(r.time_taken for r in results) / len(results),
        )

    except Exception as e:
        logger.error("fatal_error", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
