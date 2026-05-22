from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.region import Region
from app.models.triple import Triple


async def normalize_to_triples(
    records: list[dict], source: str, session: AsyncSession
) -> tuple[list[Triple], list[Indicator]]:
    """Convertit les enregistrements bruts en triples de connaissance et en indicateurs."""
    triples: list[Triple] = []
    indicators: list[Indicator] = []

    for rec in records:
        disease = rec.get("disease", "unknown")
        region_code = rec.get("region_code", "UNKNOWN")
        raw_date = rec.get("date")
        metric = rec.get("metric", "unknown")
        value = rec.get("value")

        if not raw_date or value is None:
            continue

        parsed_date = _parse_date(raw_date)
        if parsed_date is None:
            continue

        await _ensure_region(region_code, session)

        triple = Triple(
            subject=f"disease:{disease}",
            predicate=f"has_{metric}_in",
            object=f"region:{region_code}@{parsed_date}",
            source=source,
            confidence=1.0,
        )
        session.add(triple)
        triples.append(triple)

        indicator = Indicator(
            disease=disease,
            region_code=region_code,
            date=parsed_date,
            metric=metric,
            value=float(value),
            source=source,
        )
        session.add(indicator)
        indicators.append(indicator)

    await session.commit()
    return triples, indicators


def _parse_date(raw: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            from datetime import datetime
            return datetime.strptime(raw[:10], fmt).date()
        except ValueError:
            continue
    return None


async def _ensure_region(code: str, session: AsyncSession) -> None:
    from sqlalchemy import select
    exists = await session.execute(select(Region).where(Region.code == code))
    if not exists.scalar_one_or_none():
        session.add(Region(name=code, code=code, level="unknown"))
        await session.flush()
