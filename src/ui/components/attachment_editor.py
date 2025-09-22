"""
附件编辑器

用于编辑和管理文件附件
"""

from typing import List, Optional, Dict, Any
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QLabel, QMenu, QAction,
    QDialog, QLineEdit, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap


class AttachmentItem:
    """附件项"""
    
    def __init__(self, file_path: str, name: str = None, description: str = ""):
        self.file_path = file_path
        self.name = name or os.path.basename(file_path)
        self.description = description
        self.size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_path': self.file_path,
            'name': self.name,
            'description': self.description,
            'size': self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttachmentItem':
        return cls(
            file_path=data['file_path'],
            name=data['name'],
            description=data.get('description', '')
        )


class AttachmentEditDialog(QDialog):
    """附件编辑对话框"""
    
    def __init__(self, item: AttachmentItem = None, parent=None):
        super().__init__(parent)
        self.item = item
        self.setup_ui()
        
        if item:
            self.load_item(item)
    
    def setup_ui(self):
        self.setWindowTitle("编辑附件")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 文件路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("文件路径:"))
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        # 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 描述
        layout.addWidget(QLabel("描述:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*)"
        )
        if file_path:
            self.path_edit.setText(file_path)
            if not self.name_edit.text():
                self.name_edit.setText(os.path.basename(file_path))
    
    def load_item(self, item: AttachmentItem):
        self.path_edit.setText(item.file_path)
        self.name_edit.setText(item.name)
        self.description_edit.setText(item.description)
    
    def get_item(self) -> Optional[AttachmentItem]:
        file_path = self.path_edit.text().strip()
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not file_path:
            QMessageBox.warning(self, "警告", "请选择文件")
            return None
        
        if not name:
            name = os.path.basename(file_path)
        
        return AttachmentItem(file_path, name, description)


class AttachmentEditor(QWidget):
    """附件编辑器"""
    
    attachments_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attachments: List[AttachmentItem] = []
        self.setup_ui()
        self.setup_drag_drop()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.add_attachment)
        toolbar_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.edit_attachment)
        self.edit_btn.setEnabled(False)
        toolbar_layout.addWidget(self.edit_btn)
        
        self.remove_btn = QPushButton("删除")
        self.remove_btn.clicked.connect(self.remove_attachment)
        self.remove_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remove_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 附件列表
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.edit_attachment)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)
    
    def setup_drag_drop(self):
        """Setup drag and drop"""
        self.setAcceptDrops(True)
        self.list_widget.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.add_attachment_from_path(file_path)
    
    def add_attachment_from_path(self, file_path: str):
        """Add attachment from file path"""
        # Check if already exists
        for item in self.attachments:
            if item.file_path == file_path:
                QMessageBox.information(self, "提示", "该文件已存在")
                return
        
        attachment = AttachmentItem(file_path)
        self.attachments.append(attachment)
        self.refresh_list()
        self.attachments_changed.emit()
    
    def add_attachment(self):
        """Add new attachment"""
        dialog = AttachmentEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            item = dialog.get_item()
            if item:
                # Check if already exists
                for existing in self.attachments:
                    if existing.file_path == item.file_path:
                        QMessageBox.information(self, "提示", "该文件已存在")
                        return
                
                self.attachments.append(item)
                self.refresh_list()
                self.attachments_changed.emit()
    
    def edit_attachment(self):
        """Edit selected attachment"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.attachments):
            item = self.attachments[current_row]
            dialog = AttachmentEditDialog(item, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                updated_item = dialog.get_item()
                if updated_item:
                    self.attachments[current_row] = updated_item
                    self.refresh_list()
                    self.attachments_changed.emit()
    
    def remove_attachment(self):
        """Remove selected attachment"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.attachments):
            item = self.attachments[current_row]
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除附件 '{item.name}' 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.attachments[current_row]
                self.refresh_list()
                self.attachments_changed.emit()
    
    def refresh_list(self):
        """Refresh attachment list"""
        self.list_widget.clear()
        
        for item in self.attachments:
            list_item = QListWidgetItem()
            
            # Format display text
            size_str = self.format_file_size(item.size)
            text = f"{item.name}"
            if item.description:
                text += f" - {item.description}"
            text += f" ({size_str})"
            
            list_item.setText(text)
            list_item.setToolTip(
                f"名称: {item.name}\n"
                f"路径: {item.file_path}\n"
                f"大小: {size_str}\n"
                f"描述: {item.description or '无'}"
            )
            
            # Set icon based on file extension
            icon = self.get_file_icon(item.file_path)
            if icon:
                list_item.setIcon(icon)
            
            self.list_widget.addItem(list_item)
    
    def format_file_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_file_icon(self, file_path: str) -> Optional[QIcon]:
        """Get file icon based on extension"""
        # This is a simple implementation
        # In a real application, you might use system icons
        ext = os.path.splitext(file_path)[1].lower()
        
        # You can add more file type icons here
        icon_map = {
            '.txt': '📄',
            '.pdf': '📋',
            '.doc': '📝',
            '.docx': '📝',
            '.xls': '📊',
            '.xlsx': '📊',
            '.csv': '📈',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.py': '🐍',
            '.json': '📋',
            '.xml': '📋',
            '.zip': '📦',
            '.rar': '📦'
        }
        
        if ext in icon_map:
            # Create a simple text icon
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.transparent)
            return QIcon(pixmap)
        
        return None
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = self.list_widget.currentRow() >= 0
        self.edit_btn.setEnabled(has_selection)
        self.remove_btn.setEnabled(has_selection)
    
    def show_context_menu(self, position):
        """Show context menu"""
        item = self.list_widget.itemAt(position)
        if item is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self.edit_attachment)
        menu.addAction(edit_action)
        
        remove_action = QAction("删除", self)
        remove_action.triggered.connect(self.remove_attachment)
        menu.addAction(remove_action)
        
        menu.addSeparator()
        
        open_action = QAction("打开文件", self)
        open_action.triggered.connect(self.open_file)
        menu.addAction(open_action)
        
        show_in_folder_action = QAction("在文件夹中显示", self)
        show_in_folder_action.triggered.connect(self.show_in_folder)
        menu.addAction(show_in_folder_action)
        
        menu.exec_(self.list_widget.mapToGlobal(position))
    
    def open_file(self):
        """Open selected file"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.attachments):
            item = self.attachments[current_row]
            if os.path.exists(item.file_path):
                os.startfile(item.file_path)  # Windows
            else:
                QMessageBox.warning(self, "警告", "文件不存在")
    
    def show_in_folder(self):
        """Show file in folder"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.attachments):
            item = self.attachments[current_row]
            if os.path.exists(item.file_path):
                os.system(f'explorer /select,"{item.file_path}"')  # Windows
            else:
                QMessageBox.warning(self, "警告", "文件不存在")
    
    def get_attachments(self) -> List[AttachmentItem]:
        """Get all attachments"""
        return self.attachments.copy()
    
    def set_attachments(self, attachments: List[AttachmentItem]):
        """Set attachments"""
        self.attachments = attachments.copy()
        self.refresh_list()
    
    def clear_attachments(self):
        """Clear all attachments"""
        self.attachments.clear()
        self.refresh_list()
        self.attachments_changed.emit()
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert to dictionary"""
        return [item.to_dict() for item in self.attachments]
    
    def from_dict(self, data: List[Dict[str, Any]]):
        """Load from dictionary"""
        self.attachments = [AttachmentItem.from_dict(item_data) for item_data in data]
        self.refresh_list()