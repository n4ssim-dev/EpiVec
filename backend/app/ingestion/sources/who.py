"""Connecteur OMS/WHO — données épidémiologiques mondiales."""

import httpx

_URL = "https://covid19.who.int/WHO-COVID-19-global-data.csv"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()
        return _parse_csv(resp.text)


def _parse_csv(text: str) -> list[dict]:
    records = []
    lines = text.strip().splitlines()
    if not lines:
        return records

    headers = [h.strip() for h in lines[0].split(",")]
    for line in lines[1:]:
        row = dict(zip(headers, line.split(",")))
        date = row.get("Date_reported", "").strip()
        country_code = row.get("Country_code", "").strip()
        new_cases = row.get("New_cases", "0").strip()
        new_deaths = row.get("New_deaths", "0").strip()

        if not date or not country_code:
            continue

        for metric, value in [("cases", new_cases), ("deaths", new_deaths)]:
            try:
                records.append(
                    {
                        "disease": "covid19",
                        "region_code": country_code,
                        "date": date,
                        "metric": metric,
                        "value": float(value),
                    }
                )
            except ValueError:
                continue

    return records
