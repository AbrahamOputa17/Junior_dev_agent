"""
app/llm/prompts.py
Structured system & user prompt builders for each Junior Dev Agent mode.
Each builder returns (system_prompt, user_prompt) ready to send to the LLM.
"""
from typing import Dict, Any, Optional


# ---------------------------------------------------------------------------
# Shared system prompt header applied to ALL modes
# ---------------------------------------------------------------------------
_AGENT_IDENTITY = """You are Junior Dev Agent — an autonomous AI Software Engineer embedded inside a code repository.

You operate with strict guardrails:
- PHASE 1 (Read-Only): Investigate, Debug, Review, Test modes. You may NEVER write, delete, or patch files.
- PHASE 2 (Authorized Execution only): Implement mode, post user approval. You propose a unified diff patch.

Your output must be precise, grounded in the retrieved code context, and structured as clean JSON where requested.
Never hallucinate file paths or function names — only reference entities that appear in the provided CODE RAG context.
"""


# ---------------------------------------------------------------------------
# Investigate Mode
# ---------------------------------------------------------------------------
def investigate_prompts(
    task_prompt: str,
    rag_context: str,
    test_output: str,
    relevant_files: list,
) -> tuple[str, str]:
    system = _AGENT_IDENTITY + """
MODE: Investigate (Read-Only)
Your job is to analyze the provided code/issue and produce a clean analysis. Do NOT propose raw code edits yet.

Return a JSON object with these exact keys:
{
  "observations": "<detailed observations about the code structure, behavior, or issue based on the context>",
  "recommendations": ["<recommendation 1>", "<recommendation 2>", ...],
  "relevant_files": ["<file_path>", ...]
}
"""
    user = f"""## Task / User Request
{task_prompt}

## CODE RAG RETRIEVED CONTEXT
{rag_context}

## RELEVANT FILES FOUND
{", ".join(relevant_files) or "None found via search."}

Produce the Investigation JSON with observations and recommendations now.
"""
    return system, user


# ---------------------------------------------------------------------------
# Debug Mode
# ---------------------------------------------------------------------------
def debug_prompts(
    task_prompt: str,
    rag_context: str,
) -> tuple[str, str]:
    system = _AGENT_IDENTITY + """
MODE: Debug (Read-Only)
You are analysing a runtime error, stack trace, or exception log to locate the exact failure site.

Return a JSON object with these exact keys:
{
  "stack_trace_analysis": "<explanation of what the trace means and why it fails>",
  "error_location": "<file_path:LineNumber>",
  "suggested_fix": "<description of the minimal fix — do NOT write code>",
  "requires_authorization": true
}
"""
    user = f"""## Task / Error Description
{task_prompt}

## CODE RAG RETRIEVED CONTEXT
{rag_context}

Produce the Debug Report JSON now.
"""
    return system, user


# ---------------------------------------------------------------------------
# Review Mode
# ---------------------------------------------------------------------------
def review_prompts(
    task_prompt: str,
    rag_context: str,
    diff: str,
) -> tuple[str, str]:
    system = _AGENT_IDENTITY + """
MODE: Review (Read-Only)
You are performing a structured code review assessing security, style, and architectural alignment.

Return a JSON object with these exact keys:
{
  "quality_score": "<X/10>",
  "security_feedback": "<security observations>",
  "style_feedback": "<style / naming convention observations>",
  "architecture_feedback": "<structural / design pattern observations>",
  "conventions_check": "<does it match project conventions from memory?>",
  "suggested_improvements": ["<item>", ...]
}
"""
    user = f"""## Task / Review Request
{task_prompt}

## GIT DIFF (Changes to Review)
{diff or "No active diff. Reviewing the codebase context instead."}

## CODE RAG RETRIEVED CONTEXT
{rag_context}

Produce the Code Review JSON now.
"""
    return system, user


# ---------------------------------------------------------------------------
# Test Mode
# ---------------------------------------------------------------------------
def test_prompts(
    task_prompt: str,
    rag_context: str,
) -> tuple[str, str]:
    system = _AGENT_IDENTITY + """
MODE: Test (Requires Post-Approval to Write)
You are identifying untested functions/routes and generating pytest test cases as Python code.

Return a JSON object with these exact keys:
{
  "untested_routes": ["<endpoint or function>", ...],
  "generated_test_cases": [
    {
      "test_name": "<test_function_name>",
      "description": "<what this test verifies>",
      "code": "<complete pytest function as a Python string>"
    }
  ],
  "requires_authorization": true
}
"""
    user = f"""## Task
{task_prompt}

## CODE RAG RETRIEVED CONTEXT
{rag_context}

Generate the Test Report JSON now.
"""
    return system, user


# ---------------------------------------------------------------------------
# Implement Mode — Planning Phase (Pre-Approval)
# ---------------------------------------------------------------------------
def implement_plan_prompts(
    task_prompt: str,
    rag_context: str,
    target_file: Optional[str],
) -> tuple[str, str]:
    system = _AGENT_IDENTITY + """
MODE: Implement — Planning Phase (Pre-Approval)
You are producing an analysis plan before any code is modified.

Return a JSON object with these exact keys:
{
  "observations": "<detailed observations about the target file/code context>",
  "recommendations": ["<actionable recommendation 1>", "<actionable recommendation 2>", ...],
  "proposed_changes": [
    {
      "file": "<relative_file_path>",
      "change_description": "<what change will be made and why>"
    }
  ]
}
Do NOT include actual code or diffs. Just the observations and recommended changes description.
"""
    user = f"""## Task
{task_prompt}

## TARGET FILE (if specified)
{target_file or "Not specified — infer from context."}

## CODE RAG RETRIEVED CONTEXT
{rag_context}

Produce the Implementation Plan JSON now.
"""
    return system, user


# ---------------------------------------------------------------------------
# Implement Mode — Patch Generation Phase (Post-Approval)
# ---------------------------------------------------------------------------
def implement_patch_prompts(
    task_prompt: str,
    rag_context: str,
    target_file: str,
    current_file_content: str,
) -> tuple[str, str]:
    system = _AGENT_IDENTITY + """
MODE: Implement — Patch Generation Phase (Post-Approval, Authorized)
You are now authorized to write code. Generate a complete fixed version of the target file.

Return a JSON object with these exact keys:
{
  "target_file": "<relative_file_path>",
  "fixed_content": "<the complete, corrected file content as a single string>",
  "change_summary": "<brief explanation of every change made>"
}

Rules:
- fixed_content must be the ENTIRE file, not just a snippet.
- Do not remove existing functionality — only fix the reported issue.
- Preserve existing imports, docstrings, and function signatures unless they are the source of the bug.
"""
    user = f"""## Task
{task_prompt}

## TARGET FILE: {target_file}
### Current Content:
```
{current_file_content}
```

## CODE RAG RETRIEVED CONTEXT
{rag_context}

Generate the Patch JSON now.
"""
    return system, user
