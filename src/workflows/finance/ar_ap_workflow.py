"""
应收应付管理工作流模板

基于财务数据模型，提供标准的应收应付业务流程：
- 应收账款管理流程
- 应付账款管理流程
- 客户信用管理
- 供应商管理
- 账龄分析
- 催收管理
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import polars as pl

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...models.finance.account_models import ChartOfAccounts, AccountCode
from ...models.finance.transaction_models import JournalEntry, AccountingEntry, GeneralLedger, EntryType, TransactionType
from ...models.finance.audit_models import AuditEngine, AuditRule
from ...models.finance.currency_models import CurrencyManager


class AccountsReceivableWorkflow(WorkflowTemplate):
    """应收账款管理工作流
    
    标准应收账款业务流程：
    1. 销售发票生成
    2. 应收账款记账
    3. 账龄分析
    4. 信用风险评估
    5. 收款确认
    6. 坏账处理
    """
    
    def __init__(self):
        super().__init__("应收账款管理工作流")
        self.chart_of_accounts = ChartOfAccounts()
        self.general_ledger = GeneralLedger()
        self.audit_engine = AuditEngine()
        self.currency_manager = CurrencyManager()
    
    def define_steps(self) -> List[WorkflowStep]:
        """定义应收账款工作流步骤"""
        return [
            WorkflowStep(
                name="初始化应收数据",
                description="初始化客户信息和销售数据",
                execute_func=self._initialize_ar_data
            ),
            WorkflowStep(
                name="生成销售发票",
                description="根据销售订单生成销售发票",
                execute_func=self._generate_sales_invoice,
                depends_on=["初始化应收数据"]
            ),
            WorkflowStep(
                name="应收账款记账",
                description="生成应收账款会计分录",
                execute_func=self._record_accounts_receivable,
                depends_on=["生成销售发票"]
            ),
            WorkflowStep(
                name="账龄分析",
                description="计算应收账款账龄分布",
                execute_func=self._aging_analysis,
                depends_on=["应收账款记账"]
            ),
            WorkflowStep(
                name="信用风险评估",
                description="评估客户信用风险等级",
                execute_func=self._credit_risk_assessment,
                depends_on=["账龄分析"]
            ),
            WorkflowStep(
                name="收款处理",
                description="处理客户收款和核销",
                execute_func=self._process_collection,
                depends_on=["应收账款记账"],
                required=False
            ),
            WorkflowStep(
                name="坏账处理",
                description="处理坏账准备和核销",
                execute_func=self._process_bad_debt,
                depends_on=["信用风险评估"],
                required=False
            ),
            WorkflowStep(
                name="合规检查",
                description="应收账款合规性检查",
                execute_func=self._compliance_check,
                depends_on=["账龄分析", "信用风险评估"]
            )
        ]
    
    def _initialize_ar_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """初始化应收数据"""
        # 获取销售数据
        sales_data = context.get_data("sales_data", [])
        if not sales_data:
            # 示例销售数据
            sales_data = [
                {
                    "invoice_no": "INV-2024-001",
                    "customer_id": "CUST001",
                    "customer_name": "客户A",
                    "sale_date": datetime.now(),
                    "amount": Decimal("50000.00"),
                    "currency": "CNY",
                    "payment_terms": 30,  # 30天付款期
                    "salesperson": "张三"
                },
                {
                    "invoice_no": "INV-2024-002", 
                    "customer_id": "CUST002",
                    "customer_name": "客户B",
                    "sale_date": datetime.now() - timedelta(days=45),
                    "amount": Decimal("75000.00"),
                    "currency": "CNY",
                    "payment_terms": 30,
                    "salesperson": "李四"
                },
                {
                    "invoice_no": "INV-2024-003",
                    "customer_id": "CUST003", 
                    "customer_name": "客户C",
                    "sale_date": datetime.now() - timedelta(days=15),
                    "amount": Decimal("120000.00"),
                    "currency": "CNY",
                    "payment_terms": 60,
                    "salesperson": "王五"
                }
            ]
        
        # 初始化客户信息
        customer_info = {
            "CUST001": {"credit_limit": Decimal("100000"), "risk_level": "LOW"},
            "CUST002": {"credit_limit": Decimal("150000"), "risk_level": "MEDIUM"},
            "CUST003": {"credit_limit": Decimal("200000"), "risk_level": "LOW"}
        }
        
        context.set_data("sales_data", sales_data)
        context.set_data("customer_info", customer_info)
        
        return {
            "sales_count": len(sales_data),
            "total_amount": sum(item["amount"] for item in sales_data),
            "customers": list(customer_info.keys())
        }
    
    def _generate_sales_invoice(self, context: WorkflowContext) -> List[Dict[str, Any]]:
        """生成销售发票"""
        sales_data = context.get_data("sales_data")
        invoices = []
        
        for sale in sales_data:
            invoice = {
                "invoice_no": sale["invoice_no"],
                "invoice_date": sale["sale_date"],
                "customer_id": sale["customer_id"],
                "customer_name": sale["customer_name"],
                "due_date": sale["sale_date"] + timedelta(days=sale["payment_terms"]),
                "gross_amount": sale["amount"],
                "tax_amount": sale["amount"] * Decimal("0.13"),  # 13%增值税
                "net_amount": sale["amount"] * Decimal("1.13"),
                "currency": sale["currency"],
                "status": "ISSUED"
            }
            invoices.append(invoice)
        
        context.set_data("invoices", invoices)
        return invoices
    
    def _record_accounts_receivable(self, context: WorkflowContext) -> List[JournalEntry]:
        """应收账款记账"""
        invoices = context.get_data("invoices")
        journal_entries = []
        
        # 获取相关科目
        ar_candidates = self.chart_of_accounts.search_accounts("应收账款")
        ar_account = ar_candidates[0] if ar_candidates else self.chart_of_accounts.get_account("1122")
        
        revenue_candidates = self.chart_of_accounts.search_accounts("主营业务收入")
        revenue_account = revenue_candidates[0] if revenue_candidates else self.chart_of_accounts.get_account("6001")
        
        tax_candidates = self.chart_of_accounts.search_accounts("应交税费")
        tax_account = tax_candidates[0] if tax_candidates else self.chart_of_accounts.get_account("2221")
        
        for invoice in invoices:
            # 创建应收账款分录
            entries = [
                AccountingEntry(
                    account_code=ar_account.code if ar_account else "1122",
                    account_name="应收账款",
                    entry_type=EntryType.DEBIT,
                    amount=invoice["net_amount"],
                    description=f"销售商品-{invoice['customer_name']}"
                ),
                AccountingEntry(
                    account_code=revenue_account.code if revenue_account else "6001",
                    account_name="主营业务收入", 
                    entry_type=EntryType.CREDIT,
                    amount=invoice["gross_amount"],
                    description=f"确认收入-{invoice['customer_name']}"
                ),
                AccountingEntry(
                    account_code=tax_account.code if tax_account else "2221",
                    account_name="应交增值税-销项税额",
                    entry_type=EntryType.CREDIT,
                    amount=invoice["tax_amount"],
                    description=f"销项税额-{invoice['customer_name']}"
                )
            ]
            
            journal_entry = JournalEntry(
                entry_id=f"JE-AR-{invoice['invoice_no']}",
                transaction_date=invoice["invoice_date"],
                transaction_type=TransactionType.SALES,
                entries=entries,
                total_amount=invoice["net_amount"],
                description=f"确认应收账款-{invoice['invoice_no']}"
            )
            
            journal_entries.append(journal_entry)
            
            # 先添加到总账，然后过账
            self.general_ledger.add_journal_entry(journal_entry)
            self.general_ledger.post_journal_entry(journal_entry.entry_id)
        
        context.set_data("ar_journal_entries", journal_entries)
        return journal_entries
    
    def _aging_analysis(self, context: WorkflowContext) -> Dict[str, Any]:
        """账龄分析"""
        invoices = context.get_data("invoices")
        current_date = datetime.now()
        
        aging_buckets = {
            "current": {"days": 0, "amount": Decimal("0"), "count": 0},      # 未到期
            "1-30": {"days": 30, "amount": Decimal("0"), "count": 0},        # 1-30天
            "31-60": {"days": 60, "amount": Decimal("0"), "count": 0},       # 31-60天  
            "61-90": {"days": 90, "amount": Decimal("0"), "count": 0},       # 61-90天
            "over_90": {"days": 91, "amount": Decimal("0"), "count": 0}      # 90天以上
        }
        
        total_outstanding = Decimal("0")
        
        for invoice in invoices:
            due_date = invoice["due_date"]
            amount = invoice["net_amount"]
            days_overdue = (current_date - due_date).days
            
            total_outstanding += amount
            
            if days_overdue <= 0:
                aging_buckets["current"]["amount"] += amount
                aging_buckets["current"]["count"] += 1
            elif days_overdue <= 30:
                aging_buckets["1-30"]["amount"] += amount
                aging_buckets["1-30"]["count"] += 1
            elif days_overdue <= 60:
                aging_buckets["31-60"]["amount"] += amount
                aging_buckets["31-60"]["count"] += 1
            elif days_overdue <= 90:
                aging_buckets["61-90"]["amount"] += amount
                aging_buckets["61-90"]["count"] += 1
            else:
                aging_buckets["over_90"]["amount"] += amount
                aging_buckets["over_90"]["count"] += 1
        
        # 计算各账龄段占比
        aging_analysis = {}
        for bucket, data in aging_buckets.items():
            percentage = (data["amount"] / total_outstanding * 100) if total_outstanding > 0 else 0
            aging_analysis[bucket] = {
                "amount": data["amount"],
                "count": data["count"],
                "percentage": round(percentage, 2)
            }
        
        aging_result = {
            "total_outstanding": total_outstanding,
            "aging_buckets": aging_analysis,
            "analysis_date": current_date
        }
        
        context.set_data("aging_analysis", aging_result)
        return aging_result
    
    def _credit_risk_assessment(self, context: WorkflowContext) -> Dict[str, Any]:
        """信用风险评估"""
        aging_analysis = context.get_data("aging_analysis")
        customer_info = context.get_data("customer_info")
        invoices = context.get_data("invoices")
        
        risk_assessment = {}
        
        # 按客户分组分析
        customer_outstanding = {}
        for invoice in invoices:
            customer_id = invoice["customer_id"]
            if customer_id not in customer_outstanding:
                customer_outstanding[customer_id] = {
                    "customer_name": invoice["customer_name"],
                    "total_amount": Decimal("0"),
                    "invoice_count": 0,
                    "overdue_amount": Decimal("0")
                }
            
            customer_outstanding[customer_id]["total_amount"] += invoice["net_amount"]
            customer_outstanding[customer_id]["invoice_count"] += 1
            
            # 计算逾期金额
            current_date = datetime.now()
            if current_date > invoice["due_date"]:
                customer_outstanding[customer_id]["overdue_amount"] += invoice["net_amount"]
        
        # 风险评级
        for customer_id, data in customer_outstanding.items():
            customer_data = customer_info.get(customer_id, {})
            credit_limit = customer_data.get("credit_limit", Decimal("0"))
            
            # 计算风险指标
            utilization_rate = (data["total_amount"] / credit_limit * 100) if credit_limit > 0 else 0
            overdue_rate = (data["overdue_amount"] / data["total_amount"] * 100) if data["total_amount"] > 0 else 0
            
            # 风险等级判定
            if overdue_rate > 50 or utilization_rate > 90:
                risk_level = "HIGH"
            elif overdue_rate > 20 or utilization_rate > 70:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            risk_assessment[customer_id] = {
                "customer_name": data["customer_name"],
                "total_outstanding": data["total_amount"],
                "overdue_amount": data["overdue_amount"],
                "credit_limit": credit_limit,
                "utilization_rate": round(utilization_rate, 2),
                "overdue_rate": round(overdue_rate, 2),
                "risk_level": risk_level,
                "recommended_action": self._get_risk_action(risk_level)
            }
        
        context.set_data("risk_assessment", risk_assessment)
        return risk_assessment
    
    def _get_risk_action(self, risk_level: str) -> str:
        """获取风险应对措施"""
        actions = {
            "LOW": "正常监控",
            "MEDIUM": "加强催收，考虑缩短付款期限",
            "HIGH": "停止赊销，启动法律程序"
        }
        return actions.get(risk_level, "未知风险等级")
    
    def _process_collection(self, context: WorkflowContext) -> List[Dict[str, Any]]:
        """收款处理"""
        invoices = context.get_data("invoices")
        collections = []
        
        # 模拟收款数据
        collection_data = [
            {"invoice_no": "INV-2024-001", "amount": Decimal("56500.00"), "date": datetime.now()},
            {"invoice_no": "INV-2024-003", "amount": Decimal("60000.00"), "date": datetime.now()}
        ]
        
        for payment in collection_data:
            # 查找对应发票
            invoice = next((inv for inv in invoices if inv["invoice_no"] == payment["invoice_no"]), None)
            if invoice:
                collection = {
                    "payment_id": f"PAY-{payment['invoice_no']}-{payment['date'].strftime('%Y%m%d')}",
                    "invoice_no": payment["invoice_no"],
                    "customer_id": invoice["customer_id"],
                    "customer_name": invoice["customer_name"],
                    "payment_date": payment["date"],
                    "payment_amount": payment["amount"],
                    "invoice_amount": invoice["net_amount"],
                    "remaining_balance": invoice["net_amount"] - payment["amount"]
                }
                collections.append(collection)
        
        context.set_data("collections", collections)
        return collections
    
    def _process_bad_debt(self, context: WorkflowContext) -> Dict[str, Any]:
        """坏账处理"""
        risk_assessment = context.get_data("risk_assessment")
        
        # 计算坏账准备
        bad_debt_provision = Decimal("0")
        bad_debt_details = []
        
        for customer_id, assessment in risk_assessment.items():
            if assessment["risk_level"] == "HIGH":
                # 高风险客户计提50%坏账准备
                provision_rate = Decimal("0.5")
            elif assessment["risk_level"] == "MEDIUM":
                # 中风险客户计提10%坏账准备
                provision_rate = Decimal("0.1")
            else:
                # 低风险客户计提1%坏账准备
                provision_rate = Decimal("0.01")
            
            customer_provision = assessment["total_outstanding"] * provision_rate
            bad_debt_provision += customer_provision
            
            bad_debt_details.append({
                "customer_id": customer_id,
                "customer_name": assessment["customer_name"],
                "outstanding_amount": assessment["total_outstanding"],
                "provision_rate": provision_rate,
                "provision_amount": customer_provision
            })
        
        bad_debt_result = {
            "total_provision": bad_debt_provision,
            "provision_details": bad_debt_details,
            "provision_date": datetime.now()
        }
        
        context.set_data("bad_debt_provision", bad_debt_result)
        return bad_debt_result
    
    def _compliance_check(self, context: WorkflowContext) -> Dict[str, Any]:
        """合规检查"""
        # 使用审计引擎进行应收账款合规检查
        audit_results = []
        
        # 检查账龄分析合理性
        aging_analysis = context.get_data("aging_analysis")
        if aging_analysis:
            overdue_percentage = (
                aging_analysis["aging_buckets"]["1-30"]["percentage"] +
                aging_analysis["aging_buckets"]["31-60"]["percentage"] +
                aging_analysis["aging_buckets"]["61-90"]["percentage"] +
                aging_analysis["aging_buckets"]["over_90"]["percentage"]
            )
            
            if overdue_percentage > 30:
                audit_results.append({
                    "rule": "应收账款逾期率检查",
                    "status": "WARNING", 
                    "message": f"逾期应收账款占比过高: {overdue_percentage:.2f}%",
                    "recommendation": "加强应收账款管理和催收工作"
                })
        
        # 检查坏账准备计提
        bad_debt_provision = context.get_data("bad_debt_provision")
        if bad_debt_provision:
            total_outstanding = aging_analysis["total_outstanding"]
            provision_rate = bad_debt_provision["total_provision"] / total_outstanding * 100
            
            if provision_rate < 1:
                audit_results.append({
                    "rule": "坏账准备计提检查",
                    "status": "WARNING",
                    "message": f"坏账准备计提比例较低: {provision_rate:.2f}%",
                    "recommendation": "根据客户信用状况适当提高坏账准备计提比例"
                })
        
        compliance_result = {
            "check_date": datetime.now(),
            "audit_findings": audit_results,
            "compliance_score": max(0, 100 - len(audit_results) * 10),
            "overall_status": "COMPLIANT" if len(audit_results) == 0 else "WARNING"
        }
        
        context.set_data("compliance_check", compliance_result)
        return compliance_result


class AccountsPayableWorkflow(WorkflowTemplate):
    """应付账款管理工作流
    
    标准应付账款业务流程：
    1. 采购订单管理
    2. 应付账款记账
    3. 付款计划管理
    4. 供应商对账
    5. 付款处理
    6. 现金流预测
    """
    
    def __init__(self):
        super().__init__("应付账款管理工作流")
        self.chart_of_accounts = ChartOfAccounts()
        self.general_ledger = GeneralLedger()
        self.currency_manager = CurrencyManager()
    
    def define_steps(self) -> List[WorkflowStep]:
        """定义应付账款工作流步骤"""
        return [
            WorkflowStep(
                name="初始化应付数据",
                description="初始化供应商信息和采购数据",
                execute_func=self._initialize_ap_data
            ),
            WorkflowStep(
                name="采购订单处理",
                description="处理采购订单和收货确认",
                execute_func=self._process_purchase_orders,
                depends_on=["初始化应付数据"]
            ),
            WorkflowStep(
                name="应付账款记账",
                description="生成应付账款会计分录",
                execute_func=self._record_accounts_payable,
                depends_on=["采购订单处理"]
            ),
            WorkflowStep(
                name="付款计划管理",
                description="制定和管理付款计划",
                execute_func=self._manage_payment_schedule,
                depends_on=["应付账款记账"]
            ),
            WorkflowStep(
                name="供应商对账",
                description="与供应商进行账务核对",
                execute_func=self._supplier_reconciliation,
                depends_on=["应付账款记账"]
            ),
            WorkflowStep(
                name="付款处理",
                description="执行付款并更新账务",
                execute_func=self._process_payments,
                depends_on=["付款计划管理"],
                required=False
            ),
            WorkflowStep(
                name="现金流预测",
                description="基于应付账款进行现金流预测",
                execute_func=self._cash_flow_forecast,
                depends_on=["付款计划管理"]
            )
        ]
    
    def _initialize_ap_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """初始化应付数据"""
        # 示例采购数据
        purchase_data = context.get_data("purchase_data", [
            {
                "po_no": "PO-2024-001",
                "supplier_id": "SUPP001",
                "supplier_name": "供应商A",
                "purchase_date": datetime.now() - timedelta(days=5),
                "amount": Decimal("30000.00"),
                "currency": "CNY",
                "payment_terms": 45,
                "goods_received": True
            },
            {
                "po_no": "PO-2024-002",
                "supplier_id": "SUPP002", 
                "supplier_name": "供应商B",
                "purchase_date": datetime.now() - timedelta(days=10),
                "amount": Decimal("45000.00"), 
                "currency": "CNY",
                "payment_terms": 30,
                "goods_received": True
            }
        ])
        
        supplier_info = {
            "SUPP001": {"payment_terms": 45, "discount_rate": Decimal("0.02")},
            "SUPP002": {"payment_terms": 30, "discount_rate": Decimal("0.01")}
        }
        
        context.set_data("purchase_data", purchase_data)
        context.set_data("supplier_info", supplier_info)
        
        return {
            "purchase_count": len(purchase_data),
            "total_amount": sum(item["amount"] for item in purchase_data),
            "suppliers": list(supplier_info.keys())
        }
    
    def _process_purchase_orders(self, context: WorkflowContext) -> List[Dict[str, Any]]:
        """采购订单处理"""
        purchase_data = context.get_data("purchase_data")
        processed_orders = []
        
        for order in purchase_data:
            if order["goods_received"]:
                processed_order = {
                    "po_no": order["po_no"],
                    "supplier_id": order["supplier_id"],
                    "supplier_name": order["supplier_name"],
                    "invoice_date": order["purchase_date"],
                    "due_date": order["purchase_date"] + timedelta(days=order["payment_terms"]),
                    "gross_amount": order["amount"],
                    "tax_amount": order["amount"] * Decimal("0.13"),
                    "net_amount": order["amount"] * Decimal("1.13"),
                    "currency": order["currency"],
                    "status": "PENDING_PAYMENT"
                }
                processed_orders.append(processed_order)
        
        context.set_data("ap_invoices", processed_orders)
        return processed_orders
    
    def _record_accounts_payable(self, context: WorkflowContext) -> List[JournalEntry]:
        """应付账款记账"""
        ap_invoices = context.get_data("ap_invoices")
        journal_entries = []
        
        # 获取相关科目
        ap_candidates = self.chart_of_accounts.search_accounts("应付账款")
        ap_account = ap_candidates[0] if ap_candidates else self.chart_of_accounts.get_account("2202")
        
        expense_candidates = self.chart_of_accounts.search_accounts("管理费用")
        expense_account = expense_candidates[0] if expense_candidates else self.chart_of_accounts.get_account("6602")
        
        tax_candidates = self.chart_of_accounts.search_accounts("应交税费")
        tax_account = tax_candidates[0] if tax_candidates else self.chart_of_accounts.get_account("2221")
        
        for invoice in ap_invoices:
            entries = [
                AccountingEntry(
                    account_code=expense_account.code if expense_account else "6602",
                    account_name="管理费用",
                    entry_type=EntryType.DEBIT,
                    amount=invoice["gross_amount"],
                    description=f"采购费用-{invoice['supplier_name']}"
                ),
                AccountingEntry(
                    account_code=tax_account.code if tax_account else "2221",
                    account_name="应交增值税-进项税额",
                    entry_type=EntryType.DEBIT,
                    amount=invoice["tax_amount"],
                    description=f"进项税额-{invoice['supplier_name']}"
                ),
                AccountingEntry(
                    account_code=ap_account.code if ap_account else "2202",
                    account_name="应付账款",
                    entry_type=EntryType.CREDIT,
                    amount=invoice["net_amount"],
                    description=f"确认应付-{invoice['supplier_name']}"
                )
            ]
            
            journal_entry = JournalEntry(
                entry_id=f"JE-AP-{invoice['po_no']}",
                transaction_date=invoice["invoice_date"],
                transaction_type=TransactionType.PURCHASE,
                entries=entries,
                total_amount=invoice["net_amount"],
                description=f"确认应付账款-{invoice['po_no']}"
            )
            
            journal_entries.append(journal_entry)
            
            # 先添加到总账，然后过账
            self.general_ledger.add_journal_entry(journal_entry)
            self.general_ledger.post_journal_entry(journal_entry.entry_id)
        
        context.set_data("ap_journal_entries", journal_entries)
        return journal_entries
    
    def _manage_payment_schedule(self, context: WorkflowContext) -> Dict[str, Any]:
        """付款计划管理"""
        ap_invoices = context.get_data("ap_invoices")
        supplier_info = context.get_data("supplier_info")
        
        payment_schedule = []
        total_due_amounts = {}
        
        for invoice in ap_invoices:
            supplier_id = invoice["supplier_id"]
            supplier_data = supplier_info.get(supplier_id, {})
            
            # 计算早付折扣
            discount_amount = Decimal("0")
            early_pay_date = None
            discount_rate = supplier_data.get("discount_rate", Decimal("0"))
            
            if discount_rate > 0:
                # 10天内付款可享受折扣
                early_pay_date = invoice["invoice_date"] + timedelta(days=10)
                if early_pay_date <= datetime.now() + timedelta(days=10):
                    discount_amount = invoice["net_amount"] * discount_rate
            
            payment_item = {
                "po_no": invoice["po_no"],
                "supplier_id": supplier_id,
                "supplier_name": invoice["supplier_name"],
                "invoice_amount": invoice["net_amount"],
                "due_date": invoice["due_date"],
                "early_pay_date": early_pay_date,
                "discount_amount": discount_amount,
                "net_payment_amount": invoice["net_amount"] - discount_amount,
                "priority": self._calculate_payment_priority(invoice, supplier_data)
            }
            
            payment_schedule.append(payment_item)
            
            # 按月份汇总应付金额
            month_key = invoice["due_date"].strftime("%Y-%m")
            if month_key not in total_due_amounts:
                total_due_amounts[month_key] = Decimal("0")
            total_due_amounts[month_key] += payment_item["net_payment_amount"]
        
        # 按优先级排序
        payment_schedule.sort(key=lambda x: (-x["priority"], x["due_date"]))
        
        schedule_result = {
            "payment_schedule": payment_schedule,
            "monthly_due_amounts": total_due_amounts,
            "total_payable": sum(item["net_payment_amount"] for item in payment_schedule),
            "total_discount_available": sum(item["discount_amount"] for item in payment_schedule)
        }
        
        context.set_data("payment_schedule", schedule_result)
        return schedule_result
    
    def _calculate_payment_priority(self, invoice: Dict[str, Any], supplier_data: Dict[str, Any]) -> int:
        """计算付款优先级"""
        priority = 1
        
        # 金额越大优先级越高
        if invoice["net_amount"] > Decimal("50000"):
            priority += 2
        elif invoice["net_amount"] > Decimal("20000"):
            priority += 1
        
        # 有折扣的优先级更高
        if supplier_data.get("discount_rate", Decimal("0")) > 0:
            priority += 3
        
        # 即将到期的优先级更高
        days_to_due = (invoice["due_date"] - datetime.now()).days
        if days_to_due <= 5:
            priority += 5
        elif days_to_due <= 15:
            priority += 2
        
        return priority
    
    def _supplier_reconciliation(self, context: WorkflowContext) -> Dict[str, Any]:
        """供应商对账"""
        ap_invoices = context.get_data("ap_invoices")
        
        # 按供应商分组
        supplier_balances = {}
        for invoice in ap_invoices:
            supplier_id = invoice["supplier_id"]
            if supplier_id not in supplier_balances:
                supplier_balances[supplier_id] = {
                    "supplier_name": invoice["supplier_name"],
                    "total_invoices": 0,
                    "total_amount": Decimal("0"),
                    "invoice_details": []
                }
            
            supplier_balances[supplier_id]["total_invoices"] += 1
            supplier_balances[supplier_id]["total_amount"] += invoice["net_amount"]
            supplier_balances[supplier_id]["invoice_details"].append({
                "po_no": invoice["po_no"],
                "invoice_date": invoice["invoice_date"],
                "amount": invoice["net_amount"],
                "due_date": invoice["due_date"]
            })
        
        reconciliation_result = {
            "reconciliation_date": datetime.now(),
            "supplier_balances": supplier_balances,
            "total_suppliers": len(supplier_balances),
            "total_outstanding": sum(data["total_amount"] for data in supplier_balances.values())
        }
        
        context.set_data("supplier_reconciliation", reconciliation_result)
        return reconciliation_result
    
    def _process_payments(self, context: WorkflowContext) -> List[Dict[str, Any]]:
        """付款处理"""
        payment_schedule = context.get_data("payment_schedule")
        
        # 模拟付款处理
        payments = []
        payment_data = [
            {"po_no": "PO-2024-001", "amount": Decimal("33900.00"), "date": datetime.now()}
        ]
        
        for payment in payment_data:
            # 查找对应的付款计划项
            schedule_item = next(
                (item for item in payment_schedule["payment_schedule"] 
                 if item["po_no"] == payment["po_no"]), None
            )
            
            if schedule_item:
                payment_record = {
                    "payment_id": f"PAY-{payment['po_no']}-{payment['date'].strftime('%Y%m%d')}",
                    "po_no": payment["po_no"],
                    "supplier_id": schedule_item["supplier_id"],
                    "supplier_name": schedule_item["supplier_name"],
                    "payment_date": payment["date"],
                    "payment_amount": payment["amount"],
                    "invoice_amount": schedule_item["invoice_amount"],
                    "discount_taken": schedule_item["discount_amount"],
                    "remaining_balance": schedule_item["invoice_amount"] - payment["amount"]
                }
                payments.append(payment_record)
        
        context.set_data("payments", payments)
        return payments
    
    def _cash_flow_forecast(self, context: WorkflowContext) -> Dict[str, Any]:
        """现金流预测"""
        payment_schedule = context.get_data("payment_schedule")
        payments = context.get_data("payments", [])
        
        # 计算未来现金流
        current_date = datetime.now()
        forecast_periods = []
        
        # 按周预测未来8周的现金流
        for week in range(8):
            period_start = current_date + timedelta(weeks=week)
            period_end = period_start + timedelta(days=6)
            
            period_payments = Decimal("0")
            payment_count = 0
            
            for item in payment_schedule["payment_schedule"]:
                if period_start <= item["due_date"] <= period_end:
                    # 检查是否已付款
                    paid = any(p["po_no"] == item["po_no"] for p in payments)
                    if not paid:
                        period_payments += item["net_payment_amount"]
                        payment_count += 1
            
            forecast_periods.append({
                "period": f"第{week+1}周",
                "start_date": period_start,
                "end_date": period_end,
                "payment_amount": period_payments,
                "payment_count": payment_count
            })
        
        # 计算累计现金流
        cumulative_outflow = Decimal("0")
        for period in forecast_periods:
            cumulative_outflow += period["payment_amount"]
            period["cumulative_outflow"] = cumulative_outflow
        
        cash_flow_result = {
            "forecast_date": current_date,
            "forecast_periods": forecast_periods,
            "total_forecast_outflow": cumulative_outflow,
            "average_weekly_outflow": cumulative_outflow / 8 if len(forecast_periods) > 0 else Decimal("0")
        }
        
        context.set_data("cash_flow_forecast", cash_flow_result)
        return cash_flow_result