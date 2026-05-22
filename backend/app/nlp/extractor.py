"""Extraction d'entités épidémiologiques via spaCy (fr_core_news_lg)."""

from __future__ import annotations

import spacy

_nlp = None

DISEASE_KEYWORDS = {
    "covid", "covid-19", "grippe", "influenza", "dengue",
    "mpox", "monkeypox", "rougeole", "choléra", "ebola",
    "tuberculose", "sida", "vih", "hépatite",
}

METRIC_KEYWORDS = {
    "cas", "décès", "mort", "hospitalisation", "réanimation",
    "taux", "rt", "incidence", "prévalence", "mortalité",
}


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("fr_core_news_lg")
    return _nlp


def extract_entities(text: str) -> dict[str, list[str]]:
    nlp = _get_nlp()
    doc = nlp(text.lower())

    entities: dict[str, list[str]] = {
        "diseases": [],
        "regions": [],
        "dates": [],
        "metrics": [],
    }

    tokens = {token.text for token in doc}
    entities["diseases"] = list(tokens & DISEASE_KEYWORDS)
    entities["metrics"] = list(tokens & METRIC_KEYWORDS)

    for ent in doc.ents:
        if ent.label_ in ("LOC", "GPE") and ent.text not in entities["regions"]:
            entities["regions"].append(ent.text)
        if ent.label_ in ("DATE", "TIME") and ent.text not in entities["dates"]:
            entities["dates"].append(ent.text)

    return entities
