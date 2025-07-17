from utils.openai_utils import gpt_call

def classify_intention(text: str) -> str:
    """
    Classify the intention of the input text as 'simple_q', 'compliance', or 'outlier'.
    """
    prompt = f"""
    당신은 사용자의 질문을 분석하여 다음 세 가지 유형 중 하나로 정확히 분류하는 전문 어시스턴트입니다.

    - 복잡한 질문 (complex): 법률 검토, 심도 있는 규정 준수, 법적 판단, 전문적인 분석 및 추가 검토가 필요한 질문
    - 단순한 질문 (simple): 간단한 사실 확인, 미리 정의된 서비스 이용 규칙, 서비스 정책 등 즉각적으로 명확하게 답변 가능한 질문
    - 수정된 약관 확인 요청 (terms_review): 약관, 계약, 정책 등 문서의 수정 또는 갱신된 내용을 확인하고 검토를 요청하는 질문

    질문을 분석하여 반드시 'complex', 'simple', 'terms_review' 중 정확히 하나만 응답하세요.

    [입력]
    {text}
    [출력]
    """
    intent = gpt_call(prompt, model="gpt-4.1-nano").strip()
    return {
        "text": text,
        "agent": {
            "name": "intention",
            "intent": intent.lower()
        }
    }
