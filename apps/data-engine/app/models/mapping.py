from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class UniversalField(BaseModel):
    key: str
    label: str
    description: str
    required: bool = False
    example: str

class DetectColumnsRequest(BaseModel):
    headers: List[str]
    sample_rows: Optional[List[Dict[str, Any]]] = None

class ColumnMatchResult(BaseModel):
    system_field: str
    label: str
    matched_csv_header: Optional[str] = None
    confidence: float = 0.0
    is_matched: bool = False
    required: bool = False
    match_reason: Optional[str] = None

class DetectColumnsResponse(BaseModel):
    matches: Dict[str, ColumnMatchResult]
    csv_headers: List[str]
    unmatched_csv_headers: List[str]
    universal_fields: List[UniversalField]

class ApplyMappingRequest(BaseModel):
    mapping: Dict[str, str] # e.g. {"issue_key": "Chave da pendência", "status": "Status"}
    csv_content: Optional[str] = None
    project_id: Optional[str] = None

