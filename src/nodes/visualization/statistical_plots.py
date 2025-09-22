"""
统计图表节点

提供专业统计图表功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.figure import Figure

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class StatisticalPlotsNode(BaseNode):
    """统计图表节点"""
    
    def __init__(self):
        super().__init__(
            name="统计图表",
            node_type=NodeType.VISUALIZATION,
            category=NodeCategory.VISUALIZATION,
            description="创建专业的统计图表，包括概率图、残差图、诊断图等"
        )
        
        # 配置属性
        self.add_property("plot_type", "qq_plot", str, "图表类型",
                         options=["qq_plot", "pp_plot", "residual_plot", "leverage_plot", 
                                "influence_plot", "scale_location_plot", "diagnostic_plots"])
        self.add_property("distribution", "norm", str, "参考分布",
                         options=["norm", "uniform", "expon", "gamma", "beta"])
        self.add_property("x_column", "", str, "X轴列名")
        self.add_property("y_column", "", str, "Y轴列名")
        self.add_property("predicted_column", "", str, "预测值列")
        self.add_property("residual_column", "", str, "残差列")
        self.add_property("figure_size", [12, 8], list, "图表大小")
        self.add_property("confidence_interval", True, bool, "显示置信区间")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("figure", "Figure", "matplotlib图形对象")
        self.add_output_port("plot_info", "Dict", "图表信息")
        self.add_output_port("statistics", "Dict", "统计检验结果")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行统计图表创建"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            plot_type = self.get_property("plot_type")
            distribution = self.get_property("distribution")
            x_column = self.get_property("x_column")
            y_column = self.get_property("y_column")
            predicted_column = self.get_property("predicted_column")
            residual_column = self.get_property("residual_column")
            figure_size = self.get_property("figure_size")
            confidence_interval = self.get_property("confidence_interval")
            
            # 根据图表类型创建
            if plot_type == "qq_plot":
                fig, stats = self._create_qq_plot(data, y_column, distribution, figure_size)
            elif plot_type == "pp_plot":
                fig, stats = self._create_pp_plot(data, y_column, distribution, figure_size)
            elif plot_type == "residual_plot":
                fig, stats = self._create_residual_plot(data, predicted_column, residual_column, 
                                                      x_column, y_column, figure_size)
            elif plot_type == "leverage_plot":
                fig, stats = self._create_leverage_plot(data, x_column, y_column, figure_size)
            elif plot_type == "influence_plot":
                fig, stats = self._create_influence_plot(data, x_column, y_column, figure_size)
            elif plot_type == "scale_location_plot":
                fig, stats = self._create_scale_location_plot(data, predicted_column, 
                                                            residual_column, figure_size)
            elif plot_type == "diagnostic_plots":
                fig, stats = self._create_diagnostic_plots(data, x_column, y_column, figure_size)
            else:
                raise NodeExecutionError(f"不支持的图表类型: {plot_type}")
            
            plot_info = {
                "plot_type": plot_type,
                "distribution": distribution,
                "data_shape": data.shape,
                "x_column": x_column,
                "y_column": y_column
            }
            
            return {
                "figure": fig,
                "plot_info": plot_info,
                "statistics": stats
            }
            
        except Exception as e:
            raise NodeExecutionError(f"统计图表创建失败: {str(e)}")
    
    def _create_qq_plot(self, data: pd.DataFrame, column: str, distribution: str, 
                       figure_size: list) -> tuple:
        """创建QQ图"""
        if not column or column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            column = numeric_cols[0]
        
        from scipy import stats as scipy_stats
        
        # 获取分布对象
        dist_map = {
            'norm': scipy_stats.norm,
            'uniform': scipy_stats.uniform,
            'expon': scipy_stats.expon,
            'gamma': scipy_stats.gamma,
            'beta': scipy_stats.beta
        }
        
        if distribution not in dist_map:
            distribution = 'norm'
        
        dist_obj = dist_map[distribution]
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        # 清理数据
        clean_data = data[column].dropna()
        
        # 创建QQ图
        scipy_stats.probplot(clean_data, dist=dist_obj, plot=ax)
        ax.set_title(f'Q-Q Plot: {column} vs {distribution.title()} Distribution')
        ax.grid(True, alpha=0.3)
        
        # 计算相关统计量
        stats_results = {}
        
        # Shapiro-Wilk正态性检验（仅对正态分布）
        if distribution == 'norm' and len(clean_data) <= 5000:
            try:
                shapiro_stat, shapiro_p = scipy_stats.shapiro(clean_data)
                stats_results['shapiro_wilk'] = {
                    'statistic': shapiro_stat,
                    'p_value': shapiro_p,
                    'interpretation': 'Normal' if shapiro_p > 0.05 else 'Not Normal'
                }
            except Exception:
                pass
        
        # Kolmogorov-Smirnov检验
        try:
            if distribution == 'norm':
                ks_stat, ks_p = scipy_stats.kstest(clean_data, 'norm', 
                                                  args=(clean_data.mean(), clean_data.std()))
            else:
                ks_stat, ks_p = scipy_stats.kstest(clean_data, distribution)
            
            stats_results['kolmogorov_smirnov'] = {
                'statistic': ks_stat,
                'p_value': ks_p,
                'interpretation': f'Follows {distribution}' if ks_p > 0.05 else f'Does not follow {distribution}'
            }
        except Exception:
            pass
        
        # 添加统计信息到图表
        info_text = f"Sample size: {len(clean_data)}\n"
        if 'shapiro_wilk' in stats_results:
            info_text += f"Shapiro-Wilk p-value: {stats_results['shapiro_wilk']['p_value']:.4f}\n"
        if 'kolmogorov_smirnov' in stats_results:
            info_text += f"K-S p-value: {stats_results['kolmogorov_smirnov']['p_value']:.4f}"
        
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig, stats_results
    
    def _create_pp_plot(self, data: pd.DataFrame, column: str, distribution: str, 
                       figure_size: list) -> tuple:
        """创建PP图"""
        if not column or column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            column = numeric_cols[0]
        
        from scipy import stats as scipy_stats
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        clean_data = data[column].dropna()
        
        # 计算经验累积分布函数
        n = len(clean_data)
        sorted_data = np.sort(clean_data)
        empirical_cdf = np.arange(1, n + 1) / n
        
        # 计算理论累积分布函数
        if distribution == 'norm':
            mean, std = clean_data.mean(), clean_data.std()
            theoretical_cdf = scipy_stats.norm.cdf(sorted_data, mean, std)
        elif distribution == 'uniform':
            min_val, max_val = clean_data.min(), clean_data.max()
            theoretical_cdf = scipy_stats.uniform.cdf(sorted_data, min_val, max_val - min_val)
        else:
            # 使用默认参数
            dist_obj = getattr(scipy_stats, distribution)
            theoretical_cdf = dist_obj.cdf(sorted_data)
        
        # 绘制PP图
        ax.scatter(theoretical_cdf, empirical_cdf, alpha=0.6)
        ax.plot([0, 1], [0, 1], 'r--', label='Perfect Fit')
        ax.set_xlabel(f'Theoretical Cumulative Probability ({distribution})')
        ax.set_ylabel('Empirical Cumulative Probability')
        ax.set_title(f'P-P Plot: {column} vs {distribution.title()} Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 计算相关统计量
        correlation = np.corrcoef(theoretical_cdf, empirical_cdf)[0, 1]
        rmse = np.sqrt(np.mean((theoretical_cdf - empirical_cdf) ** 2))
        
        stats_results = {
            'correlation': correlation,
            'rmse': rmse,
            'sample_size': len(clean_data)
        }
        
        # 添加统计信息
        info_text = f"Correlation: {correlation:.4f}\nRMSE: {rmse:.4f}\nSample size: {len(clean_data)}"
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig, stats_results
    
    def _create_residual_plot(self, data: pd.DataFrame, predicted_column: str, 
                             residual_column: str, x_column: str, y_column: str, 
                             figure_size: list) -> tuple:
        """创建残差图"""
        fig, axes = plt.subplots(2, 2, figsize=figure_size)
        fig.suptitle('Residual Analysis', fontsize=16)
        
        # 如果没有预测值和残差，尝试计算
        if (not predicted_column or predicted_column not in data.columns or
            not residual_column or residual_column not in data.columns):
            
            if not x_column or not y_column or x_column not in data.columns or y_column not in data.columns:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) < 2:
                    raise NodeExecutionError("需要至少两个数值列进行回归分析")
                x_column = numeric_cols[0]
                y_column = numeric_cols[1]
            
            # 简单线性回归
            from sklearn.linear_model import LinearRegression
            clean_data = data[[x_column, y_column]].dropna()
            X = clean_data[[x_column]]
            y = clean_data[y_column]
            
            if len(clean_data) < 2:
                raise NodeExecutionError("数据点不足，无法进行回归分析")
            
            model = LinearRegression().fit(X, y)
            predicted = model.predict(X)
            residuals = y - predicted
        else:
            clean_data = data[[predicted_column, residual_column]].dropna()
            predicted = clean_data[predicted_column]
            residuals = clean_data[residual_column]
        
        # 1. 残差vs拟合值
        axes[0, 0].scatter(predicted, residuals, alpha=0.6)
        axes[0, 0].axhline(y=0, color='red', linestyle='--')
        axes[0, 0].set_xlabel('Fitted Values')
        axes[0, 0].set_ylabel('Residuals')
        axes[0, 0].set_title('Residuals vs Fitted')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 残差的QQ图
        from scipy.stats import probplot
        probplot(residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Normal Q-Q Plot (Residuals)')
        
        # 3. 标准化残差的直方图
        std_residuals = residuals / residuals.std()
        axes[1, 0].hist(std_residuals, bins=20, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Standardized Residuals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Residuals Histogram')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Scale-Location图
        sqrt_abs_residuals = np.sqrt(np.abs(std_residuals))
        axes[1, 1].scatter(predicted, sqrt_abs_residuals, alpha=0.6)
        axes[1, 1].set_xlabel('Fitted Values')
        axes[1, 1].set_ylabel('√|Standardized Residuals|')
        axes[1, 1].set_title('Scale-Location Plot')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 计算统计量
        stats_results = {
            'residual_mean': residuals.mean(),
            'residual_std': residuals.std(),
            'residual_min': residuals.min(),
            'residual_max': residuals.max(),
            'n_observations': len(residuals)
        }
        
        # Durbin-Watson统计量（自相关检验）
        try:
            dw_stat = np.sum(np.diff(residuals)**2) / np.sum(residuals**2)
            stats_results['durbin_watson'] = dw_stat
        except Exception:
            pass
        
        plt.tight_layout()
        return fig, stats_results
    
    def _create_leverage_plot(self, data: pd.DataFrame, x_column: str, y_column: str, 
                             figure_size: list) -> tuple:
        """创建杠杆图"""
        if not x_column or not y_column or x_column not in data.columns or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                raise NodeExecutionError("需要至少两个数值列")
            x_column = numeric_cols[0]
            y_column = numeric_cols[1]
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        clean_data = data[[x_column, y_column]].dropna()
        X = clean_data[[x_column]]
        y = clean_data[y_column]
        
        if len(clean_data) < 3:
            raise NodeExecutionError("数据点不足，无法计算杠杆值")
        
        # 计算杠杆值（hat values）
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit(X, y)
        
        # 添加常数项
        X_with_const = np.column_stack([np.ones(len(X)), X])
        
        # 计算帽子矩阵的对角元素（杠杆值）
        try:
            H = X_with_const @ np.linalg.inv(X_with_const.T @ X_with_const) @ X_with_const.T
            leverages = np.diag(H)
        except np.linalg.LinAlgError:
            # 如果矩阵奇异，使用伪逆
            H = X_with_const @ np.linalg.pinv(X_with_const.T @ X_with_const) @ X_with_const.T
            leverages = np.diag(H)
        
        # 计算残差
        predicted = model.predict(X)
        residuals = y - predicted
        std_residuals = residuals / residuals.std()
        
        # 绘制杠杆图
        ax.scatter(leverages, std_residuals, alpha=0.6)
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Standardized Residuals')
        ax.set_title('Leverage Plot')
        ax.grid(True, alpha=0.3)
        
        # 添加参考线
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        # 高杠杆点阈值
        p = X_with_const.shape[1]  # 参数个数
        n = len(clean_data)
        leverage_threshold = 2 * p / n
        ax.axvline(x=leverage_threshold, color='orange', linestyle='--', alpha=0.7, 
                  label=f'Leverage Threshold ({leverage_threshold:.3f})')
        
        # 标记高杠杆点
        high_leverage = leverages > leverage_threshold
        if np.any(high_leverage):
            high_lev_indices = np.where(high_leverage)[0]
            for idx in high_lev_indices[:5]:  # 最多标记5个点
                ax.annotate(f'{idx}', (leverages[idx], std_residuals.iloc[idx]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.legend()
        
        stats_results = {
            'leverage_mean': leverages.mean(),
            'leverage_max': leverages.max(),
            'leverage_threshold': leverage_threshold,
            'high_leverage_count': np.sum(high_leverage),
            'n_observations': len(clean_data)
        }
        
        plt.tight_layout()
        return fig, stats_results
    
    def _create_influence_plot(self, data: pd.DataFrame, x_column: str, y_column: str, 
                              figure_size: list) -> tuple:
        """创建影响图"""
        if not x_column or not y_column or x_column not in data.columns or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                raise NodeExecutionError("需要至少两个数值列")
            x_column = numeric_cols[0]
            y_column = numeric_cols[1]
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        clean_data = data[[x_column, y_column]].dropna()
        X = clean_data[[x_column]]
        y = clean_data[y_column]
        
        if len(clean_data) < 3:
            raise NodeExecutionError("数据点不足，无法计算影响值")
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit(X, y)
        
        # 计算Cook's Distance
        predicted = model.predict(X)
        residuals = y - predicted
        
        # 添加常数项计算杠杆值
        X_with_const = np.column_stack([np.ones(len(X)), X])
        try:
            H = X_with_const @ np.linalg.inv(X_with_const.T @ X_with_const) @ X_with_const.T
            leverages = np.diag(H)
        except np.linalg.LinAlgError:
            H = X_with_const @ np.linalg.pinv(X_with_const.T @ X_with_const) @ X_with_const.T
            leverages = np.diag(H)
        
        # 计算Cook's Distance
        mse = np.mean(residuals**2)
        p = X_with_const.shape[1]
        
        cooks_d = (residuals**2 / (p * mse)) * (leverages / (1 - leverages)**2)
        
        # 标准化残差
        std_residuals = residuals / residuals.std()
        
        # 创建气泡图，气泡大小表示Cook's Distance
        scatter = ax.scatter(leverages, std_residuals, s=cooks_d*1000, alpha=0.6, c=cooks_d, cmap='Reds')
        
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Standardized Residuals')
        ax.set_title('Influence Plot (Bubble size = Cook\'s Distance)')
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Cook\'s Distance')
        
        # 添加参考线
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        # Cook's Distance阈值
        cooks_threshold = 4 / len(clean_data)
        
        # 标记高影响点
        high_influence = cooks_d > cooks_threshold
        if np.any(high_influence):
            high_inf_indices = np.where(high_influence)[0]
            for idx in high_inf_indices[:5]:  # 最多标记5个点
                ax.annotate(f'{idx}', (leverages[idx], std_residuals.iloc[idx]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        stats_results = {
            'cooks_d_mean': cooks_d.mean(),
            'cooks_d_max': cooks_d.max(),
            'cooks_threshold': cooks_threshold,
            'high_influence_count': np.sum(high_influence),
            'n_observations': len(clean_data)
        }
        
        plt.tight_layout()
        return fig, stats_results
    
    def _create_scale_location_plot(self, data: pd.DataFrame, predicted_column: str, 
                                   residual_column: str, figure_size: list) -> tuple:
        """创建Scale-Location图"""
        # 如果没有预测值和残差列，使用前两个数值列进行回归
        if (not predicted_column or predicted_column not in data.columns or
            not residual_column or residual_column not in data.columns):
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                raise NodeExecutionError("需要至少两个数值列")
            
            x_column = numeric_cols[0]
            y_column = numeric_cols[1]
            
            from sklearn.linear_model import LinearRegression
            clean_data = data[[x_column, y_column]].dropna()
            X = clean_data[[x_column]]
            y = clean_data[y_column]
            
            model = LinearRegression().fit(X, y)
            predicted = model.predict(X)
            residuals = y - predicted
        else:
            clean_data = data[[predicted_column, residual_column]].dropna()
            predicted = clean_data[predicted_column]
            residuals = clean_data[residual_column]
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        # 标准化残差
        std_residuals = residuals / residuals.std()
        
        # 计算√|标准化残差|
        sqrt_abs_std_residuals = np.sqrt(np.abs(std_residuals))
        
        # 绘制Scale-Location图
        ax.scatter(predicted, sqrt_abs_std_residuals, alpha=0.6)
        
        # 添加平滑曲线
        try:
            from scipy.interpolate import UnivariateSpline
            sorted_indices = np.argsort(predicted)
            spline = UnivariateSpline(predicted.iloc[sorted_indices], 
                                    sqrt_abs_std_residuals.iloc[sorted_indices], s=0.3)
            x_smooth = np.linspace(predicted.min(), predicted.max(), 100)
            y_smooth = spline(x_smooth)
            ax.plot(x_smooth, y_smooth, 'red', linewidth=2, label='Smooth Line')
            ax.legend()
        except Exception:
            pass
        
        ax.set_xlabel('Fitted Values')
        ax.set_ylabel('√|Standardized Residuals|')
        ax.set_title('Scale-Location Plot')
        ax.grid(True, alpha=0.3)
        
        # 计算统计量
        stats_results = {
            'sqrt_residuals_mean': sqrt_abs_std_residuals.mean(),
            'sqrt_residuals_std': sqrt_abs_std_residuals.std(),
            'homoscedasticity_score': 1 - (sqrt_abs_std_residuals.std() / sqrt_abs_std_residuals.mean()),
            'n_observations': len(residuals)
        }
        
        plt.tight_layout()
        return fig, stats_results
    
    def _create_diagnostic_plots(self, data: pd.DataFrame, x_column: str, y_column: str, 
                                figure_size: list) -> tuple:
        """创建综合诊断图"""
        if not x_column or not y_column or x_column not in data.columns or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                raise NodeExecutionError("需要至少两个数值列")
            x_column = numeric_cols[0]
            y_column = numeric_cols[1]
        
        fig, axes = plt.subplots(2, 2, figsize=figure_size)
        fig.suptitle('Regression Diagnostic Plots', fontsize=16)
        
        clean_data = data[[x_column, y_column]].dropna()
        X = clean_data[[x_column]]
        y = clean_data[y_column]
        
        if len(clean_data) < 3:
            raise NodeExecutionError("数据点不足，无法进行诊断分析")
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit(X, y)
        predicted = model.predict(X)
        residuals = y - predicted
        std_residuals = residuals / residuals.std()
        
        # 1. 残差vs拟合值
        axes[0, 0].scatter(predicted, residuals, alpha=0.6)
        axes[0, 0].axhline(y=0, color='red', linestyle='--')
        axes[0, 0].set_xlabel('Fitted Values')
        axes[0, 0].set_ylabel('Residuals')
        axes[0, 0].set_title('Residuals vs Fitted')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 残差的QQ图
        from scipy.stats import probplot
        probplot(residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Normal Q-Q Plot')
        
        # 3. Scale-Location图
        sqrt_abs_residuals = np.sqrt(np.abs(std_residuals))
        axes[1, 0].scatter(predicted, sqrt_abs_residuals, alpha=0.6)
        axes[1, 0].set_xlabel('Fitted Values')
        axes[1, 0].set_ylabel('√|Standardized Residuals|')
        axes[1, 0].set_title('Scale-Location')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 杠杆图
        X_with_const = np.column_stack([np.ones(len(X)), X])
        try:
            H = X_with_const @ np.linalg.inv(X_with_const.T @ X_with_const) @ X_with_const.T
            leverages = np.diag(H)
        except np.linalg.LinAlgError:
            H = X_with_const @ np.linalg.pinv(X_with_const.T @ X_with_const) @ X_with_const.T
            leverages = np.diag(H)
        
        axes[1, 1].scatter(leverages, std_residuals, alpha=0.6)
        axes[1, 1].set_xlabel('Leverage')
        axes[1, 1].set_ylabel('Standardized Residuals')
        axes[1, 1].set_title('Residuals vs Leverage')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 添加参考线
        axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        # 计算综合统计量
        stats_results = {
            'r_squared': model.score(X, y),
            'residual_std': residuals.std(),
            'leverage_mean': leverages.mean(),
            'leverage_max': leverages.max(),
            'n_observations': len(clean_data)
        }
        
        # 添加回归系数
        stats_results['coefficients'] = {
            'intercept': model.intercept_,
            'slope': model.coef_[0]
        }
        
        plt.tight_layout()
        return fig, stats_results
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty