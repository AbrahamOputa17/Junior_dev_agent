import os
import pytest
from app.guardrails.policy import SecurityPolicyEnforcer, PermissionError
from app.guardrails.sandbox import validate_repository_path
from app.guardrails.secret_scanner import scan_and_redact_secrets
from app.sandbox.subprocess_sandbox import SubprocessSandbox

DEMO_REPO = os.path.abspath("demo_repo/auth_app")

def test_path_traversal_escapes():
    """Verify relative path traversal attempts raise PermissionError."""
    enforcer = SecurityPolicyEnforcer(DEMO_REPO)
    with pytest.raises(PermissionError):
        enforcer.validate_path("../../etc/passwd")

def test_validate_repository_path_escape():
    """Verify validate_repository_path blocks external absolute paths."""
    with pytest.raises(PermissionError):
        validate_repository_path(DEMO_REPO, "C:\\Windows\\System32\\cmd.exe")

def test_secret_scanner_redaction():
    """Verify secrets and keys are automatically redacted."""
    raw_text = "API_KEY = 'sk-12345678901234567890123456789012'\nAWS_KEY = 'AKIAIOSFODNN7EXAMPLE'"
    redacted = scan_and_redact_secrets(raw_text)
    assert "sk-12345678901234567890123456789012" not in redacted
    assert "[REDACTED_" in redacted

def test_subprocess_argument_vector_execution():
    """Verify SubprocessSandbox executes argument vectors without shell=True."""
    sandbox = SubprocessSandbox(DEMO_REPO)
    res = sandbox.execute(["python", "--version"])
    assert res.exit_code == 0
    assert "Python" in res.stdout or "Python" in res.stderr
