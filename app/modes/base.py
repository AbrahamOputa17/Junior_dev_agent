from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.guardrails.policy import SecurityPolicyEnforcer, ExecutionMode
from app.tools.registry import ToolRegistry
from app.memory.store import MemoryStore
from app.rag.context_builder import ContextBuilder

class BaseAgentMode(ABC):
    def __init__(self, repo_root: str, mode_name: str):
        self.repo_root = repo_root
        self.mode_name = mode_name
        self.policy = SecurityPolicyEnforcer(repo_root, mode=ExecutionMode.INVESTIGATION_READ_ONLY)
        self.tools = ToolRegistry(repo_root, self.policy)
        self.memory = MemoryStore(repo_root)
        self.context_builder = ContextBuilder(repo_root)

    @abstractmethod
    def execute(self, task_prompt: str, user_approved: bool = False, patch_content: Optional[str] = None, target_file: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Executes mode-specific agent workflow.
        """
        pass
