from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.ingestion.pipeline import run_ingestion

router = APIRouter()

SOURCES = {"spf", "ecdc", "who", "data_gouv"}


@router.post("/{source}")
async def ingest_source(source: str, session: AsyncSession = Depends(get_session)) -> dict:
    if source not in SOURCES:
        raise HTTPException(status_code=404, detail=f"Source inconnue : {source}. Valides : {SOURCES}")
    records = await run_ingestion(source, session)
    return {"source": source, "records_ingested": records}


@router.post("/")
async def ingest_all(session: AsyncSession = Depends(get_session)) -> dict:
    results = {}
    for source in SOURCES:
        results[source] = await run_ingestion(source, session)
    return {"results": results}
