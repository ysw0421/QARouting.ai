from utils.openai_utils import gpt_call
import json

def generate_ticket(assessment: str) -> dict:
    """
    Generate a ticket including department, deadline, and urgency from a compliance risk assessment.
    Always returns dict: {"success": bool, "data": ..., "error": ...}
    실무 확장: 실제 JIRA, GitHub Issues 등 외부 시스템 연동은 아래 확장 포인트 참고
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
                # === 실무 확장 포인트 ===
                # 실제 JIRA, GitHub Issues 등과 연동하려면 아래 부분을 구현
                # 예시:
                # ticket_id = create_jira_ticket(result)
                # result["external_ticket_id"] = ticket_id
                # =========================
                # Mock(시뮬레이션) 구현: 콘솔 출력
                print(f"[티켓 생성 - MOCK] {result}")
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": "LLM output is not a dict. Raw output: " + str(raw)}
        except Exception as e:
            return {"success": False, "error": f"LLM output parsing failed: {e}. Raw output: {raw}"}
    except Exception as e:
        return {"success": False, "error": f"티켓 생성 실패 - {e}"} 