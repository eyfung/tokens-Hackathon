"""
Clarity — FastAPI server for the React frontend.
Wraps the simulation engine from src/simulation/engine.py.
"""

import sys
from pathlib import Path

# Ensure src/ is importable
REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
SRC = str(Path(REPO_ROOT, 'src'))
for p in [REPO_ROOT, SRC]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simulation.engine import TrialDesign, simulate_trial, find_minimum_sample_size

app = FastAPI(title="Clarity API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulateRequest(BaseModel):
    disease: str = "Hypertension"
    endpoint: str = "Systolic BP Reduction (mmHg)"
    effect: float = 10.0
    variability: float = 15.0
    n: int = 100


class SimulateResponse(BaseModel):
    power: float
    advice: str
    sample_size: int
    ci_lower: float
    ci_upper: float


@app.post("/api/simulate")
async def simulate(req: SimulateRequest) -> SimulateResponse:
    """Run a trial simulation and return results."""
    try:
        design = TrialDesign(
            n_control=req.n,
            n_treatment=req.n,
            treatment_effect=req.effect,
            control_std=req.variability,
            treatment_std=req.variability,
            n_simulations=10_000,
        )
        result = simulate_trial(design)
        power = result.power

        # Find optimal sample size if power < 0.80, else use current N
        if power < 0.80:
            optimal_n, _ = find_minimum_sample_size(
                target_power=0.80,
                effect=req.effect,
                std=req.variability,
                n_simulations=5_000,
                max_n=min(req.n * 4, 1000),
            )
            rec_n = optimal_n
        else:
            rec_n = req.n

        # Advice
        if power >= 0.80:
            advice = "Trial design meets the target power threshold. Consider refining secondary endpoints."
        elif power >= 0.60:
            advice = (
                f"Design is moderately powered ({power:.0%}). "
                f"Increasing sample size to {rec_n} per arm would reach 80% power."
            )
        else:
            advice = (
                f"Design is underpowered ({power:.0%}). "
                f"Increasing sample size to {rec_n} per arm is recommended."
            )

        return SimulateResponse(
            power=round(power, 4),
            advice=advice,
            sample_size=rec_n,
            ci_lower=round(result.ci_lower, 2),
            ci_upper=round(result.ci_upper, 2),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
