"""
异常检测节点

提供异常检测功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from scipy import stats

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class AnomalyDetectionNode(BaseNode):
    """异常检测节点"""
    
    def __init__(self):
        super().__init__(
            name="异常检测",
            node_type=NodeType.ANALYSIS,
            category=NodeCategory.ANALYSIS,
            description="执行异常检测，支持统计方法、孤立森林、局部异常因子等"
        )
        
        # 配置属性
        self.add_property("detection_method", "isolation_forest", str, "检测方法",
                         options=["statistical", "isolation_forest", "local_outlier_factor", "one_class_svm"])
        self.add_property("contamination", 0.1, float, "异常比例")
        self.add_property("columns", [], list, "检测列")
        self.add_property("z_threshold", 3.0, float, "Z分数阈值")
        self.add_property("iqr_multiplier", 1.5, float, "IQR倍数")
        self.add_property("random_state", 42, int, "随机种子")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("anomaly_results", "DataFrame", "异常检测结果")
        self.add_output_port("anomaly_summary", "Dict", "异常检测摘要")
        self.add_output_port("anomaly_scores", "DataFrame", "异常分数")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行异常检测"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            detection_method = self.get_property("detection_method")
            contamination = self.get_property("contamination")
            columns = self.get_property("columns")
            z_threshold = self.get_property("z_threshold")
            iqr_multiplier = self.get_property("iqr_multiplier")
            random_state = self.get_property("random_state")
            
            # 选择检测列
            if not columns:
                columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not columns:
                raise NodeExecutionError("没有找到数值列进行异常检测")
            
            # 过滤数据
            detection_data = data[columns].dropna()
            
            if detection_data.empty:
                raise NodeExecutionError("过滤后数据为空")
            
            # 执行异常检测
            if detection_method == "statistical":
                results = self._statistical_anomaly_detection(detection_data, z_threshold, iqr_multiplier)
            elif detection_method == "isolation_forest":
                results = self._isolation_forest_detection(detection_data, contamination, random_state)
            elif detection_method == "local_outlier_factor":
                results = self._lof_detection(detection_data, contamination)
            elif detection_method == "one_class_svm":
                results = self._one_class_svm_detection(detection_data, contamination, random_state)
            else:
                raise NodeExecutionError(f"不支持的检测方法: {detection_method}")
            
            # 合并原始数据
            result_data = data.copy()
            result_data = result_data.iloc[detection_data.index]
            
            for key, value in results.items():
                if isinstance(value, (list, np.ndarray)) and len(value) == len(result_data):
                    result_data[key] = value
            
            # 生成摘要
            anomaly_count = np.sum(results.get('is_anomaly', []))
            total_count = len(detection_data)
            
            anomaly_summary = {
                "detection_method": detection_method,
                "total_records": total_count,
                "anomaly_count": int(anomaly_count),
                "anomaly_rate": float(anomaly_count / total_count) if total_count > 0 else 0,
                "detection_columns": columns,
                "parameters": {
                    "contamination": contamination,
                    "z_threshold": z_threshold,
                    "iqr_multiplier": iqr_multiplier
                }
            }
            
            # 异常分数DataFrame
            score_columns = [key for key in results.keys() if 'score' in key]
            if score_columns:
                scores_df = pd.DataFrame({col: results[col] for col in score_columns})
                scores_df['is_anomaly'] = results.get('is_anomaly', [False] * len(detection_data))
            else:
                scores_df = pd.DataFrame({'is_anomaly': results.get('is_anomaly', [False] * len(detection_data))})
            
            return {
                "anomaly_results": result_data,
                "anomaly_summary": anomaly_summary,
                "anomaly_scores": scores_df
            }
            
        except Exception as e:
            raise NodeExecutionError(f"异常检测执行失败: {str(e)}")
    
    def _statistical_anomaly_detection(self, data: pd.DataFrame, z_threshold: float, iqr_multiplier: float) -> Dict[str, Any]:
        """统计方法异常检测"""
        results = {}
        is_anomaly = np.zeros(len(data), dtype=bool)
        z_scores = np.zeros((len(data), len(data.columns)))
        iqr_flags = np.zeros((len(data), len(data.columns)), dtype=bool)
        
        for i, column in enumerate(data.columns):
            col_data = data[column].values
            
            # Z分数方法
            z_score = np.abs(stats.zscore(col_data))
            z_anomalies = z_score > z_threshold
            z_scores[:, i] = z_score
            
            # IQR方法
            Q1 = np.percentile(col_data, 25)
            Q3 = np.percentile(col_data, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - iqr_multiplier * IQR
            upper_bound = Q3 + iqr_multiplier * IQR
            iqr_anomalies = (col_data < lower_bound) | (col_data > upper_bound)
            iqr_flags[:, i] = iqr_anomalies
            
            # 合并异常标记
            is_anomaly = is_anomaly | z_anomalies | iqr_anomalies
        
        # 计算平均Z分数作为异常分数
        anomaly_scores = np.mean(z_scores, axis=1)
        
        results['is_anomaly'] = is_anomaly
        results['anomaly_score'] = anomaly_scores
        results['max_z_score'] = np.max(z_scores, axis=1)
        results['z_score_flags'] = np.any(z_scores > z_threshold, axis=1)
        results['iqr_flags'] = np.any(iqr_flags, axis=1)
        
        return results
    
    def _isolation_forest_detection(self, data: pd.DataFrame, contamination: float, random_state: int) -> Dict[str, Any]:
        """孤立森林异常检测"""
        model = IsolationForest(contamination=contamination, random_state=random_state)
        
        # 训练和预测
        anomaly_labels = model.fit_predict(data)
        anomaly_scores = model.score_samples(data)
        
        # -1表示异常，1表示正常
        is_anomaly = anomaly_labels == -1
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': -anomaly_scores,  # 转换为正分数，分数越高越异常
            'isolation_score': anomaly_scores
        }
    
    def _lof_detection(self, data: pd.DataFrame, contamination: float) -> Dict[str, Any]:
        """局部异常因子检测"""
        model = LocalOutlierFactor(contamination=contamination)
        
        # 预测
        anomaly_labels = model.fit_predict(data)
        negative_outlier_factor = model.negative_outlier_factor_
        
        # -1表示异常，1表示正常
        is_anomaly = anomaly_labels == -1
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': -negative_outlier_factor,  # 转换为正分数
            'lof_score': negative_outlier_factor
        }
    
    def _one_class_svm_detection(self, data: pd.DataFrame, contamination: float, random_state: int) -> Dict[str, Any]:
        """单类SVM异常检测"""
        nu = contamination  # nu参数近似等于异常比例
        model = OneClassSVM(nu=nu, kernel='rbf', gamma='scale')
        
        # 训练和预测
        anomaly_labels = model.fit_predict(data)
        decision_scores = model.score_samples(data)
        
        # -1表示异常，1表示正常
        is_anomaly = anomaly_labels == -1
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': -decision_scores,  # 转换为正分数
            'svm_decision_score': decision_scores
        }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty