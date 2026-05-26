"""Pipeline GraphRAG : retrieval hybride → synthèse LLM."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.rag.retriever import retrieve_context

_SYSTEM_PROMPT = (
    "Tu es un expert en épidémiologie. Réponds toujours en français, "
    "de manière précise et sourcée. Si le contexte ne permet pas de répondre, "
    "dis-le clairement plutôt que d'inventer."
)


async def run_graphrag_chain(
    question: str,
    entities: dict,
    intent: str,
    session: AsyncSession,
) -> tuple[str, list[str]]:
    import asyncio
    loop = asyncio.get_running_loop()
    context_docs = await loop.run_in_executor(None, lambda: retrieve_context(question, entities))
    context_text = "\n".join(d["text"] for d in context_docs[:10])
    sources = list({d["metadata"].get("source", "unknown") for d in context_docs})

    prompt = f"""Contexte issu du graphe de connaissances épidémiologiques :
{context_text}

Question : {question}

Réponds de manière concise en t'appuyant sur le contexte fourni."""

    if settings.llm_provider == "claude":
        from app.llm.claude import generate
    else:
        from app.llm.ollama import generate  # type: ignore[assignment]

    answer = await generate(prompt)
    return answer, sources
