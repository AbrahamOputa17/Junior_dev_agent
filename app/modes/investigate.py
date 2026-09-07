import os
import json
from typing import Dict, Any, List, Optional
from app.modes.base import BaseAgentMode
from app.llm.client import chat_completion, is_llm_available
from app.llm.prompts import (
    investigate_prompts,
    debug_prompts,
    review_prompts,
    test_prompts,
)
try:
    from openai import OpenAIError
except ImportError:
    OpenAIError = Exception  # type: ignore


def _parse_llm_json(raw: str) -> Dict[str, Any]:
    """Strips markdown code fences and parses JSON from LLM output."""
    text = raw.strip()
    if text.startswith("```"):
        # Remove ```json ... ``` fences
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Return raw text under a key so callers always get a dict
        return {"raw_response": raw, "parse_error": "LLM did not return valid JSON."}


class InvestigateMode(BaseAgentMode):
    def __init__(self, repo_root: str):
        super().__init__(repo_root, "Investigate")

    def execute(
        self,
        task_prompt: str,
        user_approved: bool = False,
        patch_content: Optional[str] = None,
        target_file: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        memory_profile = self.memory.load_memory()
        context = self.context_builder.build_prompt_context(task_prompt, memory_profile)

        # Gather diagnostic tool data
        search_res = self.tools.execute_tool("search_code", query=task_prompt)
        files_found = list(set(m["file"] for m in search_res.get("matches", [])))[:5]
        test_res = self.tools.execute_tool("run_test")
        test_output = test_res.get("output", "")

        if is_llm_available():
            try:
                system, user = investigate_prompts(task_prompt, context, test_output, files_found)
                raw = chat_completion(system, user)
                llm_data = _parse_llm_json(raw)
            except OpenAIError as e:
                err_type = type(e).__name__
                if "RateLimit" in err_type or "429" in str(e):
                    msg = "OpenAI API rate limit or billing quota exceeded. Please check your account credits at platform.openai.com."
                else:
                    msg = f"LLM API error ({err_type}): {str(e)[:200]}"
                llm_data = {
                    "observations": msg,
                    "recommendations": [
                        "Verify your OPENAI_API_KEY in .env",
                        "Check your available credit balance at https://platform.openai.com/account/billing"
                    ],
                    "relevant_files": files_found or ["(no matches found)"],
                }
        else:
            llm_data = {
                "observations": "LLM reasoning engine is currently unavailable because OPENAI_API_KEY is not configured in .env.",
                "recommendations": [
                    "Add OPENAI_API_KEY to your .env file",
                    "Restart the FastAPI application server"
                ],
                "relevant_files": files_found or ["(no matches found)"],
            }

        return {
            "mode": self.mode_name,
            "task": task_prompt,
            "status": "investigation_completed",
            "llm_powered": is_llm_available(),
            **llm_data,
            "rag_context_preview": context[:500],
        }


class DebugMode(BaseAgentMode):
    def __init__(self, repo_root: str):
        super().__init__(repo_root, "Debug")

    def execute(
        self,
        task_prompt: str,
        user_approved: bool = False,
        patch_content: Optional[str] = None,
        target_file: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        memory_profile = self.memory.load_memory()
        context = self.context_builder.build_prompt_context(task_prompt, memory_profile)

        if is_llm_available():
            try:
                system, user = debug_prompts(task_prompt, context)
                raw = chat_completion(system, user)
                llm_data = _parse_llm_json(raw)
            except OpenAIError as e:
                err_type = type(e).__name__
                msg = "OpenAI API rate limit or billing quota exceeded." if ("RateLimit" in err_type or "429" in str(e)) else f"LLM API error ({err_type})"
                llm_data = {
                    "observations": msg,
                    "recommendations": ["Check OPENAI_API_KEY credit balance at platform.openai.com"]
                }
        else:
            llm_data = {
                "observations": "LLM unavailable — OPENAI_API_KEY not set.",
                "recommendations": ["Configure OPENAI_API_KEY in .env file"]
            }

        return {
            "mode": self.mode_name,
            "task": task_prompt,
            "status": "debug_completed",
            "llm_powered": is_llm_available(),
            **llm_data,
        }


class ReviewMode(BaseAgentMode):
    def __init__(self, repo_root: str):
        super().__init__(repo_root, "Review")

    def execute(
        self,
        task_prompt: str,
        user_approved: bool = False,
        patch_content: Optional[str] = None,
        target_file: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        memory_profile = self.memory.load_memory()
        context = self.context_builder.build_prompt_context(task_prompt, memory_profile)
        diff_res = self.tools.execute_tool("git_diff")
        diff = diff_res.get("diff", "")

        if is_llm_available():
            try:
                system, user = review_prompts(task_prompt, context, diff)
                raw = chat_completion(system, user)
                llm_data = _parse_llm_json(raw)
            except OpenAIError as e:
                err_type = type(e).__name__
                msg = "OpenAI API rate limit or billing quota exceeded." if ("RateLimit" in err_type or "429" in str(e)) else f"LLM API error ({err_type})"
                llm_data = {
                    "observations": msg,
                    "recommendations": ["Check OPENAI_API_KEY credit balance at platform.openai.com"]
                }
        else:
            llm_data = {
                "observations": "LLM unavailable — OPENAI_API_KEY not set.",
                "recommendations": ["Configure OPENAI_API_KEY in .env file"]
            }

        return {
            "mode": self.mode_name,
            "task": task_prompt,
            "status": "review_completed",
            "llm_powered": is_llm_available(),
            "diff": diff,
            **llm_data,
        }


class TestMode(BaseAgentMode):
    def __init__(self, repo_root: str):
        super().__init__(repo_root, "Test")

    def execute(
        self,
        task_prompt: str,
        user_approved: bool = False,
        patch_content: Optional[str] = None,
        target_file: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        memory_profile = self.memory.load_memory()
        context = self.context_builder.build_prompt_context(task_prompt, memory_profile)

        if is_llm_available():
            try:
                system, user = test_prompts(task_prompt, context)
                raw = chat_completion(system, user)
                llm_data = _parse_llm_json(raw)
            except OpenAIError as e:
                err_type = type(e).__name__
                msg = "OpenAI API rate limit or billing quota exceeded." if ("RateLimit" in err_type or "429" in str(e)) else f"LLM API error ({err_type})"
                llm_data = {
                    "observations": msg,
                    "recommendations": ["Check OPENAI_API_KEY credit balance at platform.openai.com"]
                }
        else:
            llm_data = {
                "observations": "LLM unavailable — OPENAI_API_KEY not set.",
                "recommendations": ["Configure OPENAI_API_KEY in .env file"]
            }

        return {
            "mode": self.mode_name,
            "task": task_prompt,
            "status": "test_generation_ready",
            "llm_powered": is_llm_available(),
            **llm_data,
        }

        return {
            "mode": self.mode_name,
            "task": task_prompt,
            "status": "test_generation_ready",
            "llm_powered": is_llm_available(),
            **llm_data,
        }
