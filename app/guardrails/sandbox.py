import os
from pathlib import Path
from app.guardrails.policy import PermissionError

def validate_repository_path(repo_root: str, path: str) -> str:
    """
    Validates and returns absolute path inside target repository root using canonical resolution.
    """
    root_path = Path(repo_root).resolve()
    target = Path(path)
    if not target.is_absolute():
        target = root_path / target
    try:
        abs_target = target.resolve()
    except Exception:
        abs_target = target.absolute()

    if not abs_target.is_relative_to(root_path):
        raise PermissionError(
            f"Security Violation: Target path '{path}' is outside repository sandbox '{root_path}'."
        )
    return str(abs_target)
