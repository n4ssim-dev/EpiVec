from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.graph.builder import get_subgraph

router = APIRouter()


@router.get("/")
async def get_graph(
    disease: str | None = Query(None, description="Filtrer par maladie"),
    region: str | None = Query(None, description="Filtrer par code région"),
    depth: int = Query(2, ge=1, le=5, description="Profondeur de traversal"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    nodes, edges = await get_subgraph(disease=disease, region=region, depth=depth, session=session)
    return {"nodes": nodes, "edges": edges, "count": {"nodes": len(nodes), "edges": len(edges)}}
