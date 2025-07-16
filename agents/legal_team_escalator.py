import json
import os

def escalate_ticket(ticket: dict, departments_path=None) -> dict:
    # 기본 경로: data/legal_team_departments.json
    departments_path = departments_path or os.path.join(os.path.dirname(__file__), '../data/legal_team_departments.json')
    with open(departments_path, 'r', encoding='utf-8') as f:
        data = json.load(f)["teams"]
    team_name = ticket.get("escalation_team")
    for team in data:
        if team["team_name"] == team_name:
            return {
                "assigned_team": team["team_name"],
                "members": team["members"],
                "responsibilities": team["responsibilities"]
            }
    return {"assigned_team": team_name, "members": [], "responsibilities": []} 