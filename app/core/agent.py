from typing import Dict, Any, Optional
from app.modes.investigate import InvestigateMode, DebugMode, ReviewMode, TestMode
from app.modes.implement import ImplementMode
from app.indexer.embeddings import RepositoryIndex

class JuniorDevAgent:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.indexer = RepositoryIndex(repo_root)
        self.modes = {
            "investigate": InvestigateMode(repo_root),
            "debug": DebugMode(repo_root),
            "review": ReviewMode(repo_root),
            "test": TestMode(repo_root),
            "implement": ImplementMode(repo_root),
        }

    def index_repository(self) -> Dict[str, Any]:
        return self.indexer.build_index()

    def run_task(self, mode: str, task_prompt: str, user_approved: bool = False, patch_content: Optional[str] = None, target_file: Optional[str] = None) -> Dict[str, Any]:
        mode_key = mode.lower()
        if mode_key not in self.modes:
            return {"error": f"Unknown mode '{mode}'. Available modes: {list(self.modes.keys())}"}

        handler = self.modes[mode_key]
        return handler.execute(
            task_prompt,
            user_approved=user_approved,
            patch_content=patch_content,
            target_file=target_file
        )
