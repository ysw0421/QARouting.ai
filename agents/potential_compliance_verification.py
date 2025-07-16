import json
import os

def compliance_issue_lookup(question: str, questions_path=None):
    # 기본 경로: data/complex_legal_questions.json
    questions_path = questions_path or os.path.join(os.path.dirname(__file__), '../data/complex_legal_questions.json')
    with open(questions_path, 'r', encoding='utf-8') as f:
        data = json.load(f)["complex_questions"]
    q_norm = question.strip().lower()
    for q in data:
        if q["question"].strip().lower() == q_norm:
            return {
                "compliance_issue": True,
                "details": q["category"],
                "escalation_team": q["escalation_team"],
                "priority": q["priority"],
                "assigned_level": q["assigned_level"],
                "status": q["status"]
            }
    return {"compliance_issue": False, "details": "[DB에 없는 복잡 질문입니다. 추가 검토 필요]"}

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