from agents.document_qa import (
    DocumentIngestorAgent, SectionClassifierAgent, QAAssistantAgent,
    ComplianceDetectorAgent, EscalationAgent, TicketGeneratorAgent
)

def main():
    # 예시 입력
    file_path = './data/sample.md'
    question = '이 문서에서 개인정보 관련 법적 이슈가 있나요?'

    # 에이전트 인스턴스 생성
    ingestor = DocumentIngestorAgent()
    classifier = SectionClassifierAgent()
    qa = QAAssistantAgent()
    compliance = ComplianceDetectorAgent()
    escalation = EscalationAgent()
    ticket = TicketGeneratorAgent()

    # 워크플로우
    text = ingestor.ingest(file_path)
    sections = classifier.classify(text)
    answer = qa.answer(question, sections)
    issues = compliance.detect(sections)
    for issue in issues or []:
        if issue.get('escalate'):
            escalation.escalate(issue)
        ticket.generate(issue)
    print('답변:', answer)
    print('이슈:', issues)

if __name__ == '__main__':
    main() 