import os
from enum import Enum
from typing import List, Optional

class ExecutionMode(str, Enum):
    INVESTIGATION_READ_ONLY = "investigate_read_only"
    MODIFICATION_AUTHORIZED = "modification_authorized"

class PermissionError(Exception):
    """Raised when an unauthorized or out-of-bounds tool action is attempted."""
    pass

class SecurityPolicyEnforcer:
    MUTATING_TOOLS = {"create_patch", "apply_patch"}

    def __init__(self, repo_root: str, mode: ExecutionMode = ExecutionMode.INVESTIGATION_READ_ONLY):
        self.repo_root = os.path.abspath(repo_root)
        self.mode = mode
        self.authorized_by_user = False

    def authorize_modifications(self):
        self.mode = ExecutionMode.MODIFICATION_AUTHORIZED
        self.authorized_by_user = True

    def revoke_modifications(self):
        self.mode = ExecutionMode.INVESTIGATION_READ_ONLY
        self.authorized_by_user = False

    def validate_tool_call(self, tool_name: str, target_path: Optional[str] = None):
        """
        Validates if a tool can be called in the current execution mode
        and ensures target paths stay within repository boundaries.
        """
        # Check permission boundary
        if tool_name in self.MUTATING_TOOLS:
            if self.mode != ExecutionMode.MODIFICATION_AUTHORIZED or not self.authorized_by_user:
                raise PermissionError(
                    f"Tool '{tool_name}' requires explicit user authorization. "
                    f"Current execution mode is '{self.mode.value}'. Write actions are blocked."
                )

        # Check path boundary if path provided
        if target_path:
            self.validate_path(target_path)

    def validate_path(self, target_path: str) -> str:
        """
        Ensures target path does not escape the repository root directory.
        """
        abs_target = os.path.abspath(os.path.join(self.repo_root, target_path))
        if not abs_target.startswith(self.repo_root):
            raise PermissionError(
                f"Access denied: Target path '{target_path}' resolves outside "
                f"the repository root '{self.repo_root}'."
            )
        return abs_target
