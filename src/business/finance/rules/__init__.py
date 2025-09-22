"""Finance rule engine package.

Provides pluggable financial rule evaluation used by workflows (audit, reporting, compliance).
"""
from .base import FinanceRule, RuleContext, RuleResult, RuleSeverity, RuleCategory
from .registry import RuleRegistry
from .executor import RuleExecutor
from typing import Dict, List, Any, Optional, Union
