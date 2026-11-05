import datetime
from typing import List, Optional
import numpy as np
from ..models.simulation import (
    MonteCarloRequest,
    MonteCarloResponse,
    MonteCarloPercentiles,
    HistogramBin,
)

def run_monte_carlo_simulation(request: MonteCarloRequest) -> MonteCarloResponse:
    """
    Executes 10,000 stochastic Monte Carlo simulation trials to forecast project completion
    based on historical throughput and remaining backlog items.
    """
    history = np.array(request.throughput_history, dtype=float)
    # Filter out negative throughputs or zeros if history only contains zeros
    history = history[history >= 0]
    if len(history) == 0 or np.sum(history) == 0:
        raise ValueError("O histórico de throughput deve conter ao menos um valor positivo.")

    remaining = request.remaining_items
    n_sims = request.simulations_count
    unit = request.unit.lower()

    # Determine start date
    if request.start_date:
        try:
            start_dt = datetime.date.fromisoformat(request.start_date)
        except ValueError:
            start_dt = datetime.date.today()
    else:
        start_dt = datetime.date.today()

    # Vectorized / looped stochastic simulation
    # In each simulation, we repeatedly draw throughput until sum >= remaining
    simulated_durations = np.zeros(n_sims, dtype=int)

    # Max reasonable steps before cutoff to prevent infinite loops if throughput is tiny
    min_pos = np.min(history[history > 0])
    max_steps = int(np.ceil((remaining / min_pos) * 5)) + 20

    for i in range(n_sims):
        # Draw batch of random throughputs from historical distribution with replacement
        sample_draws = np.random.choice(history, size=max_steps, replace=True)
        cumulative = np.cumsum(sample_draws)
        # Find first index where cumulative >= remaining
        completion_indices = np.where(cumulative >= remaining)[0]
        if len(completion_indices) > 0:
            simulated_durations[i] = completion_indices[0] + 1
        else:
            # Fallback for extreme cases
            simulated_durations[i] = max_steps

    # Compute percentiles: 50%, 85%, 95%
    p50_duration = float(np.percentile(simulated_durations, 50))
    p85_duration = float(np.percentile(simulated_durations, 85))
    p95_duration = float(np.percentile(simulated_durations, 95))

    # Calculate target calendar dates
    multiplier = 7 if unit == "weeks" else 1
    p50_date = (start_dt + datetime.timedelta(days=int(np.ceil(p50_duration * multiplier)))).isoformat()
    p85_date = (start_dt + datetime.timedelta(days=int(np.ceil(p85_duration * multiplier)))).isoformat()
    p95_date = (start_dt + datetime.timedelta(days=int(np.ceil(p95_duration * multiplier)))).isoformat()

    # Build histogram bins
    min_dur = int(np.min(simulated_durations))
    max_dur = int(np.max(simulated_durations))
    
    num_bins = min(15, max(5, max_dur - min_dur + 1))
    counts, bin_edges = np.histogram(simulated_durations, bins=num_bins)

    histogram: List[HistogramBin] = []
    unit_label = "semanas" if unit == "weeks" else "dias"

    for idx, count in enumerate(counts):
        b_start = round(float(bin_edges[idx]), 1)
        b_end = round(float(bin_edges[idx + 1]), 1)
        prob_pct = round((float(count) / n_sims) * 100, 2)
        
        if b_start == b_end or (idx == len(counts) - 1 and int(b_start) == int(b_end)):
            label = f"{int(b_start)} {unit_label}"
        else:
            label = f"{b_start:.0f} - {b_end:.0f} {unit_label}"

        histogram.append(
            HistogramBin(
                range_label=label,
                min_val=b_start,
                max_val=b_end,
                frequency=int(count),
                probability_pct=prob_pct,
            )
        )

    avg_tp = round(float(np.mean(history)), 2)
    std_tp = round(float(np.std(history)), 2)

    summary_text = (
        f"Com 85% de nível de confiança, os {remaining} itens restantes serão entregues em até "
        f"{p85_duration:.0f} {unit_label} (previsão estimada: {p85_date}). "
        f"Cenário otimista (P50): {p50_duration:.0f} {unit_label} ({p50_date}). "
        f"Cenário conservador (P95): {p95_duration:.0f} {unit_label} ({p95_date})."
    )

    return MonteCarloResponse(
        simulations_count=n_sims,
        remaining_items=remaining,
        unit=unit,
        percentiles=MonteCarloPercentiles(
            p50_duration=p50_duration,
            p50_date=p50_date,
            p85_duration=p85_duration,
            p85_date=p85_date,
            p95_duration=p95_duration,
            p95_date=p95_date,
        ),
        histogram=histogram,
        historical_avg_throughput=avg_tp,
        historical_std_throughput=std_tp,
        summary_text=summary_text,
    )

