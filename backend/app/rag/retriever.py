"""Retrieval hybride : vectoriel (ChromaDB) + graphe (NetworkX)."""

from app.graph.traversal import get_neighbors
from app.rag.embedder import _get_collection


def retrieve_context(question: str, entities: dict, top_k: int = 10) -> list[dict]:
    collection = _get_collection()

    # Retrieval vectoriel
    results = collection.query(query_texts=[question], n_results=top_k)
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
