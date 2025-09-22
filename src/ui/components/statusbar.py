"""
状态栏组件

用于显示应用程序状态信息
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QStatusBar, QLabel, QProgressBar, QPushButton, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon


class StatusBar(QStatusBar):
    """状态栏"""
    
    # 信号
    progress_clicked = pyqtSignal()
    status_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        
        # 状态记录
        self.current_status = "就绪"
        self.progress_value = 0
        self.progress_max = 100
        self.is_busy = False
    
    def setup_ui(self):
        """Setup UI"""
        # 主状态消息
        self.status_label = QLabel("就绪")
        self.status_label.setMinimumWidth(200)
        self.status_label.mousePressEvent = lambda e: self.status_clicked.emit()
        self.addWidget(self.status_label)
        
        # 分隔符
        self.addPermanentWidget(QLabel("|"))
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMinimumWidth(150)
        self.progress_bar.setVisible(False)
        self.progress_bar.mousePressEvent = lambda e: self.progress_clicked.emit()
        self.addPermanentWidget(self.progress_bar)
        
        # 连接状态
        self.connection_label = QLabel()
        self.update_connection_status(False)
        self.addPermanentWidget(self.connection_label)
        
        # 内存使用情况
        self.memory_label = QLabel()
        self.update_memory_usage(0)
        self.addPermanentWidget(self.memory_label)
        
        # 时间
        self.time_label = QLabel()
        self.addPermanentWidget(self.time_label)
    
    def setup_timer(self):
        """Setup timer for updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
        # Memory update timer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_info)
        self.memory_timer.start(5000)  # Update every 5 seconds
    
    def set_status(self, message: str, timeout: int = 0):
        """Set status message"""
        self.current_status = message
        self.status_label.setText(message)
        
        if timeout > 0:
            QTimer.singleShot(timeout, self.clear_status)
    
    def clear_status(self):
        """Clear status message"""
        self.status_label.setText("就绪")
        self.current_status = "就绪"
    
    def show_progress(self, minimum: int = 0, maximum: int = 100):
        """Show progress bar"""
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(minimum)
        self.progress_bar.setVisible(True)
        self.progress_value = minimum
        self.progress_max = maximum
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
        self.progress_value = 0
    
    def set_progress(self, value: int):
        """Set progress value"""
        self.progress_value = value
        self.progress_bar.setValue(value)
        
        # Update status if needed
        if self.progress_max > 0:
            percentage = int((value / self.progress_max) * 100)
            self.set_status(f"进度: {percentage}% ({value}/{self.progress_max})")
    
    def increment_progress(self, increment: int = 1):
        """Increment progress"""
        new_value = min(self.progress_value + increment, self.progress_max)
        self.set_progress(new_value)
    
    def set_busy(self, busy: bool, message: str = ""):
        """Set busy state"""
        self.is_busy = busy
        
        if busy:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)  # Indeterminate progress
            self.progress_bar.setVisible(True)
            if message:
                self.set_status(message)
        else:
            self.hide_progress()
            if not message:
                self.clear_status()
            else:
                self.set_status(message)
    
    def update_connection_status(self, connected: bool):
        """Update connection status"""
        if connected:
            self.connection_label.setText("🟢 已连接")
            self.connection_label.setToolTip("数据库连接正常")
        else:
            self.connection_label.setText("🔴 未连接")
            self.connection_label.setToolTip("数据库连接中断")
    
    def update_memory_usage(self, usage_mb: int):
        """Update memory usage"""
        if usage_mb < 100:
            self.memory_label.setText(f"🟢 {usage_mb}MB")
        elif usage_mb < 500:
            self.memory_label.setText(f"🟡 {usage_mb}MB")
        else:
            self.memory_label.setText(f"🔴 {usage_mb}MB")
        
        self.memory_label.setToolTip(f"内存使用量: {usage_mb}MB")
    
    def update_memory_info(self):
        """Update memory information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = int(memory_info.rss / 1024 / 1024)
            self.update_memory_usage(memory_mb)
        except ImportError:
            # psutil not available
            pass
        except Exception:
            # Other errors
            pass
    
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
    
    def show_temporary_message(self, message: str, timeout: int = 3000):
        """Show temporary message"""
        original_message = self.current_status
        self.set_status(message)
        
        def restore_message():
            self.set_status(original_message)
        
        QTimer.singleShot(timeout, restore_message)
    
    def add_permanent_widget(self, widget: QWidget):
        """Add permanent widget to status bar"""
        self.addPermanentWidget(widget)
    
    def remove_permanent_widget(self, widget: QWidget):
        """Remove permanent widget from status bar"""
        self.removeWidget(widget)
    
    def get_status(self) -> str:
        """Get current status"""
        return self.current_status
    
    def get_progress(self) -> tuple:
        """Get progress information (value, minimum, maximum)"""
        return (
            self.progress_bar.value(),
            self.progress_bar.minimum(),
            self.progress_bar.maximum()
        )
    
    def is_progress_visible(self) -> bool:
        """Check if progress bar is visible"""
        return self.progress_bar.isVisible()
    
    def set_status_color(self, color: str):
        """Set status label color"""
        self.status_label.setStyleSheet(f"color: {color};")
    
    def reset_status_color(self):
        """Reset status label color to default"""
        self.status_label.setStyleSheet("")
    
    def add_action_button(self, text: str, callback) -> QPushButton:
        """Add action button to status bar"""
        button = QPushButton(text)
        button.clicked.connect(callback)
        self.addPermanentWidget(button)
        return button
    
    def set_workflow_status(self, status: str, node_count: int = 0, 
                           connection_count: int = 0):
        """Set workflow-specific status"""
        if node_count > 0 or connection_count > 0:
            status_text = f"{status} - 节点: {node_count}, 连接: {connection_count}"
        else:
            status_text = status
        
        self.set_status(status_text)
    
    def set_execution_status(self, executing: bool, current_node: str = ""):
        """Set execution status"""
        if executing:
            if current_node:
                self.set_status(f"正在执行: {current_node}")
            else:
                self.set_status("正在执行工作流...")
            self.set_busy(True)
        else:
            self.set_busy(False)
            self.set_status("执行完成")
    
    def show_error(self, error_message: str):
        """Show error message"""
        self.set_status_color("red")
        self.set_status(f"错误: {error_message}")
        
        # Reset color after 5 seconds
        QTimer.singleShot(5000, self.reset_status_color)
    
    def show_warning(self, warning_message: str):
        """Show warning message"""
        self.set_status_color("orange")
        self.set_status(f"警告: {warning_message}")
        
        # Reset color after 3 seconds
        QTimer.singleShot(3000, self.reset_status_color)
    
    def show_success(self, success_message: str):
        """Show success message"""
        self.set_status_color("green")
        self.set_status(f"成功: {success_message}")
        
        # Reset color after 2 seconds
        QTimer.singleShot(2000, self.reset_status_color)