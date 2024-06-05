from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())

from app.db.database import engine
from app.models import models
from app.graph.state import GraphState
from app.graph.graph import c_rag_app
from app.middleware import time_middleware, cors_middleware

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Middleware
cors_middleware.middleware(app)
app.middleware("http")(time_middleware.middleware)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.post("/talk_spark")
async def talk_spark(request: GraphState):
    return await c_rag_app.ainvoke(request.dict())


# Edit this to add the chain you want to add
add_routes(app, c_rag_app, path="/langserve")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
