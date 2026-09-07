from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class InvestigationReportSchema(BaseModel):
    mode: str = "Investigate"
    task: str
    status: str
    root_cause_analysis: str
    relevant_files: List[str]
    test_reproduction: Dict[str, Any]
    proposed_fix_plan: str
    requires_authorization: bool = True

class ProofOfFixReportSchema(BaseModel):
    task: str
    timestamp: str
    verification_status: str
    summary: str
    proof_logs: Dict[str, str]
    diff_summary: str
