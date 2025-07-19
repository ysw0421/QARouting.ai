from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
import shutil
from dotenv import load_dotenv
load_dotenv()
from scripts.langgraph_workflow import app, State
from fastapi.staticfiles import StaticFiles
from typing import List
import json

app_api = FastAPI(
    title="QARouting.ai API",
    description="문서/약관 QA & 컴플라이언스 자동화 API (Swagger 문서 자동화)",
    version="1.0.0"
)

# Allow all origins for demo purposes (customize for production)
app_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app_api.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app_api.mount("/results", StaticFiles(directory="results"), name="results")
app_api.mount("/eval", StaticFiles(directory="eval"), name="eval")
# 정적 파일은 /static으로만 서빙
app_api.mount("/static", StaticFiles(directory="frontend/build/static", html=False), name="static")

BENCHMARK_CASES_PATH = "eval/benchmark_cases.json"

class WorkflowResponse(BaseModel):
    result: dict | None = None
    error: str | None = None

@app_api.post(
    "/run_workflow",
    response_model=WorkflowResponse,
    summary="문서/텍스트 워크플로우 실행",
    tags=["Workflow"]
)
async def run_workflow(
    file: UploadFile = File(None, description="분석할 PDF/MD 파일 (선택)"),
    text: str = Form(None, description="분석할 텍스트 (선택)")
):
    """
    문서(PDF/MD) 또는 텍스트 입력을 받아 약관/문서 QA & 컴플라이언스 워크플로우를 실행합니다.
    - 파일 또는 텍스트 중 하나는 반드시 입력해야 합니다.
    - 결과는 구조화된 JSON으로 반환됩니다.
    """
    file_path = None
    if file:
        filename = file.filename if file.filename else "uploaded_file"
        ext = os.path.splitext(filename)[-1].lower()
        if ext not in [".pdf", ".md", ".txt"]:
            return WorkflowResponse(result=None, error="지원하지 않는 파일 형식입니다. (PDF/MD/TXT만 허용)")
        file_content = await file.read()
        # HTML 파일 업로드 방지
        if b"<!DOCTYPE html" in file_content or b"<html" in file_content:
            return WorkflowResponse(result=None, error="HTML 파일은 업로드할 수 없습니다. (마크다운/텍스트만 허용)")
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    elif text:
        if "<!DOCTYPE html" in text or "<html" in text:
            return WorkflowResponse(result=None, error="HTML 내용은 입력할 수 없습니다. (마크다운/텍스트만 허용)")
        file_path = os.path.join(UPLOAD_DIR, "input.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    if not file_path:
        return WorkflowResponse(result=None, error="No file or text provided.")
    # [수정] 질문이 없을 때 기본 질문 세팅 (Task3 실무 요구)
    if not text or not text.strip():
        text = "이 문서의 주요 위험/이슈를 분석해줘"
    state: State = {"file_path": file_path, "text": text}
    try:
        from scripts.langgraph_workflow import run_workflow
        result_dict = run_workflow(state)
        result_dict = dict(result_dict)
        # 워크플로우 결과를 results/benchmark_results.json에 append 저장
        import json
        results_path = os.path.join("results", "benchmark_results.json")
        try:
            if os.path.exists(results_path):
                with open(results_path, "r", encoding="utf-8") as f:
                    results = json.load(f)
                if not isinstance(results, list):
                    results = []
            else:
                results = []
            results.append(result_dict)
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass  # 저장 실패 시 무시(서비스 영향 없음)
        # 실패 케이스는 benchmark_failures.json에도 append 저장
        if not result_dict.get("success", True) or result_dict.get("error"):
            failures_path = os.path.join("results", "benchmark_failures.json")
            try:
                if os.path.exists(failures_path):
                    with open(failures_path, "r", encoding="utf-8") as f:
                        failures = json.load(f)
                    if not isinstance(failures, list):
                        failures = []
                else:
                    failures = []
                failures.append(result_dict)
                with open(failures_path, "w", encoding="utf-8") as f:
                    json.dump(failures, f, ensure_ascii=False, indent=2)
            except Exception as e:
                pass
    except Exception as e:
        return WorkflowResponse(result=None, error=f"Workflow execution failed: {e}")
    return WorkflowResponse(result=result_dict, error=None)

@app_api.get("/api/files", summary="업로드 파일 리스트", tags=["Files"])
async def list_files():
    files = []
    for fname in os.listdir(UPLOAD_DIR):
        if fname.lower().endswith((".pdf", ".md", ".txt", ".json")):
            files.append(fname)
    return JSONResponse(content={"files": files})

@app_api.get("/api/benchmark_cases", summary="List all benchmark cases", tags=["Benchmark"])
async def list_benchmark_cases():
    if not os.path.exists(BENCHMARK_CASES_PATH):
        return JSONResponse(content={"cases": []})
    with open(BENCHMARK_CASES_PATH, "r", encoding="utf-8") as f:
        cases = f.read()
    try:
        cases = json.loads(cases)
    except Exception:
        cases = []
    return JSONResponse(content={"cases": cases})

@app_api.post("/api/benchmark_cases", summary="Upload or create a new benchmark case", tags=["Benchmark"])
async def upload_benchmark_case(case: dict):
    cases = []
    if os.path.exists(BENCHMARK_CASES_PATH):
        with open(BENCHMARK_CASES_PATH, "r", encoding="utf-8") as f:
            try:
                cases = json.load(f)
            except Exception:
                cases = []
    cases.append(case)
    with open(BENCHMARK_CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    return {"success": True, "case": case}

@app_api.put("/api/benchmark_cases/{case_id}", summary="Edit a benchmark case by index", tags=["Benchmark"])
async def edit_benchmark_case(case_id: int, case: dict):
    if not os.path.exists(BENCHMARK_CASES_PATH):
        raise HTTPException(status_code=404, detail="Benchmark cases not found")
    with open(BENCHMARK_CASES_PATH, "r", encoding="utf-8") as f:
        try:
            cases = json.load(f)
        except Exception:
            cases = []
    if case_id < 0 or case_id >= len(cases):
        raise HTTPException(status_code=404, detail="Case not found")
    cases[case_id] = case
    with open(BENCHMARK_CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    return {"success": True, "case": case}

@app_api.delete("/api/benchmark_cases/{case_id}", summary="Delete a benchmark case by index", tags=["Benchmark"])
async def delete_benchmark_case(case_id: int):
    if not os.path.exists(BENCHMARK_CASES_PATH):
        raise HTTPException(status_code=404, detail="Benchmark cases not found")
    with open(BENCHMARK_CASES_PATH, "r", encoding="utf-8") as f:
        try:
            cases = json.load(f)
        except Exception:
            cases = []
    if case_id < 0 or case_id >= len(cases):
        raise HTTPException(status_code=404, detail="Case not found")
    deleted = cases.pop(case_id)
    with open(BENCHMARK_CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    return {"success": True, "deleted": deleted}

# React SPA 라우팅 지원: /, /index.html, /favicon.ico 등은 build/index.html 반환
@app_api.get("/", include_in_schema=False)
@app_api.get("/index.html", include_in_schema=False)
@app_api.get("/favicon.ico", include_in_schema=False)
async def serve_spa():
    return FileResponse("frontend/build/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.api_server:app_api", host="0.0.0.0", port=8000, reload=True) 