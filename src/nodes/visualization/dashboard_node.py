"""
仪表板节点

提供交互式仪表板创建功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import numpy as np

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class DashboardNode(BaseNode):
    """仪表板节点"""
    
    def __init__(self):
        super().__init__(
            name="仪表板",
            node_type=NodeType.VISUALIZATION,
            category=NodeCategory.VISUALIZATION,
            description="创建综合性数据仪表板，包含多个图表和统计信息"
        )
        
        # 配置属性
        self.add_property("dashboard_type", "overview", str, "仪表板类型",
                         options=["overview", "detailed", "comparison", "trends"])
        self.add_property("columns_to_analyze", [], list, "要分析的列")
        self.add_property("group_column", "", str, "分组列")
        self.add_property("time_column", "", str, "时间列")
        self.add_property("figure_size", [16, 12], list, "图表大小")
        self.add_property("color_palette", "Set2", str, "调色板")
        self.add_property("show_statistics", True, bool, "显示统计信息")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("figure", "Figure", "matplotlib图形对象")
        self.add_output_port("dashboard_info", "Dict", "仪表板信息")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行仪表板创建"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            dashboard_type = self.get_property("dashboard_type")
            columns_to_analyze = self.get_property("columns_to_analyze")
            group_column = self.get_property("group_column")
            time_column = self.get_property("time_column")
            figure_size = self.get_property("figure_size")
            color_palette = self.get_property("color_palette")
            show_statistics = self.get_property("show_statistics")
            
            # 设置样式
            sns.set_style("whitegrid")
            sns.set_palette(color_palette)
            
            # 根据仪表板类型创建
            if dashboard_type == "overview":
                fig = self._create_overview_dashboard(data, columns_to_analyze, 
                                                    group_column, figure_size, 
                                                    show_statistics)
            elif dashboard_type == "detailed":
                fig = self._create_detailed_dashboard(data, columns_to_analyze,
                                                    group_column, figure_size)
            elif dashboard_type == "comparison":
                fig = self._create_comparison_dashboard(data, columns_to_analyze,
                                                      group_column, figure_size)
            elif dashboard_type == "trends":
                fig = self._create_trends_dashboard(data, columns_to_analyze,
                                                   time_column, group_column, 
                                                   figure_size)
            else:
                raise NodeExecutionError(f"不支持的仪表板类型: {dashboard_type}")
            
            dashboard_info = {
                "dashboard_type": dashboard_type,
                "data_shape": data.shape,
                "analyzed_columns": columns_to_analyze or "auto",
                "group_column": group_column,
                "time_column": time_column
            }
            
            return {
                "figure": fig,
                "dashboard_info": dashboard_info
            }
            
        except Exception as e:
            raise NodeExecutionError(f"仪表板创建失败: {str(e)}")
    
    def _create_overview_dashboard(self, data: pd.DataFrame, columns_to_analyze: List[str],
                                 group_column: str, figure_size: list, 
                                 show_statistics: bool) -> Figure:
        """创建概览仪表板"""
        # 如果未指定列，自动选择数值列
        if not columns_to_analyze:
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            columns_to_analyze = numeric_cols[:4]  # 最多4列
        
        if not columns_to_analyze:
            raise NodeExecutionError("没有找到可分析的数值列")
        
        # 创建网格布局
        fig = plt.figure(figsize=figure_size)
        gs = GridSpec(3, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        # 顶部标题
        fig.suptitle('Data Overview Dashboard', fontsize=20, y=0.95)
        
        # 1. 数据概览统计表
        if show_statistics:
            ax_stats = fig.add_subplot(gs[0, :])
            self._add_statistics_table(ax_stats, data, columns_to_analyze)
        
        # 2. 分布图（第二行前两个）
        if len(columns_to_analyze) >= 1:
            ax_dist1 = fig.add_subplot(gs[1, 0])
            self._add_distribution_plot(ax_dist1, data, columns_to_analyze[0], group_column)
        
        if len(columns_to_analyze) >= 2:
            ax_dist2 = fig.add_subplot(gs[1, 1])
            self._add_distribution_plot(ax_dist2, data, columns_to_analyze[1], group_column)
        
        # 3. 箱线图（第二行后两个）
        if len(columns_to_analyze) >= 3:
            ax_box1 = fig.add_subplot(gs[1, 2])
            self._add_box_plot(ax_box1, data, columns_to_analyze[2], group_column)
        
        if len(columns_to_analyze) >= 4:
            ax_box2 = fig.add_subplot(gs[1, 3])
            self._add_box_plot(ax_box2, data, columns_to_analyze[3], group_column)
        
        # 4. 相关性热力图（第三行左半部分）
        ax_corr = fig.add_subplot(gs[2, :2])
        self._add_correlation_heatmap(ax_corr, data, columns_to_analyze)
        
        # 5. 散点图（第三行右半部分）
        if len(columns_to_analyze) >= 2:
            ax_scatter = fig.add_subplot(gs[2, 2:])
            self._add_scatter_plot(ax_scatter, data, columns_to_analyze[0], 
                                 columns_to_analyze[1], group_column)
        
        plt.tight_layout()
        return fig
    
    def _create_detailed_dashboard(self, data: pd.DataFrame, columns_to_analyze: List[str],
                                 group_column: str, figure_size: list) -> Figure:
        """创建详细仪表板"""
        if not columns_to_analyze:
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            columns_to_analyze = numeric_cols[:2]  # 选择前两列进行详细分析
        
        if not columns_to_analyze:
            raise NodeExecutionError("没有找到可分析的数值列")
        
        fig = plt.figure(figsize=figure_size)
        gs = GridSpec(4, 4, figure=fig, hspace=0.4, wspace=0.3)
        
        fig.suptitle('Detailed Analysis Dashboard', fontsize=20, y=0.95)
        
        col = columns_to_analyze[0]
        
        # 第一行：基础统计
        ax_hist = fig.add_subplot(gs[0, :2])
        data[col].hist(bins=30, ax=ax_hist, alpha=0.7)
        ax_hist.set_title(f'Distribution of {col}')
        
        ax_box = fig.add_subplot(gs[0, 2:])
        if group_column and group_column in data.columns:
            data.boxplot(column=col, by=group_column, ax=ax_box)
        else:
            data.boxplot(column=col, ax=ax_box)
        ax_box.set_title(f'Box Plot of {col}')
        
        # 第二行：QQ图和密度图
        ax_qq = fig.add_subplot(gs[1, :2])
        from scipy.stats import probplot
        probplot(data[col].dropna(), dist="norm", plot=ax_qq)
        ax_qq.set_title(f'Q-Q Plot of {col}')
        
        ax_kde = fig.add_subplot(gs[1, 2:])
        if group_column and group_column in data.columns:
            for group in data[group_column].unique():
                subset = data[data[group_column] == group][col].dropna()
                if len(subset) > 0:
                    sns.kdeplot(subset, ax=ax_kde, label=str(group))
            ax_kde.legend()
        else:
            sns.kdeplot(data[col].dropna(), ax=ax_kde)
        ax_kde.set_title(f'Density Plot of {col}')
        
        # 第三行：时间序列（如果有索引）或累积分布
        ax_cumsum = fig.add_subplot(gs[2, :2])
        data[col].cumsum().plot(ax=ax_cumsum)
        ax_cumsum.set_title(f'Cumulative Sum of {col}')
        
        ax_rolling = fig.add_subplot(gs[2, 2:])
        data[col].rolling(window=min(10, len(data)//10+1)).mean().plot(ax=ax_rolling)
        ax_rolling.set_title(f'Rolling Mean of {col}')
        
        # 第四行：统计表和相关分析
        ax_stats = fig.add_subplot(gs[3, :])
        self._add_detailed_statistics_table(ax_stats, data, col, group_column)
        
        plt.tight_layout()
        return fig
    
    def _create_comparison_dashboard(self, data: pd.DataFrame, columns_to_analyze: List[str],
                                   group_column: str, figure_size: list) -> Figure:
        """创建比较仪表板"""
        if not group_column or group_column not in data.columns:
            # 尝试找到合适的分组列
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                group_column = categorical_cols[0]
            else:
                raise NodeExecutionError("需要指定分组列进行比较")
        
        if not columns_to_analyze:
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            columns_to_analyze = numeric_cols[:3]  # 最多3列
        
        fig = plt.figure(figsize=figure_size)
        gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3)
        
        fig.suptitle(f'Comparison Dashboard by {group_column}', fontsize=20, y=0.95)
        
        # 第一行：分组统计
        ax_bar = fig.add_subplot(gs[0, :])
        if columns_to_analyze:
            grouped_means = data.groupby(group_column)[columns_to_analyze].mean()
            grouped_means.plot(kind='bar', ax=ax_bar)
            ax_bar.set_title('Mean Values by Group')
            ax_bar.tick_params(axis='x', rotation=45)
        
        # 第二行：分布比较
        for i, col in enumerate(columns_to_analyze[:3]):
            ax = fig.add_subplot(gs[1, i])
            data.boxplot(column=col, by=group_column, ax=ax)
            ax.set_title(f'{col} by {group_column}')
        
        # 第三行：热力图
        ax_heatmap = fig.add_subplot(gs[2, :])
        if columns_to_analyze:
            pivot_data = data.groupby(group_column)[columns_to_analyze].mean()
            sns.heatmap(pivot_data.T, annot=True, cmap='viridis', ax=ax_heatmap)
            ax_heatmap.set_title('Mean Values Heatmap')
        
        plt.tight_layout()
        return fig
    
    def _create_trends_dashboard(self, data: pd.DataFrame, columns_to_analyze: List[str],
                               time_column: str, group_column: str, 
                               figure_size: list) -> Figure:
        """创建趋势仪表板"""
        if not time_column or time_column not in data.columns:
            # 尝试找到时间列
            datetime_cols = data.select_dtypes(include=['datetime64']).columns
            if len(datetime_cols) > 0:
                time_column = datetime_cols[0]
            else:
                # 使用索引作为时间轴
                time_column = None
        
        if not columns_to_analyze:
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            columns_to_analyze = numeric_cols[:2]
        
        fig = plt.figure(figsize=figure_size)
        gs = GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3)
        
        fig.suptitle('Trends Dashboard', fontsize=20, y=0.95)
        
        # 准备时间数据
        if time_column:
            x_data = data[time_column]
            data_sorted = data.sort_values(time_column)
        else:
            x_data = data.index
            data_sorted = data
        
        # 第一行：主要趋势线
        ax_trend = fig.add_subplot(gs[0, :])
        for col in columns_to_analyze[:2]:
            ax_trend.plot(x_data, data[col], label=col, marker='o', markersize=3)
        ax_trend.set_title('Main Trends')
        ax_trend.legend()
        ax_trend.tick_params(axis='x', rotation=45)
        
        # 第二行：滚动平均和分组趋势
        if columns_to_analyze:
            col = columns_to_analyze[0]
            
            ax_rolling = fig.add_subplot(gs[1, 0])
            window_size = max(1, len(data) // 20)
            rolling_mean = data_sorted[col].rolling(window=window_size).mean()
            ax_rolling.plot(x_data, data[col], alpha=0.3, label='Original')
            ax_rolling.plot(x_data, rolling_mean, label=f'Rolling Mean ({window_size})', linewidth=2)
            ax_rolling.set_title(f'Rolling Average: {col}')
            ax_rolling.legend()
            
            if group_column and group_column in data.columns:
                ax_group = fig.add_subplot(gs[1, 1])
                for group in data[group_column].unique():
                    group_data = data[data[group_column] == group]
                    if time_column:
                        group_x = group_data[time_column]
                    else:
                        group_x = group_data.index
                    ax_group.plot(group_x, group_data[col], label=str(group), marker='o', markersize=2)
                ax_group.set_title(f'{col} by {group_column}')
                ax_group.legend()
        
        # 第三行：变化率和季节性
        if columns_to_analyze:
            col = columns_to_analyze[0]
            
            ax_diff = fig.add_subplot(gs[2, 0])
            diff_data = data_sorted[col].diff()
            ax_diff.plot(x_data, diff_data, label='First Difference')
            ax_diff.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax_diff.set_title(f'Change Rate: {col}')
            ax_diff.legend()
            
            ax_autocorr = fig.add_subplot(gs[2, 1])
            # 简单的滞后相关性可视化
            lags = range(1, min(20, len(data)//4))
            autocorrs = [data[col].autocorr(lag) for lag in lags]
            ax_autocorr.bar(lags, autocorrs)
            ax_autocorr.set_title(f'Autocorrelation: {col}')
            ax_autocorr.set_xlabel('Lag')
        
        plt.tight_layout()
        return fig
    
    def _add_statistics_table(self, ax, data: pd.DataFrame, columns: List[str]):
        """添加统计表"""
        stats_data = []
        for col in columns:
            if col in data.columns:
                col_data = data[col].dropna()
                stats_data.append([
                    col,
                    f"{col_data.mean():.2f}",
                    f"{col_data.std():.2f}",
                    f"{col_data.min():.2f}",
                    f"{col_data.max():.2f}",
                    str(col_data.count())
                ])
        
        table = ax.table(cellText=stats_data,
                        colLabels=['Column', 'Mean', 'Std', 'Min', 'Max', 'Count'],
                        cellLoc='center',
                        loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        ax.axis('off')
        ax.set_title('Descriptive Statistics')
    
    def _add_detailed_statistics_table(self, ax, data: pd.DataFrame, col: str, group_column: str):
        """添加详细统计表"""
        col_data = data[col].dropna()
        
        # 基础统计
        basic_stats = [
            ['Count', str(col_data.count())],
            ['Mean', f"{col_data.mean():.4f}"],
            ['Std', f"{col_data.std():.4f}"],
            ['Min', f"{col_data.min():.4f}"],
            ['25%', f"{col_data.quantile(0.25):.4f}"],
            ['50%', f"{col_data.quantile(0.50):.4f}"],
            ['75%', f"{col_data.quantile(0.75):.4f}"],
            ['Max', f"{col_data.max():.4f}"]
        ]
        
        # 添加偏度和峰度
        try:
            from scipy.stats import skew, kurtosis
            basic_stats.extend([
                ['Skewness', f"{skew(col_data):.4f}"],
                ['Kurtosis', f"{kurtosis(col_data):.4f}"]
            ])
        except ImportError:
            pass
        
        table = ax.table(cellText=basic_stats,
                        colLabels=['Statistic', 'Value'],
                        cellLoc='center',
                        loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.2)
        ax.axis('off')
        ax.set_title(f'Detailed Statistics: {col}')
    
    def _add_distribution_plot(self, ax, data: pd.DataFrame, col: str, group_column: str):
        """添加分布图"""
        if group_column and group_column in data.columns:
            for group in data[group_column].unique():
                subset = data[data[group_column] == group][col].dropna()
                if len(subset) > 0:
                    ax.hist(subset, alpha=0.6, label=str(group), bins=15)
            ax.legend()
        else:
            ax.hist(data[col].dropna(), bins=20, alpha=0.7)
        ax.set_title(f'Distribution: {col}')
        ax.set_xlabel(col)
        ax.set_ylabel('Frequency')
    
    def _add_box_plot(self, ax, data: pd.DataFrame, col: str, group_column: str):
        """添加箱线图"""
        if group_column and group_column in data.columns:
            data.boxplot(column=col, by=group_column, ax=ax)
        else:
            data.boxplot(column=col, ax=ax)
        ax.set_title(f'Box Plot: {col}')
    
    def _add_correlation_heatmap(self, ax, data: pd.DataFrame, columns: List[str]):
        """添加相关性热力图"""
        if len(columns) > 1:
            corr_data = data[columns].corr()
            sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, ax=ax)
        ax.set_title('Correlation Matrix')
    
    def _add_scatter_plot(self, ax, data: pd.DataFrame, x_col: str, y_col: str, group_column: str):
        """添加散点图"""
        if group_column and group_column in data.columns:
            for group in data[group_column].unique():
                subset = data[data[group_column] == group]
                ax.scatter(subset[x_col], subset[y_col], label=str(group), alpha=0.6)
            ax.legend()
        else:
            ax.scatter(data[x_col], data[y_col], alpha=0.6)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'{y_col} vs {x_col}')
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty