"""
成本核算工作流模板

基于成本管理数据模型，提供标准的成本核算业务流程：
- 成本数据收集
- 成本分摊计算
- 成本中心分析
- 产品成本核算
- 成本差异分析
- 成本报告生成
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import polars as pl

from .workflow_base import WorkflowTemplate, WorkflowStep, WorkflowContext
from ...models.finance.cost_models import CostAllocationEngine, CostCenter, CostPool, CostAllocation, AllocationBasis
from ...models.finance.account_models import ChartOfAccounts
from ...models.finance.transaction_models import JournalEntry, AccountingEntry


class CostAccountingWorkflow(WorkflowTemplate):
    """成本核算工作流
    
    标准成本核算业务流程：
    1. 成本数据收集和整理
    2. 直接成本归集
    3. 间接成本分摊
    4. 产品成本计算
    5. 成本差异分析
    6. 成本报告生成
    7. 成本控制建议
    """
    
    def __init__(self):
        super().__init__("成本核算工作流")
        self.cost_engine = CostAllocationEngine()
        self.chart_of_accounts = ChartOfAccounts()
    
    def define_steps(self) -> List[WorkflowStep]:
        """定义成本核算工作流步骤"""
        return [
            WorkflowStep(
                name="初始化成本数据",
                description="收集和整理成本核算基础数据",
                execute_func=self._initialize_cost_data
            ),
            WorkflowStep(
                name="设置成本中心",
                description="建立成本中心和成本对象",
                execute_func=self._setup_cost_centers,
                depends_on=["初始化成本数据"]
            ),
            WorkflowStep(
                name="归集直接成本",
                description="归集直接材料、直接人工等直接成本",
                execute_func=self._collect_direct_costs,
                depends_on=["设置成本中心"]
            ),
            WorkflowStep(
                name="分摊间接成本",
                description="按照分摊标准分摊制造费用等间接成本",
                execute_func=self._allocate_indirect_costs,
                depends_on=["归集直接成本"]
            ),
            WorkflowStep(
                name="计算产品成本",
                description="计算各产品的单位成本和总成本",
                execute_func=self._calculate_product_costs,
                depends_on=["分摊间接成本"]
            ),
            WorkflowStep(
                name="成本差异分析",
                description="分析实际成本与标准成本的差异",
                execute_func=self._analyze_cost_variances,
                depends_on=["计算产品成本"]
            ),
            WorkflowStep(
                name="生成成本报告",
                description="生成成本核算和分析报告",
                execute_func=self._generate_cost_reports,
                depends_on=["成本差异分析"]
            ),
            WorkflowStep(
                name="成本控制建议",
                description="基于分析结果提供成本控制建议",
                execute_func=self._cost_control_recommendations,
                depends_on=["成本差异分析"]
            )
        ]
    
    def _initialize_cost_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """初始化成本数据"""
        # 获取成本核算期间
        period_start = context.get_data("period_start", datetime.now().replace(day=1))
        period_end = context.get_data("period_end", 
            datetime.now().replace(day=1) + timedelta(days=32) - timedelta(days=1))
        
        # 示例成本数据
        cost_data = context.get_data("cost_data", {
            # 直接材料成本
            "direct_materials": [
                {"product": "产品A", "material": "原料1", "quantity": 1000, "unit_cost": Decimal("10.00"), "total_cost": Decimal("10000.00")},
                {"product": "产品A", "material": "原料2", "quantity": 500, "unit_cost": Decimal("15.00"), "total_cost": Decimal("7500.00")},
                {"product": "产品B", "material": "原料1", "quantity": 800, "unit_cost": Decimal("10.00"), "total_cost": Decimal("8000.00")},
                {"product": "产品B", "material": "原料3", "quantity": 300, "unit_cost": Decimal("20.00"), "total_cost": Decimal("6000.00")}
            ],
            # 直接人工成本
            "direct_labor": [
                {"product": "产品A", "department": "生产部门1", "hours": 200, "hourly_rate": Decimal("25.00"), "total_cost": Decimal("5000.00")},
                {"product": "产品A", "department": "生产部门2", "hours": 150, "hourly_rate": Decimal("30.00"), "total_cost": Decimal("4500.00")},
                {"product": "产品B", "department": "生产部门1", "hours": 180, "hourly_rate": Decimal("25.00"), "total_cost": Decimal("4500.00")},
                {"product": "产品B", "department": "生产部门2", "hours": 120, "hourly_rate": Decimal("30.00"), "total_cost": Decimal("3600.00")}
            ],
            # 制造费用
            "manufacturing_overhead": [
                {"cost_type": "设备折旧", "department": "生产部门1", "amount": Decimal("8000.00")},
                {"cost_type": "设备折旧", "department": "生产部门2", "amount": Decimal("6000.00")},
                {"cost_type": "间接材料", "department": "生产部门1", "amount": Decimal("3000.00")},
                {"cost_type": "间接材料", "department": "生产部门2", "amount": Decimal("2500.00")},
                {"cost_type": "间接人工", "department": "生产部门1", "amount": Decimal("4000.00")},
                {"cost_type": "间接人工", "department": "生产部门2", "amount": Decimal("3500.00")},
                {"cost_type": "水电费", "department": "生产部门1", "amount": Decimal("2000.00")},
                {"cost_type": "水电费", "department": "生产部门2", "amount": Decimal("1800.00")}
            ],
            # 产量数据
            "production_volume": [
                {"product": "产品A", "quantity": 100, "unit": "件"},
                {"product": "产品B", "quantity": 80, "unit": "件"}
            ]
        })
        
        # 标准成本数据
        standard_costs = context.get_data("standard_costs", {
            "产品A": {
                "direct_material_cost": Decimal("180.00"),
                "direct_labor_cost": Decimal("95.00"), 
                "manufacturing_overhead_cost": Decimal("120.00"),
                "total_standard_cost": Decimal("395.00")
            },
            "产品B": {
                "direct_material_cost": Decimal("175.00"),
                "direct_labor_cost": Decimal("100.00"),
                "manufacturing_overhead_cost": Decimal("125.00"), 
                "total_standard_cost": Decimal("400.00")
            }
        })
        
        context.set_data("period_start", period_start)
        context.set_data("period_end", period_end)
        context.set_data("cost_data", cost_data)
        context.set_data("standard_costs", standard_costs)
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "products": list(set(item["product"] for item in cost_data["direct_materials"])),
            "total_material_cost": sum(item["total_cost"] for item in cost_data["direct_materials"]),
            "total_labor_cost": sum(item["total_cost"] for item in cost_data["direct_labor"]),
            "total_overhead_cost": sum(item["amount"] for item in cost_data["manufacturing_overhead"])
        }
    
    def _setup_cost_centers(self, context: WorkflowContext) -> List[CostCenter]:
        """设置成本中心"""
        cost_data = context.get_data("cost_data")
        
        # 创建成本中心
        cost_centers = []
        
        # 生产部门成本中心
        dept1_center = CostCenter(
            center_id="CC001",
            center_name="生产部门1",
            center_type="PRODUCTION",
            manager="张经理",
            budget_amount=Decimal("50000.00")
        )
        dept1_center.allocation_basis = AllocationBasis.HOURS
        dept1_center.basis_value = Decimal(str(200 + 180))  # 产品A + 产品B的工时
        
        dept2_center = CostCenter(
            center_id="CC002", 
            center_name="生产部门2",
            center_type="PRODUCTION",
            manager="李经理", 
            budget_amount=Decimal("40000.00")
        )
        dept2_center.allocation_basis = AllocationBasis.HOURS
        dept2_center.basis_value = Decimal(str(150 + 120))
        
        # 辅助部门成本中心
        admin_center = CostCenter(
            center_id="CC003",
            center_name="行政管理部门",
            center_type="SERVICE",
            manager="王经理",
            budget_amount=Decimal("20000.00")
        )
        admin_center.allocation_basis = AllocationBasis.HEADCOUNT
        admin_center.basis_value = Decimal("50")  # 服务人数
        
        cost_centers = [dept1_center, dept2_center, admin_center]
        
        # 将成本归集到成本中心
        for overhead in cost_data["manufacturing_overhead"]:
            if overhead["department"] == "生产部门1":
                dept1_center.actual_amount += Decimal(str(overhead["amount"]))
            elif overhead["department"] == "生产部门2":
                dept2_center.actual_amount += Decimal(str(overhead["amount"]))
        
        context.set_data("cost_centers", cost_centers)
        return cost_centers
    
    def _collect_direct_costs(self, context: WorkflowContext) -> Dict[str, Any]:
        """归集直接成本"""
        cost_data = context.get_data("cost_data")
        
        # 按产品归集直接成本
        product_direct_costs = {}
        
        # 归集直接材料成本
        for material in cost_data["direct_materials"]:
            product = material["product"]
            if product not in product_direct_costs:
                product_direct_costs[product] = {
                    "direct_materials": Decimal("0"),
                    "direct_labor": Decimal("0"),
                    "material_details": [],
                    "labor_details": []
                }
            
            product_direct_costs[product]["direct_materials"] += material["total_cost"]
            product_direct_costs[product]["material_details"].append({
                "material": material["material"],
                "quantity": material["quantity"],
                "unit_cost": material["unit_cost"],
                "total_cost": material["total_cost"]
            })
        
        # 归集直接人工成本
        for labor in cost_data["direct_labor"]:
            product = labor["product"]
            if product not in product_direct_costs:
                product_direct_costs[product] = {
                    "direct_materials": Decimal("0"),
                    "direct_labor": Decimal("0"),
                    "material_details": [],
                    "labor_details": []
                }
            
            product_direct_costs[product]["direct_labor"] += labor["total_cost"]
            product_direct_costs[product]["labor_details"].append({
                "department": labor["department"],
                "hours": labor["hours"],
                "hourly_rate": labor["hourly_rate"],
                "total_cost": labor["total_cost"]
            })
        
        # 计算直接成本合计
        for product, costs in product_direct_costs.items():
            costs["total_direct_cost"] = costs["direct_materials"] + costs["direct_labor"]
        
        context.set_data("product_direct_costs", product_direct_costs)
        return product_direct_costs
    
    def _allocate_indirect_costs(self, context: WorkflowContext) -> Dict[str, Any]:
        """分摊间接成本"""
        cost_centers = context.get_data("cost_centers")
        cost_data = context.get_data("cost_data")
        
        # 使用成本分摊引擎进行分摊
        allocation_results = []
        
        # 获取分摊基础数据
        allocation_basis = {}
        for labor in cost_data["direct_labor"]:
            product = labor["product"]
            if product not in allocation_basis:
                allocation_basis[product] = 0
            allocation_basis[product] += labor["hours"]
        
        total_hours = sum(allocation_basis.values())
        
        # 计算分摊比例
        allocation_rates = {}
        for product, hours in allocation_basis.items():
            allocation_rates[product] = hours / total_hours if total_hours > 0 else 0
        
        # 执行成本分摊
        for center in cost_centers:
            if center.center_type == "PRODUCTION":
                center_total_cost = center.actual_amount
                
                # 简化分摊逻辑
                product_allocations = {}
                for product, labor_hours in allocation_basis.items():
                    allocation_ratio = Decimal(str(labor_hours)) / Decimal(str(total_hours))
                    allocated_amount = center_total_cost * allocation_ratio
                    product_allocations[product] = allocated_amount
                
                allocation_results.append({
                    "cost_center": center.center_name,
                    "total_cost": center_total_cost,
                    "allocation_method": "按直接人工小时分摊",
                    "allocations": product_allocations
                })
        
        # 汇总产品分摊的制造费用
        product_overhead_costs = {}
        for result in allocation_results:
            for product, allocated_amount in result["allocations"].items():
                if product not in product_overhead_costs:
                    product_overhead_costs[product] = Decimal("0")
                product_overhead_costs[product] += allocated_amount
        
        context.set_data("allocation_results", allocation_results)
        context.set_data("product_overhead_costs", product_overhead_costs)
        
        return {
            "allocation_results": allocation_results,
            "product_overhead_costs": product_overhead_costs
        }
    
    def _calculate_product_costs(self, context: WorkflowContext) -> Dict[str, Any]:
        """计算产品成本"""
        product_direct_costs = context.get_data("product_direct_costs")
        product_overhead_costs = context.get_data("product_overhead_costs")
        cost_data = context.get_data("cost_data")
        
        # 获取产量数据
        production_volumes = {}
        for volume in cost_data["production_volume"]:
            production_volumes[volume["product"]] = volume["quantity"]
        
        # 计算产品总成本和单位成本
        product_costs = {}
        
        for product in production_volumes.keys():
            direct_material = product_direct_costs.get(product, {}).get("direct_materials", Decimal("0"))
            direct_labor = product_direct_costs.get(product, {}).get("direct_labor", Decimal("0"))
            overhead = product_overhead_costs.get(product, Decimal("0"))
            
            total_cost = direct_material + direct_labor + overhead
            quantity = production_volumes[product]
            unit_cost = total_cost / quantity if quantity > 0 else Decimal("0")
            
            product_costs[product] = {
                "direct_material_cost": direct_material,
                "direct_labor_cost": direct_labor,
                "manufacturing_overhead_cost": overhead,
                "total_cost": total_cost,
                "production_quantity": quantity,
                "unit_cost": unit_cost,
                "cost_breakdown": {
                    "material_percentage": (direct_material / total_cost * 100) if total_cost > 0 else 0,
                    "labor_percentage": (direct_labor / total_cost * 100) if total_cost > 0 else 0,
                    "overhead_percentage": (overhead / total_cost * 100) if total_cost > 0 else 0
                }
            }
        
        context.set_data("product_costs", product_costs)
        return product_costs
    
    def _analyze_cost_variances(self, context: WorkflowContext) -> Dict[str, Any]:
        """成本差异分析"""
        product_costs = context.get_data("product_costs")
        standard_costs = context.get_data("standard_costs")
        
        variance_analysis = {}
        
        for product, actual_costs in product_costs.items():
            if product in standard_costs:
                standard = standard_costs[product]
                
                # 计算各项成本差异
                material_variance = actual_costs["direct_material_cost"] / actual_costs["production_quantity"] - standard["direct_material_cost"]
                labor_variance = actual_costs["direct_labor_cost"] / actual_costs["production_quantity"] - standard["direct_labor_cost"]
                overhead_variance = actual_costs["manufacturing_overhead_cost"] / actual_costs["production_quantity"] - standard["manufacturing_overhead_cost"]
                total_variance = actual_costs["unit_cost"] - standard["total_standard_cost"]
                
                # 计算差异率
                material_variance_rate = (material_variance / standard["direct_material_cost"] * 100) if standard["direct_material_cost"] > 0 else 0
                labor_variance_rate = (labor_variance / standard["direct_labor_cost"] * 100) if standard["direct_labor_cost"] > 0 else 0
                overhead_variance_rate = (overhead_variance / standard["manufacturing_overhead_cost"] * 100) if standard["manufacturing_overhead_cost"] > 0 else 0
                total_variance_rate = (total_variance / standard["total_standard_cost"] * 100) if standard["total_standard_cost"] > 0 else 0
                
                variance_analysis[product] = {
                    "actual_unit_cost": actual_costs["unit_cost"],
                    "standard_unit_cost": standard["total_standard_cost"],
                    "material_variance": material_variance,
                    "labor_variance": labor_variance,
                    "overhead_variance": overhead_variance,
                    "total_variance": total_variance,
                    "material_variance_rate": round(material_variance_rate, 2),
                    "labor_variance_rate": round(labor_variance_rate, 2),
                    "overhead_variance_rate": round(overhead_variance_rate, 2),
                    "total_variance_rate": round(total_variance_rate, 2),
                    "variance_analysis": self._interpret_variances(material_variance, labor_variance, overhead_variance, total_variance)
                }
        
        context.set_data("variance_analysis", variance_analysis)
        return variance_analysis
    
    def _interpret_variances(self, material_var: Decimal, labor_var: Decimal, 
                           overhead_var: Decimal, total_var: Decimal) -> Dict[str, str]:
        """解释成本差异"""
        interpretation = {}
        
        # 材料成本差异分析
        if abs(material_var) < Decimal("5.00"):
            interpretation["material"] = "材料成本差异较小，在可控范围内"
        elif material_var > 0:
            interpretation["material"] = "材料成本超标，需检查采购价格和用料标准"
        else:
            interpretation["material"] = "材料成本节约，可能存在质量风险或采购优势"
        
        # 人工成本差异分析
        if abs(labor_var) < Decimal("5.00"):
            interpretation["labor"] = "人工成本差异较小，效率正常"
        elif labor_var > 0:
            interpretation["labor"] = "人工成本超标，需检查工作效率和工资标准"
        else:
            interpretation["labor"] = "人工成本节约，生产效率较高"
        
        # 制造费用差异分析
        if abs(overhead_var) < Decimal("10.00"):
            interpretation["overhead"] = "制造费用差异可控"
        elif overhead_var > 0:
            interpretation["overhead"] = "制造费用超标，需检查费用控制和分摊标准"
        else:
            interpretation["overhead"] = "制造费用节约，成本控制良好"
        
        # 总成本差异分析
        if abs(total_var) < Decimal("10.00"):
            interpretation["total"] = "总成本基本符合预期"
        elif total_var > 0:
            interpretation["total"] = "总成本超标，需要加强成本控制"
        else:
            interpretation["total"] = "总成本低于标准，成本控制效果良好"
        
        return interpretation
    
    def _generate_cost_reports(self, context: WorkflowContext) -> Dict[str, Any]:
        """生成成本报告"""
        product_costs = context.get_data("product_costs")
        variance_analysis = context.get_data("variance_analysis")
        allocation_results = context.get_data("allocation_results")
        period_start = context.get_data("period_start")
        period_end = context.get_data("period_end")
        
        # 成本汇总报告
        cost_summary = {
            "report_period": f"{period_start.strftime('%Y-%m-%d')} 至 {period_end.strftime('%Y-%m-%d')}",
            "total_production_cost": sum(costs["total_cost"] for costs in product_costs.values()),
            "total_direct_material": sum(costs["direct_material_cost"] for costs in product_costs.values()),
            "total_direct_labor": sum(costs["direct_labor_cost"] for costs in product_costs.values()),
            "total_manufacturing_overhead": sum(costs["manufacturing_overhead_cost"] for costs in product_costs.values()),
            "products_produced": len(product_costs),
            "cost_per_product": product_costs
        }
        
        # 差异分析报告
        variance_summary = {
            "products_analyzed": len(variance_analysis),
            "variance_details": variance_analysis,
            "total_variance_amount": sum(
                analysis["total_variance"] * product_costs[product]["production_quantity"]
                for product, analysis in variance_analysis.items()
                if product in product_costs
            ),
            "variance_trends": self._analyze_variance_trends(variance_analysis)
        }
        
        # 成本分摊报告
        allocation_summary = {
            "allocation_methods_used": len(allocation_results),
            "total_overhead_allocated": sum(result["total_cost"] for result in allocation_results),
            "allocation_details": allocation_results
        }
        
        cost_reports = {
            "cost_summary": cost_summary,
            "variance_summary": variance_summary,
            "allocation_summary": allocation_summary,
            "report_generated_at": datetime.now()
        }
        
        context.set_data("cost_reports", cost_reports)
        return cost_reports
    
    def _analyze_variance_trends(self, variance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析差异趋势"""
        if not variance_analysis:
            return {}
        
        # 统计各类差异的分布
        material_variances = [analysis["material_variance"] for analysis in variance_analysis.values()]
        labor_variances = [analysis["labor_variance"] for analysis in variance_analysis.values()]
        overhead_variances = [analysis["overhead_variance"] for analysis in variance_analysis.values()]
        
        trends = {
            "material_trend": {
                "avg_variance": sum(material_variances) / len(material_variances),
                "max_variance": max(material_variances),
                "min_variance": min(material_variances),
                "variance_count": len([v for v in material_variances if abs(v) > Decimal("5.00")])
            },
            "labor_trend": {
                "avg_variance": sum(labor_variances) / len(labor_variances),
                "max_variance": max(labor_variances),
                "min_variance": min(labor_variances),
                "variance_count": len([v for v in labor_variances if abs(v) > Decimal("5.00")])
            },
            "overhead_trend": {
                "avg_variance": sum(overhead_variances) / len(overhead_variances),
                "max_variance": max(overhead_variances),
                "min_variance": min(overhead_variances),
                "variance_count": len([v for v in overhead_variances if abs(v) > Decimal("10.00")])
            }
        }
        
        return trends
    
    def _cost_control_recommendations(self, context: WorkflowContext) -> List[Dict[str, Any]]:
        """成本控制建议"""
        variance_analysis = context.get_data("variance_analysis")
        cost_reports = context.get_data("cost_reports")
        
        recommendations = []
        
        # 基于差异分析提供建议
        for product, analysis in variance_analysis.items():
            product_recommendations = []
            
            # 材料成本建议
            if analysis["material_variance"] > Decimal("10.00"):
                product_recommendations.append({
                    "category": "材料成本控制",
                    "priority": "HIGH",
                    "recommendation": "材料成本严重超标，建议：1）重新评估供应商价格；2）检查材料用量标准；3）加强采购管理",
                    "expected_savings": analysis["material_variance"] * Decimal("0.5")
                })
            elif analysis["material_variance"] > Decimal("5.00"):
                product_recommendations.append({
                    "category": "材料成本优化",
                    "priority": "MEDIUM",
                    "recommendation": "材料成本轻微超标，庭议优化采购流程和供应商管理",
                    "expected_savings": analysis["material_variance"] * Decimal("0.3")
                })
            
            # 人工成本建议
            if analysis["labor_variance"] > Decimal("10.00"):
                product_recommendations.append({
                    "category": "人工效率提升",
                    "priority": "HIGH", 
                    "recommendation": "人工成本严重超标，庭议：1）分析生产流程效率；2）加强员工培训；3）考虑工艺改进",
                    "expected_savings": analysis["labor_variance"] * Decimal("0.4")
                })
            elif analysis["labor_variance"] > Decimal("5.00"):
                product_recommendations.append({
                    "category": "生产效率优化",
                    "priority": "MEDIUM",
                    "recommendation": "人工效率有待提升，廚议优化生产流程和工作方法",
                    "expected_savings": analysis["labor_variance"] * Decimal("0.2")
                })
            
            # 制造费用廚议
            if analysis["overhead_variance"] > Decimal("15.00"):
                product_recommendations.append({
                    "category": "制造费用控制",
                    "priority": "HIGH",
                    "recommendation": "制造费用超标较多，庺议：1）重新评估费用分摊标准；2）控制间接费用支出；3）提高设备利用率",
                    "expected_savings": analysis["overhead_variance"] * Decimal("0.3")
                })
            
            if product_recommendations:
                recommendations.append({
                    "product": product,
                    "total_variance": analysis["total_variance"],
                    "recommendations": product_recommendations,
                    "priority_level": max(rec["priority"] for rec in product_recommendations)
                })
        
        # 整体成本控制庺议
        total_variance = sum(analysis["total_variance"] for analysis in variance_analysis.values())
        if total_variance > Decimal("20.00"):
            recommendations.append({
                "product": "整体成本控制",
                "total_variance": total_variance,
                "recommendations": [{
                    "category": "全面成本管理",
                    "priority": "HIGH",
                    "recommendation": "整体成本偏差较大，廊议：1）建立更完善的成本控制体系；2）加强预算管理；3）实施成本分析月度例会制度",
                    "expected_savings": total_variance * Decimal("0.3")
                }],
                "priority_level": "HIGH"
            })
        
        context.set_data("cost_control_recommendations", recommendations)
        return recommendations
