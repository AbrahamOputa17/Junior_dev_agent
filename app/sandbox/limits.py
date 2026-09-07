DEFAULT_EXECUTION_TIMEOUT_SECONDS = 30
MAX_OUTPUT_CHARACTERS = 100_000
ALLOWED_COMMAND_PREFIXES = [
    "pytest",
    "python -m pytest",
    "python",
    "npm test",
    "npm run",
    "flake8",
    "ruff",
    "eslint",
    "mypy",
    "tsc",
    "git diff",
    "git status",
    "git log",
]

SENSITIVE_ENV_KEYS = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
    "GITHUB_TOKEN",
    "DATABASE_URL",
    "SECRET_KEY",
}
