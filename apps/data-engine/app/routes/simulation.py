from fastapi import APIRouter, HTTPException
from ..models.simulation import MonteCarloRequest, MonteCarloResponse
from ..services.monte_carlo import run_monte_carlo_simulation

router = APIRouter(prefix="/simulate", tags=["Monte Carlo Simulation"])

@router.post("/monte-carlo", response_model=MonteCarloResponse)
async def simulate_monte_carlo(request: MonteCarloRequest):
    """
    Executes 10,000 stochastic Monte Carlo simulation trials using NumPy.
    Returns percentile confidence levels (50%, 85%, 95%) and histogram probability distribution.
    """
    try:
        return run_monte_carlo_simulation(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na simulação de Monte Carlo: {str(e)}")

