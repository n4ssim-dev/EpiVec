"""Connecteur Santé Publique France — données de démonstration.

Le dataset hospitalisations COVID (donnees-hospitalieres-covid19) a été retiré
de data.gouv.fr fin 2024. Ce connecteur embarque un extrait représentatif pour
permettre de tester la pipeline sans dépendance externe.
"""

_SAMPLE_CSV = """\
dep;sexe;jour;hosp;rea;rad;dc
75;0;2024-01-15;1234;56;890;12
75;0;2024-01-22;1180;51;920;10
75;0;2024-01-29;1050;44;960;8
69;0;2024-01-15;450;20;300;8
69;0;2024-01-22;420;18;315;7
13;0;2024-01-15;380;17;260;5
13;0;2024-01-22;355;15;275;4
59;0;2024-01-15;520;24;340;9
33;0;2024-01-15;290;13;195;4
06;0;2024-01-15;210;9;145;3
"""


async def fetch() -> list[dict]:
    return _parse_csv(_SAMPLE_CSV)


def _parse_csv(text: str) -> list[dict]:
    import csv
    import io

    records = []
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    for row in reader:
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
