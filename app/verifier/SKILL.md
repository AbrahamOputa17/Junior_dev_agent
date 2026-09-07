# Self-Verification & Agentic Feedback Loop Subsystem (`app/verifier/`)

The `app/verifier/` package enforces proof of fix by running automated verification checks and feeding failure diagnostic outputs back to the agent reasoning engine until all tests pass.

## Verification Protocol

1. **Patch Execution**: Apply candidate code patch in the target repository.
2. **Automated Verification Run**:
   - `run_test`: Executes unit & integration test suite.
   - `run_linter`: Checks syntax and style compliance.
   - `run_type_checker`: Checks static type safety.
3. **Feedback Loop Decision**:
   - **PASS**: Generates a **Proof of Fix** report containing passing logs, diffs, and verification summary.
   - **FAIL**: Captures error output, stack traces, and test failure logs -> feeds them back to the LLM -> drafts corrective patch -> re-runs verification.

## Key Files

- `runner.py`: Verification orchestrator running test/lint/type commands via `SandboxRunner`.
- `feedback.py`: Failure log parser and corrective feedback generator.
- `proof.py`: Proof of Fix artifact compiler.

## Extension Guidelines

- Never allow an agent task in `Implement` mode to complete without calling `VerificationRunner.verify()`.
