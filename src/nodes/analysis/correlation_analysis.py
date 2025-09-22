"""
相关性分析节点

提供数据相关性分析功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.feature_selection import mutual_info_regression

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class CorrelationAnalysisNode(BaseNode):
    """相关性分析节点"""
    
    def __init__(self):
        super().__init__(
            name="相关性分析",
            node_type=NodeType.ANALYSIS,
            category=NodeCategory.ANALYSIS,
            description="执行数据相关性分析，包括Pearson、Spearman相关系数等"
        )
        
        # 配置属性
        self.add_property("correlation_method", "pearson", str, "相关方法",
                         options=["pearson", "spearman", "kendall", "mutual_info"])
        self.add_property("significance_level", 0.05, float, "显著性水平")
        self.add_property("columns", [], list, "分析列")
        self.add_property("target_column", "", str, "目标列")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("correlation_matrix", "DataFrame", "相关矩阵")
        self.add_output_port("significance_matrix", "DataFrame", "显著性矩阵")
        self.add_output_port("correlation_pairs", "DataFrame", "相关对排序")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行相关性分析"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            correlation_method = self.get_property("correlation_method")
            significance_level = self.get_property("significance_level")
            columns = self.get_property("columns")
            target_column = self.get_property("target_column")
            
            # 选择数值列
            if not columns:
                columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not columns:
                raise NodeExecutionError("没有找到数值列进行分析")
            
            # 过滤数据
            numeric_data = data[columns].dropna()
            
            if numeric_data.empty:
                raise NodeExecutionError("过滤后数据为空")
            
            # 计算相关性
            if correlation_method == "mutual_info":
                corr_matrix, sig_matrix = self._mutual_info_analysis(numeric_data, target_column)
            else:
                corr_matrix, sig_matrix = self._correlation_analysis(numeric_data, correlation_method, significance_level)
            
            # 生成相关对排序
            correlation_pairs = self._generate_correlation_pairs(corr_matrix, sig_matrix)
            
            return {
                "correlation_matrix": corr_matrix,
                "significance_matrix": sig_matrix,
                "correlation_pairs": correlation_pairs
            }
            
        except Exception as e:
            raise NodeExecutionError(f"相关性分析执行失败: {str(e)}")
    
    def _correlation_analysis(self, data: pd.DataFrame, method: str, significance_level: float):
        """计算相关系数和显著性"""
        n_vars = len(data.columns)
        corr_matrix = np.zeros((n_vars, n_vars))
        sig_matrix = np.zeros((n_vars, n_vars))
        
        for i, col1 in enumerate(data.columns):
            for j, col2 in enumerate(data.columns):
                if i == j:
                    corr_matrix[i, j] = 1.0
                    sig_matrix[i, j] = 0.0
                else:
                    x = data[col1].values
                    y = data[col2].values
                    
                    if method == "pearson":
                        corr, p_value = stats.pearsonr(x, y)
                    elif method == "spearman":
                        corr, p_value = stats.spearmanr(x, y)
                    elif method == "kendall":
                        corr, p_value = stats.kendalltau(x, y)
                    else:
                        raise NodeExecutionError(f"不支持的相关方法: {method}")
                    
                    corr_matrix[i, j] = corr
                    sig_matrix[i, j] = p_value
        
        # 转换为DataFrame
        corr_df = pd.DataFrame(corr_matrix, index=data.columns, columns=data.columns)
        sig_df = pd.DataFrame(sig_matrix, index=data.columns, columns=data.columns)
        
        return corr_df, sig_df
    
    def _mutual_info_analysis(self, data: pd.DataFrame, target_column: str):
        """互信息分析"""
        if not target_column or target_column not in data.columns:
            # 如果没有指定目标列，使用第一列
            target_column = data.columns[0]
        
        # 准备数据
        feature_columns = [col for col in data.columns if col != target_column]
        X = data[feature_columns]
        y = data[target_column]
        
        # 计算互信息
        mi_scores = mutual_info_regression(X, y, random_state=42)
        
        # 创建互信息矩阵
        n_vars = len(data.columns)
        mi_matrix = np.zeros((n_vars, n_vars))
        
        target_idx = data.columns.get_loc(target_column)
        
        for i, col in enumerate(data.columns):
            if col == target_column:
                mi_matrix[i, target_idx] = 1.0
                mi_matrix[target_idx, i] = 1.0
            else:
                feature_idx = feature_columns.index(col)
                mi_score = mi_scores[feature_idx]
                mi_matrix[i, target_idx] = mi_score
                mi_matrix[target_idx, i] = mi_score
        
        # 转换为DataFrame
        mi_df = pd.DataFrame(mi_matrix, index=data.columns, columns=data.columns)
        sig_df = pd.DataFrame(np.zeros_like(mi_matrix), index=data.columns, columns=data.columns)
        
        return mi_df, sig_df
    
    def _generate_correlation_pairs(self, corr_matrix: pd.DataFrame, sig_matrix: pd.DataFrame) -> pd.DataFrame:
        """生成相关对排序"""
        pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                p_value = sig_matrix.iloc[i, j]
                
                pairs.append({
                    "variable_1": col1,
                    "variable_2": col2,
                    "correlation": correlation,
                    "abs_correlation": abs(correlation),
                    "p_value": p_value,
                    "significant": p_value < self.get_property("significance_level"),
                    "strength": self._correlation_strength(abs(correlation))
                })
        
        # 按绝对值排序
        pairs_df = pd.DataFrame(pairs)
        pairs_df = pairs_df.sort_values("abs_correlation", ascending=False)
        
        return pairs_df
    
    def _correlation_strength(self, abs_corr: float) -> str:
        """判断相关强度"""
        if abs_corr >= 0.7:
            return "strong"
        elif abs_corr >= 0.3:
            return "moderate"
        else:
            return "weak"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty