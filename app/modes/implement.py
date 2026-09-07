import os
import json
import time
import hmac
import hashlib
from typing import Dict, Any, Optional
from app.modes.base import BaseAgentMode
from app.verifier.runner import VerificationRunner
from app.verifier.proof import VerificationFeedback, ProofOfFixGenerator
from app.llm.client import chat_completion, is_llm_available
from app.llm.prompts import implement_plan_prompts, implement_patch_prompts
from app.core.task_store import TaskRunStore

try:
    from openai import OpenAIError
except ImportError:
    OpenAIError = Exception  # type: ignore

APPROVAL_SECRET = os.getenv("JUNIOR_DEV_APPROVAL_SECRET", "default_approval_secret_key_123")

def create_approval_record(task_prompt: str, target_file: Optional[str]) -> Dict[str, Any]:
    timestamp = int(time.time())
    expires_at = timestamp + 3600  # 1 hour validity
    payload = f"{task_prompt}:{target_file or ''}:{timestamp}:{expires_at}"
    signature = hmac.new(APPROVAL_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {
        "timestamp": timestamp,
        "expires_at": expires_at,
        "signature": signature,
        "payload": payload
    }

def verify_approval_record(record: Dict[str, Any]) -> bool:
    if not record or "signature" not in record or "payload" not in record:
        return False
    if time.time() > record.get("expires_at", 0):
        return False
    expected = hmac.new(APPROVAL_SECRET.encode(), record["payload"].encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(record["signature"], expected)

def _parse_llm_json(raw: str) -> Dict[str, Any]:
    """Strips markdown code fences and parses JSON from LLM output."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": raw, "parse_error": "LLM did not return valid JSON."}


class ImplementMode(BaseAgentMode):
    def __init__(self, repo_root: str):
        super().__init__(repo_root, "Implement")
        self.verifier = VerificationRunner(repo_root)
        self.feedback = VerificationFeedback()
        self.proof_gen = ProofOfFixGenerator()
        self.run_store = TaskRunStore(repo_root)

    def execute(
        self,
        task_prompt: str,
        user_approved: bool = False,
        patch_content: Optional[str] = None,
        target_file: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        7-Step Implement Pipeline:
        1. Plan     (LLM — Read-Only investigation)
        2. Proposed Changes  (LLM — narrated plan)
        3. User Approval Gate  ← pauses here until user_approved=True
        4. Patch Generation  (LLM — writes fixed file content)
        5. Apply Patch
        6. Self-Verification Loop
        7. Proof of Fix
        """
        memory_profile = self.memory.load_memory()
        context = self.context_builder.build_prompt_context(task_prompt, memory_profile)

        # ── Steps 1 & 2: Plan & Proposed Changes ────────────────────────────
        if not user_approved:
            if is_llm_available():
                try:
                    system, user = implement_plan_prompts(task_prompt, context, target_file)
                    raw = chat_completion(system, user)
                    plan_data = _parse_llm_json(raw)
                except OpenAIError as e:
                    plan_data = {
                        "plan": f"[LLM API error: {type(e).__name__}] {str(e)[:200]}",
                        "proposed_changes": [
                            {
                                "file": target_file or "app/auth.py",
                                "change_description": "Retry when API quota is available.",
                            }
                        ],
                    }
            else:
                self.tools.execute_tool("search_code", query=task_prompt)
                plan_data = {
                    "plan": "LLM unavailable. Static analysis: searched for relevant code chunks.",
                    "proposed_changes": [
                        {
                            "file": target_file or "app/auth.py",
                            "change_description": "Review the auth module for the reported issue.",
                        }
                    ],
                }

            approval_rec = create_approval_record(task_prompt, target_file)
            run = self.run_store.create_run(self.mode_name, task_prompt, target_file)

            return {
                "step": "3_user_approval_required",
                "mode": self.mode_name,
                "task": task_prompt,
                "run_id": run.run_id,
                "llm_powered": is_llm_available(),
                **plan_data,
                "authorization_gate": {
                    "status": "AWAITING_USER_APPROVAL",
                    "message": "Review proposed fix plan and approve execution.",
                    "approval_record": approval_rec,
                },
            }

        # ── Step 3 Approved → Step 4: Patch Generation ───────────────────────
        self.policy.authorize_modifications()

        if patch_content and target_file:
            # User provided explicit patch content — apply it directly
            apply_res = self.tools.execute_tool(
                "apply_patch", file_path=target_file, content=patch_content
            )
        elif is_llm_available() and target_file:
            # LLM generates the patch: read current file, ask LLM to fix it
            llm_patch_applied = False
            try:
                read_res = self.tools.execute_tool("read_file", file_path=target_file)
                current_content = read_res.get("content", "")
                system, user = implement_patch_prompts(
                    task_prompt, context, target_file, current_content
                )
                raw = chat_completion(system, user, max_tokens=4096)
                patch_data = _parse_llm_json(raw)
                fixed_content = patch_data.get("fixed_content", "")
                apply_res = self.tools.execute_tool(
                    "apply_patch",
                    file_path=patch_data.get("target_file", target_file),
                    content=fixed_content,
                )
                apply_res["llm_change_summary"] = patch_data.get("change_summary", "")
                llm_patch_applied = True
            except Exception as e:
                apply_res = {"status": "llm_error", "error": f"{type(e).__name__}: {str(e)[:200]}"}

            if not llm_patch_applied:
                return {
                    "step": "4_patch_generation_failed",
                    "mode": self.mode_name,
                    "task": task_prompt,
                    "status": "failed_closed",
                    "error": apply_res.get("error", "LLM patch generation failed and no manual patch_content was provided.")
                }
        else:
            return {
                "step": "4_patch_generation_failed",
                "mode": self.mode_name,
                "task": task_prompt,
                "status": "failed_closed",
                "error": "No patch_content provided and LLM is unavailable or target_file was not specified."
            }

        # ── Step 5: Self-Verification Loop ───────────────────────────────────
        verify_res = self.verifier.verify(test_cmd="pytest")

        # ── Step 6: Review Diff ──────────────────────────────────────────────
        diff_res = self.tools.execute_tool("git_diff")

        # ── Step 7: Proof of Fix ─────────────────────────────────────────────
        proof_report = self.proof_gen.generate_proof_report(
            task=task_prompt,
            result=verify_res,
            diff_summary=diff_res.get("diff", "Patch applied successfully."),
        )

        return {
            "step": "7_completed",
            "mode": self.mode_name,
            "task": task_prompt,
            "llm_powered": is_llm_available(),
            "apply_status": apply_res,
            "verification_result": verify_res.summary,
            "diff": diff_res.get("diff", ""),
            "proof_of_fix": proof_report,
        }
