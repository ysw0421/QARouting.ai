import json
from utils.openai_utils import gpt_call

def load_legal_org():
    with open("data/legal_team_departments.json", "r", encoding="utf-8") as f:
        return json.load(f)

def find_responsible_member(issue_type: str, min_level: int = 2) -> dict:
    """
    이슈 유형(예: 'data privacy', 'IP', 'compliance', 'policy')와 최소 레벨로 담당자 자동 매칭
    """
    org = load_legal_org()
    for team in org["teams"]:
        # 이슈 유형이 responsibilities에 포함된 팀 우선
        if any(issue_type.lower() in resp.lower() for resp in team["responsibilities"]):
            # 레벨 높은 멤버 우선
            sorted_members = sorted(team["members"], key=lambda m: -m["level"])
            for member in sorted_members:
                if member["level"] >= min_level:
                    return {
                        "team": team["team_name"],
                        "name_hash": member["name_hash"],
                        "position": member["position"],
                        "email": member["email"],
                        "level": member["level"]
                    }
    # fallback: 아무 팀이나
    for team in org["teams"]:
        for member in team["members"]:
            if member["level"] >= min_level:
                return {
                    "team": team["team_name"],
                    "name_hash": member["name_hash"],
                    "position": member["position"],
                    "email": member["email"],
                    "level": member["level"]
                }
    return {}

def escalate_ticket(ticket: str, issue_type: str = "compliance", min_level: int = 2) -> dict:
    """
    티켓 내용과 이슈 유형에 따라 담당자 자동 매칭 및 결과 반환
    항상 dict 반환: {"success": bool, "data": ..., "error": ...}
    """
    try:
        member = find_responsible_member(issue_type, min_level)
        if member:
            print(f"[에스컬레이션] {member['team']} - {member['position']} ({member['email']})에게 알림")
            return {
                "success": True,
                "data": {
                    "team": member["team"],
                    "position": member["position"],
                    "email": member["email"],
                    "level": member["level"]
                }
            }
        else:
            return {"success": False, "error": "에스컬레이션 대상 담당자 없음"}
    except Exception as e:
        return {"success": False, "error": f"에스컬레이션 실패 - {e}"} 