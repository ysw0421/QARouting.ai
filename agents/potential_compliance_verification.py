from utils.openai_utils import gpt_call

def generate_compliance_risk_assessment(terms: str) -> str:
    """
    Generate a compliance risk assessment for the given terms using GPT.
    """
    prompt = f"""
    아래 약관 조항을 분석하여 규정 준수 위험 평가서를 작성해줘.
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
        return gpt_call(prompt, model="gpt-4-1106-preview-nano")
    except Exception as e:
        return f"오류: 컴플라이언스 평가 실패 - {e}" 
    