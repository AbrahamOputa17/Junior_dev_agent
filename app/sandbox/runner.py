from app.sandbox.subprocess_sandbox import SubprocessSandbox, SandboxExecutionResult
from app.sandbox.docker_sandbox import DockerSandbox

class SandboxRunner:
    def __init__(self, repo_root: str, use_docker: bool = False):
        self.repo_root = repo_root
        if use_docker:
            self.provider = DockerSandbox(repo_root)
        else:
            self.provider = SubprocessSandbox(repo_root)

    def run_command(self, command: str, timeout_seconds: int = 30) -> SandboxExecutionResult:
        return self.provider.execute(command, timeout_seconds=timeout_seconds)

    def run_test(self, test_cmd: str = "pytest") -> SandboxExecutionResult:
        return self.run_command(test_cmd)

    def run_linter(self, lint_cmd: str = "ruff check .") -> SandboxExecutionResult:
        return self.run_command(lint_cmd)

    def run_type_checker(self, type_cmd: str = "mypy .") -> SandboxExecutionResult:
        return self.run_command(type_cmd)
