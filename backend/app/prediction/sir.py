"""Modèle SIR/SEIR pour la projection épidémiologique."""

import numpy as np
from scipy.integrate import odeint
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator


def _sir_ode(y: list, t: np.ndarray, beta: float, gamma: float) -> list:
    S, I, R = y
    N = S + I + R
    dS = -beta * S * I / N
    dI = beta * S * I / N - gamma * I
    dR = gamma * I
    return [dS, dI, dR]


async def run_sir(
    disease: str, region: str, days: int, session: AsyncSession
) -> list[dict]:
    result = await session.execute(
        select(Indicator)
        .where(Indicator.disease == disease, Indicator.region_code == region)
        .order_by(Indicator.date.desc())
        .limit(30)
    )
    recent = result.scalars().all()

    N = 1_000_000
    I0 = float(recent[0].value) if recent else 1_000.0
    R0_pop = sum(i.value for i in recent if i.metric == "deaths")
    S0 = max(0.0, N - I0 - R0_pop)

    # Paramètres épidémiologiques par défaut — à calibrer par maladie
    beta = 0.3
    gamma = 0.05

    t = np.linspace(0, days, days)
    sol = odeint(_sir_ode, [S0, I0, R0_pop], t, args=(beta, gamma))

    return [
        {
            "day": int(d),
            "susceptible": round(float(s), 2),
            "infected": round(float(i), 2),
            "recovered": round(float(r), 2),
        }
        for d, (s, i, r) in zip(t, sol)
    ]
