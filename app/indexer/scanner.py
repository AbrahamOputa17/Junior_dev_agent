import os
from typing import List

class RepoScanner:
    SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".html", ".css", ".json"}
    IGNORE_DIRS = {".git", "node_modules", "venv", "__pycache__", ".pytest_cache", "dist", "build"}

    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    def scan_repository(self) -> List[str]:
        """
        Scans repository directory and returns list of relative file paths.
        """
        scanned_files = []
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS and not d.startswith(".")]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.repo_root)
                    scanned_files.append(rel_path)
        return scanned_files
