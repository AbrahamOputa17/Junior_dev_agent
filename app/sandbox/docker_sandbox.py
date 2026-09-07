import shutil
from app.sandbox.subprocess_sandbox import SubprocessSandbox, SandboxExecutionResult

class DockerSandbox:
    def __init__(self, repo_root: str, image_name: str = "python:3.11-slim"):
        self.repo_root = repo_root
        self.image_name = image_name
        self.fallback = SubprocessSandbox(repo_root)
        self.docker_available = shutil.which("docker") is not None

    def execute(self, command: str, timeout_seconds: int = 30) -> SandboxExecutionResult:
        if not self.docker_available:
            return self.fallback.execute(command, timeout_seconds=timeout_seconds)

        docker_cmd = (
            f"docker run --rm -v \"{self.repo_root}:/workspace\" "
            f"-w /workspace --network none {self.image_name} sh -c \"{command}\""
        )
        return self.fallback.execute(docker_cmd, timeout_seconds=timeout_seconds)
