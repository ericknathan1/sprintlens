import pytest
from app.models.simulation import MonteCarloRequest
from app.services.monte_carlo import run_monte_carlo_simulation

def test_monte_carlo_simulation():
    req = MonteCarloRequest(
        throughput_history=[5.0, 8.0, 4.0, 6.0, 7.0, 5.0],
        remaining_items=30,
        simulations_count=10000,
        unit="weeks",
        start_date="2026-11-01",
    )

    res = run_monte_carlo_simulation(req)

    assert res.simulations_count == 10000
    assert res.remaining_items == 30
    assert res.unit == "weeks"

    p50 = res.percentiles.p50_duration
    p85 = res.percentiles.p85_duration
    p95 = res.percentiles.p95_duration

    # Percentiles must strictly satisfy: P50 <= P85 <= P95
    assert p50 <= p85 <= p95

    # Check dates are present and ordered
    assert res.percentiles.p50_date <= res.percentiles.p85_date <= res.percentiles.p95_date

    # Check histogram
    assert len(res.histogram) >= 5
    total_prob = sum(b.probability_pct for b in res.histogram)
    assert 99.0 <= total_prob <= 101.0  # approximate 100% due to rounding

def test_monte_carlo_zero_throughput_raises():
    req = MonteCarloRequest(
        throughput_history=[0.0, 0.0, 0.0],
        remaining_items=10,
        simulations_count=1000,
    )
    with pytest.raises(ValueError):
        run_monte_carlo_simulation(req)

