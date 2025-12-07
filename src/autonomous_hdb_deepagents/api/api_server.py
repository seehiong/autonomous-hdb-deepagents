import sys, os
sys.path.append(os.path.abspath("src"))

from fastapi import FastAPI
from pydantic import BaseModel
from autonomous_hdb_deepagents.agent.cli import run_cli

app = FastAPI(title="HDB DeepAgent API")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
async def query(req: QueryRequest):
    response = await run_cli(req.query)
    return {"response": response}
