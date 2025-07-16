"""LangGraph 기반 문서 QA & 컴플라이언스 자동화 워크플로우 (병렬 처리/분기 고도화)"""
# 기존 LangGraph 관련 코드는 주석 처리
# from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.simple_question_answering import SimpleQuestionAnsweringAgent
from agents.potential_compliance_verification import compliance_issue_lookup
from agents.legal_team_escalator import escalate_ticket

def classify_intent(text: str) -> str:
    if text.strip().endswith('?') or text.strip().startswith('Q:'):
        return 'simple_q'
    return 'compliance'

if __name__ == "__main__":
    print("=== Unfair Terms Compliance & Q&A Workflow ===")
    simple_qa_agent = SimpleQuestionAnsweringAgent()
    while True:
        user_input = input("\n[User] Enter a question (or type 'exit' to quit): ")
        if user_input.strip().lower() == 'exit':
            print("Exiting workflow.")
            break
        intent = classify_intent(user_input)
        if intent == 'simple_q':
            answer = simple_qa_agent.answer(user_input)
            print("[SimpleQuestionAnsweringAgent Answer]\n", answer)
        else:
            compliance_result = compliance_issue_lookup(user_input)
            print("[PotentialComplianceVerificationAgent 결과]\n", compliance_result)
            if compliance_result.get("compliance_issue"):
                ticket = {"escalation_team": compliance_result.get("escalation_team")}
                escalation = escalate_ticket(ticket)
                print("[LegalTeamEscalatorAgent 결과]\n", escalation)
            else:
                print("[TicketGeneratorAgent] 티켓 생성 필요: ", compliance_result) 