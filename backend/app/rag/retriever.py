"""Retrieval hybride : vectoriel (ChromaDB + sentence-transformers) + graphe (NetworkX)."""

from app.graph.traversal import get_neighbors
from app.rag.embedder import _get_collection, embed_query


def retrieve_context(question: str, entities: dict, top_k: int = 10) -> list[dict]:
    collection = _get_collection()

    # Retrieval vectoriel avec embedding local de la question
    query_embedding = embed_query(question)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    vector_docs = [
        {"text": doc, "metadata": meta, "source": "vector"}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

    # Retrieval par graphe — voisins des entités extraites
    graph_docs: list[dict] = []
    for disease in entities.get("diseases", []):
        neighbors = get_neighbors(f"disease:{disease}", depth=2)
        graph_docs.extend(
            {"text": n, "metadata": {"source": "graph"}, "source": "graph"}
            for n in neighbors[:5]
        )

    return vector_docs + graph_docs
