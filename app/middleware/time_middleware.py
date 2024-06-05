import time
from fastapi import Request


async def middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    duration = f"{end_time - start_time:.2f}"
    print(f"Request took {duration} seconds")
    response.headers["X-Response-Time"] = str(duration)
    return response
