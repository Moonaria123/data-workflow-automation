"""
趋势分析节点

提供时间序列趋势分析功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class TrendAnalysisNode(BaseNode):
    """趋势分析节点"""
    
    def __init__(self):
        super().__init__(
            name="趋势分析",
            node_type=NodeType.ANALYSIS,
            category=NodeCategory.ANALYSIS,
            description="执行时间序列趋势分析，包括线性趋势、季节性分析等"
        )
        
        # 配置属性
        self.add_property("time_column", "", str, "时间列名")
        self.add_property("value_column", "", str, "数值列名")
        self.add_property("trend_type", "linear", str, "趋势类型",
                         options=["linear", "polynomial", "moving_average"])
        self.add_property("polynomial_degree", 2, int, "多项式度数")
        self.add_property("window_size", 5, int, "移动平均窗口大小")
        self.add_property("seasonal_period", 12, int, "季节周期")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入时间序列数据")
        
        # 输出端口
        self.add_output_port("trend_results", "Dict", "趋势分析结果")
        self.add_output_port("fitted_data", "DataFrame", "拟合数据")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行趋势分析"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            time_column = self.get_property("time_column")
            value_column = self.get_property("value_column")
            trend_type = self.get_property("trend_type")
            
            # 数据预处理
            if time_column and time_column in data.columns:
                # 确保时间列是datetime类型
                if not pd.api.types.is_datetime64_any_dtype(data[time_column]):
                    data[time_column] = pd.to_datetime(data[time_column])
                data_sorted = data.sort_values(time_column).copy()
            else:
                # 如果没有指定时间列，使用索引
                data_sorted = data.copy()
                time_column = 'index'
                data_sorted[time_column] = range(len(data_sorted))
            
            if not value_column or value_column not in data_sorted.columns:
                # 选择第一个数值列
                numeric_cols = data_sorted.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    raise NodeExecutionError("没有找到数值列")
                value_column = numeric_cols[0]
            
            # 执行趋势分析
            if trend_type == "linear":
                results = self._linear_trend_analysis(data_sorted, time_column, value_column)
            elif trend_type == "polynomial":
                results = self._polynomial_trend_analysis(data_sorted, time_column, value_column)
            elif trend_type == "moving_average":
                results = self._moving_average_analysis(data_sorted, time_column, value_column)
            else:
                raise NodeExecutionError(f"不支持的趋势类型: {trend_type}")
            
            return results
            
        except Exception as e:
            raise NodeExecutionError(f"趋势分析执行失败: {str(e)}")
    
    def _linear_trend_analysis(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """线性趋势分析"""
        # 准备数据
        y = data[value_col].dropna()
        if time_col == 'index':
            x = np.arange(len(y)).reshape(-1, 1)
        else:
            # 将时间转换为数值
            time_values = data[time_col].iloc[:len(y)]
            x = np.arange(len(time_values)).reshape(-1, 1)
        
        # 线性回归
        model = LinearRegression()
        model.fit(x, y)
        
        # 预测值
        y_pred = model.predict(x)
        
        # 统计指标
        slope = model.coef_[0]
        intercept = model.intercept_
        r_squared = model.score(x, y)
        
        # 显著性检验
        t_stat, p_value = stats.pearsonr(x.flatten(), y)
        
        # 创建结果DataFrame
        result_data = data.copy()
        result_data['fitted_values'] = y_pred
        result_data['residuals'] = y - y_pred
        
        return {
            "trend_results": {
                "trend_type": "linear",
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_squared),
                "correlation": float(t_stat),
                "p_value": float(p_value),
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "trend_strength": "strong" if abs(t_stat) > 0.7 else "moderate" if abs(t_stat) > 0.3 else "weak"
            },
            "fitted_data": result_data
        }
    
    def _polynomial_trend_analysis(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """多项式趋势分析"""
        degree = self.get_property("polynomial_degree")
        
        # 准备数据
        y = data[value_col].dropna()
        if time_col == 'index':
            x = np.arange(len(y)).reshape(-1, 1)
        else:
            time_values = data[time_col].iloc[:len(y)]
            x = np.arange(len(time_values)).reshape(-1, 1)
        
        # 多项式特征
        poly_features = PolynomialFeatures(degree=degree)
        x_poly = poly_features.fit_transform(x)
        
        # 多项式回归
        model = LinearRegression()
        model.fit(x_poly, y)
        
        # 预测值
        y_pred = model.predict(x_poly)
        
        # 统计指标
        r_squared = model.score(x_poly, y)
        coefficients = model.coef_
        
        # 创建结果DataFrame
        result_data = data.copy()
        result_data['fitted_values'] = y_pred
        result_data['residuals'] = y - y_pred
        
        return {
            "trend_results": {
                "trend_type": "polynomial",
                "degree": degree,
                "coefficients": coefficients.tolist(),
                "intercept": float(model.intercept_),
                "r_squared": float(r_squared),
                "trend_complexity": "high" if degree > 2 else "moderate"
            },
            "fitted_data": result_data
        }
    
    def _moving_average_analysis(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """移动平均分析"""
        window_size = self.get_property("window_size")
        
        # 计算移动平均
        data_copy = data.copy()
        data_copy['moving_average'] = data_copy[value_col].rolling(window=window_size, center=True).mean()
        data_copy['trend'] = data_copy['moving_average']
        
        # 计算趋势强度
        original_values = data_copy[value_col].dropna()
        trend_values = data_copy['trend'].dropna()
        
        if len(trend_values) > 1:
            # 计算趋势的斜率
            x = np.arange(len(trend_values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, trend_values)
            
            trend_strength = abs(r_value)
        else:
            slope = 0
            r_value = 0
            p_value = 1
            trend_strength = 0
        
        return {
            "trend_results": {
                "trend_type": "moving_average",
                "window_size": window_size,
                "trend_slope": float(slope),
                "trend_correlation": float(r_value),
                "p_value": float(p_value),
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "trend_strength": "strong" if trend_strength > 0.7 else "moderate" if trend_strength > 0.3 else "weak"
            },
            "fitted_data": data_copy
        }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty