"""Tests d'intégration des routes FastAPI via ASGI transport (sans infrastructure réelle)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# GET /graph/ — graphe NetworkX vide en mémoire
# ---------------------------------------------------------------------------

async def test_graph_empty(client):
    with patch("app.api.routes.graph.get_subgraph", new_callable=AsyncMock, return_value=([], [])):
        resp = await client.get("/graph/")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert "count" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


async def test_graph_with_params(client):
    with patch("app.api.routes.graph.get_subgraph", new_callable=AsyncMock, return_value=([], [])):
        resp = await client.get("/graph/?disease=covid19&region=75&depth=2")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /graph/stats
# ---------------------------------------------------------------------------

async def test_graph_stats_empty(client):
    resp = await client.get("/graph/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "graph" in data
    assert "nodes" in data["graph"]
    assert "edges" in data["graph"]
    assert "centrality" in data
    assert "top_diseases" in data["centrality"]


# ---------------------------------------------------------------------------
# POST /ingest/<source>
# ---------------------------------------------------------------------------

async def test_ingest_unknown_source(client):
    resp = await client.post("/ingest/unknown_source")
    assert resp.status_code == 404
    assert "unknown_source" in resp.json()["detail"]


@pytest.mark.parametrize("source", ["spf", "ecdc", "who", "data_gouv"])
async def test_ingest_known_sources_mocked(client, source):
    """Vérifie que chaque source connue déclenche bien la pipeline — run_ingestion mocké."""
    with patch("app.api.routes.ingest.run_ingestion", new_callable=AsyncMock, return_value=42):
        resp = await client.post(f"/ingest/{source}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == source
    assert data["records_ingested"] == 42


# ---------------------------------------------------------------------------
# POST /query/
# ---------------------------------------------------------------------------

async def test_query_returns_answer(client):
    """Pipeline complète mockée : NER → retrieval → template."""
    fake_entities = {"diseases": ["covid19"], "regions": ["Île-de-France"], "dates": [], "metrics": []}
    fake_docs = [
        {
            "text": "COVID19 — 75 — 2024-01-15 : 1234 hospitalisations.",
            "metadata": {"subject": "disease:covid19", "predicate": "has_hospitalizations_in", "object": "region:75@2024-01-15", "source": "spf"},
            "source": "vector",
        }
    ]
    with (
        patch("app.nlp.extractor.extract_entities", return_value=fake_entities),
        patch("app.rag.retriever.retrieve_context", return_value=fake_docs),
    ):
        resp = await client.post("/query/", json={"question": "Hospitalisations covid en Île-de-France ?"})

    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "sources" in data
    assert "entities" in data
    assert "intent" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


async def test_query_empty_context(client):
    """Quand le retrieval ne trouve rien, la réponse doit l'indiquer clairement."""
    with (
        patch("app.nlp.extractor.extract_entities", return_value={"diseases": [], "regions": [], "dates": [], "metrics": []}),
        patch("app.rag.retriever.retrieve_context", return_value=[]),
    ):
        resp = await client.post("/query/", json={"question": "Quelle est la situation ?"})

    assert resp.status_code == 200
    data = resp.json()
    assert "Aucune donnée" in data["answer"]


async def test_query_missing_field(client):
    resp = await client.post("/query/", json={})
    assert resp.status_code == 422
