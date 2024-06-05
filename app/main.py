import os
import asyncio
import time

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


from app.graph.graph import c_rag_app


async def get_response(person):
    start_time = time.time()
    res = await c_rag_app.ainvoke(input={"person": person})
    end_time = time.time()
    time_taken = end_time - start_time
    return person, res, time_taken


async def main():
    print("Hello Talk Spark with LangGraph")
    people = [
        "Andrew NG",
        "Leon Noel?",
        "Ankur Warikoo",
    ]
    coroutines = [get_response(person) for person in people]
    results = await asyncio.gather(*coroutines)

    with open(os.path.join(os.environ["PYTHONPATH"], "results.md"), "w") as f:
        for people, res, time_taken in results:
            f.write(f"People: {people}\n")
            f.write(f"Time Taken: {time_taken:.2f} seconds\n")
            print("Type of response:", type(res))
            f.write(f"Bio: {res['bio']}\n\n\n\n")


if __name__ == "__main__":
    asyncio.run(main())
