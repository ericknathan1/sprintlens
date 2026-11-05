import random
import datetime
from typing import List, Dict, Any
import pandas as pd

DEVELOPERS = [
    "Lucas Ribeiro",
    "Mariana Costa",
    "Rodrigo Alves",
    "Camila Fernandes",
    "Beatriz Lima",
]

ISSUE_TYPES = ["Story", "Story", "Story", "Bug", "Task", "Story", "Bug", "Story", "Task"]
PRIORITIES = ["Highest", "High", "Medium", "Medium", "Low"]
STORY_POINTS_OPTIONS = [1, 2, 3, 5, 8, 13]

SPRINTS = [
    ("Sprint 10", datetime.date(2026, 8, 4), datetime.date(2026, 8, 15)),
    ("Sprint 11", datetime.date(2026, 8, 18), datetime.date(2026, 8, 29)),
    ("Sprint 12", datetime.date(2026, 9, 1), datetime.date(2026, 9, 12)),
    ("Sprint 13", datetime.date(2026, 9, 15), datetime.date(2026, 9, 26)),
    ("Sprint 14", datetime.date(2026, 9, 29), datetime.date(2026, 10, 10)),
]

def generate_demo_jira_issues(count: int = 120) -> List[Dict[str, Any]]:
    """
    Generates a realistic synthetic Jira dataset containing issues distributed across
    sprints, devs, types, story points, and cycle times.
    """
    random.seed(42)  # Deterministic seed for reproducible testing
    issues = []

    issue_id = 100
    for sprint_name, s_start, s_end in SPRINTS:
        # Generate 20-25 issues per sprint
        sprint_issue_count = random.randint(18, 24)
        for _ in range(sprint_issue_count):
            issue_id += 1
            key = f"LENS-{issue_id}"
            issue_type = random.choice(ISSUE_TYPES)
            priority = random.choice(PRIORITIES)
            assignee = random.choice(DEVELOPERS)
            story_points = random.choice(STORY_POINTS_OPTIONS) if issue_type != "Bug" else random.choice([1, 2, 3])

            # Dates
            created_offset = random.randint(-7, 3)
            created_dt = datetime.datetime.combine(
                s_start + datetime.timedelta(days=created_offset),
                datetime.time(random.randint(9, 18), random.randint(0, 59))
            )

            # 85% completed in past sprints
            is_done = random.random() < 0.85
            if is_done:
                status = "Done"
                lead_time_days = random.randint(1, 10)
                resolved_dt = created_dt + datetime.timedelta(days=lead_time_days, hours=random.randint(1, 8))
                updated_dt = resolved_dt
            else:
                status = random.choice(["In Progress", "In Review", "To Do"])
                resolved_dt = None
                updated_days_ago = random.randint(1, 15)
                updated_dt = datetime.datetime.now() - datetime.timedelta(days=updated_days_ago)

            time_spent = story_points * random.randint(3600, 7200) if is_done else random.randint(1800, 7200)
            orig_estimate = story_points * 7200

            issues.append({
                "Chave da pendência": key,
                "Tipo de item": issue_type,
                "Status": status,
                "Prioridade": priority,
                "Responsável": assignee,
                "Data de criação": created_dt.strftime("%d/%m/%Y %H:%M"),
                "Data de atualização": updated_dt.strftime("%d/%m/%Y %H:%M"),
                "Data de resolução": resolved_dt.strftime("%d/%m/%Y %H:%M") if resolved_dt else "",
                "Sprint": sprint_name,
                "Story Points": story_points,
                "Tempo gasto (segundos)": time_spent,
                "Estimativa original (segundos)": orig_estimate,
            })

    # Add 15 backlog items
    for _ in range(15):
        issue_id += 1
        created_dt = datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 20))
        issues.append({
            "Chave da pendência": f"LENS-{issue_id}",
            "Tipo de item": random.choice(["Story", "Task", "Bug"]),
            "Status": "Backlog",
            "Prioridade": random.choice(PRIORITIES),
            "Responsável": random.choice(DEVELOPERS + [""]),
            "Data de criação": created_dt.strftime("%d/%m/%Y %H:%M"),
            "Data de atualização": created_dt.strftime("%d/%m/%Y %H:%M"),
            "Data de resolução": "",
            "Sprint": "",
            "Story Points": random.choice(STORY_POINTS_OPTIONS),
            "Tempo gasto (segundos)": 0,
            "Estimativa original (segundos)": random.choice([7200, 14400, 21600]),
        })

    return issues

def generate_demo_csv_string() -> str:
    """Returns the synthetic Jira dataset formatted as CSV."""
    records = generate_demo_jira_issues()
    df = pd.DataFrame(records)
    return df.to_csv(index=False, sep=";")

