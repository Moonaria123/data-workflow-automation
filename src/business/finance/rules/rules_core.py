"""Core financial rules implementations."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any
from datetime import datetime

from .base import FinanceRule, RuleResult, RuleContext, RuleSeverity, RuleCategory


@dataclass
class BaseSimpleRule:
    rule_id: str
    name: str
    description: str
    category: RuleCategory
    severity: RuleSeverity

    def _result(self, passed: bool, message: str, details: Dict[str, Any], suggestions=None) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            name=self.name,
            passed=passed,
            severity=self.severity,
            category=self.category,
            message=message,
            details=details,
            suggestions=suggestions or [],
        )


class BalanceSheetEquationRule(BaseSimpleRule):
    """Assets = Liabilities + Equity basic check."""
    def __init__(self):
        super().__init__(
            rule_id="R-BS-001",
            name="Balance Sheet Equation",
            description="Validate accounting identity Assets = Liabilities + Equity",
            category=RuleCategory.ACCOUNTING,
            severity=RuleSeverity.ERROR,
        )

    def evaluate(self, context: RuleContext) -> RuleResult:
        assets = Decimal(str(context.get("assets_total", 0)))
        liabilities = Decimal(str(context.get("liabilities_total", 0)))
        equity = Decimal(str(context.get("equity_total", 0)))
        passed = assets == liabilities + equity
        diff = assets - (liabilities + equity)
        return self._result(
            passed,
            "Balance sheet equation OK" if passed else "Balance sheet equation mismatch",
            {"assets": assets, "liabilities": liabilities, "equity": equity, "difference": diff},
            [] if passed else ["Investigate retained earnings or classification errors"],
        )


class VATThresholdRule(BaseSimpleRule):
    """Check VAT payable does not exceed expected threshold ratio vs revenue (sanity)."""
    def __init__(self, max_ratio: Decimal = Decimal("0.25")):
        super().__init__(
            rule_id="R-TAX-001",
            name="VAT Threshold",
            description="VAT payable should be below configured revenue ratio threshold",
            category=RuleCategory.TAX,
            severity=RuleSeverity.WARNING,
        )
        self.max_ratio = max_ratio

    def evaluate(self, context: RuleContext) -> RuleResult:
        revenue = Decimal(str(context.get("revenue", 0)))
        vat_payable = Decimal(str(context.get("vat_payable", 0)))
        ratio = (vat_payable / revenue) if revenue else Decimal("0")
        passed = ratio <= self.max_ratio
        return self._result(
            passed,
            "VAT ratio within threshold" if passed else "VAT ratio exceeds threshold",
            {"vat_payable": vat_payable, "revenue": revenue, "ratio": ratio, "threshold": self.max_ratio},
            [] if passed else ["Review tax rate configuration", "Check revenue recognition timing"],
        )


class AgingReceivablesRule(BaseSimpleRule):
    """Flag if overdue receivables exceed allowance percentage."""
    def __init__(self, max_overdue_ratio: Decimal = Decimal("0.40")):
        super().__init__(
            rule_id="R-AR-001",
            name="Receivables Aging Risk",
            description="Overdue receivables should not exceed configured ratio of total",
            category=RuleCategory.ACCOUNTING,
            severity=RuleSeverity.WARNING,
        )
        self.max_overdue_ratio = max_overdue_ratio

    def evaluate(self, context: RuleContext) -> RuleResult:
        total_ar = Decimal(str(context.get("ar_total", 0)))
        overdue_ar = Decimal(str(context.get("ar_overdue", 0)))
        ratio = (overdue_ar / total_ar) if total_ar else Decimal("0")
        passed = ratio <= self.max_overdue_ratio
        return self._result(
            passed,
            "Receivables aging healthy" if passed else "Receivables aging risk high",
            {"overdue": overdue_ar, "total": total_ar, "ratio": ratio, "threshold": self.max_overdue_ratio},
            [] if passed else ["Tighten credit policy", "Accelerate collection process"],
        )


def register_core_rules(registry):
    registry.register(BalanceSheetEquationRule())
    registry.register(VATThresholdRule())
    registry.register(AgingReceivablesRule())
