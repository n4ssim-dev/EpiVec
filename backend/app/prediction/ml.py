"""Prédiction par régression sur features de graphe + séries temporelles."""

import numpy as np
from sklearn.linear_model import Ridge
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.features import get_propagation_features
from app.models.indicator import Indicator

_WINDOW = 7  # jours de lag comme features


async def run_ml_prediction(
    disease: str, region: str, days: int, session: AsyncSession
) -> list[dict]:
    result = await session.execute(
        select(Indicator)
        .where(
            Indicator.disease == disease,
            Indicator.region_code == region,
            Indicator.metric == "cases",
        )
        .order_by(Indicator.date.asc())
    )
    indicators = result.scalars().all()

    if len(indicators) < _WINDOW + 1:
        return []

    values = np.array([i.value for i in indicators])
    graph_feat = get_propagation_features(disease, region)
    pagerank = graph_feat.get("pagerank", 0.0)

    X, y = [], []
    for i in range(_WINDOW, len(values)):
        lag_features = list(values[i - _WINDOW : i]) + [pagerank]
        X.append(lag_features)
        y.append(values[i])

    model = Ridge(alpha=1.0)
    model.fit(X, y)

    last_window = list(values[-_WINDOW:])
    predictions = []
    for day in range(1, days + 1):
        features = last_window + [pagerank]
        pred = float(model.predict([features])[0])
        pred = max(0.0, pred)
        predictions.append({"day": day, "predicted_cases": round(pred, 2)})
        last_window = last_window[1:] + [pred]

    return predictions
