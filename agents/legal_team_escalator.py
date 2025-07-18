import json
from utils.openai_utils import gpt_call
import smtplib
from email.mime.text import MIMEText
import os

def load_legal_org():
    with open("data/legal_team_departments.json", "r", encoding="utf-8") as f:
        return json.load(f)

def find_responsible_member(issue_type: str, min_level: int = 2) -> dict:
    """
    이슈 유형(예: 'data privacy', 'IP', 'compliance', 'policy')와 최소 레벨로 담당자 자동 매칭
    """
    org = load_legal_org()
    for team in org["teams"]:
        if any(issue_type.lower() in resp.lower() for resp in team["responsibilities"]):
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

def send_email(to_address, subject, body):
    """
    실제 이메일 발송 함수 (Gmail SMTP 예시)
    환경변수 SMTP_USER, SMTP_PASSWORD 필요 (앱 비밀번호 권장)
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_user or not smtp_password:
        import logging
        logging.warning("[이메일 MOCK] SMTP 환경변수 미설정. 실제 발송되지 않음. 대상: %s | 제목: %s", to_address, subject)
        print(f"[이메일 MOCK] {to_address} | {subject} | {body}")
        return  # 환경변수 없으면 Mock
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_address
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

def escalate_ticket(ticket: str, issue_type: str = "compliance", min_level: int = 2) -> dict:
    """
    티켓 내용과 이슈 유형에 따라 담당자 자동 매칭 및 결과 반환
    항상 dict 반환: {"success": bool, "data": ..., "error": ...}
    실무 확장: 실제 이메일 연동 (환경변수 SMTP_USER, SMTP_PASSWORD 필요)
    """
    try:
        member = find_responsible_member(issue_type, min_level)
        if member:
            subject = f"[에스컬레이션] {member['team']} - {member['position']}"
            body = f"티켓 내용:\n{ticket}"
            send_email(member["email"], subject, body)
            print(f"[에스컬레이션 - MOCK] {member['team']} - {member['position']} ({member['email']})에게 알림 | 티켓: {ticket}")
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