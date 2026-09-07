import json
import os
import hashlib
from typing import Dict, Any, List
from app.indexer.scanner import RepoScanner
from app.indexer.parser import CodeParser, CodeChunk
from app.guardrails.secret_scanner import scan_and_redact_secrets

class RepositoryIndex:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)
        self.index_dir = os.path.join(self.repo_root, ".junior_dev")
        self.index_file = os.path.join(self.index_dir, "index.json")
        self.scanner = RepoScanner(self.repo_root)
        self.parser = CodeParser()
        self.chunks: List[CodeChunk] = []
        self._ensure_gitignore()

    def _ensure_gitignore(self):
        """Ensures .junior_dev directory is ignored in .gitignore."""
        gitignore_path = os.path.join(self.repo_root, ".gitignore")
        if os.path.exists(self.repo_root):
            entry = ".junior_dev/\n"
            if os.path.isfile(gitignore_path):
                with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if ".junior_dev" not in content:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write(f"\n# Junior Dev Agent internal directory\n{entry}")
            else:
                try:
                    with open(gitignore_path, "w", encoding="utf-8") as f:
                        f.write(f"# Junior Dev Agent internal directory\n{entry}")
                except Exception:
                    pass

    def build_index(self) -> Dict[str, Any]:
        """
        Scans repository, performs incremental re-indexing based on SHA256 hashes,
        extracts AST symbol graphs, redacts secrets, and updates index.json.
        """
        os.makedirs(self.index_dir, exist_ok=True)
        files = self.scanner.scan_repository()

        # Load existing index data for incremental comparison
        existing_hashes = {}
        existing_chunks_by_file = {}
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    existing_hashes = old_data.get("file_hashes", {})
                    for raw_chunk in old_data.get("chunks", []):
                        fp = raw_chunk.get("file_path")
                        if fp not in existing_chunks_by_file:
                            existing_chunks_by_file[fp] = []
                        existing_chunks_by_file[fp].append(CodeChunk(**raw_chunk))
            except Exception:
                pass

        all_chunks = []
        file_hashes = {}
        symbol_table = {}
        reparsed_count = 0

        for rel_path in files:
            abs_path = os.path.join(self.repo_root, rel_path)
            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    raw_content = f.read()

                current_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
                file_hashes[rel_path] = current_hash

                # Incremental Check: Reuse existing chunks if hash unchanged
                if rel_path in existing_hashes and existing_hashes[rel_path] == current_hash and rel_path in existing_chunks_by_file:
                    file_chunks = existing_chunks_by_file[rel_path]
                else:
                    sanitized_content = scan_and_redact_secrets(raw_content)
                    file_chunks = self.parser.parse_file(self.repo_root, rel_path, sanitized_content)
                    reparsed_count += 1

                all_chunks.extend(file_chunks)

                # Populate AST symbol table
                for chunk in file_chunks:
                    if chunk.name and chunk.name != rel_path:
                        if chunk.name not in symbol_table:
                            symbol_table[chunk.name] = []
                        symbol_table[chunk.name].append({
                            "file_path": chunk.file_path,
                            "chunk_type": chunk.chunk_type,
                            "start_line": chunk.start_line,
                            "end_line": chunk.end_line
                        })

            except Exception:
                continue

        self.chunks = all_chunks

        # Save index file
        serialized = [chunk.__dict__ for chunk in all_chunks]
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump({
                "total_files": len(files),
                "total_chunks": len(all_chunks),
                "reparsed_files": reparsed_count,
                "file_hashes": file_hashes,
                "symbol_table": symbol_table,
                "chunks": serialized
            }, f, indent=2)

        return {
            "total_files": len(files),
            "total_chunks": len(all_chunks),
            "reparsed_files": reparsed_count,
            "unique_symbols": len(symbol_table),
            "status": "indexed"
        }

    def search_chunks(self, query: str, top_k: int = 5) -> List[CodeChunk]:
        """
        Performs hybrid keyword, symbol graph, and term-frequency chunk searching.
        """
        if not self.chunks and os.path.exists(self.index_file):
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = [CodeChunk(**item) for item in data.get("chunks", [])]

        query_terms = [t for t in query.lower().split() if len(t) > 1]
        scored_chunks = []

        for chunk in self.chunks:
            score = 0.0
            name_lower = chunk.name.lower()
            content_lower = chunk.content.lower()
            path_lower = chunk.file_path.lower()

            for term in query_terms:
                if term in name_lower:
                    score += 5.0  # Exact/substring match in symbol name
                if term in path_lower:
                    score += 2.0  # Match in file path
                if term in content_lower:
                    # Term frequency count in content
                    tf = content_lower.count(term)
                    score += min(tf * 0.5, 3.0)

            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]
