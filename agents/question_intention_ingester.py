from utils.openai_utils import gpt_call
import json

def classify_intention(text: str) -> dict:
    """
    Classify the intention of the input text as 'complex', 'simple', or 'terms_review'.
    Returns a dict: {"success": bool, "data": str, "error": str}
    """
    prompt = f"""
    아래 텍스트의 의도를 분류해줘.
    - 단순 질문이면 'simple_q'
    - 불공정 약관/컴플라이언스 이슈면 'compliance'
    - 즉시 에스컬레이션이 필요한 특이 케이스면 'outlier'
    [입력]
    {text}
    [출력]
    """
    try:
        return gpt_call(prompt, model="gpt-4-1106-preview-nano").strip()
    except Exception as e:
        return f"오류: 의도 분류 실패 - {e}" 