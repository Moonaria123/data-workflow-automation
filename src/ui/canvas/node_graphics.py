"""
节点图形项

用于在画布上显示节点
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QStyleOptionGraphicsItem, QWidget, QMenu, QAction, QGraphicsProxyWidget,
    QLabel, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QObject
from PyQt5.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, QFontMetrics, QPainterPath,
    QLinearGradient, QRadialGradient
)

from ...nodes.base import BaseNode
from ...core.port import Port, PortType


class PortGraphicsItem(QGraphicsEllipseItem):
    """端口图形项"""
    
    def __init__(self, port: Port, parent=None):
        super().__init__(parent)
        self.port = port
        self.radius = 6
        self.setup_graphics()
    
    def setup_graphics(self):
        """设置图形属性"""
        # 设置大小
        self.setRect(-self.radius, -self.radius, 
                    self.radius * 2, self.radius * 2)
        
        # 根据端口类型设置颜色
        if self.port.port_type == PortType.INPUT:
            color = QColor(100, 150, 200)  # 蓝色
        else:
            color = QColor(200, 150, 100)  # 橙色
        
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor(50, 50, 50), 2))
        
        # 设置工具提示
        tooltip = f"{self.port.name}\n类型: {self.port.data_type}\n描述: {self.port.description}"
        self.setToolTip(tooltip)
        
        # 设置交互属性
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
    
    def hoverEnterEvent(self, event):
        """鼠标悬停进入"""
        # 高亮显示
        self.setBrush(QBrush(self.brush().color().lighter(150)))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标悬停离开"""
        # 恢复原色
        if self.port.port_type == PortType.INPUT:
            color = QColor(100, 150, 200)
        else:
            color = QColor(200, 150, 100)
        self.setBrush(QBrush(color))
        super().hoverLeaveEvent(event)
    
    def get_port(self) -> Port:
        """获取端口对象"""
        return self.port
    
    def get_connection_point(self) -> QPointF:
        """获取连接点（在场景坐标系中）"""
        return self.scenePos()


class NodeSignals(QObject):
    """节点信号"""
    position_changed = pyqtSignal(object)  # node
    selection_changed = pyqtSignal(object, bool)  # node, selected
    double_clicked = pyqtSignal(object)  # node


class NodeGraphicsItem(QGraphicsRectItem):
    """节点图形项"""
    
    def __init__(self, node: BaseNode):
        super().__init__()
        self.node = node
        self.signals = NodeSignals()
        
        # 图形属性
        self.width = 150
        self.height = 100
        self.corner_radius = 8
        
        # 子项
        self.title_item = None
        self.input_ports: List[PortGraphicsItem] = []
        self.output_ports: List[PortGraphicsItem] = []
        
        self.setup_graphics()
        self.create_ports()
        self.update_layout()
    
    def setup_graphics(self):
        """设置图形属性"""
        # 设置基本属性
        self.setRect(0, 0, self.width, self.height)
        
        # 设置颜色（根据节点类型）
        node_colors = {
            'INPUT': QColor(150, 200, 150),      # 绿色
            'OUTPUT': QColor(200, 150, 150),     # 红色
            'PROCESSING': QColor(150, 150, 200), # 蓝色
            'ANALYSIS': QColor(200, 200, 150),   # 黄色
            'VISUALIZATION': QColor(200, 150, 200), # 紫色
        }
        
        node_type = getattr(self.node, 'node_type', 'PROCESSING')
        if hasattr(node_type, 'value'):
            node_type = node_type.value
        
        base_color = node_colors.get(str(node_type).upper(), QColor(150, 150, 150))
        
        # 创建渐变
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(120))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor(100, 100, 100), 2))
        
        # 设置交互属性
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        
        # 设置Z值
        self.setZValue(1)
        
        # 创建标题
        self.title_item = QGraphicsTextItem(self.node.name, self)
        font = QFont("Arial", 10, QFont.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(QColor(50, 50, 50))
    
    def create_ports(self):
        """创建端口"""
        # 创建输入端口
        for port in self.node.input_ports:
            port_item = PortGraphicsItem(port, self)
            self.input_ports.append(port_item)
        
        # 创建输出端口
        for port in self.node.output_ports:
            port_item = PortGraphicsItem(port, self)
            self.output_ports.append(port_item)
    
    def update_layout(self):
        """更新布局"""
        # 调整节点大小
        port_count = max(len(self.input_ports), len(self.output_ports))
        self.height = max(100, 40 + port_count * 20)
        self.setRect(0, 0, self.width, self.height)
        
        # 更新标题位置
        if self.title_item:
            title_rect = self.title_item.boundingRect()
            title_x = (self.width - title_rect.width()) / 2
            self.title_item.setPos(title_x, 10)
        
        # 更新输入端口位置
        port_spacing = 20
        start_y = 40
        for i, port_item in enumerate(self.input_ports):
            port_item.setPos(-port_item.radius, start_y + i * port_spacing)
        
        # 更新输出端口位置
        for i, port_item in enumerate(self.output_ports):
            port_item.setPos(self.width + port_item.radius, start_y + i * port_spacing)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """自定义绘制"""
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 绘制圆角矩形
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect, self.corner_radius, self.corner_radius)
        
        # 设置画刷和画笔
        if self.isSelected():
            # 选中状态
            pen = QPen(QColor(255, 165, 0), 3)  # 橙色边框
            painter.setPen(pen)
        else:
            painter.setPen(self.pen())
        
        painter.setBrush(self.brush())
        painter.drawPath(path)
        
        # 绘制状态指示器
        if hasattr(self.node, 'is_executing') and self.node.is_executing:
            # 执行中状态
            painter.setBrush(QBrush(QColor(0, 255, 0)))
            painter.setPen(QPen(QColor(0, 200, 0), 1))
            painter.drawEllipse(rect.width() - 15, 5, 10, 10)
        elif hasattr(self.node, 'has_error') and self.node.has_error:
            # 错误状态
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.setPen(QPen(QColor(200, 0, 0), 1))
            painter.drawEllipse(rect.width() - 15, 5, 10, 10)
    
    def boundingRect(self) -> QRectF:
        """返回边界矩形"""
        rect = self.rect()
        # 扩展边界以包含端口
        port_radius = 6
        return rect.adjusted(-port_radius, 0, port_radius, 0)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
            self.signals.selection_changed.emit(self.node, True)
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            self.signals.double_clicked.emit(self.node)
        super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        menu = QMenu()
        
        # 执行节点
        execute_action = QAction("执行节点", None)
        execute_action.triggered.connect(self.execute_node)
        menu.addAction(execute_action)
        
        menu.addSeparator()
        
        # 复制节点
        copy_action = QAction("复制", None)
        copy_action.triggered.connect(self.copy_node)
        menu.addAction(copy_action)
        
        # 删除节点
        delete_action = QAction("删除", None)
        delete_action.triggered.connect(self.delete_node)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # 节点属性
        properties_action = QAction("属性", None)
        properties_action.triggered.connect(self.show_properties)
        menu.addAction(properties_action)
        
        # 显示菜单
        menu.exec_(event.screenPos())
    
    def execute_node(self):
        """执行节点"""
        if hasattr(self.scene(), 'execute_node'):
            self.scene().execute_node(self.node)
    
    def copy_node(self):
        """复制节点"""
        if hasattr(self.scene(), 'copy_node'):
            self.scene().copy_node(self.node)
    
    def delete_node(self):
        """删除节点"""
        if hasattr(self.scene(), 'remove_node'):
            self.scene().remove_node(self.node)
    
    def show_properties(self):
        """显示节点属性"""
        if hasattr(self.scene(), 'show_node_properties'):
            self.scene().show_node_properties(self.node)
    
    def itemChange(self, change, value):
        """项目变化事件"""
        if change == QGraphicsItem.ItemPositionChange:
            # 位置变化时更新连接
            if hasattr(self.scene(), 'update_connections'):
                self.scene().update_connections(self.node)
            
            self.signals.position_changed.emit(self.node)
        
        elif change == QGraphicsItem.ItemSelectedChange:
            self.signals.selection_changed.emit(self.node, value)
        
        return super().itemChange(change, value)
    
    def get_node(self) -> BaseNode:
        """获取节点对象"""
        return self.node
    
    def get_input_port_position(self, port_name: str) -> Optional[QPointF]:
        """获取输入端口位置"""
        for port_item in self.input_ports:
            if port_item.get_port().name == port_name:
                return port_item.scenePos()
        return None
    
    def get_output_port_position(self, port_name: str) -> Optional[QPointF]:
        """获取输出端口位置"""
        for port_item in self.output_ports:
            if port_item.get_port().name == port_name:
                return port_item.scenePos()
        return None
    
    def get_port_at_position(self, pos: QPointF) -> Optional[PortGraphicsItem]:
        """获取指定位置的端口"""
        local_pos = self.mapFromScene(pos)
        
        for port_item in self.input_ports + self.output_ports:
            port_rect = port_item.boundingRect().translated(port_item.pos())
            if port_rect.contains(local_pos):
                return port_item
        
        return None
    
    def set_executing(self, executing: bool):
        """设置执行状态"""
        if hasattr(self.node, 'is_executing'):
            self.node.is_executing = executing
        self.update()
    
    def set_error(self, has_error: bool):
        """设置错误状态"""
        if hasattr(self.node, 'has_error'):
            self.node.has_error = has_error
        self.update()
    
    def update_node_data(self):
        """更新节点数据显示"""
        # 更新标题
        if self.title_item:
            self.title_item.setPlainText(self.node.name)
        
        # 更新工具提示
        tooltip = f"节点: {self.node.name}\n类型: {self.node.node_type}\n描述: {self.node.description}"
        self.setToolTip(tooltip)
        
        # 重新布局
        self.update_layout()
    
    def highlight(self, highlight: bool):
        """设置高亮状态"""
        if highlight:
            # 高亮显示
            pen = QPen(QColor(255, 255, 0), 4)  # 黄色边框
            self.setPen(pen)
        else:
            # 恢复默认
            self.setPen(QPen(QColor(100, 100, 100), 2))
        
        self.update()