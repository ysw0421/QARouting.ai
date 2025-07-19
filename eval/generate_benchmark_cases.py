from utils.openai_utils import gpt_call
import json

def generate_test_cases(task_type="document_qa", num_cases=12):
    prompt = f"""
    아래 조건에 맞는 테스트 케이스를 {num_cases}개 생성해줘.
    - 각 케이스는 'file_type'(pdf/md), 'document_content'(다국어 혼합, 스캔본(텍스트 없음), 표/코드/이미지 포함, 실제 약관/매뉴얼 등 실전문서), 'question'(질문), 'expected_routing'(simple_q/compliance/outlier), 'expected_answer'(간단 요약) 필드를 포함해야 해.
    - 반드시 아래 엣지케이스를 포함해:
      1) 영어/일본어 혼합 문서
      2) 스캔본 PDF(텍스트 없음)
      3) 표/코드/이미지 등 비정형 포함 문서
      4) 실제 API 문서/제품 매뉴얼/약관 등 실전문서
    - JSON 배열로 반환해.
    """
    return gpt_call(prompt, model="gpt-4.1-nano")

if __name__ == "__main__":
    cases_json = generate_test_cases()
    try:
        cases = json.loads(cases_json)
    except Exception:
        # 혹시 LLM이 코드블록 등으로 감싸면 처리
        cases_json = cases_json.strip().strip('`').replace('json', '')
        cases = json.loads(cases_json)
    with open("eval/benchmark_cases.json", "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"{len(cases)}개 테스트 케이스가 eval/benchmark_cases.json에 저장되었습니다.") 