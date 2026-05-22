"""Découpage des records épidémiologiques en chunks textuels indexables."""

from collections import defaultdict


_METRIC_LABELS = {
    "cases": "cas confirmés",
    "deaths": "décès",
    "hospitalizations": "hospitalisations",
    "critical_care": "cas en réanimation",
    "dataset_updated": "dataset mis à jour",
}


def build_chunks(records: list[dict]) -> list[dict]:
    """
    Regroupe les records par (disease, region_code, date) et produit un chunk
    textuel par groupe avec ses métadonnées.

    Chaque chunk fait ~50-200 tokens selon le nombre de métriques disponibles.
    """
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for rec in records:
        key = (rec["disease"], rec["region_code"], rec["date"])
        groups[key].append(rec)

    chunks = []
    for (disease, region, date), group in groups.items():
        metrics_parts = []
        for rec in group:
            label = _METRIC_LABELS.get(rec["metric"], rec["metric"])
            value = int(rec["value"]) if rec["value"] == int(rec["value"]) else rec["value"]
            metrics_parts.append(f"{value} {label}")

        metrics_str = ", ".join(metrics_parts)
        text = f"{disease.upper()} — {region} — {date} : {metrics_str}."

        chunks.append({
            "text": text,
            "metadata": {
                "disease": disease,
                "region": region,
                "date": date,
                "source": group[0].get("source", "unknown"),
            },
        })

    return chunks
