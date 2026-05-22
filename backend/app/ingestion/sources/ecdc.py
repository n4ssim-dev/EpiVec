"""Connecteur ECDC (European Centre for Disease Prevention and Control)."""

import httpx

_URL = "https://opendata.ecdc.europa.eu/covid19/casedistribution/json/"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()
        return _parse(resp.json())


def _parse(raw: dict) -> list[dict]:
    records = []
    for row in raw.get("records", []):
        country = row.get("geoId", "UNKNOWN")
        date_str = f"{row.get('year', '')}-{str(row.get('month', '')).zfill(2)}-{str(row.get('day', '')).zfill(2)}"
        cases = row.get("cases")
        deaths = row.get("deaths")

        for metric, value in [("cases", cases), ("deaths", deaths)]:
            if value is not None:
                records.append(
                    {
                        "disease": "covid19",
                        "region_code": country,
                        "date": date_str,
                        "metric": metric,
                        "value": float(value),
                    }
                )
    return records
