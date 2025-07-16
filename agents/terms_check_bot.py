def extract_modified_terms(page_text: str) -> str:
    """
    입력: 수정된 약관 페이지(텍스트)
    출력: 수정된 약관(텍스트 추출)
    실제 환경에서는 diff, NLP 등 활용 가능. 여기서는 예시로 전체 텍스트 반환.
    """
    # TODO: 실제로는 변경된 부분만 추출하는 로직 필요
    return page_text.strip() 