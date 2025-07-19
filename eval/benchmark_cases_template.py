import json
import os

UPLOADS_DIR = "uploads"
CASES = []

for fname in os.listdir(UPLOADS_DIR):
    if not fname.lower().endswith((".md", ".pdf", ".txt")):
        continue
    fpath = os.path.join(UPLOADS_DIR, fname)
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        continue
    # 파일명/확장자 기반 자동 질문/expected 값 생성
    question = f"What is the main content of {fname}?"
    expected_routing = "simple"
    expected_answer = content[:200].replace("\n", " ") + ("..." if len(content) > 200 else "")
    CASES.append({
        "file_type": fname.split(".")[-1],
        "document_content": content,
        "question": question,
        "expected_routing": expected_routing,
        "expected_answer": expected_answer
    })

with open("eval/benchmark_cases.json", "w", encoding="utf-8") as f:
    json.dump(CASES, f, ensure_ascii=False, indent=2)
print(f"{len(CASES)}개 벤치마크 케이스가 eval/benchmark_cases.json에 저장되었습니다.") 