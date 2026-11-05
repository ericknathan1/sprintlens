import pytest
from app.services.column_matcher import match_columns

def test_match_portuguese_jira_headers():
    pt_headers = [
        "Chave da pendência",
        "Tipo de item",
        "Status",
        "Prioridade",
        "Responsável",
        "Data de criação",
        "Data de atualização",
        "Data de resolução",
        "Sprint",
        "Story Points",
        "Tempo gasto",
        "Estimativa original",
    ]
    response = match_columns(pt_headers)
    assert response.matches["issue_key"].is_matched
    assert response.matches["issue_key"].matched_csv_header == "Chave da pendência"
    assert response.matches["issue_type"].matched_csv_header == "Tipo de item"
    assert response.matches["status"].matched_csv_header == "Status"
    assert response.matches["assignee"].matched_csv_header == "Responsável"
    assert response.matches["created_at"].matched_csv_header == "Data de criação"
    assert response.matches["story_points"].matched_csv_header == "Story Points"
    assert len(response.unmatched_csv_headers) == 0

def test_match_english_jira_headers():
    en_headers = [
        "Issue Key",
        "Issue Type",
        "Status",
        "Priority",
        "Assignee",
        "Created",
        "Updated",
        "Resolved",
        "Sprint",
        "Custom field (Story Points)",
        "Time Spent",
        "Original Estimate",
        "Extra Column Not in Schema",
    ]
    response = match_columns(en_headers)
    assert response.matches["issue_key"].is_matched
    assert response.matches["issue_key"].matched_csv_header == "Issue Key"
    assert response.matches["issue_type"].matched_csv_header == "Issue Type"
    assert response.matches["created_at"].matched_csv_header == "Created"
    assert response.matches["resolved_at"].matched_csv_header == "Resolved"
    assert "Extra Column Not in Schema" in response.unmatched_csv_headers

