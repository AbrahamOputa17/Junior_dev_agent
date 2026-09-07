import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.core.agent import JuniorDevAgent

app = FastAPI(
    title="Junior Dev Agent API",
    description="Autonous AI Software Engineer Workstation API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    repo_path: str
    mode: str = "investigate"
    task_prompt: str
    user_approved: bool = False
    patch_content: Optional[str] = None
    target_file: Optional[str] = None

class IndexRequest(BaseModel):
    repo_path: str

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    static_html = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_html):
        return FileResponse(static_html)
    return HTMLResponse("<h1>Junior Dev Agent Backend API Online</h1>")


def _resolve_repo_path(repo_path: Optional[str]) -> str:
    """Resolves target repository path, falling back to workspace root if empty."""
    if not repo_path or not repo_path.strip():
        return os.path.abspath(".")
    
    # Try as relative or absolute
    abs_path = os.path.abspath(repo_path)
    if os.path.exists(abs_path):
        return abs_path
    
    # Try relative to project root
    project_root_rel = os.path.join(os.getcwd(), repo_path)
    if os.path.exists(project_root_rel):
        return project_root_rel

    return abs_path


@app.post("/api/index")
def index_repo(req: IndexRequest):
    target_path = _resolve_repo_path(req.repo_path)
    if not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail=f"Repository path '{req.repo_path}' not found on server.")
    agent = JuniorDevAgent(target_path)
    res = agent.index_repository()
    return res

@app.post("/api/task")
def run_task(req: TaskRequest):
    target_path = _resolve_repo_path(req.repo_path)
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=400,
            detail=f"Repository directory '{req.repo_path}' not found. Please enter a valid directory path."
        )
    agent = JuniorDevAgent(target_path)
    res = agent.run_task(
        mode=req.mode,
        task_prompt=req.task_prompt,
        user_approved=req.user_approved,
        patch_content=req.patch_content,
        target_file=req.target_file
    )
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=True)
