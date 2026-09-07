from typing import Dict, Any
from app.sandbox.runner import SandboxRunner

def run_test_tool(repo_root: str, test_cmd: str = "pytest") -> Dict[str, Any]:
    """
    Executes unit test suite inside isolated sandbox.
    """
    runner = SandboxRunner(repo_root)
    result = runner.run_test(test_cmd)
    return {
        "command": result.command,
        "exit_code": result.exit_code,
        "passed": result.exit_code == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "execution_time_ms": result.execution_time_ms
    }

def run_linter_tool(repo_root: str, lint_cmd: str = "ruff check .") -> Dict[str, Any]:
    """
    Executes linter inside isolated sandbox.
    """
    runner = SandboxRunner(repo_root)
    result = runner.run_linter(lint_cmd)
    return {
        "command": result.command,
        "exit_code": result.exit_code,
        "passed": result.exit_code == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

def run_type_checker_tool(repo_root: str, type_cmd: str = "mypy .") -> Dict[str, Any]:
    """
    Executes type checker inside isolated sandbox.
    """
    runner = SandboxRunner(repo_root)
    result = runner.run_type_checker(type_cmd)
    return {
        "command": result.command,
        "exit_code": result.exit_code,
        "passed": result.exit_code == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
