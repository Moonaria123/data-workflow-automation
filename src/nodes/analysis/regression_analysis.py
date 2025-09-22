"""
回归分析节点

提供回归分析功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class RegressionAnalysisNode(BaseNode):
    """回归分析节点"""
    
    def __init__(self):
        super().__init__(
            name="回归分析",
            node_type=NodeType.ANALYSIS,
            category=NodeCategory.ANALYSIS,
            description="执行回归分析，支持线性回归、岭回归、Lasso回归等"
        )
        
        # 配置属性
        self.add_property("regression_type", "linear", str, "回归类型",
                         options=["linear", "ridge", "lasso", "random_forest"])
        self.add_property("target_column", "", str, "目标变量列")
        self.add_property("feature_columns", [], list, "特征列")
        self.add_property("test_size", 0.2, float, "测试集比例")
        self.add_property("alpha", 1.0, float, "正则化参数")
        self.add_property("random_state", 42, int, "随机种子")
        self.add_property("normalize_features", True, bool, "特征标准化")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("model_results", "Dict", "模型结果")
        self.add_output_port("predictions", "DataFrame", "预测结果")
        self.add_output_port("feature_importance", "DataFrame", "特征重要性")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行回归分析"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            regression_type = self.get_property("regression_type")
            target_column = self.get_property("target_column")
            feature_columns = self.get_property("feature_columns")
            test_size = self.get_property("test_size")
            alpha = self.get_property("alpha")
            random_state = self.get_property("random_state")
            normalize_features = self.get_property("normalize_features")
            
            # 数据预处理
            X, y, feature_names = self._prepare_data(data, target_column, feature_columns)
            
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 特征标准化
            if normalize_features:
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)
            
            # 创建模型
            if regression_type == "linear":
                model = LinearRegression()
            elif regression_type == "ridge":
                model = Ridge(alpha=alpha, random_state=random_state)
            elif regression_type == "lasso":
                model = Lasso(alpha=alpha, random_state=random_state)
            elif regression_type == "random_forest":
                model = RandomForestRegressor(n_estimators=100, random_state=random_state)
            else:
                raise NodeExecutionError(f"不支持的回归类型: {regression_type}")
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # 评估指标
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            train_mse = mean_squared_error(y_train, y_train_pred)
            test_mse = mean_squared_error(y_test, y_test_pred)
            train_mae = mean_absolute_error(y_train, y_train_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)
            
            # 交叉验证
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            
            # 特征重要性
            feature_importance = self._get_feature_importance(model, feature_names, regression_type)
            
            # 预测结果DataFrame
            predictions_df = pd.DataFrame({
                'actual': np.concatenate([y_train, y_test]),
                'predicted': np.concatenate([y_train_pred, y_test_pred]),
                'dataset': ['train'] * len(y_train) + ['test'] * len(y_test)
            })
            predictions_df['residual'] = predictions_df['actual'] - predictions_df['predicted']
            
            model_results = {
                "regression_type": regression_type,
                "target_column": target_column,
                "feature_count": len(feature_names),
                "train_size": len(X_train),
                "test_size": len(X_test),
                "metrics": {
                    "train_r2": float(train_r2),
                    "test_r2": float(test_r2),
                    "train_mse": float(train_mse),
                    "test_mse": float(test_mse),
                    "train_mae": float(train_mae),
                    "test_mae": float(test_mae),
                    "cv_r2_mean": float(cv_scores.mean()),
                    "cv_r2_std": float(cv_scores.std())
                },
                "model_parameters": self._get_model_parameters(model, regression_type)
            }
            
            return {
                "model_results": model_results,
                "predictions": predictions_df,
                "feature_importance": feature_importance
            }
            
        except Exception as e:
            raise NodeExecutionError(f"回归分析执行失败: {str(e)}")
    
    def _prepare_data(self, data: pd.DataFrame, target_column: str, feature_columns: List[str]):
        """数据预处理"""
        # 选择目标变量
        if not target_column or target_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            target_column = numeric_cols[0]
        
        # 选择特征变量
        if not feature_columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            feature_columns = [col for col in numeric_cols if col != target_column]
        
        if not feature_columns:
            raise NodeExecutionError("没有找到特征列")
        
        # 移除缺失值
        analysis_data = data[[target_column] + feature_columns].dropna()
        
        if analysis_data.empty:
            raise NodeExecutionError("移除缺失值后数据为空")
        
        X = analysis_data[feature_columns].values
        y = analysis_data[target_column].values
        
        return X, y, feature_columns
    
    def _get_feature_importance(self, model, feature_names: List[str], regression_type: str) -> pd.DataFrame:
        """获取特征重要性"""
        importance_data = []
        
        if regression_type in ["linear", "ridge", "lasso"]:
            # 线性模型使用系数
            if hasattr(model, 'coef_'):
                importances = np.abs(model.coef_)
                for i, feature in enumerate(feature_names):
                    importance_data.append({
                        "feature": feature,
                        "importance": float(importances[i]),
                        "coefficient": float(model.coef_[i])
                    })
        elif regression_type == "random_forest":
            # 随机森林使用特征重要性
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                for i, feature in enumerate(feature_names):
                    importance_data.append({
                        "feature": feature,
                        "importance": float(importances[i])
                    })
        
        if importance_data:
            importance_df = pd.DataFrame(importance_data)
            importance_df = importance_df.sort_values('importance', ascending=False)
            return importance_df
        else:
            return pd.DataFrame()
    
    def _get_model_parameters(self, model, regression_type: str) -> Dict[str, Any]:
        """获取模型参数"""
        params = {}
        
        if hasattr(model, 'intercept_'):
            params['intercept'] = float(model.intercept_)
        
        if regression_type in ["ridge", "lasso"] and hasattr(model, 'alpha'):
            params['alpha'] = float(model.alpha)
        
        if regression_type == "random_forest":
            params['n_estimators'] = model.n_estimators
            if hasattr(model, 'max_depth'):
                params['max_depth'] = model.max_depth
        
        return params
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty