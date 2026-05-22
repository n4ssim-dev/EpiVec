"""Connecteur OMS/WHO — cas et décès COVID mondiaux."""

import csv
import io

import httpx

_URL = "https://covid19.who.int/WHO-COVID-19-global-data.csv"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()
        return _parse_csv(resp.text)


def _parse_csv(text: str) -> list[dict]:
    records = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        date = row.get("Date_reported", "").strip()
        country_code = row.get("Country_code", "").strip()
        if not date or not country_code:
            continue
        for metric, key in [("cases", "New_cases"), ("deaths", "New_deaths")]:
            raw = row.get(key, "").strip()
            if raw:
                try:
                    records.append({
                        "disease": "covid19",
                        "region_code": country_code,
                        "date": date,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
