"""Connecteur Santé Publique France — données COVID/grippe via data.gouv.fr."""

import httpx

# Données quotidiennes hospitalisations COVID par département
_URL = "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b26-b9d8-175c9b5fe5d4"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()
        return _parse(resp.json())


def _parse(raw: list[dict]) -> list[dict]:
    records = []
    for row in raw:
        dep = row.get("dep", "FR")
        date = row.get("jour")
        if not date:
            continue
        for metric, key in [
            ("hospitalizations", "hosp"),
            ("critical_care", "rea"),
            ("deaths", "dc"),
        ]:
            value = row.get(key)
            if value is not None:
                records.append(
                    {
                        "disease": "covid19",
                        "region_code": dep,
                        "date": date,
                        "metric": metric,
                        "value": float(value),
                    }
                )
    return records
