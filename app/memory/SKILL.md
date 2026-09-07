# Persistent Project Memory Subsystem (`app/memory/`)

The `app/memory/` package maintains persistent project-level memory stored in `.junior_dev/memory.json` inside the target repository.

## Memory Categories

1. **Architecture Profile**: Tech stack components (e.g. FastAPI backend, PostgreSQL database, React frontend, Redis caching).
2. **Coding Conventions**: Engineering standards and guidelines (e.g. "Services use dependency injection", "Tests use pytest", "API errors throw HTTPException").
3. **Decision History**: Historical architectural and design choices (e.g. "Auth handled via JWT", "Redis used for session state").

## Key Files

- `store.py`: Memory JSON persistence manager (`.junior_dev/memory.json`).
- `conventions.py`: Conventions and rules parser.
- `history.py`: Architectural decision recorder.

## Extension Guidelines

- When initializing a new repository workspace, `MemoryStore.initialize_default_memory()` generates a default memory template.
- Every LLM prompt injected by `ContextBuilder` includes the active project memory profile.
