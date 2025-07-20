"""
LangGraph 기반 약관/문서 QA & 라우팅 플로우 (다이어그램 일치)
"""
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.question_intention_ingester import QuestionIntentionIngesterAgent
from agents.simple_question_answering import SimpleQuestionAnsweringAgent
from agents.potential_compliance_verification import PotentialComplianceVerificationAgent
from agents.ticket_generator import TicketGeneratorAgent
from agents.legal_team_escalator import LegalTeamEscalatorAgent
from utils.pdf_ingest import extract_text_from_pdf
from langgraph.graph import StateGraph
from typing import TypedDict, Any

# === 실무적 운영 로그/모니터링 설정 ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("LangGraphWorkflow")

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
    # 디버깅용 임시 필드
    intention_agent: Any
    question_answer_agent: Any
    compliance_agent: Any
    ticket_agent: Any
    escalation_agent: Any

# LangGraph 워크플로우 정의 (다이어그램 명칭 반영)
graph = StateGraph(state_schema=State)

# 0. DocumentIngestorAgent (문서 입력/전처리)
def document_ingestor_agent(state: State) -> State:
    logger.info("[DocumentIngestorAgent] 시작: %s", state.get("file_path"))
    file_path = state.get("file_path")
    if not file_path:
        logger.error("[DocumentIngestorAgent] file_path가 제공되지 않음")
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
            logger.error("[DocumentIngestorAgent] 지원하지 않는 파일 형식: %s", ext)
            state["error"] = "지원하지 않는 파일 형식입니다."
            return state
    except Exception as e:
        logger.exception("[DocumentIngestorAgent] 파일 읽기 실패")
        state["error"] = f"파일을 읽는 중 문제가 발생했습니다 - {e}"
        return state
    state["text"] = text
    logger.info("[DocumentIngestorAgent] 성공")
    return state

# 1. QuestionIntentionIngesterAgent
# (의도 분류)
def question_intention_ingester_agent(state: State) -> State:
    logger.info("[QuestionIntentionIngesterAgent] 시작")
    text = state.get("text", "")
    agent = QuestionIntentionIngesterAgent()
    result = agent.classify(text)
    state["intention_agent"] = result
    if not result.get("success"):
        logger.error("[QuestionIntentionIngesterAgent] 실패: %s", result.get("error"))
        state["error"] = result.get("error", "의도 분류 실패")
        state["intent"] = ""
        return state
    # result["data"]는 dict이므로 intent 값만 추출
    intent = result["data"].get("intent") if isinstance(result["data"], dict) else result["data"]
    state["intent"] = intent if intent is not None else ""
    logger.info("[QuestionIntentionIngesterAgent] 성공: %s", intent)
    return state

# 2. SimpleQuestionAnsweringAgent
# (단순 질문 응답)
def simple_question_answering_agent(state: State) -> State:
    logger.info("[SimpleQuestionAnsweringAgent] 시작")
    question = state.get("text", "")
    agent = SimpleQuestionAnsweringAgent()
    result = agent.answer(question)
    state["question_answer_agent"] = result
    if not result.get("success"):
        logger.error("[SimpleQuestionAnsweringAgent] 실패: %s", result.get("error"))
        state["error"] = result.get("error", "답변 생성 실패")
        return state
    state["answer"] = result["data"]
    logger.info("[SimpleQuestionAnsweringAgent] 성공")
    return state

# 3. PotentialComplianceVerificationAgent
# (컴플라이언스 위험 평가)
def potential_compliance_verification_agent(state: State) -> State:
    logger.info("[PotentialComplianceVerificationAgent] 시작")
    agent = PotentialComplianceVerificationAgent()
    result = agent.generate(state.get("text", ""))
    state["compliance_agent"] = result
    if not result.get("success"):
        logger.error("[PotentialComplianceVerificationAgent] 실패: %s", result.get("error"))
        state["error"] = result.get("error", "컴플라이언스 평가 실패")
        return state
    state["assessment"] = result["data"]
    logger.info("[PotentialComplianceVerificationAgent] 성공")
    return state

# 4. TicketGeneratorAgent
# (티켓 생성)
def ticket_generator_agent(state: State) -> State:
    logger.info("[TicketGeneratorAgent] 시작")
    assessment = state.get("assessment", "")
    if not assessment:
        assessment = state.get("text", "")
    agent = TicketGeneratorAgent()
    result = agent.generate(assessment)
    state["ticket_agent"] = result
    if not result.get("success"):
        logger.error("[TicketGeneratorAgent] 실패: %s", result.get("error"))
        state["error"] = result.get("error", "티켓 생성 실패")
        state["escalation_needed"] = False
        return state
    state["ticket"] = result["data"]
    urgency = str(result["data"]).lower()
    state["escalation_needed"] = ("긴급" in urgency or "즉시" in urgency or "high" in urgency)
    logger.info("[TicketGeneratorAgent] 성공")
    return state

# 5. LegalTeamEscalatorAgent
# (에스컬레이션)
def legal_team_escalator_agent(state: State) -> State:
    logger.info("[LegalTeamEscalatorAgent] 시작")
    ticket = state.get("ticket", "")
    agent = LegalTeamEscalatorAgent()
    result = agent.escalate(ticket)
    state["escalation_agent"] = result
    if not result.get("success"):
        logger.error("[LegalTeamEscalatorAgent] 실패: %s", result.get("error"))
        state["error"] = result.get("error", "에스컬레이션 실패")
        return state
    state["escalation"] = result["data"]
    logger.info("[LegalTeamEscalatorAgent] 성공")
    return state

# 노드 등록 (다이어그램 명칭)
graph.add_node("ingest", document_ingestor_agent)
graph.add_node("intention", question_intention_ingester_agent)
graph.add_node("simple", simple_question_answering_agent)
graph.add_node("compliance", potential_compliance_verification_agent)
graph.add_node("ticket", ticket_generator_agent)
graph.add_node("escalation", legal_team_escalator_agent)
graph.add_node("END", lambda state: state)

graph.set_entry_point("ingest")

# 플로우 선언 (다이어그램 일치)
# 워크플로우 그래프 정의부에서 각 Agent가 항상 실행되도록 분기 조건 제거
workflow = [
    document_ingestor_agent,
    question_intention_ingester_agent,
    simple_question_answering_agent,
    potential_compliance_verification_agent,
    ticket_generator_agent,
    legal_team_escalator_agent,
]
def run_workflow(state: State) -> State:
    for step in workflow:
        state = step(state)
    return state

workflow_app = graph.compile()

if __name__ == "__main__":
    print("=== LangGraph 기반 약관/문서 QA & 라우팅 플로우 (다이어그램 일치) ===")
    file_path = input("\n[User] 분석할 문서 경로를 입력하세요 (PDF/MD, 종료: exit): ")
    if file_path.strip().lower() == 'exit':
        print("Exiting workflow.")
    else:
        state: State = {"file_path": file_path}
        result = workflow_app.run(state)  # type: ignore[attr-defined]
        print("[최종 결과]", result) 
        