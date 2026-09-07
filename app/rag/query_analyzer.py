import re
from dataclasses import dataclass
from typing import List

@dataclass
class QueryAnalysis:
    raw_query: str
    intent: str # bug_fix, feature_request, explain, refactor
    keywords: List[str]
    target_entities: List[str]

class QueryAnalyzer:
    def analyze(self, query: str) -> QueryAnalysis:
        keywords = re.findall(r'\b[a-zA-Z0-9_]{3,}\b', query)
        
        # Simple intent classification
        query_lower = query.lower()
        if any(w in query_lower for w in ["bug", "error", "fail", "logout", "crash", "issue", "fix"]):
            intent = "bug_fix"
        elif any(w in query_lower for w in ["add", "feature", "create", "implement"]):
            intent = "feature_request"
        elif any(w in query_lower for w in ["review", "check", "audit"]):
            intent = "review"
        else:
            intent = "explain"

        target_entities = [k for k in keywords if "_" in k or k[0].isupper()]
        return QueryAnalysis(
            raw_query=query,
            intent=intent,
            keywords=keywords,
            target_entities=target_entities
        )
