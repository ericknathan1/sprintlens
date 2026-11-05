import io
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from ..models.dataset import ETLProcessResponse, MetricsSummary

COMPLETED_STATUSES = {
    "done", "concluido", "concluído", "closed", "fechado", 
    "resolved", "resolvido", "finalizado", "delivered", "entregue", "complete"
}

BUG_TYPES = {
    "bug", "defeito", "erro", "incident", "incidente", "falha", "problem", "problema"
}

def detect_csv_delimiter(content: str) -> str:
    """Detects whether CSV is separated by comma or semicolon."""
    first_lines = "\n".join(content.splitlines()[:5])
    semicolon_count = first_lines.count(";")
    comma_count = first_lines.count(",")
    return ";" if semicolon_count > comma_count else ","

def safe_parse_datetime(series: pd.Series) -> pd.Series:
    """Parses various date formats from Jira exports robustly."""
    return pd.to_datetime(series, errors="coerce", format="mixed")

def run_medallion_pipeline(
    csv_content: str,
    column_mapping: Dict[str, str],
    reference_date: Optional[datetime.datetime] = None
) -> ETLProcessResponse:
    """
    Executes Bronze -> Silver -> Gold transformation pipeline on Jira CSV data.
    """
    if reference_date is None:
        reference_date = datetime.datetime.now(datetime.timezone.utc)

    # -------------------------------------------------------------
    # 1. BRONZE LAYER: Raw Ingestion
    # -------------------------------------------------------------
    delimiter = detect_csv_delimiter(csv_content)
    df_bronze = pd.read_csv(io.StringIO(csv_content), sep=delimiter, dtype=str)
    total_bronze_rows = len(df_bronze)

    if total_bronze_rows == 0:
        raise ValueError("O arquivo CSV fornecido está vazio.")

    # -------------------------------------------------------------
    # 2. SILVER LAYER: Standardized Universal Contract
    # -------------------------------------------------------------
    df_silver = pd.DataFrame(index=df_bronze.index)

    # Pre-populate all 12 standard universal fields with None
    ALL_SYSTEM_FIELDS = [
        "issue_key", "issue_type", "status", "priority", "assignee",
        "created_at", "updated_at", "resolved_at", "sprint",
        "story_points", "time_spent_sec", "original_estimate_sec"
    ]
    for field in ALL_SYSTEM_FIELDS:
        df_silver[field] = np.nan

    # Invert mapping: system_field -> csv_header
    for system_field, csv_header in column_mapping.items():
        if csv_header and csv_header in df_bronze.columns:
            df_silver[system_field] = df_bronze[csv_header].str.strip()

    # Ensure critical defaults
    if "issue_key" not in df_silver.columns or df_silver["issue_key"].isna().all():
        df_silver["issue_key"] = [f"ITEM-{i+1}" for i in range(len(df_silver))]

    if "issue_type" not in df_silver.columns:
        df_silver["issue_type"] = "Story"
    df_silver["issue_type"] = df_silver["issue_type"].fillna("Story")

    if "status" not in df_silver.columns:
        df_silver["status"] = "To Do"
    df_silver["status"] = df_silver["status"].fillna("To Do")

    # Clean story points and time numbers
    if "story_points" in df_silver.columns:
        # replace comma with dot for decimals (ex: 3,5 -> 3.5)
        cleaned_sp = df_silver["story_points"].astype(str).str.replace(",", ".")
        df_silver["story_points"] = pd.to_numeric(cleaned_sp, errors="coerce")
    else:
        df_silver["story_points"] = np.nan

    for sec_field in ["time_spent_sec", "original_estimate_sec"]:
        if sec_field in df_silver.columns:
            df_silver[sec_field] = pd.to_numeric(df_silver[sec_field], errors="coerce").fillna(0).astype(int)
        else:
            df_silver[sec_field] = 0

    # Parse dates
    dt_created = safe_parse_datetime(df_silver.get("created_at", pd.Series(index=df_silver.index)))
    dt_updated = safe_parse_datetime(df_silver.get("updated_at", pd.Series(index=df_silver.index)))
    dt_resolved = safe_parse_datetime(df_silver.get("resolved_at", pd.Series(index=df_silver.index)))

    # Fallback for updated_at
    dt_updated = dt_updated.fillna(dt_created).fillna(pd.Timestamp(reference_date))

    # -------------------------------------------------------------
    # 3. GOLD LAYER: Calculated Engineering & Agile Metrics
    # -------------------------------------------------------------
    df_gold = df_silver.copy()

    # Classification: is_completed
    clean_status = df_gold["status"].astype(str).str.strip().str.lower()
    df_gold["is_completed"] = clean_status.isin(COMPLETED_STATUSES)

    # Classification: is_bug
    clean_type = df_gold["issue_type"].astype(str).str.strip().str.lower()
    df_gold["is_bug"] = clean_type.isin(BUG_TYPES)

    # Metric: lead_time_days = (resolved_at - created_at)
    lead_time_series = (dt_resolved - dt_created).dt.total_seconds() / 86400.0
    # Replace negative or NaN values appropriately
    lead_time_series = lead_time_series.apply(lambda x: round(x, 2) if pd.notnull(x) and x >= 0 else None)
    df_gold["lead_time_days"] = lead_time_series

    # Metric: days_since_update = (reference_date - updated_at)
    ref_ts = pd.Timestamp(reference_date).tz_localize(None) if dt_updated.dt.tz is None else pd.Timestamp(reference_date)
    # Ensure both are tz-naive for calculation
    dt_updated_naive = dt_updated.dt.tz_localize(None) if dt_updated.dt.tz is not None else dt_updated
    ref_ts_naive = ref_ts.tz_localize(None) if ref_ts.tzinfo is not None else ref_ts
    
    days_since_update_series = (ref_ts_naive - dt_updated_naive).dt.total_seconds() / 86400.0
    days_since_update_series = days_since_update_series.apply(lambda x: round(max(0.0, x), 1) if pd.notnull(x) else 0.0)
    df_gold["days_since_update"] = days_since_update_series

    # Re-assign ISO string dates for export
    df_gold["created_at"] = dt_created.dt.strftime("%Y-%m-%d %H:%M:%S")
    df_gold["updated_at"] = dt_updated.dt.strftime("%Y-%m-%d %H:%M:%S")
    df_gold["resolved_at"] = dt_resolved.dt.strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------------------------------------------
    # 4. AGGREGATED METRICS SUMMARY
    # -------------------------------------------------------------
    total_issues = len(df_gold)
    completed_issues = int(df_gold["is_completed"].sum())
    open_issues = total_issues - completed_issues
    total_bugs = int(df_gold["is_bug"].sum())
    bug_ratio_pct = round((total_bugs / total_issues * 100), 1) if total_issues > 0 else 0.0

    valid_lead_times = df_gold["lead_time_days"].dropna()
    if len(valid_lead_times) > 0:
        avg_lead_time = round(float(valid_lead_times.mean()), 1)
        median_lead_time = round(float(valid_lead_times.median()), 1)
        p85_lead_time = round(float(np.percentile(valid_lead_times, 85)), 1)
    else:
        avg_lead_time, median_lead_time, p85_lead_time = None, None, None

    total_sp = float(df_gold["story_points"].fillna(0).sum())
    completed_sp = float(df_gold[df_gold["is_completed"]]["story_points"].fillna(0).sum())

    unique_assignees = int(df_gold["assignee"].dropna().nunique())
    unique_sprints = int(df_gold["sprint"].dropna().nunique())

    # Zombie tasks: days_since_update > 5 and not completed
    is_zombie = (~df_gold["is_completed"]) & (df_gold["days_since_update"] > 5)
    zombie_count = int(is_zombie.sum())

    summary = MetricsSummary(
        total_issues=total_issues,
        completed_issues=completed_issues,
        open_issues=open_issues,
        total_bugs=total_bugs,
        bug_ratio_pct=bug_ratio_pct,
        avg_lead_time_days=avg_lead_time,
        median_lead_time_days=median_lead_time,
        p85_lead_time_days=p85_lead_time,
        total_story_points=round(total_sp, 1),
        completed_story_points=round(completed_sp, 1),
        unique_assignees=unique_assignees,
        unique_sprints=unique_sprints,
        zombie_tasks_count=zombie_count,
    )

    # Convert records to dictionary replacing NaN with None for clean JSON
    df_clean = df_gold.replace({np.nan: None})
    gold_records = [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in df_clean.to_dict(orient="records")
    ]

    return ETLProcessResponse(
        success=True,
        total_bronze_rows=total_bronze_rows,
        processed_gold_rows=len(gold_records),
        gold_issues=gold_records,
        metrics_summary=summary,
    )