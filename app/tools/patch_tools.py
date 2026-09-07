import os
from typing import Dict, Any
from app.guardrails.sandbox import validate_repository_path

def create_patch_tool(repo_root: str, file_path: str, new_content: str) -> Dict[str, Any]:
    """
    Drafts proposed file changes as a patch object.
    """
    abs_path = validate_repository_path(repo_root, file_path)
    old_content = ""
    if os.path.isfile(abs_path):
        with open(abs_path, "r", encoding="utf-8") as f:
            old_content = f.read()

    return {
        "file_path": file_path,
        "old_content_bytes": len(old_content),
        "new_content_bytes": len(new_content),
        "status": "patch_drafted",
        "new_content": new_content
    }

def apply_patch_tool(repo_root: str, file_path: str, content: str) -> Dict[str, Any]:
    """
    Applies approved modifications directly to repository file.
    """
    abs_path = validate_repository_path(repo_root, file_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "file_path": file_path,
        "status": "applied",
        "message": f"Successfully updated '{file_path}'."
    }

def apply_chunk_patch_tool(repo_root: str, file_path: str, start_line: int, end_line: int, replacement: str) -> Dict[str, Any]:
    """
    Replaces a specific line range [start_line, end_line] (1-indexed) with replacement text.
    Preserves all surrounding file content untouched.
    """
    abs_path = validate_repository_path(repo_root, file_path)
    if not os.path.exists(abs_path):
        return {"status": "error", "message": f"Target file '{file_path}' does not exist."}

    with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line)

    replacement_lines = [line + "\n" if not line.endswith("\n") else line for line in replacement.splitlines()]
    lines[start_idx:end_idx] = replacement_lines

    with open(abs_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return {
        "file_path": file_path,
        "status": "applied",
        "lines_modified": f"{start_line}-{end_line}",
        "message": f"Successfully applied chunk patch to '{file_path}' lines {start_line}-{end_line}."
    }
