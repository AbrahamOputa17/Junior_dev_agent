from typing import Dict, Any
from app.sandbox.runner import SandboxRunner

def search_git_history_tool(repo_root: str, max_count: int = 10) -> Dict[str, Any]:
    """
    Inspects recent git commits and log history.
    """
    runner = SandboxRunner(repo_root)
    result = runner.run_command(f"git log -n {max_count} --oneline")
    return {
        "exit_code": result.exit_code,
        "history": result.stdout if result.exit_code == 0 else result.stderr
    }

def git_diff_tool(repo_root: str) -> Dict[str, Any]:
    """
    Inspects active working tree diffs.
    """
    runner = SandboxRunner(repo_root)
    result = runner.run_command("git diff")
    return {
        "exit_code": result.exit_code,
        "diff": result.stdout if result.stdout else "No unstaged changes."
    }
