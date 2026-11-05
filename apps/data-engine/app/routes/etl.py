from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict
import json
from ..models.dataset import ETLProcessResponse
from ..services.medallion_etl import run_medallion_pipeline

router = APIRouter(prefix="/etl", tags=["Medallion ETL"])

@router.post("/process-csv", response_model=ETLProcessResponse)
async def process_csv_pipeline(
    file: UploadFile = File(...),
    column_mapping_json: str = Form(..., description="JSON string mapeando chaves do sistema para nomes de coluna do CSV"),
):
    """
    Receives raw CSV file and user-confirmed column mapping, runs Bronze -> Silver -> Gold pipeline.
    """
    try:
        column_mapping: Dict[str, str] = json.loads(column_mapping_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="O parâmetro 'column_mapping_json' deve ser um JSON válido.")

    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8", errors="replace")
        result = run_medallion_pipeline(content, column_mapping)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no pipeline ETL: {str(e)}")

