from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SilverIssue(BaseModel):
    issue_key: str
    issue_type: str
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    resolved_at: Optional[str] = None
    sprint: Optional[str] = None
    story_points: Optional[float] = None
    time_spent_sec: Optional[int] = None
    original_estimate_sec: Optional[int] = None

class GoldIssue(SilverIssue):
    lead_time_days: Optional[float] = None
    days_since_update: Optional[float] = None
    is_bug: bool = False
    is_completed: bool = False

class MetricsSummary(BaseModel):
    total_issues: int
    completed_issues: int
    open_issues: int
    total_bugs: int
    bug_ratio_pct: float
    avg_lead_time_days: Optional[float] = None
    median_lead_time_days: Optional[float] = None
    p85_lead_time_days: Optional[float] = None
    total_story_points: float = 0.0
    completed_story_points: float = 0.0
    unique_assignees: int
    unique_sprints: int
    zombie_tasks_count: int # days_since_update > 5 and not completed

class ETLProcessResponse(BaseModel):
    success: bool
    total_bronze_rows: int
    processed_gold_rows: int
    gold_issues: List[Dict[str, Any]]
    metrics_summary: MetricsSummary

