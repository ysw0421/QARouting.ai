from utils.openai_utils import gpt_call

def generate_ticket(assessment: str) -> str:
    """
    Generate a ticket including department, deadline, and urgency from a compliance risk assessment.
    """
    prompt = f"""
    아래 규정 준수 위험 평가서를 참고하여, 담당부서, 기한, 긴급도가 포함된 티켓을 생성해줘.
    [평가서]
    {assessment}
    ---
    [출력 예시]
    담당부서: 법무팀
    기한: 3일 이내
    긴급도: 상
    """
    try:
        return gpt_call(prompt, model="gpt-4-1106-preview-nano")
    except Exception as e:
        return f"오류: 티켓 생성 실패 - {e}" 