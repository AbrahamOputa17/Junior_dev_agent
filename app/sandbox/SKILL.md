# Sandboxed Code Execution Subsystem (`app/sandbox/`)

The `app/sandbox/` package provides an isolated execution environment for executing unit tests, linters, type checkers, and repository commands without risking host machine integrity.

## Subsystem Responsibilities

1. **Host Isolation**: Isolate command executions from the host OS environment.
2. **Resource & Timeout Bounds**: Apply strict execution timeouts (default 30 seconds) and memory limits to prevent infinite loops or resource exhaustion.
3. **Environment Variable Masking**: Filter out sensitive host environment variables (API keys, SSH tokens, host credentials) from command processes.
4. **Execution Providers**:
   - `DockerSandbox`: Isolated Docker container runner when Docker is available.
   - `SubprocessSandbox`: Restricted subprocess runner with path isolation and env masking fallback.

## Key Files

- `docker_sandbox.py`: Container runner logic.
- `subprocess_sandbox.py`: Restricted subprocess runner with signal timeout handlers.
- `security.py`: Environment variable sanitizer and command policy validator.
- `limits.py`: Resource limits and timeout configuration constants.

## Extension Guidelines

- Custom test frameworks or lint runners must execute via `SandboxRunner.execute(command, cwd)`.
- All output logs must be captured and returned as `SandboxExecutionResult(exit_code, stdout, stderr, execution_time_ms)`.
