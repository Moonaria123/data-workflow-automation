"""Rule registry providing discovery & lifecycle operations."""
from __future__ import annotations
from typing import Dict, Type, List
from .base import FinanceRule


class RuleRegistry:
    _rules: Dict[str, FinanceRule] = {}

    @classmethod
    def register(cls, rule: FinanceRule) -> None:
        if rule.rule_id in cls._rules:
            raise ValueError(f"Rule id already registered: {rule.rule_id}")
        cls._rules[rule.rule_id] = rule

    @classmethod
    def get(cls, rule_id: str) -> FinanceRule:
        return cls._rules[rule_id]

    @classmethod
    def all(cls) -> List[FinanceRule]:
        return list(cls._rules.values())

    @classmethod
    def clear(cls) -> None:
        cls._rules.clear()
