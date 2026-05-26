"""Connecteur Santé Publique France — données de démonstration.

Le dataset hospitalisations COVID (donnees-hospitalieres-covid19) a été retiré
de data.gouv.fr fin 2024. Ce connecteur embarque un extrait représentatif pour
permettre de tester la pipeline sans dépendance externe.
"""

_SAMPLE_CSV = """\
dep;sexe;jour;hosp;rea;rad;dc
75;0;2021-01-04;4200;680;2100;85
75;0;2021-01-11;4050;650;2250;78
75;0;2021-02-01;3800;590;2400;62
75;0;2021-04-05;5100;820;3100;95
75;0;2021-04-19;4900;780;3300;88
75;0;2021-07-26;1200;180;900;18
75;0;2021-10-04;1800;260;1100;24
75;0;2021-11-15;2600;380;1400;35
75;0;2021-12-13;3900;560;2000;52
69;0;2021-01-04;1450;230;720;28
69;0;2021-04-05;1820;290;1050;34
69;0;2021-07-26;420;62;310;6
69;0;2021-12-13;1350;195;780;19
13;0;2021-01-04;1280;205;640;24
13;0;2021-04-05;1600;255;920;30
13;0;2021-12-13;1180;172;680;17
59;0;2021-01-04;1750;280;870;32
59;0;2021-04-05;2100;335;1200;40
59;0;2021-12-13;1620;235;920;23
33;0;2021-01-04;980;158;490;18
33;0;2021-04-05;1150;184;660;22
06;0;2021-01-04;720;116;360;13
06;0;2021-04-05;850;136;490;16
75;0;2022-01-10;6800;850;4100;110
75;0;2022-02-07;5200;640;3800;88
75;0;2022-07-11;2100;210;1500;22
59;0;2022-01-10;2800;350;1600;42
13;0;2022-01-10;2200;275;1250;33
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
