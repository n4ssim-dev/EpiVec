"""Embeddings locaux via sentence-transformers + indexation dans ChromaDB."""

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings

# Modèle multilingue léger (~50 Mo), optimisé pour la similarité sémantique
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_model: SentenceTransformer | None = None
_collection = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        # embedding_function=None : on fournit nos propres vecteurs
        _collection = client.get_or_create_collection(
            name="epigraph_chunks",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_query(question: str) -> list[float]:
    return embed_texts([question])[0]


async def index_chunks(chunks: list[dict]) -> None:
    """Indexe les chunks textuels avec leurs embeddings dans ChromaDB."""
    if not chunks:
        return

    collection = _get_collection()
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    ids = [f"{c['metadata']['disease']}_{c['metadata']['region']}_{c['metadata']['date']}" for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    collection.upsert(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )
