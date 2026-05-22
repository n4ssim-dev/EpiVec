"""Connecteur ECDC — cas et décès COVID par pays UE/EEE (données journalières)."""

import csv
import io

import httpx

# Dataset actuel ECDC : cas/décès journaliers UE/EEE
_URL = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/csv/data.csv"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()
        return _parse_csv(resp.text)


def _parse_csv(text: str) -> list[dict]:
    records = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        country = row.get("geoId", "UNKNOWN").strip()
        date = row.get("dateRep", "").strip()
        # dateRep au format DD/MM/YYYY → normaliser
        if "/" in date:
            parts = date.split("/")
            if len(parts) == 3:
                date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"

        for metric, key in [("cases", "cases"), ("deaths", "deaths")]:
            raw = row.get(key, "").strip()
            if raw:
                try:
                    records.append({
                        "disease": "covid19",
                        "region_code": country,
                        "date": date,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
