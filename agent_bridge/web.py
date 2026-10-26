import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from .adapters import get_adapter

app = FastAPI(title="AgentBridge Workbench")

COLLAB_DIR = r"C:\Users\Administrator\Desktop\agent_collab"
STATIC_HTML_PATH = os.path.join(os.path.dirname(__file__), "static", "index.html")

class DispatchRequest(BaseModel):
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    if not os.path.exists(STATIC_HTML_PATH):
        raise HTTPException(status_code=404, detail="Workbench UI not found")
    with open(STATIC_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/artifact/{filename}", response_class=PlainTextResponse)
async def get_artifact(filename: str):
    # Sanitize path to avoid path traversal
    safe_name = os.path.basename(filename)
    file_path = os.path.join(COLLAB_DIR, safe_name)
    if not os.path.exists(file_path):
        return f"(未找到文件: {safe_name})"
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

@app.post("/api/dispatch")
async def dispatch_task(req: DispatchRequest):
    # Dispatch real prompt to Codex headlessly
    try:
        codex = get_adapter("codex")
        resp = codex.send(req.prompt, timeout=40)
        return {"success": True, "response": resp.content}
    except Exception as e:
        return {"success": False, "response": f"[Agent Error]: {str(e)}"}

def start_workbench(port: int = 8765):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    start_workbench()
