import re
import unicodedata
from typing import List, Dict, Tuple, Optional
from ..models.mapping import UniversalField, ColumnMatchResult, DetectColumnsResponse

UNIVERSAL_FIELDS_DEF: List[UniversalField] = [
    UniversalField(
        key="issue_key",
        label="Chave da Issue (Key)",
        description="Identificador único da tarefa no Jira (ex: PROJ-123)",
        required=True,
        example="PROJ-101",
    ),
    UniversalField(
        key="issue_type",
        label="Tipo de Item (Type)",
        description="Classificação da tarefa: Bug, Story, Task, Epic",
        required=True,
        example="Story",
    ),
    UniversalField(
        key="status",
        label="Status da Tarefa",
        description="Estado atual no fluxo: In Progress, Done, Closed, To Do",
        required=True,
        example="Done",
    ),
    UniversalField(
        key="priority",
        label="Prioridade",
        description="Gravidade ou urgência: Highest, High, Medium, Low",
        required=False,
        example="High",
    ),
    UniversalField(
        key="assignee",
        label="Responsável (Assignee)",
        description="Nome ou usuário responsável pela execução",
        required=False,
        example="Carlos Santos",
    ),
    UniversalField(
        key="created_at",
        label="Data de Criação",
        description="Timestamp de quando o item foi cadastrado",
        required=True,
        example="2026-01-10 14:30:00",
    ),
    UniversalField(
        key="updated_at",
        label="Data de Última Atualização",
        description="Timestamp da última alteração no Jira",
        required=False,
        example="2026-01-15 09:12:00",
    ),
    UniversalField(
        key="resolved_at",
        label="Data de Resolução",
        description="Timestamp de conclusão ou encerramento da tarefa",
        required=False,
        example="2026-01-20 18:00:00",
    ),
    UniversalField(
        key="sprint",
        label="Sprint",
        description="Nome ou identificador da sprint vinculada",
        required=False,
        example="Sprint 14",
    ),
    UniversalField(
        key="story_points",
        label="Story Points",
        description="Estimativa de esforço relativo ou pontos de história",
        required=False,
        example="5",
    ),
    UniversalField(
        key="time_spent_sec",
        label="Tempo Gasto (Segundos)",
        description="Tempo logado ou apontado na tarefa",
        required=False,
        example="7200",
    ),
    UniversalField(
        key="original_estimate_sec",
        label="Estimativa Original (Segundos)",
        description="Tempo inicialmente estimado para conclusão",
        required=False,
        example="14400",
    ),
]

# Patterns dictionary for robust matching across Portuguese, English, and Jira variations
FIELD_PATTERNS: Dict[str, List[Tuple[str, float]]] = {
    "issue_key": [
        (r"^(issue[_\s\-]?key|chave([_\s\-]da[_\s\-]pend[eê]ncia)?|key|id)$", 1.0),
        (r"(issue.*key|chave|identificador)", 0.85),
    ],
    "issue_type": [
        (r"^(issue[_\s\-]?type|tipo([_\s\-]de[_\s\-](item|pend[eê]ncia))?|type)$", 1.0),
        (r"(tipo.*item|tipo.*pend[eê]ncia|issuetype)", 0.9),
    ],
    "status": [
        (r"^(status|situa[cç][aã]o|estado)$", 1.0),
        (r"(status|situa[cç][aã]o|estado)", 0.85),
    ],
    "priority": [
        (r"^(priority|prioridade|gravidade)$", 1.0),
        (r"(priority|prioridade)", 0.9),
    ],
    "assignee": [
        (r"^(assignee|respons[aá]vel|atribu[ií]do[_\s\-]a|desenvolvedor|dev|assigned[_\s\-]?to)$", 1.0),
        (r"(assignee|respons[aá]vel|atribu[ií]do)", 0.85),
    ],
    "created_at": [
        (r"^(created([_\s\-]?date)?|criado([_\s\-]?em)?|data[_\s\-]de[_\s\-]cria[cç][aã]o|dt[_\s\-]cria[cç][aã]o)$", 1.0),
        (r"(cria[cç][aã]o|created)", 0.85),
    ],
    "updated_at": [
        (r"^(updated([_\s\-]?date)?|atualizado([_\s\-]?em)?|data[_\s\-]de[_\s\-]atualiza[cç][aã]o|dt[_\s\-]atualiza[cç][aã]o)$", 1.0),
        (r"(atualiza[cç][aã]o|updated)", 0.85),
    ],
    "resolved_at": [
        (r"^(resolved([_\s\-]?date)?|resolution[_\s\-]?date|resolvido([_\s\-]?em)?|conclu[ií]do([_\s\-]?em)?|data[_\s\-]de[_\s\-]resolu[cç][aã]o|dt[_\s\-]resolu[cç][aã]o)$", 1.0),
        (r"(resolu[cç][aã]o|resolved|conclus[aã]o|finaliza[cç][aã]o)", 0.85),
    ],
    "sprint": [
        (r"^(sprint(s)?|itera[cç][aã]o(s)?|iteration)$", 1.0),
        (r"(sprint|itera[cç][aã]o)", 0.85),
    ],
    "story_points": [
        (r"^(story[_\s\-]?point(s)?|custom[_\s\-]?field[_\s\-]?\(story[_\s\-]?point(s)?\)|pontos([_\s\-]de[_\s\-]hist[oó]ria)?|storypoints)$", 1.0),
        (r"(story[_\s\-]?point|pontos)", 0.85),
    ],
    "time_spent_sec": [
        (r"^(time[_\s\-]?spent([_\s\-]?\(sec(onds)?\))?|tempo[_\s\-]gasto|horas[_\s\-]gastas|logged[_\s\-]?time)$", 1.0),
        (r"(time[_\s\-]?spent|tempo[_\s\-]gasto)", 0.85),
    ],
    "original_estimate_sec": [
        (r"^(original[_\s\-]?estimate([_\s\-]?\(sec(onds)?\))?|estimativa[_\s\-]original|tempo[_\s\-]estimado)$", 1.0),
        (r"(original[_\s\-]?estimate|estimativa[_\s\-]original)", 0.85),
    ],
}

def normalize_text(text: str) -> str:
    """Normalizes string removing accents, lowercasing, and stripping whitespace."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return normalized.lower().strip()

def match_columns(csv_headers: List[str]) -> DetectColumnsResponse:
    """
    Evaluates CSV headers against universal schema using regex and synonym dictionary.
    Returns matched fields, unmatched headers, and confidence scores.
    """
    matches: Dict[str, ColumnMatchResult] = {}
    matched_headers = set()

    # Pre-clean headers
    clean_header_map = {h: normalize_text(h) for h in csv_headers}

    for field in UNIVERSAL_FIELDS_DEF:
        best_header: Optional[str] = None
        best_score: float = 0.0
        best_reason: Optional[str] = None

        patterns = FIELD_PATTERNS.get(field.key, [])

        for original_header, clean_h in clean_header_map.items():
            if original_header in matched_headers:
                continue

            for pattern, score in patterns:
                clean_pattern = normalize_text(pattern)
                if re.search(clean_pattern, clean_h):
                    if score > best_score:
                        best_score = score
                        best_header = original_header
                        best_reason = f"Corresponde ao padrão '{pattern}' com {int(score * 100)}% de confiança"

        if best_header and best_score >= 0.70:
            matched_headers.add(best_header)
            matches[field.key] = ColumnMatchResult(
                system_field=field.key,
                label=field.label,
                matched_csv_header=best_header,
                confidence=best_score,
                is_matched=True,
                required=field.required,
                match_reason=best_reason,
            )
        else:
            matches[field.key] = ColumnMatchResult(
                system_field=field.key,
                label=field.label,
                matched_csv_header=None,
                confidence=0.0,
                is_matched=False,
                required=field.required,
                match_reason="Nenhuma coluna correspondente identificada automaticamente.",
            )

    unmatched_csv_headers = [h for h in csv_headers if h not in matched_headers]

    return DetectColumnsResponse(
        matches=matches,
        csv_headers=csv_headers,
        unmatched_csv_headers=unmatched_csv_headers,
        universal_fields=UNIVERSAL_FIELDS_DEF,
    )

