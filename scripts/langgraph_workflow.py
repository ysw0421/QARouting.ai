"""
LangGraph 기반 문서 QA & 컴플라이언스 자동화 워크플로우 (다이어그램 플로우 반영)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.question_intention_ingester import classify_intention
from agents.simple_question_answering import answer_simple_question
from agents.potential_compliance_verification import generate_compliance_risk_assessment
from agents.ticket_generator import generate_ticket
from agents.legal_team_escalator import escalate_ticket
from utils.pdf_ingest import extract_text_from_pdf
from langgraph.graph import StateGraph
from typing import TypedDict, Any

class State(TypedDict, total=False):
    file_path: str
    text: str
    intent: str
    answer: str
    assessment: Any
    ticket: Any
    escalation_needed: bool
    escalation: Any
    error: str

# LangGraph 워크플로우 정의
graph = StateGraph(state_schema=State)

def ingest_node(state: State) -> State:
    file_path = state.get("file_path")
    if not file_path:
        state["error"] = "file_path가 제공되지 않았습니다."
        return state
    ext = os.path.splitext(file_path)[-1].lower()
    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext in [".md", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            state["error"] = "지원하지 않는 파일 형식입니다."
            return state
    except Exception as e:
        state["error"] = f"파일을 읽는 중 문제가 발생했습니다 - {e}"
        return state
    state["text"] = text
    return state

def intention_node(state: State) -> State:
    text = state.get("text", "")
    result = classify_intention(text)
    if not result.get("success"):
        state["error"] = result.get("error", "의도 분류 실패")
        return state
    state["intent"] = result["data"]
    return state

def simple_node(state: State) -> State:
    question = state.get("text", "")
    result = answer_simple_question(question)
    if not result.get("success"):
        state["error"] = result.get("error", "답변 생성 실패")
        return state
    state["answer"] = result["data"]
    return state

def compliance_node(state: State) -> State:
    # 컴플라이언스 위험 평가
    result = generate_compliance_risk_assessment(state.get("text", ""))
    if not result.get("success"):
        state["error"] = result.get("error", "컴플라이언스 평가 실패")
        return state
    state["assessment"] = result["data"]
    return state

def ticket_node(state: State) -> State:
    assessment = state.get("assessment", "")
    # outlier는 assessment 없이 바로 ticket 생성 시도
    if not assessment:
        assessment = state.get("text", "")
    result = generate_ticket(assessment)
    if not result.get("success"):
        state["error"] = result.get("error", "티켓 생성 실패")
        state["escalation_needed"] = False
        return state
    state["ticket"] = result["data"]
    urgency = str(result["data"]).lower()
    state["escalation_needed"] = ("긴급" in urgency or "즉시" in urgency or "high" in urgency)
    return state

def escalation_node(state: State) -> State:
    ticket = state.get("ticket", "")
    result = escalate_ticket(ticket)
    if not result.get("success"):
        state["error"] = result.get("error", "에스컬레이션 실패")
        return state
    state["escalation"] = result["data"]
    return state

# 노드 등록
graph.add_node("ingest", ingest_node)
graph.add_node("intention", intention_node)
graph.add_node("simple", simple_node)
graph.add_node("compliance", compliance_node)
graph.add_node("ticket", ticket_node)
graph.add_node("escalation", escalation_node)

# 플로우 선언 (요구사항 반영)
graph.add_edge("ingest", "intention")
graph.add_conditional_edges("intention", lambda s: s["intent"], {
    "simple": "simple",
    "compliance": "compliance",
    "terms_review": "ticket"
})
graph.add_edge("simple", "END")
graph.add_edge("compliance", "ticket")
graph.add_edge("ticket", "escalation")
graph.add_edge("escalation", "END")

app = graph.compile()

if __name__ == "__main__":
    print("=== Unfair Terms Compliance & Q&A Workflow (LangGraph, 요구 플로우) ===")
    file_path = input("\n[User] 분석할 문서 경로를 입력하세요 (PDF/MD, 종료: exit): ")
    if file_path.strip().lower() == 'exit':
        print("Exiting workflow.")
    else:
        state: State = {"file_path": file_path}
        result = app.run(state)  # type: ignore[attr-defined]
        print("[최종 결과]", result) 