from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.nlp.extractor import extract_entities
from app.nlp.intent import classify_intent
from app.rag.chain import run_graphrag_chain

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    entities: dict[str, list[str]]
    intent: str


@router.post("/", response_model=QueryResponse)
async def query_nlp(req: QueryRequest, session: AsyncSession = Depends(get_session)) -> QueryResponse:
    entities = extract_entities(req.question)
    intent = classify_intent(req.question, entities)
    answer, sources = await run_graphrag_chain(req.question, entities, intent, session)
    return QueryResponse(answer=answer, sources=sources, entities=entities, intent=intent)
