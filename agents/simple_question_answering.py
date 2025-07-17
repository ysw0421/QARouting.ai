from utils.openai_utils import gpt_call
from langdetect import detect
import json

def detect_language(text: str) -> str:
    """
    입력 텍스트의 언어를 감지합니다.
    Args:
        text (str): 감지할 텍스트
    Returns:
        str: 언어 코드(예: 'ko', 'en', 'ja', 'unknown')
    """
    try:
        return detect(text)
    except Exception:
        return "unknown"

def answer_simple_question(question: str) -> dict:
    """
    질문의 언어를 자동 감지하여, 해당 언어에 맞는 프롬프트로 GPT에 질의하고 답변을 반환합니다.
    항상 dict 반환: {"success": bool, "data": str, "error": str}
    """
    lang = detect_language(question)
    if lang == "ko":
        prompt = f"아래 질문에 대해 간결하고 명확하게 한국어로 답변해줘. 반드시 JSON 문자열로 {{\"answer\": \"...\"}} 형태로 반환해.\n[질문]\n{question}"
    elif lang == "en":
        prompt = f"Answer the following question concisely and clearly in English. Return only a JSON string like {{\"answer\": \"...\"}}.\n[Question]\n{question}"
    elif lang == "ja":
        prompt = f"以下の質問に日本語で簡潔かつ明確に答えてください。必ず {{\"answer\": \"...\"}} のJSON文字列で返してください。\n[質問]\n{question}"
    else:
        prompt = f"아래 질문에 대해 간결하고 명확하게 답변해줘. 반드시 JSON 문자열로 {{\"answer\": \"...\"}} 형태로 반환해.\n[질문]\n{question}"
    try:
        raw = gpt_call(prompt, model="gpt-4-1106-preview-nano")
        # Robust JSON parsing
        try:
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            answer = result.get("answer", "").strip()
            if answer:
                return {"success": True, "data": answer}
            else:
                return {"success": False, "error": "No answer field in LLM output."}
        except Exception as e:
            return {"success": False, "error": f"LLM output parsing failed: {e}. Raw output: {raw}"}
    except Exception as e:
        return {"success": False, "error": f"답변 생성 실패 - {e}"} 