"""
连接图形项

用于在画布上显示节点之间的连接
"""

from typing import Optional, List
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter, QPolygonF

from ...core.connection import Connection


class ConnectionGraphicsItem(QGraphicsPathItem):
    """连接图形项"""
    
    def __init__(self, connection: Connection):
        super().__init__()
        self.connection = connection
        self.source_pos = QPointF()
        self.target_pos = QPointF()
        
        self.setup_graphics()
        self.update_path()
    
    def setup_graphics(self):
        """设置图形属性"""
        # 设置画笔
        pen = QPen(QColor(100, 100, 100), 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        
        # 设置选中时的样式
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        
        # 设置Z值（在节点下方）
        self.setZValue(-1)
    
    def set_source_pos(self, pos: QPointF):
        """设置源位置"""
        self.source_pos = pos
        self.update_path()
    
    def set_target_pos(self, pos: QPointF):
        """设置目标位置"""
        self.target_pos = pos
        self.update_path()
    
    def update_path(self):
        """更新连接路径"""
        path = QPainterPath()
        
        # 计算控制点
        dx = self.target_pos.x() - self.source_pos.x()
        dy = self.target_pos.y() - self.source_pos.y()
        
        # 贝塞尔曲线控制点
        ctrl1 = QPointF(
            self.source_pos.x() + dx * 0.5,
            self.source_pos.y()
        )
        ctrl2 = QPointF(
            self.target_pos.x() - dx * 0.5,
            self.target_pos.y()
        )
        
        # 创建贝塞尔曲线
        path.moveTo(self.source_pos)
        path.cubicTo(ctrl1, ctrl2, self.target_pos)
        
        # 添加箭头
        self.add_arrow(path, self.target_pos, ctrl2)
        
        self.setPath(path)
    
    def add_arrow(self, path: QPainterPath, target: QPointF, ctrl: QPointF):
        """添加箭头"""
        # 计算箭头方向
        direction = target - ctrl
        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5
        
        if length == 0:
            return
        
        # 标准化方向向量
        direction = QPointF(direction.x() / length, direction.y() / length)
        
        # 箭头参数
        arrow_length = 10
        arrow_angle = 0.4  # 约23度
        
        # 计算箭头两个端点
        left_point = QPointF(
            target.x() - arrow_length * (direction.x() * 0.866 - direction.y() * 0.5),
            target.y() - arrow_length * (direction.y() * 0.866 + direction.x() * 0.5)
        )
        
        right_point = QPointF(
            target.x() - arrow_length * (direction.x() * 0.866 + direction.y() * 0.5),
            target.y() - arrow_length * (direction.y() * 0.866 - direction.x() * 0.5)
        )
        
        # 绘制箭头
        arrow = QPolygonF([target, left_point, right_point])
        path.addPolygon(arrow)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """自定义绘制"""
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 根据选中状态设置颜色
        if self.isSelected():
            pen = QPen(QColor(255, 165, 0), 3)  # 橙色
        elif self.connection.is_valid():
            pen = QPen(QColor(100, 200, 100), 2)  # 绿色
        else:
            pen = QPen(QColor(200, 100, 100), 2)  # 红色
        
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        
        # 绘制路径
        painter.drawPath(self.path())
        
        # 如果选中，绘制选择框
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
    
    def boundingRect(self) -> QRectF:
        """返回边界矩形"""
        if self.path().isEmpty():
            return QRectF()
        
        rect = self.path().boundingRect()
        # 扩展边界以包含选择框
        return rect.adjusted(-2, -2, 2, 2)
    
    def shape(self):
        """返回形状（用于碰撞检测）"""
        # 创建一个稍宽的路径用于更容易的选择
        stroker = QPainterPath()
        stroker.addPath(self.path())
        return stroker
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu()
        
        # 删除连接
        delete_action = QAction("删除连接", None)
        delete_action.triggered.connect(self.delete_connection)
        menu.addAction(delete_action)
        
        # 编辑连接属性
        if hasattr(self.connection, 'properties') and self.connection.properties:
            properties_action = QAction("连接属性", None)
            properties_action.triggered.connect(self.show_properties)
            menu.addAction(properties_action)
        
        # 显示菜单
        menu.exec_(event.screenPos())
    
    def delete_connection(self):
        """删除连接"""
        if hasattr(self.scene(), 'remove_connection'):
            self.scene().remove_connection(self.connection)
    
    def show_properties(self):
        """显示连接属性"""
        # 这里可以添加连接属性对话框
        pass
    
    def get_connection(self) -> Connection:
        """获取连接对象"""
        return self.connection
    
    def set_highlight(self, highlight: bool):
        """设置高亮状态"""
        if highlight:
            pen = QPen(QColor(255, 255, 0), 3)  # 黄色高亮
        else:
            pen = QPen(QColor(100, 100, 100), 2)  # 默认颜色
        
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        
        self.update()
    
    def set_valid(self, valid: bool):
        """设置有效状态"""
        self.connection.set_valid(valid)
        self.update()
    
    def is_valid(self) -> bool:
        """检查连接是否有效"""
        return self.connection.is_valid()
    
    def get_data_type(self) -> str:
        """获取数据类型"""
        return self.connection.get_data_type()
    
    def set_animated(self, animated: bool):
        """设置动画状态（用于显示数据流动）"""
        # 这里可以添加动画效果
        pass
    
    def update_connection_info(self):
        """更新连接信息"""
        # 更新工具提示
        if self.connection.source_node and self.connection.target_node:
            tooltip = (
                f"从: {self.connection.source_node.name}\n"
                f"到: {self.connection.target_node.name}\n"
                f"端口: {self.connection.source_port} -> {self.connection.target_port}\n"
                f"类型: {self.connection.get_data_type()}\n"
                f"状态: {'有效' if self.connection.is_valid() else '无效'}"
            )
            self.setToolTip(tooltip)
    
    def itemChange(self, change, value):
        """项目变化事件"""
        if change == QGraphicsItem.ItemSelectedChange:
            # 选中状态变化时更新显示
            self.update()
        
        return super().itemChange(change, value)