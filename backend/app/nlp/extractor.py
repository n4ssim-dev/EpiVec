"""Extraction d'entités épidémiologiques via spaCy (fr_core_news_lg)."""

from __future__ import annotations

import re
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

_YEAR_RE = re.compile(r"\b(20\d{2})\b")


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("fr_core_news_lg")
    return _nlp


def extract_entities(text: str) -> dict[str, list[str]]:
    nlp = _get_nlp()
    # NER sur le texte original (la casse aide la détection des noms propres)
    doc = nlp(text)
    text_lower = text.lower()

    entities: dict[str, list[str]] = {
        "diseases": [],
        "regions": [],
        "dates": [],
        "metrics": [],
    }

    lower_tokens = {token.text.lower() for token in doc}
    entities["diseases"] = [kw for kw in DISEASE_KEYWORDS if kw in lower_tokens or kw in text_lower]
    entities["metrics"] = [kw for kw in METRIC_KEYWORDS if kw in lower_tokens]

    for ent in doc.ents:
        if ent.label_ in ("LOC", "GPE") and ent.text not in entities["regions"]:
            entities["regions"].append(ent.text)
        if ent.label_ in ("DATE", "TIME") and ent.text not in entities["dates"]:
            entities["dates"].append(ent.text)

    # Fallback : capturer les années (ex: "2021") non détectées par spaCy
    for year in _YEAR_RE.findall(text):
        if year not in entities["dates"]:
            entities["dates"].append(year)

    return entities
