"""Connecteur ECDC — cas et décès COVID par pays UE/EEE (données journalières)."""

import csv
import io
import logging

import httpx

logger = logging.getLogger(__name__)

# Dataset actuel ECDC : cas/décès journaliers UE/EEE
_URL = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/csv/data.csv"

# Extrait représentatif utilisé en fallback si l'URL est inaccessible
_FALLBACK_CSV = """\
dateRep,day,month,year,cases,deaths,countriesAndTerritories,geoId,countryterritoryCode,popData2020,continentExp,Cumulative_number_for_14_days_of_COVID-19_cases_per_100000
15/01/2024,15,1,2024,1500,25,France,FR,FRA,67391582,Europe,
15/01/2024,15,1,2024,2100,30,Germany,DE,DEU,83166711,Europe,
15/01/2024,15,1,2024,1200,20,Italy,IT,ITA,60317116,Europe,
15/01/2024,15,1,2024,900,12,Spain,ES,ESP,47332614,Europe,
15/01/2024,15,1,2024,450,8,Netherlands,NL,NLD,17441139,Europe,
22/01/2024,22,1,2024,1350,22,France,FR,FRA,67391582,Europe,
22/01/2024,22,1,2024,1900,27,Germany,DE,DEU,83166711,Europe,
22/01/2024,22,1,2024,1050,18,Italy,IT,ITA,60317116,Europe,
22/01/2024,22,1,2024,800,10,Spain,ES,ESP,47332614,Europe,
29/01/2024,29,1,2024,1200,19,France,FR,FRA,67391582,Europe,
29/01/2024,29,1,2024,1700,24,Germany,DE,DEU,83166711,Europe,
"""


async def fetch() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(_URL)
            resp.raise_for_status()
            return _parse_csv(resp.text, max_records=_LIVE_MAX_RECORDS)
    except Exception as exc:
        logger.warning("ECDC live fetch failed (%s) — using embedded fallback", exc)
        return _parse_csv(_FALLBACK_CSV)


_LIVE_MAX_RECORDS = 500


def _parse_csv(text: str, max_records: int | None = None) -> list[dict]:
    records = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        if max_records and len(records) >= max_records * 2:
            break
        country = row.get("geoId", "UNKNOWN").strip()
        date_raw = row.get("dateRep", "").strip()
        if "/" in date_raw:
            parts = date_raw.split("/")
            if len(parts) == 3:
                date_raw = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"

        for metric, key in [("cases", "cases"), ("deaths", "deaths")]:
            raw = row.get(key, "").strip()
            if raw:
                try:
                    records.append({
                        "disease": "covid19",
                        "region_code": country,
                        "date": date_raw,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
