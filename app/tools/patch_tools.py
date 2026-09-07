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
