"""Workflow integrating finance rule engine.

Provides unified execution of registered finance rules and summary reporting.
"""
from typing import List, Any
from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...business.finance.rules import RuleRegistry, RuleExecutor, RuleContext as FinRuleContext
from ...business.finance.rules.rules_core import register_core_rules


class FinanceRulesWorkflow(WorkflowTemplate):
    def __init__(self):
        super().__init__("财务规则校验工作流")

    def define_steps(self) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                name="注册核心规则",
                description="加载与注册核心财务规则",
                execute_func=self._register_rules,
            ),
            WorkflowStep(
                name="执行财务规则",
                description="执行所有已注册的财务规则",
                execute_func=self._execute_rules,
                depends_on=["注册核心规则"],
            ),
            WorkflowStep(
                name="生成规则报告",
                description="汇总规则执行结果并生成报告",
                execute_func=self._generate_report,
                depends_on=["执行财务规则"],
            ),
        ]

    # Step impls
    def _register_rules(self, context: WorkflowContext):
        RuleRegistry.clear()
        register_core_rules(RuleRegistry)
        return {"registered_rule_ids": [r.rule_id for r in RuleRegistry.all()]} 

    def _execute_rules(self, context: WorkflowContext):
        fin_context = FinRuleContext(data=context.data)
        executor = RuleExecutor(RuleRegistry.all())
        results = executor.execute(fin_context)
        context.set_data("rule_results", results)
        context.set_data("rule_summary", executor.summarize(results))
        # return lightweight summary
        return context.get_data("rule_summary")

    def _generate_report(self, context: WorkflowContext):
        summary = context.get_data("rule_summary", {})
        results = context.get_data("rule_results", [])
        # build simple report structure
        detailed = [r.to_dict() for r in results]
        report = {
            "summary": summary,
            "results": detailed,
        }
        context.set_data("rule_report", report)
        return report
