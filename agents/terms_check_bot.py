from utils.openai_utils import gpt_call
import json

def extract_modified_terms(page_text: str) -> dict:
    """
    Extract only unfair or modified terms from the input text using GPT.
    Always returns dict: {"success": bool, "data": ..., "error": ...}
    """
    prompt = f"""
    아래 텍스트에서 불공정하거나 수정된 약관 조항만 추출해서 반환해줘.
    반드시 JSON 배열로 반환해. 예시: [{{"clause": "..."}}, ...]
    [약관 원문]
    {page_text}
    """
    try:
        raw = gpt_call(prompt, model="gpt-4-1106-preview-nano")
        try:
            raw = raw.strip('`').replace('json', '').strip()
            result = json.loads(raw)
            if isinstance(result, list):
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": "LLM output is not a list. Raw output: " + str(raw)}
        except Exception as e:
            return {"success": False, "error": f"LLM output parsing failed: {e}. Raw output: {raw}"}
    except Exception as e:
        return {"success": False, "error": f"약관 추출 실패 - {e}"} 