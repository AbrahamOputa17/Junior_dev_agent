import os
import subprocess
from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.sandbox.runner import SandboxRunner

@dataclass
class VerificationResult:
    passed: bool
    test_passed: bool
    lint_passed: bool
    type_passed: bool
    summary: str
    test_output: str
    lint_output: str
    type_output: str

def smart_truncate_log(text: str, max_chars: int = 4000) -> str:
    """Preserves head and tail error tracebacks when log exceeds limit."""
    if not text or len(text) <= max_chars:
        return text
    half = max_chars // 2
    head = text[:half]
    tail = text[-half:]
    return f"{head}\n\n[... TRUNCATED MIDDLE LOGS ({len(text) - max_chars} characters) ...]\n\n{tail}"

class VerificationRunner:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)
        self.sandbox = SandboxRunner(repo_root)

    def detect_test_command(self) -> str:
        """Auto-detects appropriate test command based on project manifests."""
        if os.path.exists(os.path.join(self.repo_root, "package.json")):
            return "npm test"
        elif os.path.exists(os.path.join(self.repo_root, "Cargo.toml")):
            return "cargo test"
        elif os.path.exists(os.path.join(self.repo_root, "go.mod")):
            return "go test ./..."
        return "pytest"

    def detect_lint_command(self) -> Optional[str]:
        """Auto-detects appropriate linter based on project manifests."""
        if os.path.exists(os.path.join(self.repo_root, "package.json")):
            return "npm run lint"
        elif os.path.exists(os.path.join(self.repo_root, "pyproject.toml")) or os.path.exists(os.path.join(self.repo_root, "requirements.txt")):
            return "ruff check ."
        return None

    def detect_type_command(self) -> Optional[str]:
        """Auto-detects appropriate type checker based on project manifests."""
        if os.path.exists(os.path.join(self.repo_root, "tsconfig.json")):
            return "npx tsc --noEmit"
        elif os.path.exists(os.path.join(self.repo_root, "pyproject.toml")):
            return "mypy app"
        return None

    def create_git_checkpoint(self) -> bool:
        """Creates an atomic git stash checkpoint including untracked files."""
        try:
            res = subprocess.run(
                ["git", "-C", self.repo_root, "stash", "push", "-u", "-m", "junior_dev_checkpoint"],
                capture_output=True,
                text=True
            )
            return res.returncode == 0
        except Exception:
            return False

    def rollback_git_changes(self) -> bool:
        """Restores git working directory to clean state if verification fails."""
        try:
            res = subprocess.run(["git", "-C", self.repo_root, "checkout", "--", "."], capture_output=True, text=True)
            subprocess.run(["git", "-C", self.repo_root, "clean", "-fd"], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def verify(
        self,
        test_cmd: Optional[str] = None,
        lint_cmd: Optional[str] = None,
        type_cmd: Optional[str] = None,
        auto_rollback: bool = False
    ) -> VerificationResult:
        """
        Executes automated self-verification suite inside sandbox with project auto-detection.
        """
        resolved_test_cmd = test_cmd or self.detect_test_command()

        # Run test suite
        test_res = self.sandbox.run_test(resolved_test_cmd)
        test_passed = test_res.exit_code == 0

        # Run linter if configured
        lint_passed = True
        lint_output = ""
        if lint_cmd:
            lint_res = self.sandbox.run_linter(lint_cmd)
            lint_passed = lint_res.exit_code == 0
            lint_output = smart_truncate_log(lint_res.stdout or lint_res.stderr)

        # Run type checker if configured
        type_passed = True
        type_output = ""
        if type_cmd:
            type_res = self.sandbox.run_type_checker(type_cmd)
            type_passed = type_res.exit_code == 0
            type_output = smart_truncate_log(type_res.stdout or type_res.stderr)

        all_passed = test_passed and lint_passed and type_passed

        if not all_passed and auto_rollback:
            self.rollback_git_changes()

        summary = "✅ Self-Verification PASSED: Proof of Fix confirmed." if all_passed else "❌ Self-Verification FAILED: Automated proof failed."

        return VerificationResult(
            passed=all_passed,
            test_passed=test_passed,
            lint_passed=lint_passed,
            type_passed=type_passed,
            summary=summary,
            test_output=smart_truncate_log(test_res.stdout or test_res.stderr),
            lint_output=lint_output,
            type_output=type_output
        )
