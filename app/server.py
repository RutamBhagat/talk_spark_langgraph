from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

from app.db.database import engine
from app.models import models
from app.graph.graph import c_rag_app


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, c_rag_app, path="/code_wizard")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
