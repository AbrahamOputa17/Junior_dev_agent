import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from typing import Optional, Union, List
from app.sandbox.limits import DEFAULT_EXECUTION_TIMEOUT_SECONDS, MAX_OUTPUT_CHARACTERS
from app.sandbox.security import get_sanitized_env
from app.guardrails.sandbox import validate_repository_path

@dataclass
class SandboxExecutionResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: float
    timed_out: bool = False

class SubprocessSandbox:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    def execute(self, command: Union[str, List[str]], timeout_seconds: int = DEFAULT_EXECUTION_TIMEOUT_SECONDS) -> SandboxExecutionResult:
        """
        Executes a command inside the repository root directory as an argument vector with timeout and path sandboxing.
        """
        # Validate path
        validate_repository_path(self.repo_root, self.repo_root)
        env = get_sanitized_env()

        if isinstance(command, list):
            cmd_args = command
            cmd_str = " ".join(command)
        else:
            cmd_str = command
            cmd_args = shlex.split(command, posix=os.name != 'nt')

        start_time = time.time()
        process = None
        try:
            process = subprocess.Popen(
                cmd_args,
                shell=False,
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
                env=env
            )
            
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            
            return SandboxExecutionResult(
                command=cmd_str,
                exit_code=process.returncode,
                stdout=stdout[:MAX_OUTPUT_CHARACTERS],
                stderr=stderr[:MAX_OUTPUT_CHARACTERS],
                execution_time_ms=execution_time_ms,
                timed_out=False
            )
        except subprocess.TimeoutExpired:
            if process:
                process.kill()
                stdout, stderr = process.communicate()
            else:
                stdout, stderr = "", ""
            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            return SandboxExecutionResult(
                command=cmd_str,
                exit_code=124,
                stdout=stdout[:MAX_OUTPUT_CHARACTERS],
                stderr=f"Execution timed out after {timeout_seconds}s.\n" + stderr[:MAX_OUTPUT_CHARACTERS],
                execution_time_ms=execution_time_ms,
                timed_out=True
            )
        except Exception as e:
            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            return SandboxExecutionResult(
                command=cmd_str,
                exit_code=1,
                stdout="",
                stderr=f"Sandbox Execution Error: {str(e)}",
                execution_time_ms=execution_time_ms,
                timed_out=False
            )
