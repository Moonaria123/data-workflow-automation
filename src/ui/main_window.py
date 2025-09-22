"""
数据处理自动化工作流应用 - 主窗口

版本：V1.0
创建日期：2025-09-06
依据文档：《用户需求说明书》FR-001可视化工作流设计、《模块化开发方案》UI层设计
框架：PyQt6主窗口架构

主窗口类，负责：
1. 整体界面布局和组件管理
2. 菜单栏、工具栏、状态栏
3. 画布、面板等核心组件集成
4. 用户交互事件处理
5. 窗口状态管理
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QMenuBar,
    QToolBar,
    QStatusBar,
    QDockWidget,
    QTabWidget,
    QLabel,
    QProgressBar,
    QMessageBox,
    QDialog,
    QFileDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QKeySequence, QPixmap, QAction, QActionGroup

from src.app.application import get_application
from src.app.controllers.workflow_controller import WorkflowController


class MainWindow(QMainWindow):
    """主窗口类"""

    # 窗口信号
    workflow_changed = pyqtSignal(str)  # 当前工作流变更
    status_message = pyqtSignal(str, int)  # 状态栏消息

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = QSettings()

        # 窗口状态
        self.current_workflow_id: Optional[str] = None
        self.is_modified = False
        self.auto_save_timer = QTimer()

        # 组件引用
        self.central_widget: Optional[QWidget] = None
        self.main_splitter: Optional[QSplitter] = None
        self.canvas_widget: Optional[QWidget] = None
        self.workflow_canvas: Optional[QWidget] = None
        self.main_toolbar: Optional[QToolBar] = None
        self.property_dock: Optional[QDockWidget] = None
        self.log_dock: Optional[QDockWidget] = None
        self.monitor_dock: Optional[QDockWidget] = None
        self.node_palette_dock: Optional[QDockWidget] = None
        self.data_preview_dock: Optional[QDockWidget] = None

        # 状态栏组件（不要在此处使用内联类型注解，避免某些检查器报错）
        self.status_label = None
        self.progress_bar = None
        self.memory_label = None

        # 菜单/面板菜单句柄
        self.view_menu = None
        self.toolbar_menu = None
        self.panels_menu = None
        self._panel_actions = {}
        self._default_geometry = None
        self._default_state = None

        # 初始化窗口与UI
        self._init_window()
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbars()
        self._setup_status_bar()
        self._setup_dock_widgets()
        self._init_view_menu_panel_actions()
        self._connect_signals()
        self._restore_window_state()

        # 控制器
        self.workflow_controller = WorkflowController()

        # 连接应用程序事件
        app = get_application()
        if app:
            app.event_bus.memory_warning.connect(self._on_memory_warning)
            app.event_bus.performance_warning.connect(self._on_performance_warning)

        self.logger.info("主窗口初始化完成")

    def _init_window(self) -> None:
        """初始化窗口基本设置"""
        self.setWindowTitle("数据工作流自动化平台")
        self.setWindowIcon(self._load_icon("app.png"))

        # 设置最小尺寸
        self.setMinimumSize(1200, 800)

        # 设置默认尺寸
        self.resize(1600, 1000)

        # 居中显示
        self._center_window()

    def _setup_ui(self) -> None:
        """设置主界面布局"""
        # 导入画布组件（避免循环导入）
        from ui.canvas.workflow_canvas import WorkflowCanvas

        # 创建中央组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 创建工作流画布
        self.workflow_canvas = WorkflowCanvas(self)
        self.canvas_widget = self.workflow_canvas  # 为了兼容性
        self.main_splitter.addWidget(self.workflow_canvas)

        # 设置分割器比例
        self.main_splitter.setStretchFactor(0, 1)  # 画布占主要空间

        # 设置布局
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_splitter)

        # 连接画布信号
        self.workflow_canvas.nodeSelected.connect(self._on_node_selected)
        self.workflow_canvas.nodeDeselected.connect(self._on_node_deselected)
        self.workflow_canvas.selectionChanged.connect(self._on_selection_changed)

    def _setup_menus(self) -> None:
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_action = QAction(QIcon(self._load_icon("new.png")), "新建工作流(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_workflow)
        file_menu.addAction(new_action)

        open_action = QAction(
            QIcon(self._load_icon("open.png")), "打开工作流(&O)", self
        )
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_workflow)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction(QIcon(self._load_icon("save.png")), "保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_workflow)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为(&A)", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_workflow_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        undo_action = QAction(QIcon(self._load_icon("undo.png")), "撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(self._load_icon("redo.png")), "重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)

        # 执行菜单
        run_menu = menubar.addMenu("执行(&R)")

        run_action = QAction(QIcon(self._load_icon("run.png")), "运行工作流(&R)", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self._run_workflow)
        run_menu.addAction(run_action)

        stop_action = QAction(QIcon(self._load_icon("stop.png")), "停止执行(&S)", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        stop_action.triggered.connect(self._stop_workflow)
        run_menu.addAction(stop_action)

        # 视图菜单
        self.view_menu = menubar.addMenu("视图(&V)")

        # 工具栏显示/隐藏
        self.toolbar_menu = self.view_menu.addMenu("工具栏")

        # 面板显示/隐藏（在dock创建后填充）
        self.panels_menu = self.view_menu.addMenu("面板")

        # 重置布局
        reset_layout_action = QAction("重置布局", self)
        reset_layout_action.setStatusTip("恢复默认面板布局与位置")
        reset_layout_action.triggered.connect(self._reset_layout)
        self.view_menu.addSeparator()
        self.view_menu.addAction(reset_layout_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbars(self) -> None:
        """设置工具栏"""
        # 主工具栏
        self.main_toolbar = self.addToolBar("主工具栏")
        self.main_toolbar.setObjectName("mainToolbar")
        self.main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # 文件操作
        new_action = QAction(QIcon(self._load_icon("new.png")), "新建", self)
        new_action.triggered.connect(self._new_workflow)
        self.main_toolbar.addAction(new_action)

        open_action = QAction(QIcon(self._load_icon("open.png")), "打开", self)
        open_action.triggered.connect(self._open_workflow)
        self.main_toolbar.addAction(open_action)

        save_action = QAction(QIcon(self._load_icon("save.png")), "保存", self)
        save_action.triggered.connect(self._save_workflow)
        self.main_toolbar.addAction(save_action)

        self.main_toolbar.addSeparator()

        # 编辑操作
        undo_action = QAction(QIcon(self._load_icon("undo.png")), "撤销", self)
        undo_action.triggered.connect(self._undo)
        self.main_toolbar.addAction(undo_action)

        redo_action = QAction(QIcon(self._load_icon("redo.png")), "重做", self)
        redo_action.triggered.connect(self._redo)
        self.main_toolbar.addAction(redo_action)

        self.main_toolbar.addSeparator()

        # 画布模式切换
        select_action = QAction(QIcon(self._load_icon("select.png")), "选择", self)
        select_action.setShortcut(QKeySequence("Ctrl+S"))
        select_action.setCheckable(True)
        select_action.setChecked(True)
        select_action.triggered.connect(lambda: self._set_canvas_mode("select"))
        self.main_toolbar.addAction(select_action)

        connect_action = QAction(QIcon(self._load_icon("connect.png")), "连线", self)
        connect_action.setShortcut(QKeySequence("Ctrl+C"))
        connect_action.setCheckable(True)
        connect_action.triggered.connect(lambda: self._set_canvas_mode("connect"))
        self.main_toolbar.addAction(connect_action)

        # 创建模式按钮组以确保互斥
        mode_group = QActionGroup(self)
        mode_group.addAction(select_action)
        mode_group.addAction(connect_action)
        mode_group.setExclusive(True)

        # 保存动作引用以便后续使用
        self.select_action = select_action
        self.connect_action = connect_action

        self.main_toolbar.addSeparator()

        # 执行操作
        run_action = QAction(QIcon(self._load_icon("run.png")), "运行", self)
        run_action.triggered.connect(self._run_workflow)
        self.main_toolbar.addAction(run_action)

        stop_action = QAction(QIcon(self._load_icon("stop.png")), "停止", self)
        stop_action.triggered.connect(self._stop_workflow)
        self.main_toolbar.addAction(stop_action)

    def _setup_status_bar(self) -> None:
        """设置状态栏"""
        status_bar = self.statusBar()

        # 状态信息标签
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)

        # 内存使用标签
        self.memory_label = QLabel("内存: 0MB")
        status_bar.addPermanentWidget(self.memory_label)

        # 连接状态消息信号
        self.status_message.connect(self._update_status_message)

    def _setup_dock_widgets(self) -> None:
        """设置停靠窗口"""

        # 节点工具箱
        self.node_palette_dock = QDockWidget("节点工具箱", self)
        self.node_palette_dock.setObjectName("nodePaletteDock")
        self.node_palette_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        palette_widget = self._create_node_palette_placeholder()
        self.node_palette_dock.setWidget(palette_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.node_palette_dock)

        # 属性面板
        self.property_dock = QDockWidget("属性面板", self)
        self.property_dock.setObjectName("propertyDock")
        self.property_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        property_widget = self._create_property_panel_placeholder()
        self.property_dock.setWidget(property_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_dock)

        # 日志面板
        self.log_dock = QDockWidget("日志", self)
        self.log_dock.setObjectName("logDock")
        self.log_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        log_widget = self._create_log_panel_placeholder()
        self.log_dock.setWidget(log_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)

        # 数据预览面板
        self.data_preview_dock = QDockWidget("数据预览", self)
        self.data_preview_dock.setObjectName("dataPreviewDock")
        self.data_preview_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        preview_widget = self._create_data_preview_placeholder()
        self.data_preview_dock.setWidget(preview_widget)
        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea, self.data_preview_dock
        )

        # 监控面板
        self.monitor_dock = QDockWidget("执行监控", self)
        self.monitor_dock.setObjectName("monitorDock")
        self.monitor_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        monitor_widget = self._create_monitor_panel()
        self.monitor_dock.setWidget(monitor_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.monitor_dock)

        # 设置底部停靠窗口为选项卡模式
        self.tabifyDockWidget(self.log_dock, self.data_preview_dock)
        self.tabifyDockWidget(self.data_preview_dock, self.monitor_dock)
        self.log_dock.raise_()  # 默认显示日志面板

        # 记录默认窗口布局，以便后续"重置布局"
        try:
            self._default_geometry = self.saveGeometry()
            self._default_state = self.saveState()
        except Exception:
            pass

    def _init_view_menu_panel_actions(self) -> None:
        """在dock创建后填充"视图/面板"菜单并建立联动。"""
        if not self.panels_menu:
            return

        self.panels_menu.clear()

        def add_panel_toggle(dock: QDockWidget, title: str, key: str):
            action = QAction(title, self)
            action.setCheckable(True)
            action.setChecked(dock.isVisible())
            action.toggled.connect(
                lambda checked, d=dock: self._toggle_dock(d, checked)
            )
            # 让dock的可见性变化反向更新菜单项状态
            dock.visibilityChanged.connect(lambda vis, a=action: a.setChecked(vis))
            self.panels_menu.addAction(action)
            self._panel_actions[key] = action

        if self.node_palette_dock:
            add_panel_toggle(self.node_palette_dock, "节点工具箱", "node_palette")
        if self.property_dock:
            add_panel_toggle(self.property_dock, "属性面板", "property")
        if self.log_dock:
            add_panel_toggle(self.log_dock, "日志", "log")
        if self.data_preview_dock:
            add_panel_toggle(self.data_preview_dock, "数据预览", "data_preview")
        if self.monitor_dock:
            add_panel_toggle(self.monitor_dock, "执行监控", "monitor")

        # 额外提供：显示全部面板
        self.panels_menu.addSeparator()
        show_all_action = QAction("显示全部面板", self)
        show_all_action.triggered.connect(self._show_all_panels)
        self.panels_menu.addAction(show_all_action)

    def _toggle_dock(self, dock: QDockWidget, checked: bool) -> None:
        """切换Dock显示/隐藏。"""
        try:
            dock.setVisible(checked)
            if checked:
                dock.raise_()
        except Exception:
            pass

    def _show_all_panels(self) -> None:
        """显示所有面板。"""
        for dock in [
            self.node_palette_dock,
            self.property_dock,
            self.log_dock,
            self.data_preview_dock,
            self.monitor_dock,
        ]:
            if dock:
                dock.show()
                try:
                    dock.raise_()
                except Exception:
                    pass
        # 同步菜单勾选
        for action in self._panel_actions.values():
            action.setChecked(True)

    def _reset_layout(self) -> None:
        """重置窗口布局到默认（初次加载）布局。"""
        try:
            if self._default_geometry:
                self.restoreGeometry(self._default_geometry)
            if self._default_state:
                self.restoreState(self._default_state)
            # 确保所有面板可见
            self._show_all_panels()
            self.status_message.emit("布局已重置", 2000)
        except Exception as e:
            self.status_message.emit("重置布局失败", 3000)
            self.logger.error(f"重置布局失败: {e}")

    def _create_node_palette_placeholder(self) -> QWidget:
        """创建节点工具箱"""
        # 导入节点工具箱组件
        from ui.panels.node_palette import NodePalette

        # 创建节点工具箱
        self.node_palette = NodePalette()

        # 连接信号
        self.node_palette.nodeRequested.connect(self._on_node_requested)
        self.node_palette.nodeSelected.connect(self._on_node_selected)

        return self.node_palette

    def _create_property_panel_placeholder(self) -> QWidget:
        """创建属性面板组件"""
        # 导入属性面板组件
        from ui.panels.property_panel import PropertyPanel

        # 创建属性面板
        self.property_panel = PropertyPanel()

        # 连接属性面板信号
        self.property_panel.propertyChanged.connect(self._on_node_property_changed)
        self.property_panel.nodePropertiesUpdated.connect(
            self._on_node_properties_updated
        )
        # 连接元数据信号
        try:
            self.property_panel.metadataChanged.connect(self._on_node_metadata_changed)
            self.property_panel.nodeMetadataUpdated.connect(
                self._on_node_metadata_updated
            )
        except Exception:
            pass

        return self.property_panel

    def _create_log_panel_placeholder(self) -> QWidget:
        """创建日志面板组件"""
        # 导入日志面板组件
        from ui.panels.log_panel import LogPanel

        # 创建日志面板
        self.log_panel = LogPanel()

        # 连接日志面板信号
        self.log_panel.logExportRequested.connect(self._on_log_export_requested)
        self.log_panel.logClearRequested.connect(self._on_log_cleared)

        return self.log_panel

    def _create_data_preview_placeholder(self) -> QWidget:
        """创建数据预览面板组件"""
        # 导入数据预览面板组件
        from ui.panels.data_preview import DataPreviewPanel

        # 创建数据预览面板
        self.data_preview_panel = DataPreviewPanel()

        # 连接数据预览面板信号
        self.data_preview_panel.dataExportRequested.connect(
            self._on_data_export_requested
        )
        self.data_preview_panel.nodeDataRequested.connect(self._on_node_data_requested)

        return self.data_preview_panel

    def _create_monitor_panel(self) -> QWidget:
        """创建监控面板组件"""
        # 导入监控面板组件
        from ui.panels.monitor_panel import MonitorPanel

        # 创建监控面板
        self.monitor_panel = MonitorPanel()

        # 连接监控面板信号
        self.monitor_panel.startRequested.connect(self._on_workflow_start_requested)
        self.monitor_panel.pauseRequested.connect(self._on_workflow_pause_requested)
        self.monitor_panel.stopRequested.connect(self._on_workflow_stop_requested)
        self.monitor_panel.nodeSelected.connect(self._on_monitor_node_selected)

        return self.monitor_panel

    def _connect_signals(self) -> None:
        """连接信号和槽"""
        # 自动保存定时器
        self.auto_save_timer.timeout.connect(self._auto_save)

        # 启动自动保存（每5分钟）
        app = get_application()
        if app:
            interval = app.get_setting("ui/auto_save_interval", 300)
            self.auto_save_timer.start(interval * 1000)  # 转换为毫秒

    def _center_window(self) -> None:
        """窗口居中显示"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def _load_icon(self, filename: str) -> QIcon:
        """加载图标"""
        icon_path = Path("resources/icons") / filename
        if icon_path.exists():
            return QIcon(str(icon_path))
        else:
            # 返回默认图标或空图标
            return QIcon()

    def _restore_window_state(self) -> None:
        """恢复窗口状态"""
        # 恢复窗口几何形状
        geometry = self.settings.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # 恢复窗口状态（工具栏、停靠窗口等）
        state = self.settings.value("window/state")
        if state:
            self.restoreState(state)

    def _save_window_state(self) -> None:
        """保存窗口状态"""
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())

    # ==========================================================================
    # 菜单和工具栏动作处理
    # ==========================================================================

    def _new_workflow(self) -> None:
        """新建工作流"""
        if self._check_save_changes():
            self.current_workflow_id = None
            self.is_modified = False
            self._update_window_title()
            self.status_message.emit("新建工作流", 2000)
            self.logger.info("新建工作流")

    def _open_workflow(self) -> None:
        """打开工作流"""
        if not self._check_save_changes():
            return
        # 简易选择：从数据库列出现有工作流
        try:
            workflows = self.workflow_controller.list_workflows()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取工作流列表失败:\n{e}")
            return

        if not workflows:
            QMessageBox.information(self, "提示", "尚无已保存的工作流。")
            return

        # 使用"最近/全部工作流"对话框
        try:
            from ui.dialogs.workflow_open_dialog import WorkflowOpenDialog
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载对话框失败:\n{e}")
            return

        # Inject delete callback; on success, clear selection state if current is deleted
        def _on_delete(wid: str) -> bool:
            try:
                self.workflow_controller.delete_workflow(wid)
                if self.current_workflow_id == wid:
                    self.current_workflow_id = None
                    self.is_modified = False
                    self._update_window_title()
                return True
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败:\n{e}")
                return False

        dlg = WorkflowOpenDialog(workflows, on_delete=_on_delete, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        workflow_id = dlg.selected_workflow_id()
        if not workflow_id:
            return

        try:
            loaded = self.workflow_controller.load_canvas(
                self.workflow_canvas, workflow_id=workflow_id
            )
            if loaded:
                self.current_workflow_id = workflow_id
                self.is_modified = False
                self._update_window_title()
                self.status_message.emit(f"已打开工作流: {workflow_id}", 3000)
            else:
                QMessageBox.warning(self, "提示", f"未找到工作流: {workflow_id}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开工作流失败:\n{e}")

    def _save_workflow(self) -> None:
        """保存工作流"""
        if not self.current_workflow_id:
            return self._save_workflow_as()

        # 读取名称并保存
        workflow_id = self.current_workflow_id
        name = workflow_id  # 简化：名称默认用ID
        try:
            self.workflow_controller.save_canvas(
                self.workflow_canvas, workflow_id=workflow_id, name=name
            )
            self.is_modified = False
            self._update_window_title()
            self.status_message.emit("工作流已保存", 2000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def _save_workflow_as(self) -> None:
        """另存工作流"""
        from PyQt6.QtWidgets import QInputDialog

        workflow_id, ok = QInputDialog.getText(self, "保存工作流", "输入工作流ID:")
        if not ok or not workflow_id:
            return
        name, ok = QInputDialog.getText(self, "保存工作流", "输入工作流名称:", text=workflow_id)
        if not ok or not name:
            return

        try:
            self.workflow_controller.save_canvas(
                self.workflow_canvas, workflow_id=workflow_id, name=name
            )
            self.current_workflow_id = workflow_id
            self.is_modified = False
            self._update_window_title()
            self.status_message.emit(f"已保存工作流: {workflow_id}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def _undo(self) -> None:
        """撤销操作"""
        # TODO: 实现撤销逻辑
        self.status_message.emit("撤销", 1000)

    def _redo(self) -> None:
        """重做操作"""
        # TODO: 实现重做逻辑
        self.status_message.emit("重做", 1000)

    def _run_workflow(self) -> None:
        """运行工作流"""
        # TODO: 实现工作流运行逻辑
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_message.emit("正在运行工作流...", 0)
        self.logger.info("开始运行工作流")

    def _stop_workflow(self) -> None:
        """停止工作流"""
        # TODO: 实现工作流停止逻辑
        self.progress_bar.setVisible(False)
        self.status_message.emit("工作流已停止", 2000)
        self.logger.info("停止工作流")

    def _auto_save(self) -> None:
        """自动保存"""
        if self.is_modified and self.current_workflow_id:
            self._save_workflow()
            self.logger.debug("自动保存完成")

    def _show_about(self) -> None:
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            """<h3>数据工作流自动化平台</h3>
            <p>版本: 1.0.0</p>
            <p>一个可视化的数据处理工作流设计和执行平台</p>
            <p>技术栈: Python 3.9+ + PyQt6 + Polars</p>
            <p>©2025 DWA Development Team</p>""",
        )

    def _check_save_changes(self) -> bool:
        """检查是否保存修改"""
        if not self.is_modified:
            return True

        reply = QMessageBox.question(
            self,
            "保存修改",
            "工作流已修改，是否保存？",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Save:
            self._save_workflow()
            return True
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def _update_window_title(self) -> None:
        """更新窗口标题"""
        title = "数据工作流自动化平台"
        if self.current_workflow_id:
            title += f" - {self.current_workflow_id}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)

    def _update_status_message(self, message: str, timeout: int) -> None:
        """更新状态栏消息"""
        if self.status_label:
            self.status_label.setText(message)
            if timeout > 0:
                QTimer.singleShot(timeout, lambda: self.status_label.setText("就绪"))

    def _on_memory_warning(self, memory_mb: float) -> None:
        """内存警告处理"""
        if self.memory_label:
            self.memory_label.setText(f"内存: {memory_mb:.0f}MB ⚠️")
            self.memory_label.setStyleSheet("QLabel { color: orange; }")

    def _on_performance_warning(self, message: str) -> None:
        """性能警告处理"""
        self.status_message.emit(f"性能警告: {message}", 5000)
        self.logger.warning(f"性能警告: {message}")

    # ==========================================================================
    # 窗口事件处理
    # ==========================================================================

    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        if self._check_save_changes():
            self._save_window_state()
            self.auto_save_timer.stop()
            self.logger.info("主窗口正在关闭")
            event.accept()
        else:
            event.ignore()

    def showEvent(self, event) -> None:
        """窗口显示事件"""
        super().showEvent(event)
        self.status_message.emit("欢迎使用数据工作流自动化平台", 3000)

    # ==========================================================================
    # 公共接口
    # ==========================================================================

    def set_workflow_modified(self, modified: bool = True) -> None:
        """设置工作流修改状态"""
        if self.is_modified != modified:
            self.is_modified = modified
            self._update_window_title()

    def show_progress(self, value: int = -1, maximum: int = 100) -> None:
        """显示进度"""
        if value < 0:
            self.progress_bar.setRange(0, 0)  # 不确定进度
        else:
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)

    def hide_progress(self) -> None:
        """隐藏进度"""
        self.progress_bar.setVisible(False)

    def update_memory_usage(self, memory_mb: float) -> None:
        """更新内存使用显示"""
        if self.memory_label:
            self.memory_label.setText(f"内存: {memory_mb:.0f}MB")

            # 根据使用量设置颜色
            app = get_application()
            if app and memory_mb > app.max_memory_mb * 0.8:
                self.memory_label.setStyleSheet("QLabel { color: red; }")
            elif memory_mb > 1024:  # 1GB
                self.memory_label.setStyleSheet("QLabel { color: orange; }")
            else:
                self.memory_label.setStyleSheet("QLabel { color: green; }")

    # ==========================================================================
    # 画布信号处理
    # ==========================================================================

    def _on_node_requested(self, node_unique_id: str) -> None:
        """处理节点创建请求（使用 unique_id）"""
        self.logger.info(f"请求创建节点: {node_unique_id}")

        # 在画布中心位置创建节点
        if hasattr(self, "workflow_canvas") and self.workflow_canvas:
            # 获取画布中心点
            viewport_center = self.workflow_canvas.viewport().rect().center()
            scene_center = self.workflow_canvas.mapToScene(viewport_center)

            # 请求画布创建节点
            self.workflow_canvas.create_node_at_position(node_unique_id, scene_center)

        # TODO: 通过事件总线通知其他组件
        # 补全超时时长参数，避免信号参数不匹配导致的 TypeError
        self.status_message.emit(f"已添加节点: {node_unique_id}", 2000)

    def _on_node_selected(self, node_info) -> None:
        """节点选择事件处理"""
        # 处理来自节点工具箱的选择事件
        if isinstance(node_info, str):
            self.logger.info(f"节点工具箱选中: {node_info}")
            # 在属性面板中显示节点信息（只读模式）
            if hasattr(self, "property_panel"):
                # TODO: 实现工具箱节点信息展示
                pass
        else:
            # 处理来自画布的选择事件
            node_id = getattr(node_info, "node_id", "unknown")
            # 兼容字段名：优先使用 node_unique_id；旧字段名 node_type 将被逐步移除
            node_unique_id = getattr(node_info, "node_unique_id", None) or getattr(
                node_info, "node_type", "unknown"
            )

            self.logger.info(f"画布节点被选中: {node_id} ({node_unique_id})")

            # 在属性面板中显示节点属性
            if hasattr(self, "property_panel"):
                # 从画布读取该节点已缓存的参数作为初始属性
                node_properties = {}
                try:
                    if hasattr(self, "workflow_canvas") and self.workflow_canvas:
                        node_properties = self.workflow_canvas.get_node_parameters(
                            node_id
                        ) or {}
                except Exception:
                    node_properties = {}

                # 读取元数据，先于渲染设置到底部区域
                node_metadata = {}
                try:
                    if hasattr(self, "workflow_canvas") and self.workflow_canvas:
                        node_metadata = self.workflow_canvas.get_node_metadata(node_id) or {}
                except Exception:
                    node_metadata = {}

                # 设置属性面板
                # 新签名：传递 unique_id
                try:
                    self.property_panel.set_node_properties(
                        node_id, node_unique_id, node_properties
                    )
                except TypeError:
                    # 兼容旧签名，仍然传入第二个参数
                    self.property_panel.set_node_properties(
                        node_id, node_unique_id, node_properties
                    )

                # 尝试将元数据填充到面板（如果面板提供该接口）
                try:
                    if hasattr(self.property_panel, "set_node_metadata"):
                        self.property_panel.set_node_metadata(node_metadata)
                except Exception:
                    pass

    def _on_node_deselected(self) -> None:
        """节点取消选择事件处理"""
        self.logger.debug("节点选择已清空")

        # 清空属性面板
        if hasattr(self, "property_panel"):
            self.property_panel.clear_selection()

    def _on_selection_changed(self, selected_items) -> None:
        """选择变化事件处理"""
        count = len(selected_items)
        if count == 0:
            self.status_message.emit("", 0)
        elif count == 1:
            item_type = type(selected_items[0]).__name__
            self.status_message.emit(f"已选择1个{item_type}", 2000)
        else:
            self.status_message.emit(f"已选择{count}个项目", 2000)

    def _set_canvas_mode(self, mode: str) -> None:
        """设置画布模式"""
        if hasattr(self, "workflow_canvas") and self.workflow_canvas:
            if mode == "select":
                self.workflow_canvas._toggle_connection_mode(False)
                self.status_message.emit("已切换到选择模式", 2000)
            elif mode == "connect":
                self.workflow_canvas._toggle_connection_mode(True)
                self.status_message.emit("已切换到连线模式，点击端口开始连接", 3000)
        else:
            self.logger.warning("画布组件未初始化")

    def _on_node_property_changed(self, node_id: str, property_key: str, value) -> None:
        """处理节点属性变更"""
        self.logger.info(f"节点属性变更: {node_id}.{property_key} = {value}")

        # 如果有画布，通知画布更新节点属性
        if hasattr(self, "workflow_canvas") and self.workflow_canvas:
            try:
                self.workflow_canvas.set_node_parameter(node_id, property_key, value)
                self.is_modified = True
            except Exception as e:
                self.logger.warning(f"更新画布节点参数失败: {e}")

    def _on_node_properties_updated(self, node_id: str, all_properties: dict) -> None:
        """处理节点所有属性更新"""
        self.logger.info(f"节点所有属性更新: {node_id}")

        # 如果有画布，通知画布更新节点
        if hasattr(self, "workflow_canvas") and self.workflow_canvas:
            try:
                self.workflow_canvas.update_node_properties(node_id, all_properties)
                self.is_modified = True
            except Exception as e:
                self.logger.warning(f"批量更新节点参数失败: {e}")

    def _on_node_metadata_changed(self, node_id: str, meta_key: str, value: Any) -> None:
        """处理元数据单项变更"""
        if hasattr(self, "workflow_canvas") and self.workflow_canvas:
            try:
                current = self.workflow_canvas.get_node_metadata(node_id) or {}
                current[meta_key] = value
                self.workflow_canvas.set_node_metadata(node_id, current)
                self.is_modified = True
            except Exception as e:
                self.logger.warning(f"更新节点元数据失败: {e}")

    def _on_node_metadata_updated(self, node_id: str, metadata: Dict[str, Any]) -> None:
        """处理元数据整体更新"""
        if hasattr(self, "workflow_canvas") and self.workflow_canvas:
            try:
                self.workflow_canvas.set_node_metadata(node_id, metadata or {})
                self.is_modified = True
            except Exception as e:
                self.logger.warning(f"批量更新节点元数据失败: {e}")

    # === 新面板信号处理方法 ===

    def _on_log_export_requested(self, file_path: str, log_entries) -> None:
        """处理日志导出请求"""
        self.logger.info(f"请求导出日志到: {file_path}")
        try:
            # TODO: 实现日志导出逻辑
            # 这里可以调用日志系统的导出功能
            app = get_application()
            if app and hasattr(app, "log_manager"):
                app.log_manager.export_logs(file_path, log_entries)
                self.status_message.emit(f"日志已导出到: {file_path}", 3000)
            else:
                self.logger.warning("日志管理器不可用")

        except Exception as e:
            self.logger.error(f"导出日志失败: {e}")
            QMessageBox.critical(self, "错误", f"导出日志失败:\n{str(e)}")

    def _on_log_cleared(self) -> None:
        """处理日志清空请求"""
        self.logger.info("请求清空日志")
        try:
            # TODO: 实现日志清空逻辑
            app = get_application()
            if app and hasattr(app, "log_manager"):
                app.log_manager.clear_logs()
                self.status_message.emit("日志已清空", 2000)
            else:
                self.logger.warning("日志管理器不可用")

        except Exception as e:
            self.logger.error(f"清空日志失败: {e}")

    def _on_data_export_requested(self, file_path: str, data) -> None:
        """处理数据导出请求"""
        self.logger.info(f"请求导出数据到: {file_path}")
        try:
            # TODO: 实现数据导出逻辑
            # 根据文件扩展名选择导出格式
            if file_path.endswith(".csv"):
                # CSV导出
                pass
            elif file_path.endswith(".xlsx"):
                # Excel导出
                pass
            else:
                # 其他格式
                pass

            self.status_message.emit(f"数据已导出到: {file_path}", 3000)

        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            QMessageBox.critical(self, "错误", f"导出数据失败:\n{str(e)}")

    def _on_node_data_requested(self, node_id: str) -> None:
        """处理节点数据获取请求"""
        self.logger.info(f"请求获取节点数据: {node_id}")
        try:
            # TODO: 实现节点数据获取逻辑
            # 从工作流引擎获取节点的执行结果数据
            app = get_application()
            if app and hasattr(app, "workflow_engine"):
                data = app.workflow_engine.get_node_data(node_id)
                if data is not None and hasattr(self, "data_preview_panel"):
                    # 在数据预览面板中显示数据
                    node_name = f"Node_{node_id}"  # TODO: 获取真实节点名称
                    self.data_preview_panel.preview_data(data, node_id, node_name)
                else:
                    self.status_message.emit(f"节点 {node_id} 暂无数据", 2000)
            else:
                self.logger.warning("工作流引擎不可用")

        except Exception as e:
            self.logger.error(f"获取节点数据失败: {e}")

    def _on_workflow_start_requested(self) -> None:
        """处理工作流启动请求"""
        self.logger.info("请求启动工作流")
        try:
            # TODO: 实现工作流启动逻辑
            app = get_application()
            if app and hasattr(app, "workflow_engine"):
                # 启动工作流执行
                app.workflow_engine.start_execution()
                self.status_message.emit("工作流已启动", 2000)

                # 更新监控面板状态
                if hasattr(self, "monitor_panel"):
                    self.monitor_panel.start_monitoring()
            else:
                self.logger.warning("工作流引擎不可用")

        except Exception as e:
            self.logger.error(f"启动工作流失败: {e}")
            QMessageBox.critical(self, "错误", f"启动工作流失败:\n{str(e)}")

    def _on_workflow_pause_requested(self) -> None:
        """处理工作流暂停请求"""
        self.logger.info("请求暂停工作流")
        try:
            # TODO: 实现工作流暂停逻辑
            app = get_application()
            if app and hasattr(app, "workflow_engine"):
                app.workflow_engine.pause_execution()
                self.status_message.emit("工作流已暂停", 2000)

                # 更新监控面板状态
                if hasattr(self, "monitor_panel"):
                    self.monitor_panel.pause_monitoring()
            else:
                self.logger.warning("工作流引擎不可用")

        except Exception as e:
            self.logger.error(f"暂停工作流失败: {e}")

    def _on_workflow_stop_requested(self) -> None:
        """处理工作流停止请求"""
        self.logger.info("请求停止工作流")
        try:
            # TODO: 实现工作流停止逻辑
            app = get_application()
            if app and hasattr(app, "workflow_engine"):
                app.workflow_engine.stop_execution()
                self.status_message.emit("工作流已停止", 2000)

                # 更新监控面板状态
                if hasattr(self, "monitor_panel"):
                    self.monitor_panel.stop_monitoring()
            else:
                self.logger.warning("工作流引擎不可用")

        except Exception as e:
            self.logger.error(f"停止工作流失败: {e}")

    def _on_node_status_update_requested(self, node_id: str) -> None:
        """处理节点状态更新请求"""
        self.logger.info(f"请求更新节点状态: {node_id}")
        try:
            # TODO: 实现节点状态更新逻辑
            app = get_application()
            if app and hasattr(app, "workflow_engine"):
                status = app.workflow_engine.get_node_status(node_id)
                if hasattr(self, "monitor_panel"):
                    self.monitor_panel.update_node_status(node_id, status)
            else:
                self.logger.warning("工作流引擎不可用")

        except Exception as e:
            self.logger.error(f"更新节点状态失败: {e}")

    def _on_monitor_node_selected(self, node_id: str) -> None:
        """处理监控面板节点选择"""
        self.logger.info(f"监控面板选中节点: {node_id}")
        # TODO: 在画布中高亮选中的节点
        # TODO: 在属性面板中显示节点属性
        if hasattr(self, "data_preview_panel"):
            # 在数据预览面板中显示节点数据
            self._on_node_data_requested(node_id)