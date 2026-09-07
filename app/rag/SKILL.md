# Code RAG & Retrieval Subsystem (`app/rag/`)

The `app/rag/` package implements Code RAG (Retrieval-Augmented Generation for Code) to extract pinpointed, relevant code context for LLM prompt construction without dumping entire repository files into context.

## Subsystem Responsibilities

1. **User Query Analyzer**: Analyzes user intent, target entities, and keywords from bug reports or requests (e.g. "Where is password reset email generated?").
2. **Relevant Code Retriever**: Performs hybrid search (Vector similarity + Keyword match + AST symbol lookup) to retrieve:
   - Target files & specific function chunks
   - Related template files or schemas
   - Dependency context (imported modules & caller functions)
3. **Targeted Context Builder**: Combines retrieved code chunks, dependency context, and project memory into a compact, structured prompt context window.

## Key Files

- `query_analyzer.py`: Intent and entity extractor.
- `retriever.py`: Multi-strategy retriever query builder.
- `context_builder.py`: Context window packager and prompt formatter.

## Extension Guidelines

- Context limits are enforced via `ContextBuilder(max_tokens=4096)`. Always prioritize high-relevance function signatures and direct call dependencies over full file dumps.
