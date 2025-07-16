"""LangGraph 기반 문서 QA & 컴플라이언스 자동화 워크플로우 (병렬 처리/분기 고도화)"""
# 기존 LangGraph 관련 코드는 주석 처리
# from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.terms_check_bot import extract_modified_terms
from agents.question_intention_ingester import classify_intention
from agents.potential_compliance_verification import generate_compliance_risk_assessment
from agents.ticket_generator import generate_ticket
from agents.legal_team_escalator import escalate_ticket
from agents.simple_question_answering import answer_simple_question
from utils.pdf_ingest import extract_text_from_pdf
from langgraph.graph import StateGraph
from typing import TypedDict, Any

# 상태 정의 (필요시 TypedDict 등으로 확장)
class State(TypedDict, total=False):
    file_path: str
    text: str
    intent: str
    answer: str
    assessment: str
    ticket: str
    escalation_needed: bool
    escalation: str

graph = StateGraph(state_schema=State)

def ingest_node(state: State) -> State:
    file_path = state.get("file_path")
    if not file_path:
        state["text"] = "오류: file_path가 제공되지 않았습니다."
        return state
    ext = os.path.splitext(file_path)[-1].lower()
    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext in [".md", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise ValueError("지원하지 않는 파일 형식입니다.")
    except Exception as e:
        text = f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}"
    state["text"] = text
    return state

def intention_node(state: State) -> State:
    text = state.get("text", "")
    try:
        intent = classify_intention(text)
    except Exception as e:
        intent = f"오류: 의도 분류 실패 - {e}"
    state["intent"] = intent
    return state

def qa_node(state: State) -> State:
    question = state.get("text", "")
    try:
        answer = answer_simple_question(question)
    except Exception as e:
        answer = f"오류: 답변 생성 실패 - {e}"
    state["answer"] = answer
    return state

def compliance_node(state: State) -> State:
    try:
        terms = extract_modified_terms(state.get("text", ""))
        assessment = generate_compliance_risk_assessment(terms)
    except Exception as e:
        assessment = f"오류: 컴플라이언스 평가 실패 - {e}"
    state["assessment"] = assessment
    return state

def ticket_node(state: State) -> State:
    assessment = state.get("assessment", "")
    try:
        ticket = generate_ticket(assessment)
        escalation_needed = "긴급" in ticket or "즉시" in ticket
    except Exception as e:
        ticket = f"오류: 티켓 생성 실패 - {e}"
        escalation_needed = False
    state["ticket"] = ticket
    state["escalation_needed"] = escalation_needed
    return state

def escalation_node(state: State) -> State:
    ticket = state.get("ticket", "")
    try:
        escalation = escalate_ticket(ticket)
    except Exception as e:
        escalation = f"오류: 에스컬레이션 실패 - {e}"
    state["escalation"] = escalation
    return state

# Register nodes
graph.add_node("ingest", ingest_node)
graph.add_node("intention", intention_node)
graph.add_node("qa", qa_node)
graph.add_node("compliance", compliance_node)
graph.add_node("ticket", ticket_node)
graph.add_node("escalation", escalation_node)

# 플로우 선언
graph.add_edge("ingest", "intention")
graph.add_conditional_edges("intention", lambda s: s["intent"], {
    "simple_q": "qa",
    "compliance": "compliance",
    "outlier": "ticket"
})
graph.add_edge("qa", "END")
graph.add_edge("compliance", "ticket")
graph.add_conditional_edges("ticket", lambda s: s["escalation_needed"], {
    True: "escalation",
    False: "END"
})
graph.add_edge("escalation", "END")

app = graph.compile()

if __name__ == "__main__":
    print("=== Unfair Terms Compliance & Q&A Workflow (LangGraph) ===")
    file_path = input("\n[User] 분석할 문서 경로를 입력하세요 (PDF/MD, 종료: exit): ")
    if file_path.strip().lower() == 'exit':
        print("Exiting workflow.")
    else:
        state: State = {"file_path": file_path}
        result = app.run(state)  # type: ignore[attr-defined]
        print("[최종 결과]", result) 