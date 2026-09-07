import json
import os
from typing import Dict, Any, List

class MemoryStore:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)
        self.memory_dir = os.path.join(self.repo_root, ".junior_dev")
        self.memory_file = os.path.join(self.memory_dir, "memory.json")

    def load_memory(self) -> Dict[str, Any]:
        """
        Loads project memory or initializes defaults.
        """
        if not os.path.exists(self.memory_file):
            return self.initialize_default_memory()

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.initialize_default_memory()

    def save_memory(self, memory_data: Dict[str, Any]):
        """
        Saves updated project memory data.
        """
        os.makedirs(self.memory_dir, exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=2)

    def initialize_default_memory(self) -> Dict[str, Any]:
        default_memory = {
            "project_name": os.path.basename(self.repo_root),
            "tech_stack": {
                "backend": "FastAPI / Python",
                "frontend": "React / TypeScript",
                "database": "PostgreSQL",
                "cache": "Redis"
            },
            "conventions": [
                "Services use dependency injection pattern",
                "Tests are written using pytest framework",
                "API errors throw HTTPException instances",
                "Frontend auth state synced with session API"
            ],
            "decisions": [
                {"topic": "Authentication", "decision": "JWT bearer tokens in HTTP headers"},
                {"topic": "Caching", "decision": "Redis used for session state"}
            ]
        }
        self.save_memory(default_memory)
        return default_memory

    def add_convention(self, convention: str):
        memory = self.load_memory()
        if convention not in memory["conventions"]:
            memory["conventions"].append(convention)
            self.save_memory(memory)

    def add_decision(self, topic: str, decision: str):
        memory = self.load_memory()
        memory["decisions"].append({"topic": topic, "decision": decision})
        self.save_memory(memory)
