# Repository Indexing Pipeline Subsystem (`app/indexer/`)

The `app/indexer/` package scans, parses, chunks, and indexes target software repositories across multiple programming languages (Python, JavaScript, TypeScript, Java, Go).

## Subsystem Responsibilities

1. **Multi-Language Repo Scanner**: Walks target directory while respecting `.gitignore` rules.
2. **AST & Structural Parser**: Parses code files into structured AST nodes, extracting:
   - Functions & Methods (signature, docstring, body bounds)
   - Classes & Interfaces (inheritance, methods)
   - Import Statements & External Dependencies
   - API Routes & Endpoints (e.g. FastAPI `@app.get`, Express `app.post`)
3. **Symbol Table & Reference Graph**: Builds a bidirectional call graph mapping definition sites to call sites.
4. **Vector Store & Index Persistence**: Stores code chunk embeddings and metadata in local JSON/SQLite vector index (`.junior_dev/index.json`).

## Key Files

- `scanner.py`: Directory scanner respecting gitignore filters.
- `parser.py`: Multi-language AST parser for structural code extraction.
- `symbol_table.py`: Symbol definition and reference graph builder.
- `embeddings.py`: Semantic embedding generator and vector similarity search engine.

## Extension Guidelines

- To add support for a new language parser, implement a parser class inheriting from `BaseLanguageParser` in `parser.py` and register the extension in `LanguageParserRegistry`.
