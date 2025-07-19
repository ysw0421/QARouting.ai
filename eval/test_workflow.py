from scripts.langgraph_workflow import app, State

def test_document_qa():
    print("==== [문서 QA & 컴플라이언스 자동화 테스트] ====")
    # 샘플 파일 경로 (존재하는 md 또는 pdf 파일로 수정 가능)
    sample_file = "data/sample_openai.md"
    state = State({"file_path": sample_file})
    result = app.invoke(state)
    print("[워크플로우 결과]", result)
    print("==== [테스트 종료] ====")

if __name__ == "__main__":
    test_document_qa() 
