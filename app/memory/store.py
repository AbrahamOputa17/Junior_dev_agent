import json
import os
import time
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
        tech_stack = {}
        conventions = []
        decisions = []

        # Detect Python
        if os.path.exists(os.path.join(self.repo_root, "pyproject.toml")) or os.path.exists(os.path.join(self.repo_root, "requirements.txt")):
            tech_stack["language"] = "Python"
            conventions.append("Tests are written using pytest framework")

        # Detect Node / JS / TS
        if os.path.exists(os.path.join(self.repo_root, "package.json")):
            tech_stack["runtime"] = "Node.js"
            if os.path.exists(os.path.join(self.repo_root, "tsconfig.json")):
                tech_stack["language"] = "TypeScript"
            else:
                tech_stack["language"] = "JavaScript"

        # Detect Rust
        if os.path.exists(os.path.join(self.repo_root, "Cargo.toml")):
            tech_stack["language"] = "Rust"

        # Detect Go
        if os.path.exists(os.path.join(self.repo_root, "go.mod")):
            tech_stack["language"] = "Go"

        if not tech_stack:
            tech_stack["detected"] = "General Software Repository"

        default_memory = {
            "project_name": os.path.basename(self.repo_root),
            "tech_stack": tech_stack,
            "conventions": conventions,
            "decisions": decisions
        }
        self.save_memory(default_memory)
        return default_memory

    def add_convention(self, convention: str, source: str = "user_prompt", confidence: float = 1.0):
        memory = self.load_memory()
        now = time.time()
        entry = {
            "fact": convention,
            "source": source,
            "timestamp": now,
            "confidence": confidence
        }
        existing_facts = [c["fact"] if isinstance(c, dict) else c for c in memory.get("conventions", [])]
        if convention not in existing_facts:
            if "conventions" not in memory:
                memory["conventions"] = []
            memory["conventions"].append(entry)
            self.save_memory(memory)

    def add_decision(self, topic: str, decision: str, source: str = "llm_reasoning", confidence: float = 0.9):
        memory = self.load_memory()
        now = time.time()
        entry = {
            "topic": topic,
            "decision": decision,
            "source": source,
            "timestamp": now,
            "confidence": confidence
        }
        if "decisions" not in memory:
            memory["decisions"] = []
        memory["decisions"].append(entry)
        self.save_memory(memory)

    def resolve_conflict(self, topic: str, new_decision: str, source: str = "verifier_feedback"):
        """
        Overwrites outdated decisions on a specific topic with newer evidence.
        """
        memory = self.load_memory()
        decisions = memory.get("decisions", [])
        updated = [d for d in decisions if not (isinstance(d, dict) and d.get("topic") == topic)]
        updated.append({
            "topic": topic,
            "decision": new_decision,
            "source": source,
            "timestamp": time.time(),
            "confidence": 1.0
        })
        memory["decisions"] = updated
        self.save_memory(memory)
