# Developer Tool Suite Subsystem (`app/tools/`)

The `app/tools/` package defines all developer tools accessible to the LLM agent during investigation, debugging, review, testing, and implementation.

## Tool Inventory

| Tool | Category | Policy Required | Description |
| :--- | :--- | :--- | :--- |
| `search_code` | Read-Only | Safe | Code RAG & regex search across repository index |
| `read_file` | Read-Only | Safe | Reads file contents with line range bounds |
| `list_files` | Read-Only | Safe | Lists files and directory structure |
| `find_references` | Read-Only | Safe | Locates symbol references and call sites via AST graph |
| `search_git_history` | Read-Only | Safe | Inspects git log and commit history |
| `run_test` | Diagnostic | Safe (Sandbox) | Executes unit test suite inside sandbox |
| `run_linter` | Diagnostic | Safe (Sandbox) | Executes linter inside sandbox |
| `run_type_checker` | Diagnostic | Safe (Sandbox) | Executes type checker inside sandbox |
| `git_diff` | Read-Only | Safe | Inspects active git working tree diff |
| `create_patch` | Mutating | Write-Authorized | Drafts unified diff patch for proposed changes |
| `apply_patch` | Mutating | Write-Authorized | Applies patch to repository files |

## Key Files

- `code_search.py`: Ripgrep/regex & AST symbol search handlers.
- `file_ops.py`: File reading and directory listing handlers.
- `git_tools.py`: Git log, blame, and diff handlers.
- `execution_tools.py`: Sandboxed test, lint, and type checker runners.
- `patch_tools.py`: Patch drafting and application handlers.
- `registry.py`: Central tool registry exposing OpenAI/Anthropic/Gemini compatible JSON schemas and binding tools to policy enforcers.

## Extension Guidelines

- Define new tools as Pydantic models in `registry.py`.
- Annotate tools with `@requires_policy(ExecutionMode.READ_ONLY)` or `@requires_policy(ExecutionMode.WRITE_AUTHORIZED)`.
