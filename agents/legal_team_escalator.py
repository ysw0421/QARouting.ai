import logging
import json
from utils.openai_utils import gpt_call
import smtplib
from email.mime.text import MIMEText
import os
from agents.base_agent import BaseAgent

logger = logging.getLogger("LegalTeamEscalatorAgent")

class LegalTeamEscalatorAgent(BaseAgent):
    def load_legal_org(self):
        with open("data/legal_team_departments.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def find_responsible_member(self, issue_type: str, min_level: int = 2) -> dict:
        org = self.load_legal_org()
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

    def send_email(self, to_address, subject, body):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        if not smtp_user or not smtp_password:
            self.logger.warning(f"[이메일 MOCK] SMTP 환경변수 미설정. 실제 발송되지 않음. 대상: {to_address} | 제목: {subject}")
            self.logger.info(f"[이메일 MOCK] {to_address} | {subject} | {body}")
            return
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_address
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    def escalate(self, ticket: str, issue_type: str = "compliance", min_level: int = 2) -> dict:
        try:
            self.logger.info("[에스컬레이션 시작]")
            member = self.find_responsible_member(issue_type, min_level)
            if member:
                subject = f"[에스컬레이션] {member['team']} - {member['position']}"
                body = f"티켓 내용:\n{ticket}"
                self.send_email(member["email"], subject, body)
                self.logger.info(f"[에스컬레이션 - MOCK] {member['team']} - {member['position']} ({member['email']})에게 알림 | 티켓: {ticket}")
                return self.success({
                    "team": member["team"],
                    "position": member["position"],
                    "email": member["email"],
                    "level": member["level"]
                })
            else:
                return self.fail("에스컬레이션 대상 담당자 없음")
        except Exception as e:
            return self.fail(f"에스컬레이션 실패 - {e}") 