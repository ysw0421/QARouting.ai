from utils.openai_utils import gpt_call
import json

def generate_ticket(assessment: str) -> dict:
    """
    Generate a ticket including department, deadline, and urgency from a compliance risk assessment.
    Always returns dict: {"success": bool, "data": ..., "error": ...}
    """
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
    try:
        raw = gpt_call(prompt, model="gpt-4-1106-preview-nano")
        try:
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            if isinstance(result, dict):
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": "LLM output is not a dict. Raw output: " + str(raw)}
        except Exception as e:
            return {"success": False, "error": f"LLM output parsing failed: {e}. Raw output: {raw}"}
    except Exception as e:
        return {"success": False, "error": f"티켓 생성 실패 - {e}"} 