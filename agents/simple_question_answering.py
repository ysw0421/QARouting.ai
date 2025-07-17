from utils.openai_utils import gpt_call
from langdetect import detect

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

def answer_simple_question(question: str) -> str:
    """
    질문의 언어를 자동 감지하여, 해당 언어에 맞는 프롬프트로 GPT에 질의하고 답변을 반환합니다.
    Args:
        question (str): 질의 텍스트
    Returns:
        str: GPT 답변 또는 오류 메시지
    """
    lang = detect_language(question)
    if lang == "ko":
        prompt = f"아래 질문에 대해 간결하고 명확하게 한국어로 답변해줘.\n[질문]\n{question}"
    elif lang == "en":
        prompt = f"Answer the following question concisely and clearly in English.\n[Question]\n{question}"
    elif lang == "ja":
        prompt = f"以下の質問に日本語で簡潔かつ明確に答えてください。\n[質問]\n{question}"
    else:
        prompt = f"아래 질문에 대해 간결하고 명확하게 답변해줘.\n[질문]\n{question}"
    return gpt_call(prompt, model="gpt-4.1-nano")