import pytest
import datetime
from app.services.medallion_etl import run_medallion_pipeline

def test_medallion_pipeline_calculations():
    sample_csv = """Chave;Tipo;Situação;Dev;Criação;Resolução;Atualização;Pontos
PROJ-1;Story;Done;Lucas;2026-01-01 10:00:00;2026-01-05 10:00:00;2026-01-05 10:00:00;5
PROJ-2;Bug;Closed;Mariana;2026-01-02 10:00:00;2026-01-03 10:00:00;2026-01-03 10:00:00;2
PROJ-3;Task;In Progress;Lucas;2026-01-01 10:00:00;;2026-01-02 10:00:00;3
"""
    mapping = {
        "issue_key": "Chave",
        "issue_type": "Tipo",
        "status": "Situação",
        "assignee": "Dev",
        "created_at": "Criação",
        "resolved_at": "Resolução",
        "updated_at": "Atualização",
        "story_points": "Pontos",
    }
    ref_date = datetime.datetime(2026, 1, 10, 10, 0, 0, tzinfo=datetime.timezone.utc)
    res = run_medallion_pipeline(sample_csv, mapping, reference_date=ref_date)

    assert res.success is True
    assert res.total_bronze_rows == 3
    assert len(res.gold_issues) == 3

    # Check PROJ-1 (Story, Done)
    p1 = res.gold_issues[0]
    assert p1["issue_key"] == "PROJ-1"
    assert p1["is_completed"] is True
    assert p1["is_bug"] is False
    assert p1["lead_time_days"] == 4.0

    # Check PROJ-2 (Bug, Closed)
    p2 = res.gold_issues[1]
    assert p2["issue_key"] == "PROJ-2"
    assert p2["is_completed"] is True
    assert p2["is_bug"] is True
    assert p2["lead_time_days"] == 1.0

    # Check PROJ-3 (Task, In Progress)
    p3 = res.gold_issues[2]
    assert p3["issue_key"] == "PROJ-3"
    assert p3["is_completed"] is False
    assert p3["lead_time_days"] is None
    assert p3["days_since_update"] == 8.0  # 2026-01-10 - 2026-01-02 = 8 days

    # Check summary KPIs
    summary = res.metrics_summary
    assert summary.total_issues == 3
    assert summary.completed_issues == 2
    assert summary.total_bugs == 1
    assert round(summary.bug_ratio_pct, 1) == 33.3
    assert summary.zombie_tasks_count == 1  # PROJ-3 is not completed and updated > 5 days ago

