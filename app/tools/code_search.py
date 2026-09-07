import os
import re
from typing import Dict, Any, List
from app.guardrails.sandbox import validate_repository_path

def search_code_tool(repo_root: str, query: str, file_pattern: str = "") -> Dict[str, Any]:
    """
    Searches repository code for a pattern or keyword.
    """
    abs_repo = validate_repository_path(repo_root, repo_root)
    results = []
    regex = re.compile(query, re.IGNORECASE)

    for root, dirs, files in os.walk(abs_repo):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__")]
        for file in files:
            if file.startswith("."):
                continue
            if file_pattern and not file.endswith(file_pattern):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, abs_repo)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append({
                                "file": rel_path,
                                "line_number": line_num,
                                "content": line.strip()
                            })
                            if len(results) >= 100: # Cap search at 100 matches
                                break
            except Exception:
                continue

    return {
        "query": query,
        "total_matches": len(results),
        "matches": results
    }

def find_references_tool(repo_root: str, symbol_name: str) -> Dict[str, Any]:
    """
    Locates call sites and references for a symbol (function, class, variable).
    """
    return search_code_tool(repo_root, r"\b" + re.escape(symbol_name) + r"\b")
