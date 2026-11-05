import pytest
import asyncio
from main import health_check
from app.routes.mapping import detect_columns_from_headers
from app.routes.simulation import simulate_monte_carlo
from app.routes.demo import get_demo_csv_file, get_processed_demo_data
from app.models.mapping import DetectColumnsRequest
from app.models.simulation import MonteCarloRequest

def test_health_endpoint():
    res = asyncio.run(health_check())
    assert res["status"] == "healthy"
    assert "SprintLens Data Engine" in res["service"]

def test_mapping_detect_columns_endpoint():
    req = DetectColumnsRequest(
        headers=["Key", "Issue Type", "Status", "Assignee", "Created", "Story Points"]
    )
    res = asyncio.run(detect_columns_from_headers(req))
    assert res.matches["issue_key"].is_matched is True
    assert res.matches["issue_key"].matched_csv_header == "Key"
    assert res.matches["story_points"].is_matched is True

def test_monte_carlo_endpoint():
    req = MonteCarloRequest(
        throughput_history=[6.0, 7.0, 5.0, 8.0],
        remaining_items=20,
        simulations_count=5000,
        unit="weeks",
    )
    res = asyncio.run(simulate_monte_carlo(req))
    assert res.simulations_count == 5000
    assert res.percentiles.p50_duration <= res.percentiles.p85_duration <= res.percentiles.p95_duration
    assert len(res.histogram) >= 5

def test_demo_csv_endpoint():
    res = asyncio.run(get_demo_csv_file())
    assert "text/csv" in res.media_type
    assert "Chave da pendência" in res.body.decode("utf-8")

def test_demo_processed_endpoint():
    res = asyncio.run(get_processed_demo_data())
    assert res.success is True
    assert res.processed_gold_rows > 100
    assert res.metrics_summary.total_issues > 100
    assert res.metrics_summary.total_bugs > 0
    assert res.metrics_summary.p85_lead_time_days is not None