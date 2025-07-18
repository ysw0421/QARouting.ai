from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from scripts.langgraph_workflow import app, State
from fastapi.staticfiles import StaticFiles

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
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif text:
        file_path = os.path.join(UPLOAD_DIR, "input.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    if not file_path:
        return WorkflowResponse(result=None, error="No file or text provided.")
    state: State = {"file_path": file_path}
    try:
        result = app.run(state)  # type: ignore[attr-defined]
    except Exception as e:
        return WorkflowResponse(result=None, error=f"Workflow execution failed: {e}")
    return WorkflowResponse(result=result, error=None)

@app_api.get("/api/files", summary="업로드 파일 리스트", tags=["Files"])
async def list_files():
    files = []
    for fname in os.listdir(UPLOAD_DIR):
        if fname.lower().endswith((".pdf", ".md", ".txt", ".json")):
            files.append(fname)
    return JSONResponse(content={"files": files})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.api_server:app_api", host="0.0.0.0", port=8000, reload=True) 