import logging
from agents.base_agent import BaseAgent
from utils.openai_utils import gpt_call
import json

logger = logging.getLogger("PotentialComplianceVerificationAgent")

class PotentialComplianceVerificationAgent(BaseAgent):
    def generate(self, terms: str) -> dict:
        try:
            prompt = f"""
            아래 약관 조항을 분석하여 규정 준수 위험 평가서를 작성해줘.
            반드시 아래 예시처럼 JSON 배열로 반환해. 예시: [{{"issue_type": "법적 위험", "risk": ["...", "..."]}}]
            [약관 조항]
            {terms}
            ---
            [출력 예시]
            [이슈 유형]
            법적 위험 / 불공정 약관 개선
            [예상 위험성]
            1. ...
            2. ...
            3. ...
            """
            self.logger.info("[컴플라이언스 평가 시작]")
            raw = gpt_call(prompt, model="gpt-4.1-nano")
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            if isinstance(result, list):
                self.logger.info("[컴플라이언스 평가 성공]")
                return self.success(result)
            else:
                return self.fail(f"LLM output is not a list. Raw output: {raw}")
        except Exception as e:
            return self.fail(f"컴플라이언스 평가 실패 - {e}") 
    