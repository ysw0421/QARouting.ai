import json
from scripts.langgraph_workflow import app, State

# 외부 파일에서 테스트 케이스 로드
def load_cases(path="eval/benchmark_cases.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_benchmark():
    test_cases = load_cases()
    results = []
    for idx, case in enumerate(test_cases):
        print(f"[{idx+1}/{len(test_cases)}] 파일: {case['file_type']} 질문: {case['question']}")
        # 문서 내용을 임시 파일로 저장
        ext = ".md" if case["file_type"] == "md" else ".pdf"
        temp_path = f"eval/temp_input_{idx}{ext}"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(case["document_content"])
        state = State({"file_path": temp_path})
        result = app.run(state)  # type: ignore[attr-defined]
        routing = result.get("intent", "unknown")
        success = routing == case.get("expected_routing")
        results.append({
            "file_type": case["file_type"],
            "question": case["question"],
            "expected_routing": case.get("expected_routing"),
            "actual_routing": routing,
            "success": success,
            "error": result.get("error", ""),
            "answer": result.get("answer", ""),
            "assessment": result.get("assessment", ""),
            "ticket": result.get("ticket", ""),
            "escalation": result.get("escalation", ""),
            "expected_answer": case.get("expected_answer", "")
        })
    with open("eval/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    # 통계 리포트
    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    print(f"테스트 케이스: {total} / 성공: {success_count} / 성공률: {success_count/total*100:.1f}%")
    for r in results:
        if not r["success"]:
            print(f"[실패] 질문: {r['question']} | 기대: {r['expected_routing']} | 실제: {r['actual_routing']}")

if __name__ == "__main__":
    run_benchmark() 