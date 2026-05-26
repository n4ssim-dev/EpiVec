"""Connecteur Dengue — données de démonstration PAHO/OMS.

Données représentatives des épidémies de dengue en Amérique latine et en Asie
du Sud-Est, principales zones endémiques mondiales. Les chiffres sont basés
sur les rapports épidémiologiques hebdomadaires de l'OPS/PAHO et de l'OMS
pour les saisons 2023 et 2024 (année record pour le Brésil).
"""

_SAMPLE_CSV = """\
country_code,date,new_cases,new_deaths
BR,2023-01-09,28000,15
BR,2023-01-23,42000,22
BR,2023-02-06,68000,35
BR,2023-02-20,95000,48
BR,2023-03-06,145000,72
BR,2023-03-20,198000,98
BR,2023-04-03,215000,108
BR,2023-04-17,189000,94
BR,2023-05-01,142000,70
BR,2023-05-15,98000,48
BR,2024-01-15,52000,26
BR,2024-02-05,138000,68
BR,2024-02-26,245000,122
BR,2024-03-11,380000,190
BR,2024-03-25,420000,210
BR,2024-04-08,356000,178
CO,2023-01-09,4200,8
CO,2023-01-23,6800,13
CO,2023-02-06,9500,18
CO,2023-02-20,12000,23
CO,2023-03-06,14500,28
CO,2023-03-20,11200,21
CO,2023-04-03,8600,16
CO,2023-04-17,6200,12
CO,2024-01-15,3800,7
CO,2024-02-05,8900,17
CO,2024-02-26,15600,30
CO,2024-03-11,21000,40
MX,2023-06-05,1800,4
MX,2023-07-03,4500,9
MX,2023-08-07,8900,18
MX,2023-08-21,12500,25
MX,2023-09-04,15800,32
MX,2023-09-18,14200,28
MX,2023-10-02,10500,21
MX,2023-10-16,7200,14
MX,2024-08-05,6800,14
MX,2024-09-02,11200,22
PH,2023-01-09,2800,12
PH,2023-02-06,4500,19
PH,2023-03-06,6800,29
PH,2023-07-03,12500,53
PH,2023-08-07,18900,80
PH,2023-09-04,21500,91
PH,2023-10-02,16800,71
PH,2023-11-06,9200,39
PH,2024-01-08,3600,15
TH,2023-04-03,3200,8
TH,2023-05-08,5800,14
TH,2023-06-05,9200,23
TH,2023-07-03,14800,37
TH,2023-08-07,18200,46
TH,2023-09-04,15600,39
TH,2023-10-02,10400,26
TH,2023-11-06,5800,14
IN,2023-06-05,8500,28
IN,2023-07-03,18000,59
IN,2023-08-07,28500,94
IN,2023-09-04,42000,138
IN,2023-10-02,38500,126
IN,2023-10-30,24000,79
IN,2023-11-27,12000,39
AR,2023-02-06,12000,14
AR,2023-02-20,28000,32
AR,2023-03-06,52000,60
AR,2023-03-20,68000,78
AR,2023-04-03,58000,67
AR,2023-04-17,38000,44
AR,2024-02-05,18000,21
AR,2024-03-11,95000,109
AR,2024-04-08,120000,138
PE,2023-01-23,8500,18
PE,2023-02-20,15800,33
PE,2023-03-20,24500,51
PE,2023-04-17,31200,65
PE,2023-05-15,22800,48
PE,2023-06-12,14500,30
VN,2023-06-05,5200,14
VN,2023-07-03,9800,26
VN,2023-08-07,15600,42
VN,2023-09-04,18900,51
VN,2023-10-02,13400,36
VN,2023-11-06,7200,19
BD,2023-07-03,4800,38
BD,2023-08-07,9200,73
BD,2023-09-04,18500,147
BD,2023-10-02,14200,113
BD,2023-11-06,6800,54
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
                        "disease": "dengue",
                        "region_code": country,
                        "date": date,
                        "metric": metric,
                        "value": float(raw),
                    })
                except ValueError:
                    continue
    return records
