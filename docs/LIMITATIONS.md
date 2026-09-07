# Known Limitations

This document records the current limitations of Junior Dev Agent. It is intentionally honest and incomplete by design: the project is a prototype, and community review is welcome.

Please read this document before running the agent against a real repository. The agent can inspect files, call an LLM, execute commands, and apply changes. Those capabilities should not be treated as a security boundary or as a replacement for human review.

## Status

- **Project stage:** early prototype
- **Version:** `0.1.0`
- **Last reviewed:** 2026-09-07
- **Expected behavior:** features may be incomplete, experimental, or demo-oriented

## Security And Safety

These are the highest-priority limitations because they can affect the safety of a repository or host system.

### The subprocess runner is not a true sandbox

The local subprocess implementation runs commands on the host. It now passes commands as argument vectors with `shell=False`, sets a working directory, limits execution time, and truncates output, but it does not provide operating-system isolation or prevent access to the host outside the repository.

The Docker implementation is safer only when Docker is available. When Docker is unavailable, it silently falls back to the same host subprocess implementation. Even with Docker enabled, the repository is mounted into the container and the container configuration is intentionally minimal.

### Shell command construction is fragile

The Docker command is assembled as a shell string and embeds the repository path and requested command. Paths or commands containing shell-sensitive characters may break quoting or create command-injection risk.

### Path validation is incomplete

Repository path checks use string-prefix comparisons. They do not robustly handle every path-boundary case, symbolic links, junctions, or filesystem race conditions. A path that appears to be inside a repository should not be assumed to be securely confined.

### The API has no authentication or authorization

The FastAPI server exposes repository indexing, cloning, task execution, and patch application without user authentication, roles, rate limits, CSRF protection, or an authorization service. It should not be exposed directly to an untrusted network.

### CORS is fully permissive

The API allows all origins, methods, and headers. This is convenient for local development but is not an appropriate production configuration.

### Clone and execution endpoints can consume resources

Repository cloning and task execution are synchronous. There are no quotas for repository size, number of files, disk usage, CPU usage, concurrent requests, or total request duration. A user can also request arbitrary public GitHub repositories, subject to the basic URL check.

### Secrets and sensitive source code need stronger handling

The system has pattern-based secret scanning and redaction, but it is not comprehensive and can miss non-standard or encoded secrets. Retrieved source context and task information may still be sent to the configured LLM provider. There is no data-classification policy, tenant isolation, or audit trail for what leaves the local machine.

## Agent Behavior

### Implement mode requires a patch source

When patch generation cannot use the LLM, Implement mode fails closed unless the caller supplies patch content. A supplied patch can still replace the selected target file with unrelated content if used without careful review.

### The approval gate is not a complete authorization system

Approval is represented by a boolean supplied to the process or API request. There is no durable approval record, identity binding, expiration, second-person review, signed patch, or protection against replay.

### The agent does not reliably produce minimal patches

LLM patch generation asks for complete fixed file content. It can therefore rewrite unrelated parts of a file, lose formatting, or make changes that are broader than the requested task.

### LLM output is only lightly validated

Responses are parsed as JSON after a simple code-fence removal step. There is no schema validation for every response, semantic validation of proposed changes, or independent check that an LLM-selected target file matches the approved target.

### LLM failures are only partially handled

The code reports common API errors, but there is no general retry policy, exponential backoff, circuit breaker, provider fallback, request cancellation, or robust handling for malformed, partial, or unexpectedly large responses.

### Debug, review, and test modes are mostly report-generation modes

These modes use the LLM to produce observations or recommendations. Test mode reports that test generation is ready; it does not consistently create or apply test files. Review mode does not provide a deterministic static-analysis review, and Debug mode does not attach to a running process or debugger.

### The agent has no reliable task state or resume protocol

Long-running work, approval requests, failed patches, and verification results are returned in individual requests. There is no durable job queue, resumable workflow, cancellation model, or persistent run history.

## Repository Understanding

### Search is keyword-based, not semantic

The repository index is stored as JSON and searches lower-cased terms with simple substring scoring. The indexing module is named around embeddings, but the current retrieval path does not provide vector embeddings or a vector database.

### Index freshness is not managed

There is no incremental indexing, file watcher, content hash validation, locking, or automatic invalidation after edits. A stale `.junior_dev/index.json` can be used until the repository is indexed again.

### Parsing and file support are limited

The parser is not a complete multi-language code intelligence system. Parse failures are skipped broadly, which can make the resulting context incomplete without clearly reporting every omitted file or reason.

### Context can be incomplete or poorly ranked

Retrieval is limited to a small number of chunks and prompt context is truncated in some responses. There is no symbol graph, call graph, dependency graph, cross-file reasoning guarantee, or evaluation suite for retrieval quality.

### Generated index and memory files are written into target repositories

The agent creates `.junior_dev` inside the target repository. There is no built-in cleanup, retention policy, migration system, concurrent-write protection, or documented guarantee that this directory is ignored by Git.

## Verification And Correctness

### Verification has limited project awareness

Verification runs inside the configured sandbox and detects only a small set of manifest-based commands (`npm test`, `cargo test`, `go test ./...`, or `pytest`). It does not install dependencies, select the correct environment, or understand project-specific test commands beyond those defaults.

### Linting and type checking are opt-in

The verification runner marks lint and type checks as passed when no commands are supplied. A successful proof report therefore does not necessarily mean that linting or static typing passed.

### Passing tests do not prove the requested fix

The verifier checks command exit codes and captures output. It does not compare behavior against a generated regression test, measure coverage, inspect the final diff for scope, or independently confirm that the original defect was addressed.

### Verification output is bounded and may lose important evidence

Sandbox output is truncated to a fixed character limit. Long test failures, compiler diagnostics, and logs can be cut off.

### Rollback is optional and Git-dependent

If a patch is applied and verification fails, the caller must opt in to rollback. The available rollback uses `git checkout -- .`, requires a Git working tree, can discard unrelated tracked changes, and does not restore untracked files or provide a durable checkpoint.

### Windows subprocess output encoding is not fully controlled

Subprocess output is decoded using the platform's default text encoding. Commands that emit bytes invalid for that encoding can produce decoding warnings or incomplete captured output, especially on Windows.

## Memory And Configuration

### Project memory starts with hard-coded example assumptions

The default memory claims technologies and conventions such as React, PostgreSQL, Redis, JWT authentication, and dependency injection even when the target repository may use none of them. This can introduce misleading context into future prompts.

### Memory has no provenance or conflict resolution

Stored conventions and decisions are plain JSON. There is no source reference, timestamped history, confidence level, schema migration, locking, or mechanism for resolving stale or contradictory facts.

### Configuration validation is limited

Environment variables, model settings, repository paths, and external tool availability are not validated comprehensively at startup. Missing or invalid configuration is often discovered only when a task runs.

## API And Product Gaps

- No production deployment configuration, observability, metrics, tracing, or structured audit logs.
- No multi-user isolation or tenant model.
- No persistent database for projects, runs, approvals, or findings.
- No streaming progress updates for indexing, LLM calls, patching, or verification.
- No standard error schema shared consistently by all endpoints.
- No documented API versioning or compatibility policy.
- No background worker for slow operations; requests can remain open while cloning, indexing, or testing runs.
- The dashboard is a local prototype and is not a complete production user interface.

## Testing And Documentation Gaps

- The test suite covers core happy paths but has limited coverage for failure, concurrency, security, and platform-specific behavior.
- Security tests cover basic path traversal, external paths, secret redaction, and argument-vector execution, but coverage is still incomplete for symlinks, shell metacharacters, oversized repositories, malformed LLM output, and Docker failures.
- End-to-end coverage includes the approved patch workflow for the demo Python repository, but not multiple repository types or failure paths.
- There are no benchmarks or quality evaluations for retrieval, plan quality, patch quality, or false-positive findings.
- Setup, deployment, threat model, supported platforms, and contribution workflows need more documentation.

## Contributions Welcome

Useful improvements include:

- replacing host subprocess execution with a clearly documented, enforced isolation model;
- adding authentication, authorization, rate limits, and safe CORS configuration;
- hardening path and shell handling, including symlink and Windows junction tests;
- expanding fail-closed behavior tests to cover malformed, partial, and unexpected patch inputs;
- adding schema validation and safer patch application;
- implementing real semantic retrieval and index invalidation;
- making verification project-aware, transactional, and reproducible;
- removing inaccurate default memory assumptions;
- adding failure-focused, security-focused, and cross-platform tests;
- improving the documentation, threat model, and operational guidance.

When opening an issue or pull request, please describe the limitation, the risk or user impact, a reproducible example, the proposed design, and the tests that demonstrate the change.

## Disclaimer

This software is experimental. Review every proposed change, inspect the complete diff, run tests in an environment appropriate for the repository, and do not grant it access to sensitive code or production systems without adding the security controls your use case requires.