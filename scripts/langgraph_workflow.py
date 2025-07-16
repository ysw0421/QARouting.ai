"""LangGraph 기반 문서 QA & 컴플라이언스 자동화 워크플로우 (병렬 처리/분기 고도화)"""
# 기존 LangGraph 관련 코드는 주석 처리
# from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.terms_check_bot import extract_modified_terms
from agents.question_intention_ingester import forward_to_compliance_verification
from agents.potential_compliance_verification import generate_compliance_risk_assessment
from agents.ticket_generator import generate_ticket
from agents.legal_team_escalator import escalate_ticket
from agents.simple_question_answering import answer_simple_question

def classify_intent(text: str) -> str:
    """
    Very simple intent classifier: returns 'simple_q' if the text looks like a question,
    otherwise 'compliance'. In production, use a proper intent classifier.
    """
    if text.strip().endswith('?') or text.strip().startswith('Q:'):
        return 'simple_q'
    return 'compliance'

if __name__ == "__main__":
    print("=== Unfair Terms Compliance & Q&A Workflow ===")
    while True:
        user_input = input("\n[User] Enter modified terms or a question (or type 'exit' to quit): ")
        if user_input.strip().lower() == 'exit':
            print("Exiting workflow.")
            break
        # 1. 약관/질문 입력 처리
        intent = classify_intent(user_input)
        if intent == 'simple_q':
            # Simple Q&A branch
            answer = answer_simple_question(user_input)
            print("[SimpleQuestionAnsweringAgent Answer]\n", answer)
        else:
            # Compliance branch
            modified_terms = extract_modified_terms(user_input)
            print("[수정된 약관 추출 결과]\n", modified_terms)
            forwarded_terms = forward_to_compliance_verification(modified_terms)
            print("[QuestionIntentionIngesterAgent 결과]\n", forwarded_terms)
            assessment = generate_compliance_risk_assessment(forwarded_terms)
            print("[규정 준수 위험 평가서]\n", assessment)
            ticket = generate_ticket(assessment)
            print("[티켓 생성 결과]\n", ticket)
            escalation = escalate_ticket(ticket)
            print("[에스컬레이션 결과]\n", escalation) 