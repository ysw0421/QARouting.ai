import logging
from agents.base_agent import BaseAgent
from utils.openai_utils import gpt_call
from langdetect import detect
import json

logger = logging.getLogger("SimpleQuestionAnsweringAgent")


class SimpleQuestionAnsweringAgent(BaseAgent):
    def detect_language(self, text: str) -> str:
        """
        입력 텍스트의 언어를 감지합니다.
        Args:
            text (str): 감지할 텍스트
        Returns:
            str: 언어 코드(예: 'ko', 'en', 'ja', 'unknown')
        """
        try:
            return detect(text)
        except Exception as e:
            self.logger.error(f"[언어 감지 실패] {e}")
            return "unknown"

    def answer(self, question: str) -> dict:
        """
        질문의 언어를 자동 감지하여, 해당 언어에 맞는 프롬프트로 GPT에 질의하고 답변을 반환합니다.
        항상 dict 반환: {"success": bool, "data": str, "error": str}
        """
        try:
            lang = self.detect_language(question)
            self.logger.info(f"[질문 언어 감지] 감지된 언어: {lang}")
            if lang == "ko":
                prompt = f"아래 질문에 대해 간결하고 명확하게 한국어로 답변해줘.\n[질문]\n{question}"
            elif lang == "en":
                prompt = f"Answer the following question concisely and clearly in English.\n[Question]\n{question}"
            elif lang == "ja":
                prompt = f"以下の質問に日本語で簡潔かつ明確に答えてください。必ず \n[질문]\n{question}"
            else:
                prompt = f"아래 질문에 대해 간결하고 명확하게 답변해줘.\n[질문]\n{question}"
            answer = gpt_call(prompt, model="gpt-4.1-nano")
            self.logger.info("[질문 응답 성공]")
            return self.success(answer)
        except Exception as e:
            return self.fail(f"[질문 응답 실패] {e}")
