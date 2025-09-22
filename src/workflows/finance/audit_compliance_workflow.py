"""
审计合规工作流模板

基于审计合规数据模型，提供标准的审计合规业务流程
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...models.finance.audit_models import AuditEngine, AuditRule, AuditFinding, AuditStatus, AuditPriority


class AuditComplianceWorkflow(WorkflowTemplate):
    """审计合规工作流"""
    
    def __init__(self):
        super().__init__("审计合规工作流")
        self.audit_engine = AuditEngine()
    
    def define_steps(self) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                name="审计数据收集",
                description="收集审计所需的财务数据",
                execute_func=self._collect_audit_data
            ),
            WorkflowStep(
                name="执行审计规则",
                description="执行预定义的审计规则检查",
                execute_func=self._execute_audit_rules,
                depends_on=["审计数据收集"]
            ),
            WorkflowStep(
                name="生成审计报告",
                description="生成审计发现和合规报告",
                execute_func=self._generate_audit_report,
                depends_on=["执行审计规则"]
            )
        ]
    
    def _collect_audit_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """收集审计数据"""
        audit_data = {
            "transactions": [
                {"id": "T001", "debit": Decimal("10000"), "credit": Decimal("10000")},
                {"id": "T002", "debit": Decimal("5000"), "credit": Decimal("5000")},
                {"id": "T003", "debit": Decimal("0"), "credit": Decimal("0")}  # 异常数据
            ],
            "accounts": [
                {"code": "1001", "balance": Decimal("100000")},
                {"code": "2001", "balance": Decimal("-50000")}
            ]
        }
        
        context.set_data("audit_data", audit_data)
        return {"transactions_count": len(audit_data["transactions"])}
    
    def _execute_audit_rules(self, context: WorkflowContext) -> List[AuditFinding]:
        """执行审计规则"""
        audit_data = context.get_data("audit_data")
        
        # 执行审计引擎检查 (简化版本)
        audit_results = []
        
        # 模拟审计发现
        from ...models.finance.audit_models import AuditFinding
        
        # 检查账户余额合理性
        from datetime import date
        if len(audit_data.get("accounts", [])) > 0:
            audit_results.append(AuditFinding(
                finding_id="AF001",
                rule_id="R001", 
                audit_date=date.today(),
                status=AuditStatus.PENDING,
                priority=AuditPriority.LOW,
                description="科目余额检查",
                affected_records=len(audit_data["accounts"]),
                risk_level="low",
                recommendation="定期复核科目余额"
            ))
        
        # 检查交易记录完整性
        if len(audit_data.get("transactions", [])) > 0:
            audit_results.append(AuditFinding(
                finding_id="AF002",
                rule_id="R002",
                audit_date=date.today(),
                status=AuditStatus.PENDING,
                priority=AuditPriority.MEDIUM,
                description="交易记录完整性检查", 
                affected_records=len(audit_data["transactions"]),
                risk_level="medium",
                recommendation="确保所有交易均有完整记录"
            ))
        
        context.set_data("audit_results", audit_results)
        return audit_results
    
    def _generate_audit_report(self, context: WorkflowContext) -> Dict[str, Any]:
        """生成审计报告"""
        audit_results = context.get_data("audit_results")
        
        high_risk_findings = [f for f in audit_results if f.risk_level == "HIGH"]
        medium_risk_findings = [f for f in audit_results if f.risk_level == "MEDIUM"]
        
        audit_report = {
            "audit_date": datetime.now(),
            "total_findings": len(audit_results),
            "high_risk_count": len(high_risk_findings),
            "medium_risk_count": len(medium_risk_findings),
            "compliance_score": max(0, 100 - len(audit_results) * 10),
            "findings_summary": [
                {
                    "rule_id": finding.rule_id,
                    "risk_level": finding.risk_level,
                    "description": finding.description,
                    "affected_records": finding.affected_records
                }
                for finding in audit_results
            ]
        }
        
        context.set_data("audit_report", audit_report)
        return audit_report
