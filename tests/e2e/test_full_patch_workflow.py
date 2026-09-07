import os
import pytest
from app.core.agent import JuniorDevAgent
from app.verifier.runner import VerificationRunner

DEMO_REPO = os.path.abspath("demo_repo/auth_app")

def test_implement_mode_fail_closed_without_patch():
    """Verify Implement mode fails closed when user_approved=True but no patch or LLM is available."""
    agent = JuniorDevAgent(DEMO_REPO)
    res = agent.run_task(
        mode="implement",
        task_prompt="Fix session handling bug",
        user_approved=True,
        target_file=None,
        patch_content=None
    )
    assert res["status"] == "failed_closed"
    assert "No patch_content provided" in res["error"]

def test_verifier_project_manifest_autodetect():
    """Verify VerificationRunner auto-detects test runner command for Python project."""
    runner = VerificationRunner(DEMO_REPO)
    cmd = runner.detect_test_command()
    assert cmd == "pytest"

def test_full_patch_application_and_verification():
    """Verify full authorized patch application and self-verification pipeline."""
    agent = JuniorDevAgent(DEMO_REPO)
    patch_code = "# Auth App - Tested Fix\ndef check_session():\n    return {'valid': True}"
    res = agent.run_task(
        mode="implement",
        task_prompt="Verify session status",
        user_approved=True,
        target_file="app/auth.py",
        patch_content=patch_code
    )
    assert res["step"] == "7_completed"
    assert "proof_of_fix" in res
    assert res["apply_status"]["status"] == "applied"
