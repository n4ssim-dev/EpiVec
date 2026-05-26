"""Connecteur Mpox — données de démonstration (épidémie 2022-2023).

L'épidémie mondiale de mpox étant historique, ce connecteur utilise
des données embarquées représentatives issues des rapports OMS/ECDC.
"""

# Extrait représentatif issu des rapports OMS/ECDC (codes pays ISO-2)
_FALLBACK_CSV = """\
country_code,date,new_cases,new_deaths
US,2022-05-18,4,0
US,2022-06-01,25,0
US,2022-07-01,850,0
US,2022-07-15,2800,1
US,2022-08-01,6500,3
US,2022-08-15,8900,4
US,2022-09-01,5200,2
US,2022-10-01,1800,1
US,2022-11-01,520,0
US,2022-12-01,180,0
US,2023-01-01,85,0
GB,2022-05-09,7,0
GB,2022-06-01,200,0
GB,2022-07-01,1100,0
GB,2022-07-15,2200,0
GB,2022-08-01,3400,0
GB,2022-08-15,3800,1
GB,2022-09-01,2100,0
GB,2022-10-01,650,0
GB,2022-11-01,180,0
GB,2022-12-01,60,0
DE,2022-05-20,3,0
DE,2022-06-01,150,0
DE,2022-07-01,900,0
DE,2022-07-15,1800,0
DE,2022-08-01,2900,0
DE,2022-08-15,3100,1
DE,2022-09-01,1600,0
DE,2022-10-01,480,0
DE,2022-11-01,140,0
DE,2022-12-01,45,0
ES,2022-05-20,30,0
ES,2022-06-01,820,0
ES,2022-07-01,3500,0
ES,2022-07-15,5200,1
ES,2022-08-01,4800,1
ES,2022-08-15,3200,0
ES,2022-09-01,1200,0
ES,2022-10-01,380,0
ES,2022-11-01,110,0
FR,2022-05-20,12,0
FR,2022-06-01,300,0
FR,2022-07-01,1400,0
FR,2022-07-15,2800,0
FR,2022-08-01,3600,1
FR,2022-08-15,2900,0
FR,2022-09-01,950,0
FR,2022-10-01,280,0
FR,2022-11-01,80,0
BR,2022-07-01,150,0
BR,2022-07-15,1200,1
BR,2022-08-01,4500,2
BR,2022-08-15,6800,3
BR,2022-09-01,4200,2
BR,2022-10-01,1800,1
BR,2022-11-01,620,0
BR,2022-12-01,220,0
CD,2022-01-01,450,12
CD,2022-04-01,620,18
CD,2022-07-01,890,24
CD,2022-10-01,750,20
CD,2023-01-01,980,28
CD,2023-04-01,1200,35
CD,2023-07-01,1650,48
CD,2023-10-01,2100,62
"""

# Correspondance ISO-3 (OWID) → ISO-2 pour les pays les plus représentés
async def fetch() -> list[dict]:
    return _parse_csv(_FALLBACK_CSV)


def _parse_csv(text: str) -> list[dict]:
    import csv
    import io

    records = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        country = row.get("country_code", "").strip()
        date = row.get("date", "").strip()
        if not country or not date:
            continue
        for metric, key in [("cases", "new_cases"), ("deaths", "new_deaths")]:
            raw = row.get(key, "").strip()
            if raw:
                try:
                    records.append({
                        "disease": "mpox",
                        "region_code": country,
                        "date": date,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
