import os
import re
import logging
from sentence_transformers import SentenceTransformer, util
import pdfplumber
from utils.openai_utils import gpt_call
from agents.base_agent import BaseAgent
from typing import Any, Dict

logger = logging.getLogger("DocumentQAAgent")

class DocumentIngestorAgent(BaseAgent):
    def __init__(self):
        self.logger = logging.getLogger("DocumentIngestorAgent")

    def ingest(self, file_path: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"[문서 인식 시작] {file_path}")
            if not os.path.exists(file_path):
                return self.fail("파일을 찾을 수 없습니다.")
            ext = os.path.splitext(file_path)[-1].lower()
            if ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif ext == '.pdf':
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                if not text.strip():
                    return self.fail("PDF에서 텍스트를 추출할 수 없습니다. (스캔본 등)")
            else:
                return self.fail(f"지원하지 않는 파일 형식입니다: {ext}")
            self.logger.info("[문서 인식 성공]")
            return self.success(text)
        except Exception as e:
            return self.fail(f"파일을 읽는 중 문제가 발생했습니다 - {e}")

class SectionClassifierAgent(BaseAgent):
    def __init__(self):
        self.logger = logging.getLogger("SectionClassifierAgent")

    def classify(self, text: str) -> Dict[str, Any]:
        try:
            self.logger.info("[섹션 분리 시작]")
            sections = {}
            current_title = None
            current_content = []
            for line in text.splitlines():
                header_match = re.match(r'^(#+)\s+(.*)', line)
                if header_match:
                    if current_title:
                        sections[current_title] = '\n'.join(current_content).strip()
                    current_title = header_match.group(2).strip()
                    current_content = []
                else:
                    if current_title:
                        current_content.append(line)
            if current_title:
                sections[current_title] = '\n'.join(current_content).strip()
            self.logger.info("[섹션 분리 성공]")
            return self.success(sections)
        except Exception as e:
            return self.fail(f"섹션 분리 실패 - {e}")

class QAAssistantAgent(BaseAgent):
    def __init__(self):
        self.logger = logging.getLogger("QAAssistantAgent")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def answer(self, question: str, sections: dict) -> Dict[str, Any]:
        try:
            self.logger.info("[질의응답 시작]")
            section_titles = list(sections.keys())
            section_texts = list(sections.values())
            section_embeddings = self.model.encode(section_texts, convert_to_tensor=True)
            question_embedding = self.model.encode([question], convert_to_tensor=True)[0]
            scores = util.cos_sim(question_embedding, section_embeddings)[0]
            best_idx = int(scores.argmax())
            best_title = section_titles[best_idx]
            best_content = section_texts[best_idx]
            self.logger.info(f"[질의응답 성공] {best_title}")
            return self.success(f"[{best_title}]\n{best_content}")
        except Exception as e:
            return self.fail(f"질의응답 실패 - {e}")

class ComplianceDetectorAgent(BaseAgent):
    def __init__(self):
        self.logger = logging.getLogger("ComplianceDetectorAgent")

    def detect(self, sections: dict) -> Dict[str, Any]:
        import json
        try:
            self.logger.info("[컴플라이언스 탐지 시작]")
            text = "\n\n".join([f"[{title}]\n{content}" for title, content in sections.items()])
            prompt = f"""
            아래 문서 섹션에서 컴플라이언스(법적/불공정/개인정보 등) 이슈가 의심되는 부분을 모두 찾아,
            [이슈 유형], [관련 법령], [설명], [근거(문장)] 형태로 JSON 배열로 정리해줘.
            반드시 JSON 배열로 반환해. 예시: [{{"issue_type": "법적 위험", "law": "GDPR", "desc": "...", "evidence": "..."}}]
            [문서]
            {text}
            """
            raw = gpt_call(prompt, model="gpt-4.1-nano")
            try:
                raw = raw.strip('`').replace('json', '').strip()
                result = json.loads(raw)
                if isinstance(result, list):
                    self.logger.info("[컴플라이언스 탐지 성공]")
                    return self.success(result)
                else:
                    return self.fail(f"LLM output is not a list. Raw output: {raw}")
            except Exception as e:
                return self.fail(f"LLM output parsing failed: {e}. Raw output: {raw}")
        except Exception as e:
            return self.fail(f"컴플라이언스 이슈 추출 실패 - {e}")

class EscalationAgent(BaseAgent):
    def __init__(self):
        self.logger = logging.getLogger("EscalationAgent")

    def escalate(self, issue: dict) -> Dict[str, Any]:
        try:
            self.logger.info(f"[에스컬레이션] 법률팀에 자동 전달: 섹션={issue.get('section')}, 사유={issue.get('desc')}")
            return self.success(issue)
        except Exception as e:
            return self.fail(f"에스컬레이션 실패 - {e}")

class TicketGeneratorAgent(BaseAgent):
    def __init__(self):
        self.logger = logging.getLogger("TicketGeneratorAgent")

    def generate(self, issue: dict) -> Dict[str, Any]:
        try:
            self.logger.info(f"[티켓 생성] 제목: [컴플라이언스] {issue.get('section')} - {issue.get('desc')}")
            self.logger.info(f"내용: {str(issue.get('evidence', ''))[:100]}... (법령: {issue.get('law')})\n")
            return self.success(issue)
        except Exception as e:
            return self.fail(f"티켓 생성 실패 - {e}") 
