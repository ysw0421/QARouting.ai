import logging
from agents.base_agent import BaseAgent
from utils.openai_utils import gpt_call
import json

logger = logging.getLogger("TermsCheckBotAgent")

class TermsCheckBotAgent(BaseAgent):
    def extract(self, page_text: str) -> dict:
        try:
            prompt = f"""
            아래 텍스트에서 불공정하거나 수정된 약관 조항만 추출해서 반환해줘.
            반드시 JSON 배열로 반환해. 예시: [{{"clause": "..."}}, ...]
            [약관 원문]
            {page_text}
            """
            self.logger.info("[약관 추출 시작]")
            raw = gpt_call(prompt, model="gpt-4.1-nano")
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            if isinstance(result, list):
                self.logger.info("[약관 추출 성공]")
                return self.success(result)
            else:
                return self.fail(f"LLM output is not a list. Raw output: {raw}")
        except Exception as e:
            return self.fail(f"약관 추출 실패 - {e}") 