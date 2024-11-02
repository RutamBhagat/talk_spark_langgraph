from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from langserve import add_routes
from dotenv import load_dotenv, find_dotenv
from typing import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langchain_core.messages import AIMessageChunk
from app.db.database import engine
from app.models import models
from app.graph.state import GraphState
from app.graph.graph import c_rag_app
from app.middleware import time_middleware

load_dotenv(find_dotenv())

# API versioning
api_v1_router = APIRouter(prefix="/api/v1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events for the FastAPI application."""
    models.Base.metadata.create_all(bind=engine)
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
    """Generate streamed response from c_rag_app in 'messages' stream mode."""
    async for chunk in c_rag_app.astream(request.dict(), stream_mode="messages"):
        if isinstance(chunk, AIMessageChunk):
            if chunk.content:
                yield chunk.content
            if chunk.tool_call_chunks:
                yield str(chunk.tool_calls)


@api_v1_router.post("/talk_spark")
async def talk_spark(request: GraphState) -> JSONResponse:
    """Handle a synchronous conversation request."""
    return await c_rag_app.ainvoke(request.dict())


@api_v1_router.post("/talk_spark/stream")
async def talk_spark_stream(request: GraphState) -> StreamingResponse:
    """Handle a streamed conversation request."""
    return StreamingResponse(stream_response(request), media_type="text/event-stream")


# Include API v1 router
app.include_router(api_v1_router)

add_routes(
    app,
    c_rag_app,
    path="/api/v1/langserve",
    enabled_endpoints=["invoke", "stream", "batch"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)
