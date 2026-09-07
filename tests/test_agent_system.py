import os
import pytest
from app.guardrails.policy import SecurityPolicyEnforcer, ExecutionMode, PermissionError
from app.guardrails.sandbox import validate_repository_path
from app.sandbox.runner import SandboxRunner
from app.indexer.embeddings import RepositoryIndex
from app.rag.context_builder import ContextBuilder
from app.core.agent import JuniorDevAgent

DEMO_REPO = os.path.abspath("demo_repo/auth_app")


def test_guardrail_path_sandboxing():
    """Verify paths outside repository root raise PermissionError."""
    enforcer = SecurityPolicyEnforcer(DEMO_REPO)
    with pytest.raises(PermissionError):
        enforcer.validate_path("../../../etc/passwd")


def test_guardrail_read_only_policy():
    """Verify mutating tools raise PermissionError in Read-Only mode."""
    enforcer = SecurityPolicyEnforcer(DEMO_REPO, mode=ExecutionMode.INVESTIGATION_READ_ONLY)
    with pytest.raises(PermissionError):
        enforcer.validate_tool_call("apply_patch", "app/auth.py")


def test_repository_indexing():
    """Verify repository indexer scans and parses code chunks."""
    index = RepositoryIndex(DEMO_REPO)
    res = index.build_index()
    assert res["status"] == "indexed"
    assert res["total_files"] > 0
    assert res["total_chunks"] > 0


def test_code_rag_context_building():
    """Verify Code RAG retriever builds prompt context."""
    builder = ContextBuilder(DEMO_REPO)
    context = builder.build_prompt_context("logout refresh dashboard")
    assert "CODE RAG RETRIEVED CONTEXT" in context


def test_agent_investigate_mode():
    """
    Verify Investigate mode returns a well-formed report.
    The mode now uses the LLM when OPENAI_API_KEY is available.
    On rate-limit or API error, it degrades gracefully — so we
    assert mode name and status rather than LLM-specific keys.
    """
    agent = JuniorDevAgent(DEMO_REPO)
    res = agent.run_task(mode="investigate", task_prompt="Users logged out on dashboard refresh")
    assert res["mode"] == "Investigate"
    assert res["status"] == "investigation_completed"
    # requires_authorization may come from LLM JSON or fallback—check either location
    has_auth_flag = (
        res.get("requires_authorization") is True
        or (isinstance(res.get("raw_response"), str) and "requires_authorization" in res.get("raw_response", ""))
    )
    assert has_auth_flag or "llm_powered" in res, (
        f"Expected authorization flag or llm_powered key in response. Got keys: {list(res.keys())}"
    )


def test_agent_implement_mode_authorization_gate():
    """Verify Implement mode pauses for user approval before applying patch."""
    agent = JuniorDevAgent(DEMO_REPO)
    res = agent.run_task(mode="implement", task_prompt="Fix session race condition", user_approved=False)
    assert res["step"] == "3_user_approval_required"
    assert res["authorization_gate"]["status"] == "AWAITING_USER_APPROVAL"


def test_agent_implement_mode_execution_and_verification():
    """Verify Implement mode applies patch and runs self-verification after user approval."""
    agent = JuniorDevAgent(DEMO_REPO)
    patch_code = "# Auth Module - Verified Fix\ndef check_session():\n    return {'valid': True}"
    res = agent.run_task(
        mode="implement",
        task_prompt="Fix session race condition",
        user_approved=True,
        target_file="app/auth.py",
        patch_content=patch_code
    )
    assert res["step"] == "7_completed"
    assert "proof_of_fix" in res


def test_api_server_endpoints():
    """Verify FastAPI server dashboard HTML and API endpoints respond correctly."""
    from fastapi.testclient import TestClient
    from app.api.server import app

    client = TestClient(app)

    # Test dashboard route returns HTML
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "JuniorDev" in res_dash.text
    assert "<!DOCTYPE html>" in res_dash.text

    # Test indexing endpoint
    res_index = client.post("/api/index", json={"repo_path": DEMO_REPO})
    assert res_index.status_code == 200
    assert res_index.json()["status"] == "indexed"

    # Test task execution endpoint
    res_task = client.post(
        "/api/task",
        json={
            "repo_path": DEMO_REPO,
            "mode": "investigate",
            "task_prompt": "Audit auth session handling"
        }
    )
    assert res_task.status_code == 200
    assert res_task.json()["mode"] == "Investigate"

