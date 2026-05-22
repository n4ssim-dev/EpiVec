"""Indexation des triples dans ChromaDB pour le retrieval vectoriel."""

import chromadb

from app.core.config import settings
from app.models.triple import Triple

_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        _collection = client.get_or_create_collection(
            name="epigraph_triples",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


async def index_triples(triples: list[Triple]) -> None:
    if not triples:
        return

    collection = _get_collection()
    documents = [f"{t.subject} {t.predicate} {t.object}" for t in triples]
    ids = [str(t.id) for t in triples]
    metadatas = [
        {"subject": t.subject, "predicate": t.predicate, "object": t.object, "source": t.source}
        for t in triples
    ]
    collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
