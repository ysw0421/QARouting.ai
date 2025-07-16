from utils.openai_utils import gpt_call

def extract_modified_terms(page_text: str) -> str:
    """
    Extract only unfair or modified terms from the input text using GPT.
    """
    prompt = f"""
    아래 텍스트에서 불공정하거나 수정된 약관 조항만 추출해서 반환해줘.
    [약관 원문]
    {page_text}
    """
    try:
        return gpt_call(prompt, model="gpt-4-1106-preview-nano")
    except Exception as e:
        return f"오류: 약관 추출 실패 - {e}" 