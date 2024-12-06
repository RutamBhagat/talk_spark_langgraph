from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
from langserve import add_routes
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from app.db.database import engine, init_db
from app.graph.state import GraphState
from app.graph.graph import graph
from app.middleware import time_middleware
import asyncio

load_dotenv(find_dotenv())

# API versioning
api_v1_router = APIRouter(prefix="/api/v1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events for the FastAPI application."""
    # Initialize database tables
    init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(time_middleware.middleware)


@app.head("/health")
@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for uptime monitoring."""
    return JSONResponse(content={"status": "healthy"}, status_code=200)


@app.get("/")
async def redirect_root_to_docs() -> RedirectResponse:
    """Redirect root URL to the documentation page."""
    return RedirectResponse("/docs")


async def stream_response(request: GraphState) -> AsyncGenerator[str, None]:
    """Generate streamed response from graph in 'messages' stream mode."""
    async for chunk in graph.astream(request.dict(), stream_mode="messages"):
        if chunk.content:
            yield chunk.content


@api_v1_router.post("/talk_spark")
async def talk_spark(request: GraphState) -> JSONResponse:
    """Handle a asynchronous conversation request."""
    return await graph.ainvoke(request)


@api_v1_router.post("/talk_spark/stream")
async def talk_spark_stream(request: GraphState) -> StreamingResponse:
    """Handle a streamed conversation request."""
    return StreamingResponse(stream_response(request), media_type="text/event-stream")


# Include API v1 router
app.include_router(api_v1_router)

add_routes(
    app,
    graph,
    path="/api/v1/langserve",
    enabled_endpoints=["invoke", "stream", "batch"],
)

if __name__ == "__main__":
    import uvicorn

    # Start FastAPI server and hit the stream route
    async def main():
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)

    asyncio.run(main())
