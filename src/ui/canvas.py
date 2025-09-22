"""
数据处理自动化工作流应用 - 工作流画布UI组件

文档版本：V1.0
创建日期：2025-09-06
依据文档：《用户需求说明书》FR-001、《UI界面设计》第2章
适用范围：Stage 2 前端开发 - 可视化工作流编辑器

核心功能：
- 拖拽式节点编排
- 连接线管理
- 画布缩放平移
- 节点选择操作
- 工作流可视化
"""

from typing import Dict, List, Optional, Tuple, Any
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, 
                             QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem,
                             QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QToolBar, QAction, QMenu)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import (QPen, QBrush, QColor, QPainter, QFont, 
                         QWheelEvent, QMouseEvent, QPalette)

from ..common.contracts import NodeInfo, NodeType, ParameterInfo


class WorkflowNode(QGraphicsRectItem):
    """工作流节点图形组件"""
    
    def __init__(self, node_info: NodeInfo, x: float = 0, y: float = 0):
        super().__init__(0, 0, 120, 80)
        self.node_info = node_info
        self.setPos(x, y)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                     QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                     QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # 节点外观设置
        self._setup_appearance()
        
        # 节点标签
        self.label = QGraphicsTextItem(self.node_info.name, self)
        self.label.setPos(5, 5)
        self.label.setFont(QFont("Microsoft YaHei", 10))
        
        # 连接点
        self.input_ports: List[QPointF] = []
        self.output_ports: List[QPointF] = []
        self._create_ports()
    
    def _setup_appearance(self):
        """设置节点外观"""
        # 根据节点类型设置颜色
        color_map = {
            NodeType.INPUT_FILE: QColor(100, 150, 200),     # 蓝色
            NodeType.INPUT_DATABASE: QColor(100, 150, 200),
            NodeType.PROCESS_CLEAN: QColor(150, 200, 100), # 绿色
            NodeType.PROCESS_TRANSFORM: QColor(150, 200, 100),
            NodeType.OUTPUT_FILE: QColor(200, 150, 100),     # 橙色
            NodeType.OUTPUT_DATABASE: QColor(200, 150, 100),
        }
        
        base_color = color_map.get(self.node_info.node_type, QColor(180, 180, 180))
        
        # 设置画笔和画刷
        pen = QPen(base_color.darker(120), 2)
        brush = QBrush(base_color)
        
        self.setPen(pen)
        self.setBrush(brush)
    
    def _create_ports(self):
        """创建输入输出端口"""
        # 输入端口（左侧）
        input_count = len(self.node_info.inputs)
        for i in range(input_count):
            y_pos = 20 + (i * 15) if input_count > 1 else 40
            self.input_ports.append(QPointF(0, y_pos))
        
        # 输出端口（右侧）
        output_count = len(self.node_info.outputs)
        for i in range(output_count):
            y_pos = 20 + (i * 15) if output_count > 1 else 40
            self.output_ports.append(QPointF(120, y_pos))
    
    def paint(self, painter: QPainter, option, widget=None):
        """自定义绘制"""
        super().paint(painter, option, widget)
        
        # 绘制端口
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        
        # 输入端口
        for port in self.input_ports:
            painter.drawEllipse(port.x() - 3, port.y() - 3, 6, 6)
        
        # 输出端口
        for port in self.output_ports:
            painter.drawEllipse(port.x() - 3, port.y() - 3, 6, 6)
    
    def get_input_port_pos(self, index: int) -> QPointF:
        """获取输入端口的全局坐标"""
        if 0 <= index < len(self.input_ports):
            return self.mapToScene(self.input_ports[index])
        return QPointF()
    
    def get_output_port_pos(self, index: int) -> QPointF:
        """获取输出端口的全局坐标"""
        if 0 <= index < len(self.output_ports):
            return self.mapToScene(self.output_ports[index])
        return QPointF()


class ConnectionLine(QGraphicsLineItem):
    """节点连接线"""
    
    def __init__(self, start_pos: QPointF, end_pos: QPointF):
        super().__init__()
        self.start_node: Optional[WorkflowNode] = None
        self.end_node: Optional[WorkflowNode] = None
        self.start_port: int = -1
        self.end_port: int = -1
        
        # 设置连线样式
        pen = QPen(QColor(80, 80, 80), 2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        self.setPen(pen)
        
        self.update_line(start_pos, end_pos)
    
    def update_line(self, start_pos: QPointF, end_pos: QPointF):
        """更新连线位置"""
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
    
    def set_connection(self, start_node: WorkflowNode, start_port: int,
                      end_node: WorkflowNode, end_port: int):
        """设置连接的节点和端口"""
        self.start_node = start_node
        self.end_node = end_node
        self.start_port = start_port
        self.end_port = end_port
        
        # 更新连线位置
        start_pos = start_node.get_output_port_pos(start_port)
        end_pos = end_node.get_input_port_pos(end_port)
        self.update_line(start_pos, end_pos)


class WorkflowCanvas(QGraphicsView):
    """工作流画布"""
    
    # 信号定义
    node_selected = pyqtSignal(WorkflowNode)
    node_moved = pyqtSignal(str, QPointF)  # node_id, new_position
    connection_created = pyqtSignal(str, int, str, int)  # from_node, from_port, to_node, to_port
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # 初始化场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 设置视图属性
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # 节点管理
        self.nodes: Dict[str, WorkflowNode] = {}
        self.connections: List[ConnectionLine] = []
        
        # 连接模式
        self.connecting_mode = False
        self.temp_connection: Optional[ConnectionLine] = None
        self.connection_start_node: Optional[WorkflowNode] = None
        self.connection_start_port: int = -1
    
    def add_node(self, node_info: NodeInfo, position: QPointF) -> WorkflowNode:
        """添加节点到画布"""
        node = WorkflowNode(node_info, position.x(), position.y())
        self.scene.addItem(node)
        self.nodes[node_info.id] = node
        return node
    
    def remove_node(self, node_id: str):
        """从画布移除节点"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # 移除相关连接
            to_remove = []
            for conn in self.connections:
                if (conn.start_node == node or conn.end_node == node):
                    to_remove.append(conn)
            
            for conn in to_remove:
                self.scene.removeItem(conn)
                self.connections.remove(conn)
            
            # 移除节点
            self.scene.removeItem(node)
            del self.nodes[node_id]
    
    def create_connection(self, from_node_id: str, from_port: int, 
                         to_node_id: str, to_port: int) -> bool:
        """创建节点连接"""
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return False
        
        from_node = self.nodes[from_node_id]
        to_node = self.nodes[to_node_id]
        
        # 检查端口有效性
        if (from_port >= len(from_node.output_ports) or 
            to_port >= len(to_node.input_ports)):
            return False
        
        # 创建连接线
        start_pos = from_node.get_output_port_pos(from_port)
        end_pos = to_node.get_input_port_pos(to_port)
        
        connection = ConnectionLine(start_pos, end_pos)
        connection.set_connection(from_node, from_port, to_node, to_port)
        
        self.scene.addItem(connection)
        self.connections.append(connection)
        
        # 发出信号
        self.connection_created.emit(from_node_id, from_port, to_node_id, to_port)
        
        return True
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件 - 缩放功能"""
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        self.scale(factor, factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, WorkflowNode):
                self.node_selected.emit(item)
        
        super().mousePressEvent(event)
    
    def clear_canvas(self):
        """清空画布"""
        self.scene.clear()
        self.nodes.clear()
        self.connections.clear()
        self.connecting_mode = False
        self.temp_connection = None
        self.connection_start_node = None
        self.connection_start_port = -1
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """获取工作流数据"""
        nodes_data = []
        for node_id, node in self.nodes.items():
            pos = node.pos()
            nodes_data.append({
                "id": node_id,
                "type": node.node_info.node_type.value,
                "name": node.node_info.name,
                "position": {"x": pos.x(), "y": pos.y()},
                "parameters": {}  # 参数由属性面板管理
            })
        
        connections_data = []
        for i, conn in enumerate(self.connections):
            if conn.start_node and conn.end_node:
                connections_data.append({
                    "id": f"conn_{i}",
                    "from_node": conn.start_node.node_info.id,
                    "from_port": conn.start_port,
                    "to_node": conn.end_node.node_info.id,
                    "to_port": conn.end_port
                })
        
        return {
            "nodes": nodes_data,
            "connections": connections_data
        }
    
    def load_workflow_data(self, data: Dict[str, Any]):
        """加载工作流数据"""
        self.clear_canvas()
        
        # 加载节点
        # 这里需要从节点注册表获取NodeInfo
        # 简化实现，实际需要注册表支持
        
        # 加载连接
        if "connections" in data:
            for conn_data in data["connections"]:
                self.create_connection(
                    conn_data["from_node"],
                    conn_data["from_port"],
                    conn_data["to_node"],
                    conn_data["to_port"]
                )
