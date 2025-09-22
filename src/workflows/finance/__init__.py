"""
财务工作流模板模块

基于完成的8包财务数据模型，提供标准财务业务流程模板：
- 应收应付管理流程
- 成本核算流程
- 财务报表生成流程
- 资产管理流程
- 税务处理流程
- 审计合规流程

所有工作流模板都利用已实现的数据模型类进行业务逻辑处理
"""

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from .ar_ap_workflow import AccountsReceivableWorkflow, AccountsPayableWorkflow
from .cost_accounting_workflow import CostAccountingWorkflow
from .reporting_workflow import FinancialReportingWorkflow
from .asset_management_workflow import AssetManagementWorkflow
from .tax_processing_workflow import TaxProcessingWorkflow
from .audit_compliance_workflow import AuditComplianceWorkflow
from typing import Dict, List, Any, Optional, Union

# 导出所有工作流模板
__all__ = [
    # 基础工作流框架
    'WorkflowTemplate',
    'WorkflowStep',
    'WorkflowContext',

    # 具体业务工作流
    'AccountsReceivableWorkflow',
    'AccountsPayableWorkflow',
    'CostAccountingWorkflow',
    'FinancialReportingWorkflow',
    'AssetManagementWorkflow',
    'TaxProcessingWorkflow',
    'AuditComplianceWorkflow'
]
