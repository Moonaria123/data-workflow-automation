"""
绘图节点

提供高级绘图功能
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.figure import Figure

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class PlotNode(BaseNode):
    """绘图节点"""
    
    def __init__(self):
        super().__init__(
            name="高级绘图",
            node_type=NodeType.VISUALIZATION,
            category=NodeCategory.VISUALIZATION,
            description="创建高级统计图表，包括分布图、相关图、热力图等"
        )
        
        # 配置属性
        self.add_property("plot_type", "distribution", str, "图表类型",
                         options=["distribution", "correlation", "regression", "violin", "swarm", "joint"])
        self.add_property("x_column", "", str, "X轴列名")
        self.add_property("y_column", "", str, "Y轴列名")
        self.add_property("hue_column", "", str, "分组列")
        self.add_property("title", "", str, "图表标题")
        self.add_property("figure_size", [12, 8], list, "图表大小")
        self.add_property("color_palette", "viridis", str, "调色板")
        self.add_property("show_stats", True, bool, "显示统计信息")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("figure", "Figure", "matplotlib图形对象")
        self.add_output_port("plot_info", "Dict", "图表信息")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行绘图"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            plot_type = self.get_property("plot_type")
            x_column = self.get_property("x_column")
            y_column = self.get_property("y_column")
            hue_column = self.get_property("hue_column")
            title = self.get_property("title")
            figure_size = self.get_property("figure_size")
            color_palette = self.get_property("color_palette")
            show_stats = self.get_property("show_stats")
            
            # 设置样式
            sns.set_style("whitegrid")
            sns.set_palette(color_palette)
            
            # 根据图表类型绘制
            if plot_type == "distribution":
                fig = self._create_distribution_plot(data, x_column, hue_column, figure_size)
            elif plot_type == "correlation":
                fig = self._create_correlation_plot(data, figure_size)
            elif plot_type == "regression":
                fig = self._create_regression_plot(data, x_column, y_column, hue_column, figure_size)
            elif plot_type == "violin":
                fig = self._create_violin_plot(data, x_column, y_column, hue_column, figure_size)
            elif plot_type == "swarm":
                fig = self._create_swarm_plot(data, x_column, y_column, hue_column, figure_size)
            elif plot_type == "joint":
                fig = self._create_joint_plot(data, x_column, y_column, figure_size)
            else:
                raise NodeExecutionError(f"不支持的图表类型: {plot_type}")
            
            # 设置标题
            if title:
                fig.suptitle(title, size=16, y=0.98)
            
            plt.tight_layout()
            
            plot_info = {
                "plot_type": plot_type,
                "data_shape": data.shape,
                "x_column": x_column,
                "y_column": y_column,
                "hue_column": hue_column,
                "color_palette": color_palette
            }
            
            return {
                "figure": fig,
                "plot_info": plot_info
            }
            
        except Exception as e:
            raise NodeExecutionError(f"绘图执行失败: {str(e)}")
    
    def _create_distribution_plot(self, data: pd.DataFrame, x_column: str, hue_column: str, figure_size: list):
        """创建分布图"""
        if not x_column or x_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            x_column = numeric_cols[0]
        
        fig, axes = plt.subplots(2, 2, figsize=figure_size)
        fig.suptitle(f'Distribution Analysis: {x_column}', size=16)
        
        # 直方图
        if hue_column and hue_column in data.columns:
            sns.histplot(data=data, x=x_column, hue=hue_column, ax=axes[0,0], kde=True)
        else:
            sns.histplot(data=data, x=x_column, ax=axes[0,0], kde=True)
        axes[0,0].set_title('Histogram with KDE')
        
        # 箱线图
        if hue_column and hue_column in data.columns:
            sns.boxplot(data=data, x=hue_column, y=x_column, ax=axes[0,1])
        else:
            sns.boxplot(data=data, y=x_column, ax=axes[0,1])
        axes[0,1].set_title('Box Plot')
        
        # QQ图
        from scipy.stats import probplot
        probplot(data[x_column].dropna(), dist="norm", plot=axes[1,0])
        axes[1,0].set_title('Q-Q Plot (Normal)')
        
        # 密度图
        if hue_column and hue_column in data.columns:
            for category in data[hue_column].unique():
                subset = data[data[hue_column] == category][x_column].dropna()
                if len(subset) > 0:
                    sns.kdeplot(subset, ax=axes[1,1], label=str(category))
            axes[1,1].legend()
        else:
            sns.kdeplot(data[x_column].dropna(), ax=axes[1,1])
        axes[1,1].set_title('Density Plot')
        
        return fig
    
    def _create_correlation_plot(self, data: pd.DataFrame, figure_size: list):
        """创建相关性图"""
        numeric_data = data.select_dtypes(include=[np.number])
        if numeric_data.empty:
            raise NodeExecutionError("没有找到数值列")
        
        # 计算相关矩阵
        corr_matrix = numeric_data.corr()
        
        fig, axes = plt.subplots(1, 2, figsize=figure_size)
        fig.suptitle('Correlation Analysis', size=16)
        
        # 热力图
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=axes[0], cbar_kws={'shrink': 0.8})
        axes[0].set_title('Correlation Heatmap')
        
        # 聚类图
        sns.clustermap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                      square=True, figsize=(8, 8))
        plt.close()  # 关闭clustermap自动创建的figure
        
        # 散点图矩阵（选择前几列）
        if len(numeric_data.columns) <= 5:
            scatter_data = numeric_data
        else:
            scatter_data = numeric_data.iloc[:, :5]
        
        # 创建散点图矩阵
        from pandas.plotting import scatter_matrix
        scatter_matrix(scatter_data, ax=axes[1], alpha=0.6, figsize=(6, 6), diagonal='hist')
        axes[1].set_title('Scatter Matrix (Top 5 Variables)')
        
        return fig
    
    def _create_regression_plot(self, data: pd.DataFrame, x_column: str, y_column: str, hue_column: str, figure_size: list):
        """创建回归图"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if not x_column or x_column not in numeric_cols:
            x_column = numeric_cols[0] if len(numeric_cols) > 0 else None
        if not y_column or y_column not in numeric_cols:
            y_column = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        if not x_column or not y_column:
            raise NodeExecutionError("需要至少两个数值列")
        
        fig, axes = plt.subplots(2, 2, figsize=figure_size)
        fig.suptitle(f'Regression Analysis: {y_column} vs {x_column}', size=16)
        
        # 散点图与回归线
        if hue_column and hue_column in data.columns:
            sns.scatterplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=axes[0,0])
            sns.regplot(data=data, x=x_column, y=y_column, ax=axes[0,0], scatter=False)
        else:
            sns.regplot(data=data, x=x_column, y=y_column, ax=axes[0,0])
        axes[0,0].set_title('Scatter Plot with Regression Line')
        
        # 残差图
        from sklearn.linear_model import LinearRegression
        clean_data = data[[x_column, y_column]].dropna()
        if len(clean_data) > 1:
            X = clean_data[[x_column]]
            y = clean_data[y_column]
            model = LinearRegression().fit(X, y)
            residuals = y - model.predict(X)
            axes[0,1].scatter(model.predict(X), residuals, alpha=0.6)
            axes[0,1].axhline(y=0, color='red', linestyle='--')
            axes[0,1].set_xlabel('Fitted Values')
            axes[0,1].set_ylabel('Residuals')
            axes[0,1].set_title('Residual Plot')
        
        # QQ图（残差）
        if len(clean_data) > 1:
            from scipy.stats import probplot
            probplot(residuals, dist="norm", plot=axes[1,0])
            axes[1,0].set_title('Q-Q Plot (Residuals)')
        
        # 残差直方图
        if len(clean_data) > 1:
            axes[1,1].hist(residuals, bins=20, alpha=0.7, edgecolor='black')
            axes[1,1].set_xlabel('Residuals')
            axes[1,1].set_ylabel('Frequency')
            axes[1,1].set_title('Residuals Histogram')
        
        return fig
    
    def _create_violin_plot(self, data: pd.DataFrame, x_column: str, y_column: str, hue_column: str, figure_size: list):
        """创建小提琴图"""
        if not y_column or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            y_column = numeric_cols[0]
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        if x_column and x_column in data.columns:
            sns.violinplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=ax)
            ax.tick_params(axis='x', rotation=45)
        else:
            sns.violinplot(data=data, y=y_column, ax=ax)
        
        ax.set_title(f'Violin Plot: {y_column}')
        return fig
    
    def _create_swarm_plot(self, data: pd.DataFrame, x_column: str, y_column: str, hue_column: str, figure_size: list):
        """创建蜂群图"""
        if not y_column or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            y_column = numeric_cols[0]
        
        fig, ax = plt.subplots(figsize=figure_size)
        
        if x_column and x_column in data.columns:
            sns.swarmplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=ax)
            ax.tick_params(axis='x', rotation=45)
        else:
            sns.swarmplot(data=data, y=y_column, ax=ax)
        
        ax.set_title(f'Swarm Plot: {y_column}')
        return fig
    
    def _create_joint_plot(self, data: pd.DataFrame, x_column: str, y_column: str, figure_size: list):
        """创建联合图"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if not x_column or x_column not in numeric_cols:
            x_column = numeric_cols[0] if len(numeric_cols) > 0 else None
        if not y_column or y_column not in numeric_cols:
            y_column = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        if not x_column or not y_column:
            raise NodeExecutionError("需要至少两个数值列")
        
        # jointplot返回JointGrid对象，需要获取其figure
        joint_plot = sns.jointplot(data=data, x=x_column, y=y_column, 
                                  kind='scatter', height=figure_size[0])
        joint_plot.plot_joint(sns.regplot, scatter=False, color='red')
        
        return joint_plot.fig
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty