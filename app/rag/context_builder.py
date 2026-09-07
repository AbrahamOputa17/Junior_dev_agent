import os
from typing import Dict, Any, List
from app.indexer.embeddings import RepositoryIndex, CodeChunk
from app.rag.query_analyzer import QueryAnalyzer

class CodeRAGRetriever:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.indexer = RepositoryIndex(repo_root)
        self.analyzer = QueryAnalyzer()

    def retrieve_context(self, query: str, max_chunks: int = 5) -> Dict[str, Any]:
        analysis = self.analyzer.analyze(query)
        chunks = self.indexer.search_chunks(query, top_k=max_chunks)

        retrieved_files = list(set(chunk.file_path for chunk in chunks))
        
        return {
            "query_analysis": {
                "raw_query": analysis.raw_query,
                "intent": analysis.intent,
                "target_entities": analysis.target_entities
            },
            "retrieved_files": retrieved_files,
            "chunks": [chunk.__dict__ for chunk in chunks]
        }

class ContextBuilder:
    def __init__(self, repo_root: str):
        self.retriever = CodeRAGRetriever(repo_root)

    def build_prompt_context(self, query: str, memory_profile: Dict[str, Any] = None) -> str:
        rag_data = self.retriever.retrieve_context(query)
        
        context_parts = []
        context_parts.append("=== CODE RAG RETRIEVED CONTEXT ===")
        context_parts.append(f"User Query: {query}")
        context_parts.append(f"Query Intent: {rag_data['query_analysis']['intent']}")
        
        if memory_profile:
            context_parts.append("\n--- PROJECT MEMORY & CONVENTIONS ---")
            context_parts.append(f"Tech Stack: {memory_profile.get('tech_stack', {})}")
            context_parts.append(f"Conventions: {memory_profile.get('conventions', [])}")

        context_parts.append("\n--- RELEVANT CODE CHUNKS ---")
        for chunk in rag_data["chunks"]:
            context_parts.append(
                f"\nFile: {chunk['file_path']} ({chunk['chunk_type']}: {chunk['name']}) [Lines {chunk['start_line']}-{chunk['end_line']}]"
            )
            context_parts.append("```")
            context_parts.append(chunk["content"])
            context_parts.append("```")

        return "\n".join(context_parts)
