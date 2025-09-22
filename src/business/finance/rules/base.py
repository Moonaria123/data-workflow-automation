"""Finance rule engine base abstractions.

Design aligned with project modular architecture & documentation standards:
- Modular, pluggable rule definitions
- Clear separation of rule metadata, context, execution, result
- Extensible severity & category enums for governance
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, List, Protocol, runtime_checkable
from datetime import datetime


class RuleSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RuleCategory(str, Enum):
    ACCOUNTING = "accounting"
    TAX = "tax"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"
    CONTROL = "control"
    PERFORMANCE = "performance"


@dataclass
class RuleContext:
    """Execution context for rules.

    Holds transactional, master data and configuration required by rules.
    """
    data: Dict[str, Any]
    as_of: datetime = field(default_factory=datetime.utcnow)
    config: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


@dataclass
class RuleResult:
    rule_id: str
    name: str
    passed: bool
    severity: RuleSeverity
    category: RuleCategory
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:  # convenience for reporting
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions,
            "duration_ms": self.duration_ms,
        }


@runtime_checkable
class FinanceRule(Protocol):
    """Protocol for finance rules.

    Concrete rule classes must implement required properties and evaluate().
    """

    rule_id: str
    name: str
    description: str
    category: RuleCategory
    severity: RuleSeverity

    def evaluate(self, context: RuleContext) -> RuleResult:
        ...
