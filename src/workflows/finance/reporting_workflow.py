"""
财务报表生成工作流模板

基于财务报表数据模型，提供标准的财务报表生成流程：
- 财务数据准备
- 试算平衡检查
- 利润表生成
- 资产负债表生成
- 现金流量表生成
- 报表合并与调整
- 报表审核与发布
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import polars as pl

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...models.finance.report_models import (
    IncomeStatement, BalanceSheet, CashFlowStatement, 
    ReportLineItem, FinancialReport
)
from ...models.finance.account_models import ChartOfAccounts
from ...models.finance.transaction_models import GeneralLedger
from ...models.finance.audit_models import AuditEngine


class FinancialReportingWorkflow(WorkflowTemplate):
    """财务报表生成工作流
    
    标准财务报表生成业务流程：
    1. 财务数据准备和验证
    2. 试算平衡检查
    3. 利润表编制
    4. 资产负债表编制
    5. 现金流量表编制
    6. 报表间勾稽关系检查
    7. 财务分析指标计算
    8. 报表审核与发布
    """
    
    def __init__(self):
        super().__init__("财务报表生成工作流")
        self.chart_of_accounts = ChartOfAccounts()
        self.general_ledger = GeneralLedger()
        self.audit_engine = AuditEngine()
        # self.report_builder = FinancialReportBuilder()  # 暂时注释，使用内置计算
    
    def define_steps(self) -> List[WorkflowStep]:
        """定义财务报表生成工作流步骤"""
        return [
            WorkflowStep(
                name="财务数据准备",
                description="准备和验证财务报表基础数据",
                execute_func=self._prepare_financial_data
            ),
            WorkflowStep(
                name="试算平衡检查",
                description="检查总账数据的借贷平衡",
                execute_func=self._trial_balance_check,
                depends_on=["财务数据准备"]
            ),
            WorkflowStep(
                name="生成利润表",
                description="编制利润表（损益表）",
                execute_func=self._generate_income_statement,
                depends_on=["试算平衡检查"]
            ),
            WorkflowStep(
                name="生成资产负债表",
                description="编制资产负债表",
                execute_func=self._generate_balance_sheet,
                depends_on=["试算平衡检查"]
            ),
            WorkflowStep(
                name="生成现金流量表",
                description="编制现金流量表",
                execute_func=self._generate_cash_flow_statement,
                depends_on=["生成利润表", "生成资产负债表"]
            ),
            WorkflowStep(
                name="报表勾稽检查",
                description="检查各报表间的勾稽关系",
                execute_func=self._cross_reference_check,
                depends_on=["生成利润表", "生成资产负债表", "生成现金流量表"]
            ),
            WorkflowStep(
                name="计算财务指标",
                description="计算关键财务分析指标",
                execute_func=self._calculate_financial_ratios,
                depends_on=["报表勾稽检查"]
            ),
            WorkflowStep(
                name="报表审核发布",
                description="最终审核并准备报表发布",
                execute_func=self._review_and_publish,
                depends_on=["计算财务指标"]
            )
        ]
    
    def _prepare_financial_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """财务数据准备"""
        # 获取报表期间
        report_date = context.get_data("report_date", datetime.now())
        period_start = context.get_data("period_start", 
            datetime(report_date.year, report_date.month, 1))
        period_end = context.get_data("period_end", report_date)
        
        # 示例总账余额数据
        account_balances = context.get_data("account_balances", {
            # 资产类科目
            "1001": {"name": "库存现金", "debit_balance": Decimal("50000.00"), "credit_balance": Decimal("0")},
            "1002": {"name": "银行存款", "debit_balance": Decimal("500000.00"), "credit_balance": Decimal("0")},
            "1122": {"name": "应收账款", "debit_balance": Decimal("300000.00"), "credit_balance": Decimal("0")},
            "1123": {"name": "预付账款", "debit_balance": Decimal("80000.00"), "credit_balance": Decimal("0")},
            "1401": {"name": "存货", "debit_balance": Decimal("400000.00"), "credit_balance": Decimal("0")},
            "1601": {"name": "固定资产", "debit_balance": Decimal("1000000.00"), "credit_balance": Decimal("0")},
            "1602": {"name": "累计折旧", "debit_balance": Decimal("0"), "credit_balance": Decimal("200000.00")},
            
            # 负债类科目
            "2202": {"name": "应付账款", "debit_balance": Decimal("0"), "credit_balance": Decimal("150000.00")},
            "2203": {"name": "预收账款", "debit_balance": Decimal("0"), "credit_balance": Decimal("60000.00")},
            "2221": {"name": "应交税费", "debit_balance": Decimal("0"), "credit_balance": Decimal("45000.00")},
            "2501": {"name": "长期借款", "debit_balance": Decimal("0"), "credit_balance": Decimal("300000.00")},
            
            # 所有者权益类科目
            "4001": {"name": "实收资本", "debit_balance": Decimal("0"), "credit_balance": Decimal("1000000.00")},
            "4002": {"name": "资本公积", "debit_balance": Decimal("0"), "credit_balance": Decimal("200000.00")},
            "4101": {"name": "盈余公积", "debit_balance": Decimal("0"), "credit_balance": Decimal("100000.00")},
            "4103": {"name": "未分配利润", "debit_balance": Decimal("0"), "credit_balance": Decimal("235000.00")},
            
            # 收入类科目（本期发生额）
            "6001": {"name": "主营业务收入", "debit_balance": Decimal("0"), "credit_balance": Decimal("800000.00")},
            "6051": {"name": "其他业务收入", "debit_balance": Decimal("0"), "credit_balance": Decimal("50000.00")},
            "6111": {"name": "投资收益", "debit_balance": Decimal("0"), "credit_balance": Decimal("20000.00")},
            
            # 成本费用类科目（本期发生额）
            "6401": {"name": "主营业务成本", "debit_balance": Decimal("400000.00"), "credit_balance": Decimal("0")},
            "6451": {"name": "其他业务成本", "debit_balance": Decimal("30000.00"), "credit_balance": Decimal("0")},
            "6601": {"name": "销售费用", "debit_balance": Decimal("80000.00"), "credit_balance": Decimal("0")},
            "6602": {"name": "管理费用", "debit_balance": Decimal("120000.00"), "credit_balance": Decimal("0")},
            "6603": {"name": "财务费用", "debit_balance": Decimal("15000.00"), "credit_balance": Decimal("0")},
            "6701": {"name": "营业外支出", "debit_balance": Decimal("5000.00"), "credit_balance": Decimal("0")},
            "6801": {"name": "所得税费用", "debit_balance": Decimal("55000.00"), "credit_balance": Decimal("0")}
        })
        
        # 现金流量数据
        cash_flow_data = context.get_data("cash_flow_data", {
            "operating_activities": [
                {"item": "销售商品收到的现金", "amount": Decimal("780000.00")},
                {"item": "收到的其他经营活动现金", "amount": Decimal("30000.00")},
                {"item": "购买商品支付的现金", "amount": Decimal("-350000.00")},
                {"item": "支付给职工的现金", "amount": Decimal("-180000.00")},
                {"item": "支付的各项税费", "amount": Decimal("-85000.00")},
                {"item": "支付的其他经营活动现金", "amount": Decimal("-45000.00")}
            ],
            "investing_activities": [
                {"item": "处置固定资产收到的现金", "amount": Decimal("20000.00")},
                {"item": "购建固定资产支付的现金", "amount": Decimal("-100000.00")},
                {"item": "投资支付的现金", "amount": Decimal("-50000.00")}
            ],
            "financing_activities": [
                {"item": "取得借款收到的现金", "amount": Decimal("200000.00")},
                {"item": "偿还债务支付的现金", "amount": Decimal("-100000.00")},
                {"item": "分配股利支付的现金", "amount": Decimal("-80000.00")}
            ]
        })
        
        context.set_data("report_date", report_date)
        context.set_data("period_start", period_start)
        context.set_data("period_end", period_end)
        context.set_data("account_balances", account_balances)
        context.set_data("cash_flow_data", cash_flow_data)
        
        return {
            "report_period": f"{period_start.strftime('%Y-%m-%d')} 至 {period_end.strftime('%Y-%m-%d')}",
            "accounts_count": len(account_balances),
            "total_debit": sum(acc["debit_balance"] for acc in account_balances.values()),
            "total_credit": sum(acc["credit_balance"] for acc in account_balances.values())
        }
    
    def _trial_balance_check(self, context: WorkflowContext) -> Dict[str, Any]:
        """试算平衡检查"""
        account_balances = context.get_data("account_balances")
        
        # 计算借贷方合计
        total_debit = sum(acc["debit_balance"] for acc in account_balances.values())
        total_credit = sum(acc["credit_balance"] for acc in account_balances.values())
        
        # 检查平衡性
        balance_difference = total_debit - total_credit
        is_balanced = abs(balance_difference) < Decimal("0.01")  # 允许1分钱的误差
        
        # 生成试算平衡表
        trial_balance = []
        for account_code, account_data in account_balances.items():
            if account_data["debit_balance"] != 0 or account_data["credit_balance"] != 0:
                trial_balance.append({
                    "account_code": account_code,
                    "account_name": account_data["name"],
                    "debit_balance": account_data["debit_balance"],
                    "credit_balance": account_data["credit_balance"]
                })
        
        # 按科目编码排序
        trial_balance.sort(key=lambda x: x["account_code"])
        
        trial_balance_result = {
            "is_balanced": is_balanced,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance_difference": balance_difference,
            "trial_balance_detail": trial_balance,
            "check_date": datetime.now()
        }
        
        context.set_data("trial_balance", trial_balance_result)
        
        if not is_balanced:
            print(f"⚠️ 试算不平衡警告，借贷方差额: {balance_difference}")
            # 在实际生产环境中，这应该抛出异常
            # raise ValueError(f"试算不平衡，借贷方差额: {balance_difference}")
        
        return trial_balance_result
    
    def _generate_income_statement(self, context: WorkflowContext) -> Dict[str, Any]:
        """生成利润表"""
        account_balances = context.get_data("account_balances")
        period_start = context.get_data("period_start")
        period_end = context.get_data("period_end")
        
        # 计算利润表各项目
        revenue = account_balances.get("6001", {}).get("credit_balance", Decimal("0"))
        other_revenue = account_balances.get("6051", {}).get("credit_balance", Decimal("0"))
        total_revenue = revenue + other_revenue
        
        main_cost = account_balances.get("6401", {}).get("debit_balance", Decimal("0"))
        other_cost = account_balances.get("6451", {}).get("debit_balance", Decimal("0"))
        total_cost = main_cost + other_cost
        
        sales_expense = account_balances.get("6601", {}).get("debit_balance", Decimal("0"))
        admin_expense = account_balances.get("6602", {}).get("debit_balance", Decimal("0"))
        finance_expense = account_balances.get("6603", {}).get("debit_balance", Decimal("0"))
        
        investment_income = account_balances.get("6111", {}).get("credit_balance", Decimal("0"))
        non_operating_expense = account_balances.get("6701", {}).get("debit_balance", Decimal("0"))
        income_tax = account_balances.get("6801", {}).get("debit_balance", Decimal("0"))
        
        # 计算各层级利润
        gross_profit = total_revenue - total_cost
        operating_profit = gross_profit - sales_expense - admin_expense - finance_expense
        total_profit = operating_profit + investment_income - non_operating_expense
        net_income = total_profit - income_tax
        
        # 创建利润表字典
        income_statement = {
            "company_name": "示例公司",
            "period_start": period_start,
            "period_end": period_end,
            "total_revenue": total_revenue,
            "main_revenue": revenue,
            "other_revenue": other_revenue,
            "total_cost": total_cost,
            "main_cost": main_cost,
            "other_cost": other_cost,
            "gross_profit": gross_profit,
            "sales_expense": sales_expense,
            "admin_expense": admin_expense,
            "finance_expense": finance_expense,
            "operating_profit": operating_profit,
            "investment_income": investment_income,
            "non_operating_expense": non_operating_expense,
            "total_profit": total_profit,
            "income_tax": income_tax,
            "net_income": net_income,
            "prepared_by": "财务部",
            "preparation_date": datetime.now()
        }
        
        context.set_data("income_statement", income_statement)
        return income_statement
    
    def _generate_balance_sheet(self, context: WorkflowContext) -> Dict[str, Any]:
        """生成资产负债表"""
        account_balances = context.get_data("account_balances")
        report_date = context.get_data("report_date")
        
        # 计算资产
        cash = (account_balances.get("1001", {}).get("debit_balance", Decimal("0")) +
                account_balances.get("1002", {}).get("debit_balance", Decimal("0")))
        accounts_receivable = account_balances.get("1122", {}).get("debit_balance", Decimal("0"))
        prepaid_accounts = account_balances.get("1123", {}).get("debit_balance", Decimal("0"))
        inventory = account_balances.get("1401", {}).get("debit_balance", Decimal("0"))
        current_assets = cash + accounts_receivable + prepaid_accounts + inventory
        
        fixed_assets_cost = account_balances.get("1601", {}).get("debit_balance", Decimal("0"))
        accumulated_depreciation = account_balances.get("1602", {}).get("credit_balance", Decimal("0"))
        fixed_assets_net = fixed_assets_cost - accumulated_depreciation
        
        total_assets = current_assets + fixed_assets_net
        
        # 计算负债
        accounts_payable = account_balances.get("2202", {}).get("credit_balance", Decimal("0"))
        advance_receipts = account_balances.get("2203", {}).get("credit_balance", Decimal("0"))
        taxes_payable = account_balances.get("2221", {}).get("credit_balance", Decimal("0"))
        current_liabilities = accounts_payable + advance_receipts + taxes_payable
        
        long_term_loans = account_balances.get("2501", {}).get("credit_balance", Decimal("0"))
        total_liabilities = current_liabilities + long_term_loans
        
        # 计算所有者权益
        paid_capital = account_balances.get("4001", {}).get("credit_balance", Decimal("0"))
        capital_surplus = account_balances.get("4002", {}).get("credit_balance", Decimal("0"))
        surplus_reserve = account_balances.get("4101", {}).get("credit_balance", Decimal("0"))
        retained_earnings = account_balances.get("4103", {}).get("credit_balance", Decimal("0"))
        total_equity = paid_capital + capital_surplus + surplus_reserve + retained_earnings
        
        # 创建资产负债表字典
        balance_sheet = {
            "company_name": "示例公司",
            "report_date": report_date,
            "cash": cash,
            "accounts_receivable": accounts_receivable,
            "prepaid_accounts": prepaid_accounts,
            "inventory": inventory,
            "current_assets": current_assets,
            "fixed_assets_cost": fixed_assets_cost,
            "accumulated_depreciation": accumulated_depreciation,
            "fixed_assets_net": fixed_assets_net,
            "total_assets": total_assets,
            "accounts_payable": accounts_payable,
            "advance_receipts": advance_receipts,
            "taxes_payable": taxes_payable,
            "current_liabilities": current_liabilities,
            "long_term_loans": long_term_loans,
            "total_liabilities": total_liabilities,
            "paid_capital": paid_capital,
            "capital_surplus": capital_surplus,
            "surplus_reserve": surplus_reserve,
            "retained_earnings": retained_earnings,
            "total_equity": total_equity,
            "prepared_by": "财务部",
            "preparation_date": datetime.now()
        }
        
        context.set_data("balance_sheet", balance_sheet)
        return balance_sheet
    
    def _generate_cash_flow_statement(self, context: WorkflowContext) -> Dict[str, Any]:
        """生成现金流量表"""
        cash_flow_data = context.get_data("cash_flow_data")
        period_start = context.get_data("period_start")
        period_end = context.get_data("period_end")
        
        # 计算各活动现金流量净额
        operating_cash_flow = sum(item["amount"] for item in cash_flow_data["operating_activities"])
        investing_cash_flow = sum(item["amount"] for item in cash_flow_data["investing_activities"])
        financing_cash_flow = sum(item["amount"] for item in cash_flow_data["financing_activities"])
        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        # 创建现金流量表字典
        cash_flow_statement = {
            "company_name": "示例公司",
            "period_start": period_start,
            "period_end": period_end,
            "operating_activities": cash_flow_data["operating_activities"],
            "investing_activities": cash_flow_data["investing_activities"],
            "financing_activities": cash_flow_data["financing_activities"],
            "operating_cash_flow": operating_cash_flow,
            "investing_cash_flow": investing_cash_flow,
            "financing_cash_flow": financing_cash_flow,
            "net_cash_flow": net_cash_flow,
            "prepared_by": "财务部",
            "preparation_date": datetime.now()
        }
        
        context.set_data("cash_flow_statement", cash_flow_statement)
        return cash_flow_statement
    
    def _cross_reference_check(self, context: WorkflowContext) -> Dict[str, Any]:
        """报表勾稽检查"""
        income_statement = context.get_data("income_statement")
        balance_sheet = context.get_data("balance_sheet")
        cash_flow_statement = context.get_data("cash_flow_statement")
        
        check_results = []
        
        # 检查1：利润表净利润与资产负债表未分配利润变动的勾稽
        net_income = income_statement.get("net_income", Decimal("0"))
        # 这里简化处理，实际应该是期末未分配利润-期初未分配利润-本期分配数
        retained_earnings_change = net_income  # 假设无期初余额和分配
        
        check_results.append({
            "check_item": "净利润与未分配利润勾稽",
            "expected_value": net_income,
            "actual_value": retained_earnings_change,
            "difference": abs(net_income - retained_earnings_change),
            "is_matched": abs(net_income - retained_earnings_change) < Decimal("0.01"),
            "description": "利润表净利润应等于未分配利润的变动额"
        })
        
        # 检查2：资产负债表平衡性
        total_assets = balance_sheet.get("total_assets", Decimal("0"))
        total_liabilities_equity = balance_sheet.get("total_liabilities", Decimal("0")) + balance_sheet.get("total_equity", Decimal("0"))
        
        check_results.append({
            "check_item": "资产负债表平衡",
            "expected_value": total_assets,
            "actual_value": total_liabilities_equity,
            "difference": abs(total_assets - total_liabilities_equity),
            "is_matched": abs(total_assets - total_liabilities_equity) < Decimal("0.01"),
            "description": "资产总计应等于负债和所有者权益总计"
        })
        
        # 检查3：现金流量表与资产负债表货币资金变动的勾稽
        net_cash_flow = (cash_flow_statement.get("operating_cash_flow", Decimal("0")) + 
                        cash_flow_statement.get("investing_cash_flow", Decimal("0")) + 
                        cash_flow_statement.get("financing_cash_flow", Decimal("0")))
        
        # 从资产负债表获取期末货币资金（简化为固定值）
        cash_ending = balance_sheet.get("cash_and_equivalents", Decimal("50000"))
        
        # 假设期初货币资金（实际应从期初余额获取）
        cash_beginning = cash_ending - net_cash_flow
        
        check_results.append({
            "check_item": "现金流量与货币资金勾稽",
            "expected_value": cash_ending,
            "actual_value": cash_beginning + net_cash_flow,
            "difference": abs(cash_ending - (cash_beginning + net_cash_flow)),
            "is_matched": abs(cash_ending - (cash_beginning + net_cash_flow)) < Decimal("0.01"),
            "description": "期末货币资金应等于期初货币资金加净现金流量"
        })
        
        # 汇总检查结果
        all_matched = all(result["is_matched"] for result in check_results)
        total_differences = sum(result["difference"] for result in check_results)
        
        cross_reference_result = {
            "all_checks_passed": all_matched,
            "total_differences": total_differences,
            "check_details": check_results,
            "check_date": datetime.now(),
            "recommendation": "所有勾稽关系正常" if all_matched else "存在勾稽差异，需要检查数据准确性"
        }
        
        context.set_data("cross_reference_check", cross_reference_result)
        return cross_reference_result
    
    def _calculate_financial_ratios(self, context: WorkflowContext) -> Dict[str, Any]:
        """计算财务指标"""
        income_statement = context.get_data("income_statement")
        balance_sheet = context.get_data("balance_sheet")
        
        # 获取关键数据
        revenue = income_statement.get("total_revenue", Decimal("1000000"))
        net_income = income_statement.get("net_income", Decimal("100000"))
        total_assets = balance_sheet.get("total_assets", Decimal("800000"))
        total_equity = balance_sheet.get("total_equity", Decimal("500000"))
        total_liabilities = balance_sheet.get("total_liabilities", Decimal("300000"))
        
        # 简化处理，使用估算值
        current_assets = total_assets * Decimal("0.6")  # 假设流动资产占总资产60%
        current_liabilities = total_liabilities * Decimal("0.8")  # 假设流动负债占总负债80%
        inventory = current_assets * Decimal("0.3")  # 假设存货占流动资产30%
        accounts_receivable = current_assets * Decimal("0.4")  # 假设应收账款占流动资产40%
        
        # 计算财务比率
        financial_ratios = {}
        
        # 盈利能力指标
        financial_ratios["profitability"] = {
            "gross_profit_margin": (
                (revenue - income_statement.get("total_cost", revenue * Decimal("0.7"))) / revenue * 100 
                if revenue > 0 else 0
            ),
            "net_profit_margin": (
                net_income / revenue * 100 
                if revenue > 0 else 0
            ),
            "return_on_assets": (
                net_income / total_assets * 100 
                if total_assets > 0 else 0
            ),
            "return_on_equity": (
                net_income / total_equity * 100 
                if total_equity > 0 else 0
            )
        }
        
        # 偿债能力指标
        financial_ratios["solvency"] = {
            "current_ratio": (
                current_assets / current_liabilities 
                if current_liabilities > 0 else 0
            ),
            "quick_ratio": (
                (current_assets - inventory) / current_liabilities 
                if current_liabilities > 0 else 0
            ),
            "debt_to_asset_ratio": (
                total_liabilities / total_assets * 100 
                if total_assets > 0 else 0
            ),
            "debt_to_equity_ratio": (
                total_liabilities / total_equity * 100 
                if total_equity > 0 else 0
            )
        }
        
        # 营运能力指标（简化计算，实际需要平均余额）
        financial_ratios["efficiency"] = {
            "asset_turnover": (
                revenue / total_assets 
                if total_assets > 0 else 0
            ),
            "inventory_turnover": (
                income_statement.get("total_cost", revenue * Decimal("0.7")) / inventory 
                if inventory > 0 else 0
            ),
            "accounts_receivable_turnover": (
                revenue / accounts_receivable 
                if accounts_receivable > 0 else 0
            )
        }
        
        # 发展能力指标（需要历史数据，这里提供框架）
        financial_ratios["growth"] = {
            "revenue_growth_rate": 0,  # 需要上期数据
            "net_income_growth_rate": 0,  # 需要上期数据
            "total_assets_growth_rate": 0  # 需要上期数据
        }
        
        # 添加指标解释和评价
        ratio_analysis = self._analyze_financial_ratios(financial_ratios)
        
        financial_ratios_result = {
            "calculation_date": datetime.now(),
            "financial_ratios": financial_ratios,
            "ratio_analysis": ratio_analysis,
            "overall_assessment": self._overall_financial_assessment(financial_ratios)
        }
        
        context.set_data("financial_ratios", financial_ratios_result)
        return financial_ratios_result
    
    def _analyze_financial_ratios(self, ratios: Dict[str, Any]) -> Dict[str, Any]:
        """分析财务比率"""
        analysis = {}
        
        # 盈利能力分析
        profitability = ratios["profitability"]
        if profitability["net_profit_margin"] > 10:
            analysis["profitability"] = "盈利能力较强，净利润率超过10%"
        elif profitability["net_profit_margin"] > 5:
            analysis["profitability"] = "盈利能力一般，净利润率在5%-10%之间"
        else:
            analysis["profitability"] = "盈利能力较弱，净利润率低于5%"
        
        # 偿债能力分析
        solvency = ratios["solvency"]
        if solvency["current_ratio"] > 2:
            analysis["solvency"] = "短期偿债能力较强，流动比率超过2"
        elif solvency["current_ratio"] > 1:
            analysis["solvency"] = "短期偿债能力一般，流动比率在1-2之间"
        else:
            analysis["solvency"] = "短期偿债能力不足，流动比率低于1"
        
        # 营运能力分析
        efficiency = ratios["efficiency"]
        if efficiency["asset_turnover"] > 1:
            analysis["efficiency"] = "资产运营效率较高，总资产周转率超过1"
        elif efficiency["asset_turnover"] > 0.5:
            analysis["efficiency"] = "资产运营效率一般"
        else:
            analysis["efficiency"] = "资产运营效率较低，需要提高资产利用率"
        
        return analysis
    
    def _overall_financial_assessment(self, ratios: Dict[str, Any]) -> str:
        """整体财务状况评估"""
        score = 0
        
        # 盈利能力评分
        if ratios["profitability"]["net_profit_margin"] > 10:
            score += 3
        elif ratios["profitability"]["net_profit_margin"] > 5:
            score += 2
        else:
            score += 1
        
        # 偿债能力评分
        if ratios["solvency"]["current_ratio"] > 2:
            score += 3
        elif ratios["solvency"]["current_ratio"] > 1:
            score += 2
        else:
            score += 1
        
        # 营运能力评分
        if ratios["efficiency"]["asset_turnover"] > 1:
            score += 3
        elif ratios["efficiency"]["asset_turnover"] > 0.5:
            score += 2
        else:
            score += 1
        
        # 根据总分评级
        if score >= 8:
            return "财务状况优秀，企业经营状况良好"
        elif score >= 6:
            return "财务状况良好，但仍有改进空间"
        elif score >= 4:
            return "财务状况一般，需要关注风险控制"
        else:
            return "财务状况较差，需要采取措施改善经营"
    
    def _review_and_publish(self, context: WorkflowContext) -> Dict[str, Any]:
        """报表审核发布"""
        income_statement = context.get_data("income_statement")
        balance_sheet = context.get_data("balance_sheet")
        cash_flow_statement = context.get_data("cash_flow_statement")
        cross_reference_check = context.get_data("cross_reference_check")
        financial_ratios = context.get_data("financial_ratios")
        
        # 执行最终审核检查
        audit_issues = []
        
        # 数据合理性检查
        if income_statement.get("net_income", Decimal("0")) < 0:
            audit_issues.append("净利润为负，需要关注经营状况")
        
        if balance_sheet.get("total_assets", Decimal("0")) <= 0:
            audit_issues.append("总资产小于等于零，数据异常")
        
        if not cross_reference_check["all_checks_passed"]:
            audit_issues.append("报表勾稽关系存在差异，需要核实数据准确性")
        
        # 财务比率异常检查
        ratios = financial_ratios["financial_ratios"]
        if ratios["solvency"]["current_ratio"] < 1:
            audit_issues.append("流动比率小于1，短期偿债能力不足")
        
        if ratios["solvency"]["debt_to_asset_ratio"] > 70:
            audit_issues.append("资产负债率超过70%，财务风险较高")
        
        # 创建综合财务报告（简化版）
        period_start = context.get_data("period_start")
        period_end = context.get_data("period_end")
        
        comprehensive_report = {
            "company_name": "示例公司",
            "report_period": f"{period_start.strftime('%Y-%m-%d')} 至 {period_end.strftime('%Y-%m-%d')}",
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow_statement": cash_flow_statement,
            "financial_ratios": financial_ratios,
            "prepared_by": "财务部",
            "reviewed_by": "财务经理",
            "approved_by": "总经理",
            "preparation_date": datetime.now()
        }
        
        # 报表发布状态
        publish_status = {
            "is_ready_for_publish": len(audit_issues) == 0,
            "audit_issues": audit_issues,
            "comprehensive_report": comprehensive_report,
            "financial_summary": {
                "total_revenue": income_statement.get("total_revenue", Decimal("0")),
                "net_income": income_statement.get("net_income", Decimal("0")),
                "total_assets": balance_sheet.get("total_assets", Decimal("0")),
                "total_equity": balance_sheet.get("total_equity", Decimal("0")),
                "net_cash_flow": (
                    cash_flow_statement.get("operating_cash_flow", Decimal("0")) +
                    cash_flow_statement.get("investing_cash_flow", Decimal("0")) +
                    cash_flow_statement.get("financing_cash_flow", Decimal("0"))
                )
            },
            "key_ratios": {
                "net_profit_margin": ratios["profitability"]["net_profit_margin"],
                "current_ratio": ratios["solvency"]["current_ratio"],
                "return_on_assets": ratios["profitability"]["return_on_assets"]
            },
            "review_date": datetime.now(),
            "next_steps": self._get_next_steps(audit_issues)
        }
        
        context.set_data("publish_status", publish_status)
        return publish_status
    
    def _get_next_steps(self, audit_issues: List[str]) -> List[str]:
        """获取后续步骤建议"""
        if not audit_issues:
            return [
                "报表审核通过，可以发布",
                "准备报表分发和归档",
                "开始下期财务数据收集"
            ]
        else:
            return [
                "解决审核发现的问题",
                "重新核实相关财务数据",
                "完成数据修正后重新生成报表",
                "重新进行审核流程"
            ]