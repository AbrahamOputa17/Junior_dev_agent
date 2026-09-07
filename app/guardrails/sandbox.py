import os
from app.guardrails.policy import PermissionError

def validate_repository_path(repo_root: str, path: str) -> str:
    """
    Validates and returns absolute path inside target repository root.
    """
    abs_repo = os.path.abspath(repo_root)
    if os.path.isabs(path):
        abs_target = os.path.abspath(path)
    else:
        abs_target = os.path.abspath(os.path.join(abs_repo, path))

    if not abs_target.startswith(abs_repo):
        raise PermissionError(
            f"Security Violation: Target path '{path}' is outside repository sandbox '{abs_repo}'."
        )
    return abs_target
