"""Rule executor for batch evaluation."""
from __future__ import annotations
from time import perf_counter
from typing import List, Dict, Any
from .base import RuleContext, RuleResult, FinanceRule


class RuleExecutor:
    def __init__(self, rules: List[FinanceRule]):
        self.rules = rules

    def execute(self, context: RuleContext) -> List[RuleResult]:
        results: List[RuleResult] = []
        for rule in self.rules:
            start = perf_counter()
            res = rule.evaluate(context)
            res.duration_ms = (perf_counter() - start) * 1000.0
            results.append(res)
        return results

    @staticmethod
    def summarize(results: List[RuleResult]) -> Dict[str, Any]:
        total = len(results)
        failed = [r for r in results if not r.passed]
        return {
            "total": total,
            "passed": total - len(failed),
            "failed": len(failed),
            "by_severity": {
                sev: len([r for r in results if r.severity.value == sev])
                for sev in {r.severity.value for r in results}
            },
            "fail_details": [r.to_dict() for r in failed],
        }
