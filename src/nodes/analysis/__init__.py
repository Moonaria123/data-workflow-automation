"""
数据分析节点模块

提供各种数据分析功能的节点实现
"""

from .statistical_analysis import StatisticalAnalysisNode
from .trend_analysis import TrendAnalysisNode
from .correlation_analysis import CorrelationAnalysisNode
from .regression_analysis import RegressionAnalysisNode
from .anomaly_detection import AnomalyDetectionNode

__all__ = [
    'StatisticalAnalysisNode',
    'TrendAnalysisNode', 
    'CorrelationAnalysisNode',
    'RegressionAnalysisNode',
    'AnomalyDetectionNode'
]