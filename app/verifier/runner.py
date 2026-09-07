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

class VerificationRunner:
    def __init__(self, repo_root: str):
        self.sandbox = SandboxRunner(repo_root)

    def verify(self, test_cmd: str = "pytest", lint_cmd: str = None, type_cmd: str = None) -> VerificationResult:
        """
        Executes automated self-verification suite inside sandbox.
        """
        # Run test suite
        test_res = self.sandbox.run_test(test_cmd)
        test_passed = test_res.exit_code == 0

        # Run linter if configured
        lint_passed = True
        lint_output = ""
        if lint_cmd:
            lint_res = self.sandbox.run_linter(lint_cmd)
            lint_passed = lint_res.exit_code == 0
            lint_output = lint_res.stdout or lint_res.stderr

        # Run type checker if configured
        type_passed = True
        type_output = ""
        if type_cmd:
            type_res = self.sandbox.run_type_checker(type_cmd)
            type_passed = type_res.exit_code == 0
            type_output = type_res.stdout or type_res.stderr

        all_passed = test_passed and lint_passed and type_passed
        
        summary = "✅ Self-Verification PASSED: Proof of Fix confirmed." if all_passed else "❌ Self-Verification FAILED: Automated proof failed."

        return VerificationResult(
            passed=all_passed,
            test_passed=test_passed,
            lint_passed=lint_passed,
            type_passed=type_passed,
            summary=summary,
            test_output=test_res.stdout or test_res.stderr,
            lint_output=lint_output,
            type_output=type_output
        )
