"""
税务处理工作流模板

基于税务管理数据模型，提供标准的税务处理业务流程
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...models.finance.tax_models import TaxEngine, TaxRate, TaxType


class TaxProcessingWorkflow(WorkflowTemplate):
    """税务处理工作流"""
    
    def __init__(self):
        super().__init__("税务处理工作流")
        self.tax_engine = TaxEngine()
    
    def define_steps(self) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                name="税务数据准备",
                description="准备税务计算所需的基础数据",
                execute_func=self._prepare_tax_data
            ),
            WorkflowStep(
                name="增值税计算",
                description="计算增值税应纳税额",
                execute_func=self._calculate_vat_tax,
                depends_on=["税务数据准备"]
            ),
            WorkflowStep(
                name="所得税计算",
                description="计算企业所得税",
                execute_func=self._calculate_income_tax,
                depends_on=["税务数据准备"]
            ),
            WorkflowStep(
                name="税务申报准备",
                description="准备税务申报资料",
                execute_func=self._prepare_tax_filing,
                depends_on=["增值税计算", "所得税计算"]
            )
        ]
    
    def _prepare_tax_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """准备税务数据"""
        tax_data = {
            "sales_revenue": Decimal("1000000.00"),
            "purchase_amount": Decimal("600000.00"),
            "vat_rate": Decimal("0.13"),
            "income_tax_rate": Decimal("0.25"),
            "taxable_income": Decimal("200000.00")
        }
        
        context.set_data("tax_data", tax_data)
        return tax_data
    
    def _calculate_vat_tax(self, context: WorkflowContext) -> Dict[str, Any]:
        """计算增值税"""
        tax_data = context.get_data("tax_data")
        
        output_vat = tax_data["sales_revenue"] * tax_data["vat_rate"]
        input_vat = tax_data["purchase_amount"] * tax_data["vat_rate"]
        vat_payable = output_vat - input_vat
        
        vat_calculation = {
            "output_vat": output_vat,
            "input_vat": input_vat,
            "vat_payable": vat_payable
        }
        
        context.set_data("vat_calculation", vat_calculation)
        return vat_calculation
    
    def _calculate_income_tax(self, context: WorkflowContext) -> Dict[str, Any]:
        """计算所得税"""
        tax_data = context.get_data("tax_data")
        
        income_tax = tax_data["taxable_income"] * tax_data["income_tax_rate"]
        
        income_tax_calculation = {
            "taxable_income": tax_data["taxable_income"],
            "tax_rate": tax_data["income_tax_rate"],
            "income_tax_payable": income_tax
        }
        
        context.set_data("income_tax_calculation", income_tax_calculation)
        return income_tax_calculation
    
    def _prepare_tax_filing(self, context: WorkflowContext) -> Dict[str, Any]:
        """准备税务申报"""
        vat_calculation = context.get_data("vat_calculation")
        income_tax_calculation = context.get_data("income_tax_calculation")
        
        tax_filing = {
            "filing_period": datetime.now().strftime("%Y-%m"),
            "vat_filing": vat_calculation,
            "income_tax_filing": income_tax_calculation,
            "total_tax_payable": vat_calculation["vat_payable"] + income_tax_calculation["income_tax_payable"],
            "filing_deadline": datetime.now().replace(day=15) + timedelta(days=30)
        }
        
        context.set_data("tax_filing", tax_filing)
        return tax_filing
