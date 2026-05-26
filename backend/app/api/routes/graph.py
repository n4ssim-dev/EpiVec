from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.graph.builder import get_graph, get_collapsed_graph, get_subgraph, rebuild_graph
from app.graph.features import compute_centrality

router = APIRouter()


@router.get("/")
async def get_graph_route(
    disease: str | None = Query(None, description="Filtrer par maladie"),
    region: str | None = Query(None, description="Filtrer par code région"),
    depth: int = Query(2, ge=1, le=5, description="Profondeur de traversal"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    nodes, edges = await get_subgraph(disease=disease, region=region, depth=depth, session=session)
    return {"nodes": nodes, "edges": edges, "count": {"nodes": len(nodes), "edges": len(edges)}}


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_session)) -> dict:
    if get_graph().number_of_nodes() == 0:
        await rebuild_graph(session)
    G = get_collapsed_graph()
    centrality = compute_centrality()

    top_diseases: list[dict] = []
    if centrality:
        pagerank = centrality.get("pagerank", {})
        disease_nodes = {n: s for n, s in pagerank.items() if n.startswith("disease:")}
        top_diseases = [
            {"node": n, "score": round(s, 4)}
            for n, s in sorted(disease_nodes.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

    return {
        "graph": {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
        },
        "centrality": {
            "top_diseases": top_diseases,
        },
    }
