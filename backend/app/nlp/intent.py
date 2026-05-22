"""Classification de l'intention d'une requête en langage naturel."""

_PATTERNS: dict[str, list[str]] = {
    "prediction": [
        "prévoir", "prédire", "évolution", "tendance", "projection",
        "combien dans", "dans combien", "prochaines semaines", "prochains mois",
    ],
    "comparison": [
        "comparer", "différence", "versus", "par rapport", "plus que",
        "moins que", "entre", "comparaison",
    ],
    "explanation": [
        "pourquoi", "cause", "raison", "expliquer", "facteur",
        "comment se fait", "qu'est-ce qui",
    ],
    "geographic": [
        "où", "région", "département", "pays", "territoire",
        "carte", "géographie", "localisation",
    ],
}


def classify_intent(question: str, entities: dict) -> str:
    q = question.lower()
    for intent, keywords in _PATTERNS.items():
        if any(kw in q for kw in keywords):
            return intent
    return "query"
