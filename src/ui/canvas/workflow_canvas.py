"""
工作流画布

用于编辑和显示工作流图
"""

from typing import Dict, List, Optional, Tuple, Any
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu, QAction,
    QApplication, QRubberBand, QMessageBox
)
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import (
    QPainter, QWheelEvent, QMouseEvent, QKeyEvent, QDragEnterEvent,
    QDropEvent, QPen, QBrush, QColor
)

from ...core.workflow import Workflow
from ...nodes.base import BaseNode
from ...core.connection import Connection
from .node_graphics import NodeGraphicsItem
from .connection_graphics import ConnectionGraphicsItem


class WorkflowCanvas(QGraphicsView):
    """工作流画布"""
    
    # 信号
    node_selected = pyqtSignal(object)  # BaseNode
    node_double_clicked = pyqtSignal(object)  # BaseNode
    connection_created = pyqtSignal(object)  # Connection
    selection_changed = pyqtSignal(list)  # List[BaseNode]
    canvas_clicked = pyqtSignal(QPointF)  # scene position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 工作流
        self.workflow: Optional[Workflow] = None
        
        # 图形项映射
        self.node_graphics: Dict[str, NodeGraphicsItem] = {}  # node_id -> graphics
        self.connection_graphics: Dict[str, ConnectionGraphicsItem] = {}  # connection_id -> graphics
        
        # 连接创建状态
        self.creating_connection = False
        self.connection_start_port = None
        self.temp_connection = None
        
        # 选择状态
        self.selection_rect = None
        self.selection_start = None
        
        self.setup_canvas()
        self.setup_scene()
    
    def setup_canvas(self):
        """设置画布属性"""
        # 设置渲染属性
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # 设置拖拽模式
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # 设置滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 设置变换锚点
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 启用拖放
        self.setAcceptDrops(True)
        
        # 设置最小尺寸
        self.setMinimumSize(400, 300)
    
    def setup_scene(self):
        """设置场景"""
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        # 设置背景
        self.scene.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # 连接场景信号
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
        self.setScene(self.scene)
    
    def set_workflow(self, workflow: Workflow):
        """设置工作流"""
        self.workflow = workflow
        self.refresh_canvas()
    
    def refresh_canvas(self):
        """刷新画布"""
        # 清除所有图形项
        self.clear_canvas()
        
        if not self.workflow:
            return
        
        # 添加节点
        for node in self.workflow.get_nodes():
            self.add_node_graphics(node)
        
        # 添加连接
        for connection in self.workflow.get_connections():
            self.add_connection_graphics(connection)
    
    def clear_canvas(self):
        """清除画布"""
        self.scene.clear()
        self.node_graphics.clear()
        self.connection_graphics.clear()
    
    def add_node_graphics(self, node: BaseNode) -> NodeGraphicsItem:
        """添加节点图形项"""
        # 创建图形项
        graphics_item = NodeGraphicsItem(node)
        
        # 连接信号
        graphics_item.signals.position_changed.connect(self.on_node_position_changed)
        graphics_item.signals.selection_changed.connect(self.on_node_selection_changed)
        graphics_item.signals.double_clicked.connect(self.node_double_clicked.emit)
        
        # 添加到场景
        self.scene.addItem(graphics_item)
        
        # 设置位置
        if hasattr(node, 'position'):
            graphics_item.setPos(node.position['x'], node.position['y'])
        
        # 保存映射
        self.node_graphics[node.id] = graphics_item
        
        return graphics_item
    
    def remove_node_graphics(self, node: BaseNode):
        """移除节点图形项"""
        if node.id in self.node_graphics:
            graphics_item = self.node_graphics[node.id]
            self.scene.removeItem(graphics_item)
            del self.node_graphics[node.id]
    
    def add_connection_graphics(self, connection: Connection) -> ConnectionGraphicsItem:
        """添加连接图形项"""
        # 创建图形项
        graphics_item = ConnectionGraphicsItem(connection)
        
        # 添加到场景
        self.scene.addItem(graphics_item)
        
        # 更新连接位置
        self.update_connection_graphics(connection)
        
        # 保存映射
        self.connection_graphics[connection.id] = graphics_item
        
        return graphics_item
    
    def remove_connection_graphics(self, connection: Connection):
        """移除连接图形项"""
        if connection.id in self.connection_graphics:
            graphics_item = self.connection_graphics[connection.id]
            self.scene.removeItem(graphics_item)
            del self.connection_graphics[connection.id]
    
    def update_connection_graphics(self, connection: Connection):
        """更新连接图形项位置"""
        if connection.id not in self.connection_graphics:
            return
        
        graphics_item = self.connection_graphics[connection.id]
        
        # 获取源节点和目标节点的图形项
        source_graphics = self.node_graphics.get(connection.source_node.id)
        target_graphics = self.node_graphics.get(connection.target_node.id)
        
        if source_graphics and target_graphics:
            # 源端口位置
            source_pos = source_graphics.get_output_port_position(connection.source_port)
            if source_pos:
                graphics_item.set_source_pos(source_pos)
            
            # 目标端口位置
            target_pos = target_graphics.get_input_port_position(connection.target_port)
            if target_pos:
                graphics_item.set_target_pos(target_pos)
    
    def update_all_connections(self):
        """更新所有连接"""
        if not self.workflow:
            return
        
        for connection in self.workflow.get_connections():
            self.update_connection_graphics(connection)
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件（缩放）"""
        # 缩放因子
        scale_factor = 1.15
        
        if event.angleDelta().y() > 0:
            # 向上滚动，放大
            self.scale(scale_factor, scale_factor)
        else:
            # 向下滚动，缩小
            self.scale(1.0 / scale_factor, 1.0 / scale_factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == Qt.LeftButton:
            # 检查是否点击在端口上
            item = self.scene.itemAt(scene_pos, self.transform())
            
            if hasattr(item, 'get_port'):
                # 开始创建连接
                self.start_connection(item)
                return
            
            # 发送画布点击信号
            self.canvas_clicked.emit(scene_pos)
        
        elif event.button() == Qt.RightButton:
            # 右键菜单
            self.show_context_menu(event.pos(), scene_pos)
            return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.creating_connection and self.temp_connection:
            # 更新临时连接
            scene_pos = self.mapToScene(event.pos())
            self.temp_connection.set_target_pos(scene_pos)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.creating_connection:
            # 完成连接创建
            scene_pos = self.mapToScene(event.pos())
            self.finish_connection(scene_pos)
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """键盘按下事件"""
        if event.key() == Qt.Key_Delete:
            # 删除选中的项目
            self.delete_selected_items()
        elif event.key() == Qt.Key_Escape:
            # 取消连接创建
            self.cancel_connection()
        elif event.key() == Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            # 全选
            self.select_all_nodes()
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            # 复制
            self.copy_selected_nodes()
        elif event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            # 粘贴
            self.paste_nodes()
        
        super().keyPressEvent(event)
    
    def start_connection(self, port_item):
        """开始创建连接"""
        self.creating_connection = True
        self.connection_start_port = port_item
        
        # 创建临时连接
        from ...core.connection import Connection
        temp_conn = Connection(None, None, "", "")
        self.temp_connection = ConnectionGraphicsItem(temp_conn)
        self.temp_connection.set_source_pos(port_item.scenePos())
        self.scene.addItem(self.temp_connection)
    
    def finish_connection(self, target_pos: QPointF):
        """完成连接创建"""
        if not self.creating_connection or not self.connection_start_port:
            return
        
        # 查找目标端口
        target_item = self.scene.itemAt(target_pos, self.transform())
        
        if hasattr(target_item, 'get_port'):
            source_port = self.connection_start_port.get_port()
            target_port = target_item.get_port()
            
            # 检查连接是否有效
            if self.can_create_connection(source_port, target_port):
                self.create_connection(source_port, target_port)
        
        self.cancel_connection()
    
    def cancel_connection(self):
        """取消连接创建"""
        if self.temp_connection:
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
        
        self.creating_connection = False
        self.connection_start_port = None
    
    def can_create_connection(self, source_port, target_port) -> bool:
        """检查是否可以创建连接"""
        from ...core.port import PortType
        
        # 检查端口类型
        if source_port.port_type == target_port.port_type:
            return False
        
        # 检查数据类型兼容性
        if not self.workflow:
            return True
        
        return self.workflow.can_connect(source_port, target_port)
    
    def create_connection(self, source_port, target_port):
        """创建连接"""
        if not self.workflow:
            return
        
        try:
            # 在工作流中创建连接
            connection = self.workflow.add_connection(
                source_port.node, target_port.node,
                source_port.name, target_port.name
            )
            
            if connection:
                # 添加图形项
                self.add_connection_graphics(connection)
                
                # 发送信号
                self.connection_created.emit(connection)
                
        except Exception as e:
            QMessageBox.warning(self, "连接创建失败", str(e))
    
    def show_context_menu(self, pos: QPoint, scene_pos: QPointF):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 获取点击的项目
        item = self.scene.itemAt(scene_pos, self.transform())
        
        if isinstance(item, NodeGraphicsItem):
            # 节点菜单
            self.add_node_menu_actions(menu, item.get_node())
        elif isinstance(item, ConnectionGraphicsItem):
            # 连接菜单
            self.add_connection_menu_actions(menu, item.get_connection())
        else:
            # 画布菜单
            self.add_canvas_menu_actions(menu, scene_pos)
        
        if not menu.isEmpty():
            menu.exec_(self.mapToGlobal(pos))
    
    def add_node_menu_actions(self, menu: QMenu, node: BaseNode):
        """添加节点菜单项"""
        # 执行节点
        execute_action = QAction("执行节点", self)
        execute_action.triggered.connect(lambda: self.execute_node(node))
        menu.addAction(execute_action)
        
        menu.addSeparator()
        
        # 复制/删除
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(lambda: self.copy_node(node))
        menu.addAction(copy_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_node(node))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # 属性
        properties_action = QAction("属性", self)
        properties_action.triggered.connect(lambda: self.show_node_properties(node))
        menu.addAction(properties_action)
    
    def add_connection_menu_actions(self, menu: QMenu, connection: Connection):
        """添加连接菜单项"""
        # 删除连接
        delete_action = QAction("删除连接", self)
        delete_action.triggered.connect(lambda: self.delete_connection(connection))
        menu.addAction(delete_action)
    
    def add_canvas_menu_actions(self, menu: QMenu, scene_pos: QPointF):
        """添加画布菜单项"""
        # 粘贴
        if hasattr(self, 'clipboard_nodes') and self.clipboard_nodes:
            paste_action = QAction("粘贴", self)
            paste_action.triggered.connect(lambda: self.paste_nodes(scene_pos))
            menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.triggered.connect(self.select_all_nodes)
        menu.addAction(select_all_action)
        
        # 清空选择
        clear_selection_action = QAction("清空选择", self)
        clear_selection_action.triggered.connect(self.clear_selection)
        menu.addAction(clear_selection_action)
    
    def execute_node(self, node: BaseNode):
        """执行节点"""
        if hasattr(self.parent(), 'execute_node'):
            self.parent().execute_node(node)
    
    def copy_node(self, node: BaseNode):
        """复制节点"""
        # 这里实现节点复制逻辑
        pass
    
    def delete_node(self, node: BaseNode):
        """删除节点"""
        if self.workflow:
            self.workflow.remove_node(node)
            self.remove_node_graphics(node)
    
    def delete_connection(self, connection: Connection):
        """删除连接"""
        if self.workflow:
            self.workflow.remove_connection(connection)
            self.remove_connection_graphics(connection)
    
    def show_node_properties(self, node: BaseNode):
        """显示节点属性"""
        if hasattr(self.parent(), 'show_node_properties'):
            self.parent().show_node_properties(node)
    
    def delete_selected_items(self):
        """删除选中的项目"""
        selected_items = self.scene.selectedItems()
        
        for item in selected_items:
            if isinstance(item, NodeGraphicsItem):
                self.delete_node(item.get_node())
            elif isinstance(item, ConnectionGraphicsItem):
                self.delete_connection(item.get_connection())
    
    def select_all_nodes(self):
        """全选节点"""
        for graphics_item in self.node_graphics.values():
            graphics_item.setSelected(True)
    
    def clear_selection(self):
        """清空选择"""
        self.scene.clearSelection()
    
    def copy_selected_nodes(self):
        """复制选中的节点"""
        selected_nodes = []
        for item in self.scene.selectedItems():
            if isinstance(item, NodeGraphicsItem):
                selected_nodes.append(item.get_node())
        
        if selected_nodes:
            self.clipboard_nodes = selected_nodes.copy()
    
    def paste_nodes(self, position: QPointF = None):
        """粘贴节点"""
        if not hasattr(self, 'clipboard_nodes') or not self.clipboard_nodes:
            return
        
        if position is None:
            position = self.mapToScene(self.viewport().rect().center())
        
        # 这里实现节点粘贴逻辑
        # 需要根据具体的节点复制实现
        pass
    
    def on_node_position_changed(self, node: BaseNode):
        """节点位置变化处理"""
        # 更新相关连接
        if self.workflow:
            for connection in self.workflow.get_connections():
                if connection.source_node == node or connection.target_node == node:
                    self.update_connection_graphics(connection)
    
    def on_node_selection_changed(self, node: BaseNode, selected: bool):
        """节点选择状态变化处理"""
        if selected:
            self.node_selected.emit(node)
    
    def on_selection_changed(self):
        """选择变化处理"""
        selected_nodes = []
        for item in self.scene.selectedItems():
            if isinstance(item, NodeGraphicsItem):
                selected_nodes.append(item.get_node())
        
        self.selection_changed.emit(selected_nodes)
    
    def zoom_to_fit(self):
        """缩放以适应所有内容"""
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    
    def zoom_to_selection(self):
        """缩放到选中项目"""
        selected_items = self.scene.selectedItems()
        if selected_items:
            # 计算选中项目的边界
            rect = QRectF()
            for item in selected_items:
                rect = rect.united(item.sceneBoundingRect())
            
            self.fitInView(rect, Qt.KeepAspectRatio)
    
    def set_zoom(self, zoom_level: float):
        """设置缩放级别"""
        # 重置变换
        self.resetTransform()
        # 应用缩放
        self.scale(zoom_level, zoom_level)
    
    def get_zoom(self) -> float:
        """获取当前缩放级别"""
        return self.transform().m11()
    
    def center_on_node(self, node: BaseNode):
        """居中显示指定节点"""
        if node.id in self.node_graphics:
            graphics_item = self.node_graphics[node.id]
            self.centerOn(graphics_item)
    
    def get_selected_nodes(self) -> List[BaseNode]:
        """获取选中的节点"""
        selected_nodes = []
        for item in self.scene.selectedItems():
            if isinstance(item, NodeGraphicsItem):
                selected_nodes.append(item.get_node())
        return selected_nodes
    
    def highlight_node(self, node: BaseNode, highlight: bool = True):
        """高亮显示节点"""
        if node.id in self.node_graphics:
            graphics_item = self.node_graphics[node.id]
            graphics_item.highlight(highlight)
    
    def set_node_executing(self, node: BaseNode, executing: bool):
        """设置节点执行状态"""
        if node.id in self.node_graphics:
            graphics_item = self.node_graphics[node.id]
            graphics_item.set_executing(executing)
    
    def set_node_error(self, node: BaseNode, has_error: bool):
        """设置节点错误状态"""
        if node.id in self.node_graphics:
            graphics_item = self.node_graphics[node.id]
            graphics_item.set_error(has_error)