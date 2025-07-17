from utils.openai_utils import gpt_call
import json

def classify_intention(text: str) -> dict:
    """
    Classify the intention of the input text as 'complex', 'simple', or 'terms_review'.
    Returns a dict: {"success": bool, "data": str, "error": str}
    """
    prompt = f"""
    당신은 사용자의 질문을 분석하여 다음 세 가지 유형으로 정확히 분류하는 전문 어시스턴트입니다.

    - 복잡한 질문 (Complex): 법률 검토, 심도 있는 규정 준수, 법적 판단, 전문적인 분석 및 추가 검토가 필요한 질문
    - 단순한 질문 (Simple): 간단한 사실 확인, 미리 정의된 서비스 이용 규칙, 서비스 정책 등 즉각적으로 명확하게 답변 가능한 질문
    - 수정된 약관 확인 요청 (Terms Review): 약관, 계약, 정책 등 문서의 수정 또는 갱신된 내용을 확인하고 검토를 요청하는 질문

    질문을 분석하여 반드시 아래 중 하나의 유형으로만 분류하세요. 반드시 JSON 문자열로 {{\"intent\": \"complex|simple|terms_review\"}} 형태로만 반환하세요.
    [입력]
    {text}
    [출력]
    """
    try:
        raw = gpt_call(prompt, model="gpt-4.1-nano").strip()
        try:
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            intent = result.get("intent", "").strip().lower()
            if intent in {"complex", "simple", "terms_review"}:
                return {"success": True, "data": intent}
            else:
                return {"success": False, "error": f"Invalid intent value: {intent}"}
        except Exception as e:
            return {"success": False, "error": f"LLM output parsing failed: {e}. Raw output: {raw}"}
    except Exception as e:
        return {"success": False, "error": f"의도 분류 실패 - {e}"} 