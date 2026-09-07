# Agent Execution Modes Subsystem (`app/modes/`)

The `app/modes/` package defines the 5 operational modes for the Junior Dev Agent and manages mode-specific lifecycle workflows.

## Mode Specs

1. **`InvestigateMode`**: Read-only analysis of issues/bugs. Produces an `InvestigationReport`. Writes are hard-blocked.
2. **`DebugMode`**: Traces exception stack traces and runtime errors to pinpoint root causes. Writes are hard-blocked.
3. **`ReviewMode`**: Performs code and PR reviews evaluating security, performance, and style guidelines. Writes are hard-blocked.
4. **`TestMode`**: Scans codebase for untested functions/routes and generates unit/integration tests.
5. **`ImplementMode`**: Executes code modifications following a strict 7-step pipeline:
   `Plan -> Proposed Changes -> User Approval -> Apply Patch -> Self-Verification Loop -> Review Diff -> Proof of Fix`

## Key Files

- `base.py`: Base abstract class for operational modes.
- `investigate.py`: Investigate mode implementation.
- `debug.py`: Debug mode implementation.
- `review.py`: Review mode implementation.
- `test.py`: Test generation mode implementation.
- `implement.py`: Implement mode handler with Authorization Gate and Self-Verification loop.

## Extension Guidelines

- Custom execution modes must inherit from `BaseAgentMode` in `base.py` and implement `execute(task_prompt, context)`.
