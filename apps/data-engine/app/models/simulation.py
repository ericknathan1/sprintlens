from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class MonteCarloRequest(BaseModel):
    throughput_history: List[float] = Field(
        ...,
        description="Histórico de Throughput (ex: itens entregues por dia ou semana)",
        min_length=3
    )
    remaining_items: int = Field(
        ...,
        description="Quantidade de itens pendentes no backlog para simular a entrega",
        gt=0
    )
    simulations_count: int = Field(
        10000,
        description="Número de iterações da simulação estocástica (padrão: 10.000)",
        ge=1000,
        le=50000
    )
    unit: str = Field(
        "weeks",
        description="Unidade do throughput fornecido: 'days' ou 'weeks'"
    )
    start_date: Optional[str] = Field(
        None,
        description="Data de início da previsão (ISO string YYYY-MM-DD). Padrão: hoje."
    )

class HistogramBin(BaseModel):
    range_label: str
    min_val: float
    max_val: float
    frequency: int
    probability_pct: float

class MonteCarloPercentiles(BaseModel):
    p50_duration: float
    p50_date: str
    p85_duration: float
    p85_date: str
    p95_duration: float
    p95_date: str

class MonteCarloResponse(BaseModel):
    simulations_count: int
    remaining_items: int
    unit: str
    percentiles: MonteCarloPercentiles
    histogram: List[HistogramBin]
    historical_avg_throughput: float
    historical_std_throughput: float
    summary_text: str

