"""LangGraph 기반 문서 QA & 컴플라이언스 자동화 워크플로우"""
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.document_qa import (
    DocumentIngestorAgent, SectionClassifierAgent, QAAssistantAgent,
    ComplianceDetectorAgent, EscalationAgent, TicketGeneratorAgent
)

class DocQAState(TypedDict, total=False):
    """LangGraph 워크플로우 상태 정의"""
    file_path: str
    question: str
    text: str
    sections: dict
    answer: str
    issues: list
    result: str

def ingest_node(state: DocQAState) -> DocQAState:
    """문서 파일 ingest 노드"""
    ingestor = DocumentIngestorAgent()
    file_path = state.get('file_path')
    text = ingestor.ingest(file_path)
    state['text'] = text
    return state

def classify_node(state: DocQAState) -> DocQAState:
    """문서 섹션 분류 노드"""
    classifier = SectionClassifierAgent()
    text = state.get('text', '')
    sections = classifier.classify(text)
    state['sections'] = sections
    return state

def qa_node(state: DocQAState) -> DocQAState:
    """질의응답 노드"""
    qa = QAAssistantAgent()
    question = state.get('question')
    sections = state.get('sections', {})
    answer = qa.answer(question, sections)
    state['answer'] = answer
    return state

def compliance_node(state: DocQAState) -> DocQAState:
    """컴플라이언스 이슈 탐지 노드"""
    compliance = ComplianceDetectorAgent()
    sections = state.get('sections', {})
    issues = compliance.detect(sections)
    state['issues'] = issues
    return state

def ticket_node(state: DocQAState) -> DocQAState:
    """티켓 생성 노드"""
    ticket = TicketGeneratorAgent()
    issues = state.get('issues', [])
    for issue in issues:
        ticket.generate(issue)
    state['result'] = 'ticket'
    return state

def escalation_node(state: DocQAState) -> DocQAState:
    """에스컬레이션 노드"""
    escalation = EscalationAgent()
    issues = state.get('issues', [])
    for issue in issues:
        escalation.escalate(issue)
    state['result'] = 'escalation'
    return state

def branch_node(state: DocQAState) -> str:
    """이슈에 따라 티켓/에스컬레이션 분기 노드"""
    issues = state.get('issues', [])
    for issue in issues:
        if '긴급' in issue.get('desc', ''):
            return 'escalation'
    return 'ticket'

graph = StateGraph(DocQAState)
graph.add_node('ingest', ingest_node)
graph.add_node('classify', classify_node)
graph.add_node('qa', qa_node)
graph.add_node('compliance', compliance_node)
graph.add_node('branch', branch_node)
graph.add_node('ticket', ticket_node)
graph.add_node('escalation', escalation_node)

graph.add_edge('ingest', 'classify')
graph.add_edge('classify', 'qa')
graph.add_edge('classify', 'compliance')
graph.add_edge('qa', 'branch')
graph.add_edge('compliance', 'branch')
graph.add_conditional_edges('branch', lambda s: s, {'ticket': 'ticket', 'escalation': 'escalation'})
graph.add_edge('ticket', END)
graph.add_edge('escalation', END)

app = graph.compile()

if __name__ == '__main__':
    """LangGraph 기반 문서 QA & 컴플라이언스 자동화 테스트 실행"""
    TEST_FILE_PATH = './data/sample.md'
    TEST_QUESTION = '이 문서에서 개인정보 관련 법적 이슈가 있나요?'
    state: DocQAState = {'file_path': TEST_FILE_PATH, 'question': TEST_QUESTION}
    print('==== [LangGraph 기반 문서 QA & 컴플라이언스 자동화] ====')
    for s in app.stream(state):
        print(f'--- [상태] ---\n{s}\n')
    print('==== [종료] ====') 