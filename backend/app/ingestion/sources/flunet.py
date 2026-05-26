"""Connecteur OMS FluNet — surveillance de la grippe saisonnière (données de démonstration).

Représente des données typiques issues du réseau mondial FluNet de l'OMS.
Les valeurs correspondent à des cas confirmés en laboratoire lors de la
saison grippale 2023-2024 (pic boréal : jan-fév 2024 ; pic austral : juil 2023).
"""

_SAMPLE_CSV = """\
country_code,date,new_cases,new_deaths
FR,2023-11-06,820,45
FR,2023-11-20,1320,72
FR,2023-12-04,2100,115
FR,2023-12-18,3800,208
FR,2024-01-08,6200,340
FR,2024-01-15,8100,445
FR,2024-01-29,7200,395
FR,2024-02-12,4200,231
FR,2024-02-26,2100,115
DE,2023-11-06,1100,60
DE,2023-11-20,1900,104
DE,2023-12-04,3200,175
DE,2023-12-18,5600,308
DE,2024-01-08,9800,538
DE,2024-01-15,12400,682
DE,2024-01-29,10800,594
DE,2024-02-12,5600,308
DE,2024-02-26,2800,154
IT,2023-11-06,750,41
IT,2023-12-04,2600,143
IT,2023-12-18,4800,264
IT,2024-01-08,7600,418
IT,2024-01-15,9200,506
IT,2024-01-29,8100,445
IT,2024-02-12,4100,225
ES,2023-12-04,2000,110
ES,2023-12-18,3900,214
ES,2024-01-08,6400,352
ES,2024-01-15,7800,429
ES,2024-01-29,6900,379
ES,2024-02-12,3500,192
GB,2023-11-06,1200,66
GB,2023-12-04,3500,192
GB,2023-12-18,6200,341
GB,2024-01-08,10500,578
GB,2024-01-15,12600,693
GB,2024-01-29,11200,616
GB,2024-02-12,5900,324
US,2023-11-06,8500,468
US,2023-12-04,23000,1265
US,2023-12-18,42000,2310
US,2024-01-08,68000,3740
US,2024-01-15,82000,4510
US,2024-01-29,72000,3960
US,2024-02-12,38000,2090
US,2024-02-26,18000,990
BR,2023-11-06,2100,115
BR,2023-12-04,5200,286
BR,2023-12-18,8400,462
BR,2024-01-08,12500,688
BR,2024-01-15,15600,858
BR,2024-01-29,13800,759
BR,2024-02-12,7100,390
IN,2023-12-04,9200,506
IN,2023-12-18,16000,880
IN,2024-01-08,24000,1320
IN,2024-01-15,31000,1705
IN,2024-01-29,27000,1485
IN,2024-02-12,13000,715
AU,2023-05-15,5800,319
AU,2023-06-05,12000,660
AU,2023-06-19,18000,990
AU,2023-07-03,24000,1320
AU,2023-07-17,26000,1430
AU,2023-07-31,22000,1210
AU,2023-08-14,16000,880
AU,2023-09-11,6400,352
"""


async def fetch() -> list[dict]:
    return _parse_csv(_SAMPLE_CSV)


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
                        "disease": "influenza",
                        "region_code": country,
                        "date": date,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
