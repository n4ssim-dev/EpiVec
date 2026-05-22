from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import graph, ingest, query

app = FastAPI(
    title="EpiGraph API",
    version="0.1.0",
    description="Plateforme d'analyse épidémiologique par GraphRAG",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Electron consomme l'API en localhost
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
app.include_router(query.router, prefix="/query", tags=["nlp"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok"}
