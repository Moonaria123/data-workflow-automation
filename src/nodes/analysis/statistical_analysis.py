"""
统计分析节点

提供基础统计分析功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class StatisticalAnalysisNode(BaseNode):
    """统计分析节点"""
    
    def __init__(self):
        super().__init__(
            name="统计分析",
            node_type=NodeType.ANALYSIS,
            category=NodeCategory.ANALYSIS,
            description="执行基础统计分析，包括描述性统计、分布分析等"
        )
        
        # 配置属性
        self.add_property("analysis_type", "descriptive", str, "分析类型",
                         options=["descriptive", "distribution", "hypothesis_test"])
        self.add_property("confidence_level", 0.95, float, "置信水平")
        self.add_property("columns", [], list, "分析列")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("statistics", "Dict", "统计结果")
        self.add_output_port("summary", "DataFrame", "统计摘要")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行统计分析"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            analysis_type = self.get_property("analysis_type")
            confidence_level = self.get_property("confidence_level")
            columns = self.get_property("columns") or data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not columns:
                raise NodeExecutionError("没有找到数值列进行分析")
            
            # 过滤数值列
            numeric_data = data[columns]
            
            if analysis_type == "descriptive":
                results = self._descriptive_analysis(numeric_data, confidence_level)
            elif analysis_type == "distribution":
                results = self._distribution_analysis(numeric_data)
            elif analysis_type == "hypothesis_test":
                results = self._hypothesis_test(numeric_data, confidence_level)
            else:
                raise NodeExecutionError(f"不支持的分析类型: {analysis_type}")
            
            return {
                "statistics": results,
                "summary": pd.DataFrame(results).T if isinstance(results, dict) else results
            }
            
        except Exception as e:
            raise NodeExecutionError(f"统计分析执行失败: {str(e)}")
    
    def _descriptive_analysis(self, data: pd.DataFrame, confidence_level: float) -> Dict[str, Any]:
        """描述性统计分析"""
        results = {}
        
        for column in data.columns:
            col_data = data[column].dropna()
            if len(col_data) == 0:
                continue
            
            # 基础统计量
            stats_dict = {
                "count": len(col_data),
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "std": float(col_data.std()),
                "var": float(col_data.var()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "range": float(col_data.max() - col_data.min()),
                "skewness": float(col_data.skew()),
                "kurtosis": float(col_data.kurtosis())
            }
            
            # 分位数
            quantiles = col_data.quantile([0.25, 0.5, 0.75])
            stats_dict.update({
                "q1": float(quantiles[0.25]),
                "q2": float(quantiles[0.5]),
                "q3": float(quantiles[0.75]),
                "iqr": float(quantiles[0.75] - quantiles[0.25])
            })
            
            # 置信区间
            if len(col_data) > 1:
                alpha = 1 - confidence_level
                sem = stats.sem(col_data)
                ci = stats.t.interval(confidence_level, len(col_data) - 1, 
                                     loc=col_data.mean(), scale=sem)
                stats_dict["confidence_interval"] = [float(ci[0]), float(ci[1])]
            
            results[column] = stats_dict
        
        return results
    
    def _distribution_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分布分析"""
        results = {}
        
        for column in data.columns:
            col_data = data[column].dropna()
            if len(col_data) < 3:
                continue
            
            # 正态性检验
            shapiro_stat, shapiro_p = stats.shapiro(col_data)
            
            # Kolmogorov-Smirnov检验
            ks_stat, ks_p = stats.kstest(col_data, 'norm', 
                                        args=(col_data.mean(), col_data.std()))
            
            results[column] = {
                "shapiro_wilk": {
                    "statistic": float(shapiro_stat),
                    "p_value": float(shapiro_p),
                    "is_normal": shapiro_p > 0.05
                },
                "kolmogorov_smirnov": {
                    "statistic": float(ks_stat),
                    "p_value": float(ks_p),
                    "is_normal": ks_p > 0.05
                }
            }
        
        return results
    
    def _hypothesis_test(self, data: pd.DataFrame, confidence_level: float) -> Dict[str, Any]:
        """假设检验"""
        results = {}
        columns = data.columns.tolist()
        
        # 单样本t检验 (检验均值是否为0)
        for column in columns:
            col_data = data[column].dropna()
            if len(col_data) < 2:
                continue
            
            t_stat, p_value = stats.ttest_1samp(col_data, 0)
            
            results[f"{column}_ttest"] = {
                "test_type": "one_sample_ttest",
                "null_hypothesis": "mean = 0",
                "statistic": float(t_stat),
                "p_value": float(p_value),
                "reject_null": p_value < (1 - confidence_level),
                "confidence_level": confidence_level
            }
        
        # 双样本t检验 (如果有多列)
        if len(columns) >= 2:
            for i in range(len(columns)):
                for j in range(i + 1, len(columns)):
                    col1_data = data[columns[i]].dropna()
                    col2_data = data[columns[j]].dropna()
                    
                    if len(col1_data) < 2 or len(col2_data) < 2:
                        continue
                    
                    # 等方差ft检验
                    t_stat, p_value = stats.ttest_ind(col1_data, col2_data)
                    
                    results[f"{columns[i]}_vs_{columns[j]}_ttest"] = {
                        "test_type": "two_sample_ttest",
                        "null_hypothesis": "means are equal",
                        "statistic": float(t_stat),
                        "p_value": float(p_value),
                        "reject_null": p_value < (1 - confidence_level),
                        "confidence_level": confidence_level
                    }
        
        return results
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty