import os
import shutil
from typing import Dict, Any, List, Optional

def validate_startup_config(repo_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates environment settings, external dependencies (git, docker),
    write permissions, and repository paths at startup.
    """
    checks = {
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "api_auth_enabled": bool(os.getenv("JUNIOR_DEV_API_KEY")),
        "git_available": shutil.which("git") is not None,
        "docker_available": shutil.which("docker") is not None,
        "warnings": [],
        "errors": []
    }

    if not checks["openai_api_key_set"]:
        checks["warnings"].append("OPENAI_API_KEY is not set in environment. LLM mode will operate in fallback mode.")

    if not checks["api_auth_enabled"]:
        checks["warnings"].append("JUNIOR_DEV_API_KEY is not set. API endpoints will operate without authentication.")

    if not checks["git_available"]:
        checks["warnings"].append("Git CLI is not installed or not found in PATH.")

    if not checks["docker_available"]:
        checks["warnings"].append("Docker daemon is not running or not installed. Subprocess sandbox fallback will be used.")

    if repo_root:
        if not os.path.exists(repo_root):
            checks["errors"].append(f"Repository root directory does not exist: '{repo_root}'")
        elif not os.access(repo_root, os.W_OK):
            checks["errors"].append(f"Repository directory is not writable: '{repo_root}'")

    checks["valid"] = len(checks["errors"]) == 0
    return checks
