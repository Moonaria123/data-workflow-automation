"""
热力图节点

提供热力图可视化功能
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.figure import Figure

from ..base import BaseNode, NodeCategory, NodeType
from ...common.exceptions import NodeExecutionError


class HeatmapNode(BaseNode):
    """热力图节点"""
    
    def __init__(self):
        super().__init__(
            name="热力图",
            node_type=NodeType.VISUALIZATION,
            category=NodeCategory.VISUALIZATION,
            description="创建热力图，用于展示数据的相关性、密度分布等"
        )
        
        # 配置属性
        self.add_property("heatmap_type", "correlation", str, "热力图类型",
                         options=["correlation", "pivot_table", "matrix", "confusion_matrix"])
        self.add_property("index_column", "", str, "行索引列")
        self.add_property("columns_column", "", str, "列索引列")
        self.add_property("values_column", "", str, "数值列")
        self.add_property("aggfunc", "mean", str, "聚合函数",
                         options=["mean", "sum", "count", "max", "min", "std"])
        self.add_property("colormap", "viridis", str, "颜色映射",
                         options=["viridis", "plasma", "inferno", "magma", "coolwarm", "RdYlBu"])
        self.add_property("figure_size", [10, 8], list, "图表大小")
        self.add_property("show_annotations", True, bool, "显示数值标注")
        self.add_property("center_colormap", False, bool, "居中颜色映射")
        
        # 输入端口
        self.add_input_port("data", "DataFrame", "输入数据")
        
        # 输出端口  
        self.add_output_port("figure", "Figure", "matplotlib图形对象")
        self.add_output_port("heatmap_data", "DataFrame", "热力图数据")
        self.add_output_port("plot_info", "Dict", "图表信息")
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行热力图绘制"""
        try:
            data = inputs.get("data")
            if data is None or data.empty:
                raise NodeExecutionError("输入数据为空")
            
            heatmap_type = self.get_property("heatmap_type")
            index_column = self.get_property("index_column")
            columns_column = self.get_property("columns_column")
            values_column = self.get_property("values_column")
            aggfunc = self.get_property("aggfunc")
            colormap = self.get_property("colormap")
            figure_size = self.get_property("figure_size")
            show_annotations = self.get_property("show_annotations")
            center_colormap = self.get_property("center_colormap")
            
            # 根据热力图类型处理数据
            if heatmap_type == "correlation":
                heatmap_data, fig = self._create_correlation_heatmap(
                    data, colormap, figure_size, show_annotations, center_colormap
                )
            elif heatmap_type == "pivot_table":
                heatmap_data, fig = self._create_pivot_heatmap(
                    data, index_column, columns_column, values_column, aggfunc,
                    colormap, figure_size, show_annotations, center_colormap
                )
            elif heatmap_type == "matrix":
                heatmap_data, fig = self._create_matrix_heatmap(
                    data, colormap, figure_size, show_annotations, center_colormap
                )
            elif heatmap_type == "confusion_matrix":
                heatmap_data, fig = self._create_confusion_matrix_heatmap(
                    data, index_column, columns_column,
                    colormap, figure_size, show_annotations
                )
            else:
                raise NodeExecutionError(f"不支持的热力图类型: {heatmap_type}")
            
            plot_info = {
                "heatmap_type": heatmap_type,
                "data_shape": heatmap_data.shape,
                "colormap": colormap,
                "show_annotations": show_annotations,
                "aggregation_function": aggfunc if heatmap_type == "pivot_table" else None
            }
            
            return {
                "figure": fig,
                "heatmap_data": heatmap_data,
                "plot_info": plot_info
            }
            
        except Exception as e:
            raise NodeExecutionError(f"热力图创建失败: {str(e)}")
    
    def _create_correlation_heatmap(self, data: pd.DataFrame, colormap: str, 
                                   figure_size: list, show_annotations: bool, 
                                   center_colormap: bool) -> tuple:
        """创建相关性热力图"""
        # 选择数值列
        numeric_data = data.select_dtypes(include=[np.number])
        if numeric_data.empty:
            raise NodeExecutionError("没有找到数值列")
        
        # 计算相关矩阵
        correlation_matrix = numeric_data.corr()
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figure_size)
        
        # 绘制热力图
        sns.heatmap(
            correlation_matrix,
            annot=show_annotations,
            cmap=colormap,
            center=0 if center_colormap else None,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Correlation Heatmap', fontsize=16, pad=20)
        plt.tight_layout()
        
        return correlation_matrix, fig
    
    def _create_pivot_heatmap(self, data: pd.DataFrame, index_column: str,
                             columns_column: str, values_column: str, aggfunc: str,
                             colormap: str, figure_size: list, show_annotations: bool,
                             center_colormap: bool) -> tuple:
        """创建数据透视表热力图"""
        # 验证列名
        if not index_column or index_column not in data.columns:
            non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_cols) == 0:
                raise NodeExecutionError("没有找到适合作为行索引的列")
            index_column = non_numeric_cols[0]
        
        if not columns_column or columns_column not in data.columns:
            available_cols = [col for col in data.columns if col != index_column]
            non_numeric_cols = data[available_cols].select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_cols) == 0:
                raise NodeExecutionError("没有找到适合作为列索引的列")
            columns_column = non_numeric_cols[0]
        
        if not values_column or values_column not in data.columns:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise NodeExecutionError("没有找到数值列")
            values_column = numeric_cols[0]
        
        # 创建数据透视表
        try:
            pivot_data = data.pivot_table(
                values=values_column,
                index=index_column,
                columns=columns_column,
                aggfunc=aggfunc,
                fill_value=0
            )
        except Exception as e:
            raise NodeExecutionError(f"创建数据透视表失败: {str(e)}")
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figure_size)
        
        # 绘制热力图
        sns.heatmap(
            pivot_data,
            annot=show_annotations,
            cmap=colormap,
            center=0 if center_colormap else None,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title(f'Pivot Table Heatmap: {values_column} by {index_column} and {columns_column}', 
                    fontsize=14, pad=20)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        return pivot_data, fig
    
    def _create_matrix_heatmap(self, data: pd.DataFrame, colormap: str,
                              figure_size: list, show_annotations: bool,
                              center_colormap: bool) -> tuple:
        """创建矩阵热力图"""
        # 选择数值数据
        numeric_data = data.select_dtypes(include=[np.number])
        if numeric_data.empty:
            raise NodeExecutionError("没有找到数值列")
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figure_size)
        
        # 绘制热力图
        sns.heatmap(
            numeric_data,
            annot=show_annotations,
            cmap=colormap,
            center=0 if center_colormap else None,
            linewidths=0.1,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Data Matrix Heatmap', fontsize=16, pad=20)
        plt.tight_layout()
        
        return numeric_data, fig
    
    def _create_confusion_matrix_heatmap(self, data: pd.DataFrame, actual_column: str,
                                        predicted_column: str, colormap: str,
                                        figure_size: list, show_annotations: bool) -> tuple:
        """创建混淆矩阵热力图"""
        # 验证列名
        if not actual_column or actual_column not in data.columns:
            non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_cols) == 0:
                raise NodeExecutionError("没有找到适合作为实际值的列")
            actual_column = non_numeric_cols[0]
        
        if not predicted_column or predicted_column not in data.columns:
            available_cols = [col for col in data.columns if col != actual_column]
            if len(available_cols) == 0:
                raise NodeExecutionError("没有找到适合作为预测值的列")
            predicted_column = available_cols[0]
        
        # 创建混淆矩阵
        confusion_matrix = pd.crosstab(
            data[actual_column], 
            data[predicted_column],
            margins=False
        )
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figure_size)
        
        # 绘制热力图
        sns.heatmap(
            confusion_matrix,
            annot=show_annotations,
            fmt='d',
            cmap=colormap,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title(f'Confusion Matrix: {actual_column} vs {predicted_column}', 
                    fontsize=14, pad=20)
        ax.set_xlabel(f'Predicted {predicted_column}')
        ax.set_ylabel(f'Actual {actual_column}')
        plt.tight_layout()
        
        return confusion_matrix, fig
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入"""
        data = inputs.get("data")
        if data is None:
            return False
        
        if not isinstance(data, pd.DataFrame):
            return False
        
        return not data.empty