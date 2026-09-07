import time
from typing import Dict, Any
from app.verifier.runner import VerificationResult

class VerificationFeedback:
    def format_failure_feedback(self, result: VerificationResult) -> str:
        """
        Formats error logs into feedback for agent re-planning loop.
        """
        feedback_parts = ["=== AUTOMATED SELF-VERIFICATION FAILURE FEEDBACK ==="]
        feedback_parts.append("The attempted patch did NOT pass self-verification checks. Analyze failure output below:")
        
        if not result.test_passed:
            feedback_parts.append("\n--- TEST FAILURE OUTPUT ---")
            feedback_parts.append(result.test_output[:2000])
            
        if not result.lint_passed:
            feedback_parts.append("\n--- LINT FAILURE OUTPUT ---")
            feedback_parts.append(result.lint_output[:1000])

        if not result.type_passed:
            feedback_parts.append("\n--- TYPE CHECK FAILURE OUTPUT ---")
            feedback_parts.append(result.type_output[:1000])

        feedback_parts.append("\nAction Required: Revise diagnosis, construct a corrected patch, and verify again.")
        return "\n".join(feedback_parts)

class ProofOfFixGenerator:
    def generate_proof_report(self, task: str, result: VerificationResult, diff_summary: str) -> Dict[str, Any]:
        """
        Generates a Proof of Fix artifact proving the solution works.
        """
        return {
            "task": task,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "verification_status": "PASSED" if result.passed else "FAILED",
            "summary": result.summary,
            "proof_logs": {
                "test_output": result.test_output,
                "lint_output": result.lint_output,
                "type_output": result.type_output
            },
            "diff_summary": diff_summary
        }
