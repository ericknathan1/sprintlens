from fastapi import APIRouter, Response
from ..services.demo_generator import generate_demo_csv_string, generate_demo_jira_issues
from ..services.medallion_etl import run_medallion_pipeline
from ..services.column_matcher import match_columns
from ..models.dataset import ETLProcessResponse

router = APIRouter(prefix="/demo", tags=["Demo Dataset"])

@router.get("/csv")
async def get_demo_csv_file():
    """
    Returns synthetic Jira demo dataset formatted as CSV file attachment.
    """
    csv_data = generate_demo_csv_string()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="sprintlens_jira_demo.csv"'},
    )

@router.get("/processed", response_model=ETLProcessResponse)
async def get_processed_demo_data():
    """
    Directly returns the demo dataset processed through Medallion pipeline (Gold layer & KPIs).
    """
    csv_data = generate_demo_csv_string()
    # Standard mapping for the demo generator headers
    mapping = {
        "issue_key": "Chave da pendência",
        "issue_type": "Tipo de item",
        "status": "Status",
        "priority": "Prioridade",
        "assignee": "Responsável",
        "created_at": "Data de criação",
        "updated_at": "Data de atualização",
        "resolved_at": "Data de resolução",
        "sprint": "Sprint",
        "story_points": "Story Points",
        "time_spent_sec": "Tempo gasto (segundos)",
        "original_estimate_sec": "Estimativa original (segundos)",
    }
    return run_medallion_pipeline(csv_data, mapping)

