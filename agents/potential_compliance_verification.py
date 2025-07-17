from utils.openai_utils import gpt_call
import json

def generate_compliance_risk_assessment(terms: str) -> dict:
    """
    Generate a compliance risk assessment for the given terms using GPT.
    Always returns dict: {"success": bool, "data": ..., "error": ...}
    """
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
    try:
        raw = gpt_call(prompt, model="gpt-4-1106-preview-nano")
        try:
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            if isinstance(result, list):
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": "LLM output is not a list. Raw output: " + str(raw)}
        except Exception as e:
            return {"success": False, "error": f"LLM output parsing failed: {e}. Raw output: {raw}"}
    except Exception as e:
        return {"success": False, "error": f"컴플라이언스 평가 실패 - {e}"} 
    