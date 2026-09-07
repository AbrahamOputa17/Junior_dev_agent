# Guardrails & Security Subsystem (`app/guardrails/`)

The `app/guardrails/` package enforces security policies, execution permission boundaries, and path sandboxing for the Junior Dev Agent.

## Subsystem Responsibilities

1. **Execution Mode Policy**: Enforces `READ_ONLY` vs `WRITE_AUTHORIZED` permissions.
2. **Mutating Tool Interception**: Hard-blocks mutating tool calls (`create_patch`, `apply_patch`) during Phase 1 (`READ_ONLY`) or in un-authorized modes (`Investigate`, `Debug`, `Review`).
3. **Repository Path Sandboxing**: Verifies that all file paths accessed or modified remain strictly within the root directory of the target repository, preventing path traversal attacks (e.g. `../../etc/passwd`).

## Key Files

- `policy.py`: `SecurityPolicyEnforcer` class validating tool calls against current agent execution state.
- `sandbox.py`: Path boundary validator and security assertion helpers.

## Extension Guidelines

- When adding new mutating tools to `app/tools/`, register their names in `SecurityPolicyEnforcer.MUTATING_TOOLS`.
- Never bypass path boundary checks in tool implementations; always pass target paths through `validate_repository_path(repo_root, target_path)`.
