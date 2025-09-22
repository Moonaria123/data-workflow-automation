"""
图表节点

提供基础图表绘制功能
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
import numpy as np

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class ChartNode(BaseNode):
    """图表节点"""
    
    def __init__(self):
        super().__init__(
            name="图表",
            node_type=NodeType.VISUALIZATION,
            category=NodeCategory.VISUALIZATION,
            description="创建各种类型的图表，包括线图、柱状图、散点图等"
        )
        
        # 配置属性
        self.add_property("chart_type", "line", str, "图表类型",
                         options=["line", "bar", "scatter", "histogram", "box", "pie"])
        self.add_property("x_column", "", str, "X轴列名")
        self.add_property("y_column", "", str, "Y轴列名")
        self.add_property("title", "", str, "图表标题")
        self.add_property("x_label", "", str, "X轴标签")
        self.add_property("y_label", "", str, "Y轴标签")
        self.add_property("color_column", "", str, "颜色分组列")
        self.add_property("figure_size", [10, 6], list, "图表大小")
        self.add_property("style", "default", str, "图表样式",
                         options=["default", "seaborn", "ggplot", "bmh"])
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口
        self.add_output_port("figure", "Figure", "matplotlib图形对象")
        self.add_output_port("chart_info", "Dict", "图表信息")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行图表绘制"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            chart_type = self.get_property("chart_type")
            x_column = self.get_property("x_column")
            y_column = self.get_property("y_column")
            title = self.get_property("title")
            x_label = self.get_property("x_label")
            y_label = self.get_property("y_label")
            color_column = self.get_property("color_column")
            figure_size = self.get_property("figure_size")
            style = self.get_property("style")
            
            # 设置样式
            if style != "default":
                plt.style.use(style)
            
            # 创建图形
            fig, ax = plt.subplots(figsize=figure_size)
            
            # 根据图表类型绘制
            if chart_type == "line":
                figure = self._create_line_chart(data, ax, x_column, y_column, color_column)
            elif chart_type == "bar":
                figure = self._create_bar_chart(data, ax, x_column, y_column, color_column)
            elif chart_type == "scatter":
                figure = self._create_scatter_chart(data, ax, x_column, y_column, color_column)
            elif chart_type == "histogram":
                figure = self._create_histogram(data, ax, y_column or x_column, color_column)
            elif chart_type == "box":
                figure = self._create_box_plot(data, ax, x_column, y_column, color_column)
            elif chart_type == "pie":
                figure = self._create_pie_chart(data, ax, x_column, y_column)
            else:
                raise NodeExecutionError(f"不支持的图表类型: {chart_type}")
            
            # 设置标题和标签
            if title:
                ax.set_title(title)
            if x_label:
                ax.set_xlabel(x_label)
            elif x_column:
                ax.set_xlabel(x_column)
            if y_label:
                ax.set_ylabel(y_label)
            elif y_column:
                ax.set_ylabel(y_column)
            
            # 调整布局
            plt.tight_layout()
            
            chart_info = {
                "chart_type": chart_type,
                "data_shape": data.shape,
                "x_column": x_column,
                "y_column": y_column,
                "color_column": color_column,
                "title": title
            }
            
            return {
                "figure": fig,
                "chart_info": chart_info
            }
            
        except Exception as e:
            raise NodeExecutionError(f"图表创建失败: {str(e)}")
    
    def _create_line_chart(self, data: pd.DataFrame, ax, x_column: str, y_column: str, color_column: str = None):
        """创建线图"""
        if not x_column or x_column not in data.columns:
            x_column = data.index.name or 'index'
            x_data = data.index
        else:
            x_data = data[x_column]
        
        if not y_column or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            y_column = numeric_cols[0]
        
        y_data = data[y_column]
        
        if color_column and color_column in data.columns:
            # 按颜色分组绘制
            groups = data.groupby(color_column)
            for name, group in groups:
                ax.plot(group[x_column] if x_column in data.columns else group.index, 
                       group[y_column], label=str(name), marker='o')
            ax.legend()
        else:
            ax.plot(x_data, y_data, marker='o')
        
        return ax.figure
    
    def _create_bar_chart(self, data: pd.DataFrame, ax, x_column: str, y_column: str, color_column: str = None):
        """创建柱状图"""
        if not x_column or x_column not in data.columns:
            # 使用索引或第一个非数值列
            non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_cols) > 0:
                x_column = non_numeric_cols[0]
            else:
                x_column = data.index.name or 'index'
                x_data = data.index
        
        if x_column in data.columns:
            x_data = data[x_column]
        else:
            x_data = data.index
        
        if not y_column or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            y_column = numeric_cols[0]
        
        y_data = data[y_column]
        
        if color_column and color_column in data.columns:
            # 分组柱状图
            pivot_data = data.pivot_table(values=y_column, index=x_column, columns=color_column, aggfunc='mean')
            pivot_data.plot(kind='bar', ax=ax)
        else:
            ax.bar(x_data, y_data)
        
        ax.tick_params(axis='x', rotation=45)
        return ax.figure
    
    def _create_scatter_chart(self, data: pd.DataFrame, ax, x_column: str, y_column: str, color_column: str = None):
        """创建散点图"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise NodeExecutionError("散点图需要至少两个数值列")
        
        if not x_column or x_column not in numeric_cols:
            x_column = numeric_cols[0]
        if not y_column or y_column not in numeric_cols:
            y_column = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        x_data = data[x_column]
        y_data = data[y_column]
        
        if color_column and color_column in data.columns:
            # 彩色散点图
            groups = data.groupby(color_column)
            for name, group in groups:
                ax.scatter(group[x_column], group[y_column], label=str(name), alpha=0.7)
            ax.legend()
        else:
            ax.scatter(x_data, y_data, alpha=0.7)
        
        return ax.figure
    
    def _create_histogram(self, data: pd.DataFrame, ax, column: str, color_column: str = None):
        """创建直方图"""
        if not column or column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            column = numeric_cols[0]
        
        col_data = data[column].dropna()
        
        if color_column and color_column in data.columns:
            # 分组直方图
            groups = data.groupby(color_column)
            for name, group in groups:
                ax.hist(group[column].dropna(), alpha=0.7, label=str(name), bins=20)
            ax.legend()
        else:
            ax.hist(col_data, bins=20, alpha=0.7)
        
        return ax.figure
    
    def _create_box_plot(self, data: pd.DataFrame, ax, x_column: str, y_column: str, color_column: str = None):
        """创建箱线图"""
        if not y_column or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            y_column = numeric_cols[0]
        
        if x_column and x_column in data.columns:
            # 分组箱线图
            data.boxplot(column=y_column, by=x_column, ax=ax)
        else:
            # 单一箱线图
            ax.boxplot(data[y_column].dropna())
        
        return ax.figure
    
    def _create_pie_chart(self, data: pd.DataFrame, ax, x_column: str, y_column: str):
        """创建饼图"""
        if not x_column or x_column not in data.columns:
            non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_cols) == 0:
                raise NodeExecutionError("饼图需要分类列")
            x_column = non_numeric_cols[0]
        
        if not y_column or y_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                # 使用计数
                value_counts = data[x_column].value_counts()
                ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            else:
                y_column = numeric_cols[0]
                grouped = data.groupby(x_column)[y_column].sum()
                ax.pie(grouped.values, labels=grouped.index, autopct='%1.1f%%')
        else:
            grouped = data.groupby(x_column)[y_column].sum()
            ax.pie(grouped.values, labels=grouped.index, autopct='%1.1f%%')
        
        return ax.figure
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty