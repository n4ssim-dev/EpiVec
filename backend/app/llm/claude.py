import anthropic

from app.core.config import settings

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def generate(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    client = _get_client()
    message = await client.messages.create(
        model=model,
        max_tokens=1024,
        system=(
            "Tu es un assistant spécialisé en analyse épidémiologique. "
            "Réponds toujours en français, de manière factuelle et sourcée."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
