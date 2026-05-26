"""Connecteur OMS/WHO — données de démonstration.

L'URL CSV de l'OMS (covid19.who.int) redirige désormais vers un dashboard web.
Ce connecteur embarque un extrait représentatif des données mondiales COVID.
"""

_SAMPLE_CSV = """\
Date_reported,Country_code,Country,WHO_region,New_cases,Cumulative_cases,New_deaths,Cumulative_deaths
2024-01-15,FR,France,EURO,1500,38000000,25,165000
2024-01-15,DE,Germany,EURO,2100,38500000,30,174000
2024-01-15,IT,Italy,EURO,1200,26000000,20,195000
2024-01-15,ES,Spain,EURO,900,13500000,12,121000
2024-01-15,US,United States of America,AMRO,15000,103000000,200,1180000
2024-01-15,BR,Brazil,AMRO,3000,37500000,50,702000
2024-01-15,IN,India,SEARO,5000,44800000,30,531000
2024-01-22,FR,France,EURO,1350,38010000,22,165022
2024-01-22,DE,Germany,EURO,1900,38520000,27,174027
2024-01-22,US,United States of America,AMRO,13000,103050000,180,1180180
"""


async def fetch() -> list[dict]:
    return _parse_csv(_SAMPLE_CSV)


def _parse_csv(text: str) -> list[dict]:
    import csv
    import io

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
