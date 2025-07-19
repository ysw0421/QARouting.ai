import logging
from agents.base_agent import BaseAgent
from utils.openai_utils import gpt_call
import json

logger = logging.getLogger("TicketGeneratorAgent")

class TicketGeneratorAgent(BaseAgent):
    def generate(self, assessment: str) -> dict:
        try:
            prompt = f"""
            아래 규정 준수 위험 평가서를 참고하여, 담당부서, 기한, 긴급도가 포함된 티켓을 생성해줘.
            반드시 JSON 객체로 반환해. 예시: {{"department": "법무팀", "deadline": "3일 이내", "urgency": "상"}}
            [평가서]
            {assessment}
            ---
            [출력 예시]
            담당부서: 법무팀
            기한: 3일 이내
            긴급도: 상
            """
            self.logger.info("[티켓 생성 시작]")
            raw = gpt_call(prompt, model="gpt-4.1-nano")
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            if isinstance(result, dict):
                self.logger.info(f"[티켓 생성 - MOCK] {result}")
                return self.success(result)
            else:
                return self.fail(f"LLM output is not a dict. Raw output: {raw}")
        except Exception as e:
            return self.fail(f"티켓 생성 실패 - {e}") 