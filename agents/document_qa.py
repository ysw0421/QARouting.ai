import os
import re
from sentence_transformers import SentenceTransformer, util
import pdfplumber
import json
import openai

class DocumentIngestorAgent:
    def ingest(self, file_path):
        """
        문서 파일을 입력받아 텍스트로 변환/전처리
        .md(마크다운) 및 .pdf 지원
        """
        if not os.path.exists(file_path):
            return "오류: 파일을 찾을 수 없습니다."

        ext = os.path.splitext(file_path)[-1].lower()
        try:
            if ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext == '.pdf':
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                if not text.strip():
                    return "오류: PDF에서 텍스트를 추출할 수 없습니다. (스캔본 등)"
                return text
            else:
                return f"오류: 지원하지 않는 파일 형식입니다: {ext}"
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
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def answer(self, question, sections):
        section_titles = list(sections.keys())
        section_texts = list(sections.values())
        section_embeddings = self.model.encode(section_texts, convert_to_tensor=True)
        question_embedding = self.model.encode([question], convert_to_tensor=True)[0]
        scores = util.cos_sim(question_embedding, section_embeddings)[0]
        best_idx = int(scores.argmax())
        best_title = section_titles[best_idx]
        best_content = section_texts[best_idx]
        return f"[{best_title}]\n{best_content}"

class ComplianceDetectorAgent:
    def __init__(self, openai_api_key=None, model_name="gpt-4-1106-preview"):
        self.model_name = model_name
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")

    def detect(self, sections):
        """
        sections: dict (title -> content)
        반드시 OpenAI GPT API를 사용하여 컴플라이언스(법적/윤리적) 이슈를 판단함.
        """
        issues = []
        openai.api_key = self.openai_api_key
        for title, content in sections.items():
            prompt = f"다음 텍스트에서 컴플라이언스(법적/윤리적) 이슈가 있는지 한국어로 요약해줘.\n\n[{title}]\n{content}"
            try:
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "당신은 컴플라이언스 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=512
                )
                llm_result = response.choices[0].message.content or ""
                llm_result = llm_result.strip()
                if llm_result:
                    issues.append({
                        "section": title,
                        "law": "LLM 기반 추출",
                        "desc": llm_result,
                        "evidence": content
                    })
            except Exception as e:
                issues.append({
                    "section": title,
                    "law": "LLM 오류",
                    "desc": f"OpenAI API 호출 오류: {e}",
                    "evidence": content
                })
        return issues

class EscalationAgent:
    def escalate(self, issue):
        # 실무에서는 Slack, 이메일, 이슈 트래커 등과 연동
        print(f"[에스컬레이션] 법률팀에 자동 전달: 섹션={issue['section']}, 사유={issue['desc']}")

class TicketGeneratorAgent:
    def generate(self, issue):
        # 실무에서는 JIRA, GitHub Issues 등과 연동
        print(f"[티켓 생성] 제목: [컴플라이언스] {issue['section']} - {issue['desc']}")
        print(f"내용: {issue['evidence'][:100]}... (법령: {issue['law']})\n") 
