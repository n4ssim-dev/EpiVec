"""Retrieval hybride : vectoriel filtré (ChromaDB) + graphe (NetworkX)."""

import re

from app.graph.traversal import get_neighbors
from app.rag.embedder import _get_collection, embed_query

_DISEASE_ALIASES: dict[str, str] = {
    "covid":      "covid19",
    "covid-19":   "covid19",
    "sars-cov-2": "covid19",
    "grippe":     "influenza",
    "monkeypox":  "mpox",
}

_REGION_CODES: dict[str, str] = {
    "france":          "FR",
    "allemagne":       "DE",
    "espagne":         "ES",
    "italie":          "IT",
    "royaume-uni":     "GB",
    "grande-bretagne": "GB",
    "angleterre":      "GB",
    "états-unis":      "US",
    "etats-unis":      "US",
    "usa":             "US",
    "brésil":          "BR",
    "bresil":          "BR",
    "inde":            "IN",
    "australie":       "AU",
    "canada":          "CA",
    "mexique":         "MX",
    "colombie":        "CO",
    "pérou":           "PE",
    "argentina":       "AR",
    "argentine":       "AR",
    "philippines":     "PH",
    "thaïlande":       "TH",
    "vietnam":         "VN",
    "bangladesh":      "BD",
    "congo":           "CD",
    "rdc":             "CD",
}

_YEAR_RE = re.compile(r"\b(20\d{2})\b")

# Codes INSEE pour la France métropolitaine (SPF stocke les départements)
_FR_DEPT_CODES = {str(i).zfill(2) for i in range(1, 96)} | {"2A", "2B"}


def _normalize_disease(raw: str) -> str:
    return _DISEASE_ALIASES.get(raw.lower(), raw.lower())


def _normalize_region(raw: str) -> str | None:
    return _REGION_CODES.get(raw.lower())


def _extract_year(dates: list[str]) -> str | None:
    for d in dates:
        m = _YEAR_RE.search(d)
        if m:
            return m.group(1)
    return None


def _matches_region(stored_region: str, target_code: str | None) -> bool:
    """Vérifie si un code région stocké correspond à la région demandée.

    "France" (→ "FR") accepte aussi les codes département INSEE (75, 59…).
    """
    if target_code is None:
        return True
    if stored_region == target_code:
        return True
    # Si on cherche la France, on accepte tous les départements français
    if target_code == "FR" and stored_region in _FR_DEPT_CODES:
        return True
    return False


def _query_with_fallback(
    collection,
    query_embedding: list[float],
    disease: str | None,
    top_k: int,
) -> list[dict]:
    """Requête ChromaDB avec filtre maladie, fallback sans filtre si vide."""
    def _run(where=None):
        kwargs = {"query_embeddings": [query_embedding], "n_results": top_k}
        if where:
            kwargs["where"] = where
        return collection.query(**kwargs)

    if disease:
        try:
            results = _run({"disease": disease})
            docs = results["documents"][0]
            if docs:
                return _pack(results)
        except Exception:
            pass

    # Fallback : sans filtre
    results = _run()
    return _pack(results)


def _pack(results) -> list[dict]:
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def retrieve_context(question: str, entities: dict, top_k: int = 20) -> list[dict]:
    collection = _get_collection()
    query_embedding = embed_query(question)

    diseases = entities.get("diseases", [])
    normalized_disease = _normalize_disease(diseases[0]) if diseases else None

    regions = entities.get("regions", [])
    target_region = _normalize_region(regions[0]) if regions else None

    year = _extract_year(entities.get("dates", []))

    # 1. Retrieval vectoriel filtré par maladie (ChromaDB)
    # On demande plus de résultats pour compenser le post-filtrage
    all_docs = _query_with_fallback(collection, query_embedding, normalized_disease, top_k)

    # 2. Post-filtrage par année et région en Python
    filtered = [
        d for d in all_docs
        if (year is None or d["metadata"].get("date", "").startswith(year))
        and _matches_region(d["metadata"].get("region", ""), target_region)
    ]

    # Si le post-filtrage est trop restrictif, on relâche progressivement
    if not filtered and year:
        filtered = [
            d for d in all_docs
            if _matches_region(d["metadata"].get("region", ""), target_region)
        ]
    if not filtered:
        filtered = all_docs

    vector_docs = [{"text": d["text"], "metadata": d["metadata"], "source": "vector"}
                   for d in filtered[:10]]

    # 3. Retrieval par graphe
    graph_docs: list[dict] = []
    if normalized_disease:
        neighbors = get_neighbors(f"disease:{normalized_disease}", depth=2)
        graph_docs = [
            {"text": n, "metadata": {"source": "graph"}, "source": "graph"}
            for n in neighbors[:5]
        ]

    return vector_docs + graph_docs
