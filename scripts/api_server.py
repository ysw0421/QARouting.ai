from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from scripts.langgraph_workflow import app, State

app_api = FastAPI()

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

@app_api.post("/run_workflow")
async def run_workflow(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    """
    Run the unfair terms workflow on an uploaded file (PDF/MD) or raw text.
    Returns the workflow result as JSON.
    """
    file_path = None
    if file:
        filename = file.filename if file.filename else "uploaded_file"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif text:
        # Save text to a temporary .md file
        file_path = os.path.join(UPLOAD_DIR, "input.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        return JSONResponse({"error": "No file or text provided."}, status_code=400)

    state: State = {"file_path": file_path}
    try:
        result = app.run(state)  # type: ignore[attr-defined]
    except Exception as e:
        return JSONResponse({"error": f"Workflow execution failed: {e}"}, status_code=500)
    return JSONResponse({"result": result})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.api_server:app_api", host="0.0.0.0", port=8000, reload=True) 