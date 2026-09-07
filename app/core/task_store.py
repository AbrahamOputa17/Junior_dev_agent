import os
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

@dataclass
class TaskRunRecord:
    run_id: str
    mode: str
    task_prompt: str
    status: str
    created_at: float
    updated_at: float
    target_file: Optional[str] = None
    approval_granted: bool = False
    verification_passed: bool = False
    logs: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d["logs"] is None:
            d["logs"] = []
        return d

class TaskRunStore:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)
        self.runs_dir = os.path.join(self.repo_root, ".junior_dev", "runs")
        self.runs_file = os.path.join(self.runs_dir, "runs.json")

    def _ensure_dir(self):
        os.makedirs(self.runs_dir, exist_ok=True)

    def _load_all(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.runs_file):
            return {}
        try:
            with open(self.runs_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_all(self, runs: Dict[str, Dict[str, Any]]):
        self._ensure_dir()
        with open(self.runs_file, "w", encoding="utf-8") as f:
            json.dump(runs, f, indent=2)

    def create_run(self, mode: str, task_prompt: str, target_file: Optional[str] = None) -> TaskRunRecord:
        now = time.time()
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        record = TaskRunRecord(
            run_id=run_id,
            mode=mode,
            task_prompt=task_prompt,
            status="INITIALIZED",
            created_at=now,
            updated_at=now,
            target_file=target_file,
            logs=[f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task initialized."]
        )
        all_runs = self._load_all()
        all_runs[run_id] = record.to_dict()
        self._save_all(all_runs)
        return record

    def update_run_status(self, run_id: str, status: str, log_message: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        all_runs = self._load_all()
        if run_id not in all_runs:
            return None

        record = all_runs[run_id]
        record["status"] = status
        record["updated_at"] = time.time()
        if log_message:
            if "logs" not in record or record["logs"] is None:
                record["logs"] = []
            record["logs"].append(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {log_message}")

        for k, v in kwargs.items():
            record[k] = v

        all_runs[run_id] = record
        self._save_all(all_runs)
        return record

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._load_all().get(run_id)

    def list_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_runs = list(self._load_all().values())
        all_runs.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return all_runs[:limit]
