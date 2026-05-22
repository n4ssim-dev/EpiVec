from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import graph, ingest, predict, query
from app.core.database import create_tables

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
app.include_router(predict.router, prefix="/predict", tags=["prediction"])


@app.on_event("startup")
async def startup() -> None:
    await create_tables()


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok"}
