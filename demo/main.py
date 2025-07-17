from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (프론트엔드 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 항상 프로젝트 루트의 results 폴더를 가리키도록 수정
RESULTS_DIR = Path(__file__).parent.parent / "results"

@app.get("/questions")
def get_questions():
    files = list(RESULTS_DIR.glob("*.json"))
    return [{"filename": file.name} for file in files]

@app.get("/questions/{filename}")
def get_question_detail(filename: str):
    # 디렉토리 트래버설 방지
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = RESULTS_DIR / filename
    if not file_path.exists() or file_path.suffix != ".json":
        raise HTTPException(status_code=404, detail="File not found")
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data
