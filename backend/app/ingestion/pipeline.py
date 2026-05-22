from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.normalizer import normalize_to_triples
from app.ingestion.sources import data_gouv, ecdc, spf, who

_CONNECTORS = {
    "spf": spf.fetch,
    "ecdc": ecdc.fetch,
    "who": who.fetch,
    "data_gouv": data_gouv.fetch,
}


async def run_ingestion(source: str, session: AsyncSession) -> int:
    fetch = _CONNECTORS[source]
    raw_records = await fetch()
    triples, indicators = await normalize_to_triples(raw_records, source, session)

    # Reconstruction du graphe en mémoire et réindexation des vecteurs
    from app.graph.builder import rebuild_graph
    from app.rag.embedder import index_triples

    await rebuild_graph(session)
    await index_triples(triples)

    return len(indicators)
