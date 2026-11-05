from fastapi import APIRouter, UploadFile, File, HTTPException
import io
import pandas as pd
from ..models.mapping import DetectColumnsRequest, DetectColumnsResponse
from ..services.column_matcher import match_columns, UNIVERSAL_FIELDS_DEF
from ..services.medallion_etl import detect_csv_delimiter

router = APIRouter(prefix="/mapping", tags=["Column Mapping"])

@router.post("/detect-columns", response_model=DetectColumnsResponse)
async def detect_columns_from_headers(request: DetectColumnsRequest):
    """
    Recognizes universal contract fields from a list of header strings.
    """
    if not request.headers:
        raise HTTPException(status_code=400, detail="A lista de cabeçalhos não pode ser vazia.")
    return match_columns(request.headers)

@router.post("/detect-from-csv", response_model=DetectColumnsResponse)
async def detect_columns_from_file(file: UploadFile = File(...)):
    """
    Extracts headers directly from an uploaded CSV file and executes auto-matching.
    """
    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8", errors="replace")
        delimiter = detect_csv_delimiter(content)
        df_sample = pd.read_csv(io.StringIO(content), sep=delimiter, nrows=5)
        headers = list(df_sample.columns)
        return match_columns(headers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo CSV: {str(e)}")

@router.get("/universal-fields")
async def get_universal_schema():
    """Returns the universal schema definition."""
    return {"fields": UNIVERSAL_FIELDS_DEF}

