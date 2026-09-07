from typing import Dict, Any, Callable, List
from app.guardrails.policy import SecurityPolicyEnforcer, ExecutionMode
from app.tools.file_ops import read_file_tool, list_files_tool
from app.tools.code_search import search_code_tool, find_references_tool
from app.tools.git_tools import search_git_history_tool, git_diff_tool
from app.tools.execution_tools import run_test_tool, run_linter_tool, run_type_checker_tool
from app.tools.patch_tools import create_patch_tool, apply_patch_tool

class ToolRegistry:
    def __init__(self, repo_root: str, enforcer: SecurityPolicyEnforcer):
        self.repo_root = repo_root
        self.enforcer = enforcer

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Validates policy enforcer boundary and routes tool call.
        """
        # Validate path if present in kwargs
        target_path = kwargs.get("file_path") or kwargs.get("directory_path") or kwargs.get("path")
        self.enforcer.validate_tool_call(tool_name, target_path)

        if tool_name == "read_file":
            return read_file_tool(self.repo_root, **kwargs)
        elif tool_name == "list_files":
            return list_files_tool(self.repo_root, **kwargs)
        elif tool_name == "search_code":
            return search_code_tool(self.repo_root, **kwargs)
        elif tool_name == "find_references":
            return find_references_tool(self.repo_root, **kwargs)
        elif tool_name == "search_git_history":
            return search_git_history_tool(self.repo_root, **kwargs)
        elif tool_name == "git_diff":
            return git_diff_tool(self.repo_root)
        elif tool_name == "run_test":
            return run_test_tool(self.repo_root, **kwargs)
        elif tool_name == "run_linter":
            return run_linter_tool(self.repo_root, **kwargs)
        elif tool_name == "run_type_checker":
            return run_type_checker_tool(self.repo_root, **kwargs)
        elif tool_name == "create_patch":
            return create_patch_tool(self.repo_root, **kwargs)
        elif tool_name == "apply_patch":
            return apply_patch_tool(self.repo_root, **kwargs)
        else:
            return {"error": f"Unknown tool: '{tool_name}'"}

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns JSON schemas for LLM tool binding.
        """
        return [
            {"name": "search_code", "description": "Search codebase using regex or keywords"},
            {"name": "read_file", "description": "Read file content with line bounds"},
            {"name": "list_files", "description": "List files and directory structure"},
            {"name": "find_references", "description": "Locate symbol references and call sites"},
            {"name": "search_git_history", "description": "Inspect commit logs"},
            {"name": "git_diff", "description": "View uncommitted changes"},
            {"name": "run_test", "description": "Run test suite inside sandbox"},
            {"name": "run_linter", "description": "Run linter inside sandbox"},
            {"name": "run_type_checker", "description": "Run type checker inside sandbox"},
            {"name": "create_patch", "description": "Draft patch file (Requires authorization)"},
            {"name": "apply_patch", "description": "Apply approved patch (Requires authorization)"},
        ]
