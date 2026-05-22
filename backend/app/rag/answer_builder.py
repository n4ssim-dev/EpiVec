"""Assemblage de réponse par template depuis les documents récupérés — sans LLM."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _format_doc(doc: dict) -> str:
    meta = doc.get("metadata", {})
    subject = meta.get("subject", "")
    predicate = meta.get("predicate", "")
    obj = meta.get("object", "")
    if subject and predicate and obj:
        return f"• {subject} {predicate} {obj}"
    return f"• {doc['text']}"


def _build_answer(question: str, docs: list[dict], intent: str) -> str:
    if not docs:
        return (
            "Aucune donnée disponible dans le graphe de connaissances pour cette question.\n"
            "Lancez d'abord une ingestion via POST /ingest/<source>."
        )

    vector_docs = [d for d in docs if d["source"] == "vector"]
    graph_docs = [d for d in docs if d["source"] == "graph"]

    lines = [f"Résultats pour : « {question} »\n"]

    if vector_docs:
        label = "Évolution temporelle :" if intent == "trend" else "Données épidémiologiques :"
        lines.append(label)
        ordered = (
            sorted(vector_docs[:6], key=lambda d: d["metadata"].get("object", ""))
            if intent == "trend"
            else vector_docs[:6]
        )
        lines.extend(_format_doc(d) for d in ordered)

    if not vector_docs:
        lines.append("Faits disponibles :")
        lines.extend(_format_doc(d) for d in graph_docs[:8])
    elif graph_docs:
        lines.append("\nRelations dans le graphe :")
        lines.extend(f"  → {d['text']}" for d in graph_docs[:3])

    return "\n".join(lines)


async def run_graphrag_chain(
    question: str,
    entities: dict,
    intent: str,
    session: AsyncSession,
) -> tuple[str, list[str]]:
    from app.rag.retriever import retrieve_context
    docs = retrieve_context(question, entities)
    sources = list({d["metadata"].get("source", "inconnu") for d in docs if d["source"] == "vector"})
    answer = _build_answer(question, docs, intent)
    return answer, sources
