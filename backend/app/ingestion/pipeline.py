from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.chunker import build_chunks
from app.ingestion.normalizer import normalize_to_triples
from app.ingestion.sources import data_gouv, dengue, ecdc, flunet, mpox, spf, who

_CONNECTORS = {
    "spf": spf.fetch,
    "ecdc": ecdc.fetch,
    "who": who.fetch,
    "data_gouv": data_gouv.fetch,
    "flunet": flunet.fetch,
    "mpox": mpox.fetch,
    "dengue": dengue.fetch,
}


async def run_ingestion(source: str, session: AsyncSession) -> int:
    fetch = _CONNECTORS[source]
    raw_records = await fetch()

    # Ajout de la source sur chaque record pour les métadonnées des chunks
    for rec in raw_records:
        rec["source"] = source

    # 1. Normalisation → triples PostgreSQL + indicateurs
    triples, indicators = await normalize_to_triples(raw_records, source, session)

    # 2. Reconstruction du graphe NetworkX en mémoire
    from app.graph.builder import rebuild_graph
    await rebuild_graph(session)

    # 3. Chunking → embeddings locaux → ChromaDB
    from app.rag.embedder import index_chunks
    chunks = build_chunks(raw_records)
    await index_chunks(chunks)

    return len(indicators)
