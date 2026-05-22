"""Tests unitaires — modules sans dépendances externes (pas de DB, pas de ChromaDB)."""

import pytest

# ---------------------------------------------------------------------------
# chunker
# ---------------------------------------------------------------------------

from app.ingestion.chunker import build_chunks


def test_chunker_groups_by_disease_region_date():
    records = [
        {"disease": "covid19", "region_code": "75", "date": "2024-01-15", "metric": "hospitalizations", "value": 1234.0, "source": "spf"},
        {"disease": "covid19", "region_code": "75", "date": "2024-01-15", "metric": "critical_care", "value": 56.0, "source": "spf"},
        {"disease": "covid19", "region_code": "69", "date": "2024-01-15", "metric": "hospitalizations", "value": 450.0, "source": "spf"},
    ]
    chunks = build_chunks(records)
    assert len(chunks) == 2


def test_chunker_text_format():
    records = [
        {"disease": "grippe", "region_code": "FR", "date": "2024-02-01", "metric": "cases", "value": 5000.0, "source": "ecdc"},
    ]
    chunks = build_chunks(records)
    assert len(chunks) == 1
    text = chunks[0]["text"]
    assert "GRIPPE" in text
    assert "FR" in text
    assert "2024-02-01" in text
    assert "5000" in text


def test_chunker_metadata():
    records = [
        {"disease": "covid19", "region_code": "75", "date": "2024-01-01", "metric": "deaths", "value": 12.0, "source": "spf"},
    ]
    chunks = build_chunks(records)
    meta = chunks[0]["metadata"]
    assert meta["disease"] == "covid19"
    assert meta["region"] == "75"
    assert meta["date"] == "2024-01-01"
    assert meta["source"] == "spf"


def test_chunker_empty_input():
    assert build_chunks([]) == []


def test_chunker_integer_values():
    records = [
        {"disease": "covid19", "region_code": "75", "date": "2024-01-01", "metric": "hospitalizations", "value": 100.0, "source": "spf"},
    ]
    chunks = build_chunks(records)
    # 100.0 doit apparaître comme "100" (entier) et non "100.0"
    assert "100 " in chunks[0]["text"]
    assert "100.0" not in chunks[0]["text"]


# ---------------------------------------------------------------------------
# answer_builder
# ---------------------------------------------------------------------------

from app.rag.answer_builder import _build_answer, _format_doc


def _make_doc(subject, predicate, obj, source="vector"):
    return {
        "text": f"{subject} {predicate} {obj}",
        "metadata": {"subject": subject, "predicate": predicate, "object": obj, "source": "spf"},
        "source": source,
    }


def test_answer_builder_empty_docs():
    answer = _build_answer("question ?", [], "stats")
    assert "Aucune donnée" in answer
    assert "ingestion" in answer.lower() or "ingest" in answer.lower()


def test_answer_builder_with_vector_docs():
    docs = [_make_doc("disease:covid19", "has_hospitalizations_in", "region:75@2024-01-15")]
    answer = _build_answer("Hospitalisations en Paris ?", docs, "stats")
    assert "Résultats pour" in answer
    assert "Données épidémiologiques" in answer
    assert "disease:covid19" in answer


def test_answer_builder_trend_intent():
    docs = [
        _make_doc("disease:covid19", "has_cases_in", "region:FR@2024-01-01"),
        _make_doc("disease:covid19", "has_cases_in", "region:FR@2024-02-01"),
    ]
    answer = _build_answer("Évolution des cas ?", docs, "trend")
    assert "Évolution temporelle" in answer


def test_answer_builder_with_graph_docs():
    vector = [_make_doc("disease:covid19", "has_cases_in", "region:FR@2024-01-01")]
    graph = [{"text": "region:75", "metadata": {"source": "graph"}, "source": "graph"}]
    answer = _build_answer("question ?", vector + graph, "stats")
    assert "Relations dans le graphe" in answer
    assert "region:75" in answer


def test_format_doc_with_full_metadata():
    doc = _make_doc("disease:grippe", "has_deaths_in", "region:69@2024-03-01")
    result = _format_doc(doc)
    assert result.startswith("•")
    assert "disease:grippe" in result
    assert "has_deaths_in" in result


def test_format_doc_fallback_to_text():
    doc = {"text": "nœud brut", "metadata": {}, "source": "graph"}
    result = _format_doc(doc)
    assert "nœud brut" in result


# ---------------------------------------------------------------------------
# intent classifier
# ---------------------------------------------------------------------------

from app.nlp.intent import classify_intent


@pytest.mark.parametrize("question,expected", [
    ("Quelle est l'évolution des cas ?", "prediction"),
    ("Comparer la grippe et le covid", "comparison"),
    ("Pourquoi le taux augmente ?", "explanation"),
    ("Où sont les cas les plus élevés ?", "geographic"),
    ("Combien de cas en janvier ?", "query"),
])
def test_classify_intent(question, expected):
    assert classify_intent(question, {}) == expected


# ---------------------------------------------------------------------------
# normalizer — _parse_date
# ---------------------------------------------------------------------------

from app.ingestion.normalizer import _parse_date
from datetime import date


@pytest.mark.parametrize("raw,expected", [
    ("2024-01-15", date(2024, 1, 15)),
    ("15/01/2024", date(2024, 1, 15)),
    ("2024/01/15", date(2024, 1, 15)),
    ("2024-01-15T12:00:00", date(2024, 1, 15)),
    ("not-a-date", None),
    ("", None),
])
def test_parse_date(raw, expected):
    assert _parse_date(raw) == expected
