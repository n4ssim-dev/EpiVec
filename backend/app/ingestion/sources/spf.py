"""Connecteur Santé Publique France — hospitalisations COVID par département."""

import csv
import io

import httpx

# CSV séparé par ";" : dep;sexe;jour;hosp;rea;rad;dc
_URL = "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b26-b9d8-175c9b5fe5d4"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()
        return _parse_csv(resp.text)


def _parse_csv(text: str) -> list[dict]:
    records = []
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    for row in reader:
        # sexe=0 = tous sexes confondus
        if row.get("sexe", "") != "0":
            continue
        dep = row.get("dep", "FR").strip()
        date = row.get("jour", "").strip()
        if not date:
            continue
        for metric, key in [
            ("hospitalizations", "hosp"),
            ("critical_care", "rea"),
            ("deaths", "dc"),
        ]:
            raw = row.get(key, "").strip()
            if raw:
                try:
                    records.append({
                        "disease": "covid19",
                        "region_code": dep,
                        "date": date,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
