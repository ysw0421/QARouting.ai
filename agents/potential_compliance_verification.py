def generate_compliance_risk_assessment(terms: str) -> str:
    """
    입력: 불공정 약관(텍스트)
    출력: 규정 준수 위험 평가서(Compliance Risk Assessment)
    """
    # 실제로는 GPT 등 LLM 활용, 여기서는 예시 포맷
    assessment = f"""
[이슈 유형]
법적 위험 / 불공정 약관 개선
[예상 위험성]
1. 접근 및 이용권한의 과도한 제한성
2. 정책 변경의 일방적 권한 행사
3. 약관 간 충돌 시 회사에 유리한 해석

원문:
{terms}
"""
    return assessment 