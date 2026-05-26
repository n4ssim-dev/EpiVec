from datetime import date

from sqlalchemy import insert as sa_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.region import Region
from app.models.triple import Triple


async def normalize_to_triples(
    records: list[dict], source: str, session: AsyncSession
) -> tuple[list, list]:
    """Convertit les enregistrements bruts en triples de connaissance et en indicateurs.

    Utilise un bulk insert (2 requêtes) au lieu d'un INSERT par ligne.
    Les régions inconnues sont créées en une passe dédiée avant les inserts.
    """
    triple_rows: list[dict] = []
    indicator_rows: list[dict] = []
    seen_regions: set[str] = set()

    # Passe 1 : créer toutes les régions inconnues (une SELECT par code unique)
    for rec in records:
        code = rec.get("region_code", "UNKNOWN")
        if code not in seen_regions:
            await _ensure_region(code, session)
            seen_regions.add(code)
    await session.flush()

    # Passe 2 : construire les listes de valeurs à insérer
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

        triple_rows.append({
            "subject": f"disease:{disease}",
            "predicate": f"has_{metric}_in",
            "object": f"region:{region_code}@{parsed_date}",
            "source": source,
            "confidence": 1.0,
        })
        indicator_rows.append({
            "disease": disease,
            "region_code": region_code,
            "date": parsed_date,
            "metric": metric,
            "value": float(value),
            "source": source,
        })

    # Passe 3 : bulk insert en 2 requêtes
    if triple_rows:
        await session.execute(sa_insert(Triple), triple_rows)
    if indicator_rows:
        await session.execute(sa_insert(Indicator), indicator_rows)

    await session.commit()
    return triple_rows, indicator_rows


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
