"""
资产管理工作流模板

基于资产管理数据模型，提供标准的资产管理业务流程
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...models.finance.asset_models import AssetType


class AssetManagementWorkflow(WorkflowTemplate):
    """资产管理工作流"""
    
    def __init__(self):
        super().__init__("资产管理工作流")
    
    def define_steps(self) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                name="资产信息收集",
                description="收集资产基本信息",
                execute_func=self._collect_asset_info
            ),
            WorkflowStep(
                name="折旧计算",
                description="计算资产折旧",
                execute_func=self._calculate_depreciation,
                depends_on=["资产信息收集"]
            ),
            WorkflowStep(
                name="生成资产报告",
                description="生成资产管理报告",
                execute_func=self._generate_asset_report,
                depends_on=["折旧计算"]
            )
        ]
    
    def _collect_asset_info(self, context: WorkflowContext) -> Dict[str, Any]:
        """收集资产信息"""
        asset_info = {
            "asset_id": "A001",
            "asset_name": "办公设备",
            "asset_type": AssetType.EQUIPMENT,
            "original_cost": Decimal("50000.00"),
            "acquisition_date": date(2023, 1, 1),
            "useful_life": 5,  # 年
            "residual_value": Decimal("5000.00")
        }
        
        context.set_data("asset_info", asset_info)
        return asset_info
    
    def _calculate_depreciation(self, context: WorkflowContext) -> Dict[str, Any]:
        """计算折旧"""
        asset_info = context.get_data("asset_info")
        
        # 直线法折旧
        annual_depreciation = (asset_info["original_cost"] - asset_info["residual_value"]) / asset_info["useful_life"]
        
        depreciation_info = {
            "method": "直线法",
            "annual_depreciation": annual_depreciation,
            "monthly_depreciation": annual_depreciation / 12,
            "accumulated_depreciation": annual_depreciation  # 假设已使用1年
        }
        
        context.set_data("depreciation_info", depreciation_info)
        return depreciation_info
    
    def _generate_asset_report(self, context: WorkflowContext) -> Dict[str, Any]:
        """生成资产报告"""
        asset_info = context.get_data("asset_info")
        depreciation_info = context.get_data("depreciation_info")
        
        net_book_value = asset_info["original_cost"] - depreciation_info["accumulated_depreciation"]
        
        asset_report = {
            "report_date": datetime.now(),
            "asset_summary": {
                "asset_id": asset_info["asset_id"],
                "asset_name": asset_info["asset_name"],
                "original_cost": asset_info["original_cost"],
                "accumulated_depreciation": depreciation_info["accumulated_depreciation"],
                "net_book_value": net_book_value
            },
            "depreciation_schedule": {
                "method": depreciation_info["method"],
                "annual_amount": depreciation_info["annual_depreciation"],
                "remaining_life": asset_info["useful_life"] - 1  # 假设已使用1年
            }
        }
        
        context.set_data("asset_report", asset_report)
        return asset_report
