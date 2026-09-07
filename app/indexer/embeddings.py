import json
import os
from typing import Dict, Any, List
from app.indexer.scanner import RepoScanner
from app.indexer.parser import CodeParser, CodeChunk

class RepositoryIndex:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)
        self.index_dir = os.path.join(self.repo_root, ".junior_dev")
        self.index_file = os.path.join(self.index_dir, "index.json")
        self.scanner = RepoScanner(self.repo_root)
        self.parser = CodeParser()
        self.chunks: List[CodeChunk] = []

    def build_index(self) -> Dict[str, Any]:
        """
        Scans repository, parses chunks, and builds index.
        """
        os.makedirs(self.index_dir, exist_ok=True)
        files = self.scanner.scan_repository()
        all_chunks = []

        for rel_path in files:
            abs_path = os.path.join(self.repo_root, rel_path)
            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                file_chunks = self.parser.parse_file(self.repo_root, rel_path, content)
                all_chunks.extend(file_chunks)
            except Exception:
                continue

        self.chunks = all_chunks
        
        # Save to index file
        serialized = [chunk.__dict__ for chunk in all_chunks]
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump({"total_files": len(files), "total_chunks": len(all_chunks), "chunks": serialized}, f, indent=2)

        return {
            "total_files": len(files),
            "total_chunks": len(all_chunks),
            "status": "indexed"
        }

    def search_chunks(self, query: str, top_k: int = 5) -> List[CodeChunk]:
        """
        Performs keyword and semantic chunk searching.
        """
        if not self.chunks and os.path.exists(self.index_file):
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = [CodeChunk(**item) for item in data.get("chunks", [])]

        query_terms = set(query.lower().split())
        scored_chunks = []

        for chunk in self.chunks:
            score = 0
            text = (chunk.name + " " + chunk.content + " " + chunk.file_path).lower()
            for term in query_terms:
                if term in text:
                    score += 1
                    if term in chunk.name.lower():
                        score += 3
            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]
