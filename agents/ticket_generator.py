def generate_ticket(assessment: str) -> dict:
    """
    입력: 규정 준수 위험 평가서(Compliance Risk Assessment)
    출력: 티켓(담당부서, 기한, 긴급도 포함)
    """
    # 실제로는 GPT, 규칙 기반 등 활용 가능. 예시 값 사용
    ticket = {
        '담당부서': '법무팀',
        '기한': '2024-06-30',
        '긴급도': '상',
        '내용': assessment
    }
    return ticket 