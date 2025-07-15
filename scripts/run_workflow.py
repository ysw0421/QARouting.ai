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
    print('--- [문서 섹션 분리 결과] ---')
    for k, v in sections.items():
        print(f'[{k}]\n{v}\n')

    answer = qa.answer(question, sections)
    print('--- [질문 응답 결과] ---')
    print(answer)

    issues = compliance.detect(sections)
    print('--- [컴플라이언스 이슈 탐지 결과] ---')
    for issue in issues:
        print(f"섹션: {issue['section']}")
        print(f"법령: {issue['law']}")
        print(f"설명: {issue['desc']}")
        print(f"근거: {issue['evidence'][:100]}...\n")

    for issue in issues or []:
        if issue.get('escalate'):
            escalation.escalate(issue)
        ticket.generate(issue)

if __name__ == '__main__':
    main() 