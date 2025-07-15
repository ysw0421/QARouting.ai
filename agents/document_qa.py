import os
import re

class DocumentIngestorAgent:
    def ingest(self, file_path):
        """
        문서 파일을 입력받아 텍스트로 변환/전처리
        현재는 .md 파일만 지원
        """
        if not os.path.exists(file_path):
            return "오류: 파일을 찾을 수 없습니다."

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}"

class SectionClassifierAgent:
    def classify(self, text):
        """
        Markdown 텍스트를 헤더(예: #, ##) 기준으로 섹션별로 분리
        각 섹션의 제목을 key, 본문을 value로 저장한 딕셔너리 반환
        """
        sections = {}
        current_title = None
        current_content = []
        for line in text.splitlines():
            header_match = re.match(r'^(#+)\s+(.*)', line)
            if header_match:
                # 이전 섹션 저장
                if current_title:
                    sections[current_title] = '\n'.join(current_content).strip()
                # 새 섹션 시작
                current_title = header_match.group(2).strip()
                current_content = []
            else:
                if current_title:
                    current_content.append(line)
        # 마지막 섹션 저장
        if current_title:
            sections[current_title] = '\n'.join(current_content).strip()
        return sections

class QAAssistantAgent:
    def answer(self, question, sections):
        """질문에 대해 섹션 기반 답변 생성"""
        pass

class ComplianceDetectorAgent:
    def detect(self, sections):
        """컴플라이언스 이슈 자동 탐지"""
        pass

class EscalationAgent:
    def escalate(self, issue):
        """복잡/자동화 불가 이슈를 담당자에게 에스컬레이션"""
        pass

class TicketGeneratorAgent:
    def generate(self, issue):
        """이슈/질문에 대해 티켓(이슈/작업) 자동 생성"""
        pass 
    