import os
from typing import Dict, Any, List
from app.guardrails.sandbox import validate_repository_path

def read_file_tool(repo_root: str, file_path: str, start_line: int = 1, end_line: int = 500) -> Dict[str, Any]:
    """
    Reads file content with line numbers and bounds.
    """
    abs_path = validate_repository_path(repo_root, file_path)
    if not os.path.isfile(abs_path):
        return {"error": f"File '{file_path}' does not exist."}

    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(total_lines, end_line)
        
        selected_lines = lines[start_idx:end_idx]
        formatted = "".join(f"{i + start_idx + 1:4d} | {line}" for i, line in enumerate(selected_lines))
        
        return {
            "file_path": file_path,
            "total_lines": total_lines,
            "showing_range": [start_idx + 1, end_idx],
            "content": formatted
        }
    except Exception as e:
        return {"error": f"Error reading file '{file_path}': {str(e)}"}

def list_files_tool(repo_root: str, directory_path: str = ".") -> Dict[str, Any]:
    """
    Lists directory file tree while respecting repository boundaries.
    """
    abs_dir = validate_repository_path(repo_root, directory_path)
    if not os.path.exists(abs_dir):
        return {"error": f"Directory '{directory_path}' does not exist."}

    file_list = []
    dir_list = []
    for root, dirs, files in os.walk(abs_dir):
        # Filter out hidden directories like .git
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        rel_root = os.path.relpath(root, repo_root)
        
        for f in files:
            if not f.startswith("."):
                file_list.append(os.path.join(rel_root if rel_root != "." else "", f))
        for d in dirs:
            dir_list.append(os.path.join(rel_root if rel_root != "." else "", d))

    return {
        "directory": directory_path,
        "files_count": len(file_list),
        "files": file_list[:200], # Cap at 200 files
        "directories": dir_list[:50]
    }
