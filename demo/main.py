from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (프론트엔드 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_DIR = Path("../results")

@app.get("/questions")
def get_questions():
    files = list(RESULTS_DIR.glob("*.json"))
    return [{"filename": file.name} for file in files]

@app.get("/questions/{filename}")
def get_question_detail(filename: str):
    file_path = RESULTS_DIR / filename
    if not file_path.exists() or file_path.suffix != ".json":
        raise HTTPException(status_code=404, detail="File not found")
    
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data
