from utils.openai_utils import gpt_call
import json

def generate_test_cases(task_type="document_qa", num_cases=8):
    prompt = f"""
    아래 조건에 맞는 테스트 케이스를 {num_cases}개 생성해줘.
    - 각 케이스는 'file_type'(pdf/md), 'document_content'(간단한 약관/매뉴얼/기술문서 등), 'question'(질문), 'expected_routing'(simple_q/compliance/outlier), 'expected_answer'(간단 요약) 필드를 포함해야 해.
    - 다양한 엣지케이스(다국어, 스캔본, 비정형, 복잡한 질문 등)도 반드시 포함해.
    - JSON 배열로 반환해.
    """
    return gpt_call(prompt, model="gpt-4-1106-preview-nano")

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