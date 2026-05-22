from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.prediction.ml import run_ml_prediction
from app.prediction.sir import run_sir

router = APIRouter()


@router.get("/{disease}")
async def predict(
    disease: str,
    region: str = Query(..., description="Code région (ex: FR, 75)"),
    days: int = Query(30, ge=7, le=365, description="Horizon de prédiction en jours"),
    model: str = Query("sir", pattern="^(sir|ml)$", description="Modèle : sir ou ml"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if model == "sir":
        predictions = await run_sir(disease, region, days, session)
    else:
        predictions = await run_ml_prediction(disease, region, days, session)

    return {
        "disease": disease,
        "region": region,
        "model": model,
        "horizon_days": days,
        "predictions": predictions,
    }
