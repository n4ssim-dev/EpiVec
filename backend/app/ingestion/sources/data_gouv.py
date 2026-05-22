"""Connecteur data.gouv.fr — datasets épidémiologiques génériques."""

import httpx

# Catalogue des datasets utilisés (dataset_id → description)
_DATASETS = {
    "maladies-a-declaration-obligatoire": "https://www.data.gouv.fr/api/1/datasets/maladies-a-declaration-obligatoire/",
}

_SEARCH_URL = "https://www.data.gouv.fr/api/1/datasets/?tag=epidemiologie&page_size=20"


async def fetch() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(_SEARCH_URL)
        resp.raise_for_status()
        return _parse(resp.json())


def _parse(raw: dict) -> list[dict]:
    # Retourne les métadonnées des datasets disponibles comme des triples de connaissance
    records = []
    for dataset in raw.get("data", []):
        title = dataset.get("title", "")
        slug = dataset.get("slug", "")
        records.append(
            {
                "disease": slug,
                "region_code": "FR",
                "date": dataset.get("last_modified", "")[:10],
                "metric": "dataset_updated",
                "value": 1.0,
            }
        )
    return records
