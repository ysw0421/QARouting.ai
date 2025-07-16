def extract_modified_terms(page_text: str, use_llm=False, llm_model=None) -> str:
    """
    입력: 수정된 약관 페이지(텍스트)
    출력: 수정된 약관(텍스트 추출)
    실제 환경에서는 diff, NLP, 또는 LLM(GPT-4.1 nano 등) 활용 가능.
    """
    if use_llm and llm_model:
        # LLM 기반 변경점 추출 예시 (pseudo-code)
        prompt = f"다음 약관 텍스트에서 기존 버전 대비 변경된 조항만 한국어로 요약해줘.\n\n{page_text}"
        return llm_model.generate(prompt)
    # TODO: 실제로는 변경된 부분만 추출하는 로직 필요
    return page_text.strip() 