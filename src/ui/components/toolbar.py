"""
工具栏组件

用于显示常用操作按钮
"""

from typing import Dict, List, Optional, Callable
from PyQt5.QtWidgets import (
    QToolBar, QAction, QActionGroup, QToolButton, QMenu, QSeparator,
    QWidget, QHBoxLayout, QLabel, QComboBox, QSpinBox, QSlider,
    QCheckBox, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QPainter, QColor


class CustomToolBar(QToolBar):
    """自定义工具栏"""
    
    # 信号
    action_triggered = pyqtSignal(str)  # action_name
    zoom_changed = pyqtSignal(int)  # zoom_level
    view_mode_changed = pyqtSignal(str)  # view_mode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions_dict: Dict[str, QAction] = {}
        self.widgets_dict: Dict[str, QWidget] = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.setMovable(True)
        self.setFloatable(True)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    
    def add_action_with_icon(self, name: str, text: str, icon_path: str = None,
                           shortcut: str = None, tooltip: str = None,
                           callback: Callable = None, checkable: bool = False) -> QAction:
        """Add action with icon"""
        action = QAction(text, self)
        
        # Set icon
        if icon_path:
            action.setIcon(QIcon(icon_path))
        else:
            # Create simple text icon
            action.setIcon(self.create_text_icon(text[0]))
        
        # Set shortcut
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        # Set tooltip
        if tooltip:
            action.setToolTip(tooltip)
        else:
            tooltip_text = text
            if shortcut:
                tooltip_text += f" ({shortcut})"
            action.setToolTip(tooltip_text)
        
        # Set checkable
        if checkable:
            action.setCheckable(True)
        
        # Connect callback
        if callback:
            action.triggered.connect(callback)
        else:
            action.triggered.connect(lambda: self.action_triggered.emit(name))
        
        # Add to toolbar and dictionary
        self.addAction(action)
        self.actions_dict[name] = action
        
        return action
    
    def add_separator_with_label(self, label: str = None):
        """Add separator with optional label"""
        self.addSeparator()
        if label:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
            self.addWidget(label_widget)
    
    def add_combo_box(self, name: str, label: str, items: List[str],
                     callback: Callable = None) -> QComboBox:
        """Add combo box"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        if label:
            label_widget = QLabel(label + ":")
            layout.addWidget(label_widget)
        
        combo_box = QComboBox()
        combo_box.addItems(items)
        if callback:
            combo_box.currentTextChanged.connect(callback)
        layout.addWidget(combo_box)
        
        self.addWidget(widget)
        self.widgets_dict[name] = combo_box
        
        return combo_box
    
    def add_spin_box(self, name: str, label: str, min_val: int, max_val: int,
                    default_val: int, callback: Callable = None) -> QSpinBox:
        """Add spin box"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        if label:
            label_widget = QLabel(label + ":")
            layout.addWidget(label_widget)
        
        spin_box = QSpinBox()
        spin_box.setMinimum(min_val)
        spin_box.setMaximum(max_val)
        spin_box.setValue(default_val)
        if callback:
            spin_box.valueChanged.connect(callback)
        layout.addWidget(spin_box)
        
        self.addWidget(widget)
        self.widgets_dict[name] = spin_box
        
        return spin_box
    
    def add_slider(self, name: str, label: str, min_val: int, max_val: int,
                  default_val: int, callback: Callable = None) -> QSlider:
        """Add slider"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        if label:
            label_widget = QLabel(label + ":")
            layout.addWidget(label_widget)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setMaximumWidth(100)
        if callback:
            slider.valueChanged.connect(callback)
        layout.addWidget(slider)
        
        # Add value label
        value_label = QLabel(str(default_val))
        value_label.setMinimumWidth(30)
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        layout.addWidget(value_label)
        
        self.addWidget(widget)
        self.widgets_dict[name] = slider
        
        return slider
    
    def add_checkbox(self, name: str, label: str, checked: bool = False,
                    callback: Callable = None) -> QCheckBox:
        """Add checkbox"""
        checkbox = QCheckBox(label)
        checkbox.setChecked(checked)
        if callback:
            checkbox.toggled.connect(callback)
        
        self.addWidget(checkbox)
        self.widgets_dict[name] = checkbox
        
        return checkbox
    
    def add_line_edit(self, name: str, label: str, placeholder: str = "",
                     callback: Callable = None) -> QLineEdit:
        """Add line edit"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        if label:
            label_widget = QLabel(label + ":")
            layout.addWidget(label_widget)
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setMaximumWidth(150)
        if callback:
            line_edit.textChanged.connect(callback)
        layout.addWidget(line_edit)
        
        self.addWidget(widget)
        self.widgets_dict[name] = line_edit
        
        return line_edit
    
    def add_button(self, name: str, text: str, callback: Callable = None) -> QPushButton:
        """Add button"""
        button = QPushButton(text)
        button.setMaximumWidth(80)
        if callback:
            button.clicked.connect(callback)
        else:
            button.clicked.connect(lambda: self.action_triggered.emit(name))
        
        self.addWidget(button)
        self.widgets_dict[name] = button
        
        return button
    
    def create_text_icon(self, text: str, size: QSize = QSize(24, 24)) -> QIcon:
        """Create simple text icon"""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background circle
        painter.setBrush(QColor(100, 150, 200))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size.width(), size.height())
        
        # Draw text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def get_action(self, name: str) -> Optional[QAction]:
        """Get action by name"""
        return self.actions_dict.get(name)
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """Get widget by name"""
        return self.widgets_dict.get(name)
    
    def set_action_enabled(self, name: str, enabled: bool):
        """Set action enabled state"""
        action = self.get_action(name)
        if action:
            action.setEnabled(enabled)
    
    def set_action_checked(self, name: str, checked: bool):
        """Set action checked state"""
        action = self.get_action(name)
        if action and action.isCheckable():
            action.setChecked(checked)
    
    def set_widget_enabled(self, name: str, enabled: bool):
        """Set widget enabled state"""
        widget = self.get_widget(name)
        if widget:
            widget.setEnabled(enabled)
    
    def set_combo_box_items(self, name: str, items: List[str]):
        """Set combo box items"""
        combo_box = self.get_widget(name)
        if isinstance(combo_box, QComboBox):
            combo_box.clear()
            combo_box.addItems(items)
    
    def get_combo_box_value(self, name: str) -> str:
        """Get combo box current value"""
        combo_box = self.get_widget(name)
        if isinstance(combo_box, QComboBox):
            return combo_box.currentText()
        return ""
    
    def set_combo_box_value(self, name: str, value: str):
        """Set combo box current value"""
        combo_box = self.get_widget(name)
        if isinstance(combo_box, QComboBox):
            index = combo_box.findText(value)
            if index >= 0:
                combo_box.setCurrentIndex(index)
    
    def get_spin_box_value(self, name: str) -> int:
        """Get spin box value"""
        spin_box = self.get_widget(name)
        if isinstance(spin_box, QSpinBox):
            return spin_box.value()
        return 0
    
    def set_spin_box_value(self, name: str, value: int):
        """Set spin box value"""
        spin_box = self.get_widget(name)
        if isinstance(spin_box, QSpinBox):
            spin_box.setValue(value)
    
    def get_slider_value(self, name: str) -> int:
        """Get slider value"""
        slider = self.get_widget(name)
        if isinstance(slider, QSlider):
            return slider.value()
        return 0
    
    def set_slider_value(self, name: str, value: int):
        """Set slider value"""
        slider = self.get_widget(name)
        if isinstance(slider, QSlider):
            slider.setValue(value)
    
    def get_checkbox_value(self, name: str) -> bool:
        """Get checkbox value"""
        checkbox = self.get_widget(name)
        if isinstance(checkbox, QCheckBox):
            return checkbox.isChecked()
        return False
    
    def set_checkbox_value(self, name: str, checked: bool):
        """Set checkbox value"""
        checkbox = self.get_widget(name)
        if isinstance(checkbox, QCheckBox):
            checkbox.setChecked(checked)
    
    def get_line_edit_value(self, name: str) -> str:
        """Get line edit value"""
        line_edit = self.get_widget(name)
        if isinstance(line_edit, QLineEdit):
            return line_edit.text()
        return ""
    
    def set_line_edit_value(self, name: str, text: str):
        """Set line edit value"""
        line_edit = self.get_widget(name)
        if isinstance(line_edit, QLineEdit):
            line_edit.setText(text)
    
    def clear_all_widgets(self):
        """Clear all widget values"""
        for name, widget in self.widgets_dict.items():
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QSpinBox):
                widget.setValue(widget.minimum())
            elif isinstance(widget, QSlider):
                widget.setValue(widget.minimum())
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QLineEdit):
                widget.clear()
    
    def save_state(self) -> Dict:
        """Save toolbar state"""
        state = {}
        
        # Save action states
        for name, action in self.actions_dict.items():
            if action.isCheckable():
                state[f"action_{name}"] = action.isChecked()
        
        # Save widget states
        for name, widget in self.widgets_dict.items():
            if isinstance(widget, QComboBox):
                state[f"combo_{name}"] = widget.currentText()
            elif isinstance(widget, QSpinBox):
                state[f"spin_{name}"] = widget.value()
            elif isinstance(widget, QSlider):
                state[f"slider_{name}"] = widget.value()
            elif isinstance(widget, QCheckBox):
                state[f"check_{name}"] = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                state[f"edit_{name}"] = widget.text()
        
        return state
    
    def restore_state(self, state: Dict):
        """Restore toolbar state"""
        # Restore action states
        for key, value in state.items():
            if key.startswith("action_"):
                name = key[7:]  # Remove "action_" prefix
                action = self.get_action(name)
                if action and action.isCheckable():
                    action.setChecked(value)
            elif key.startswith("combo_"):
                name = key[6:]  # Remove "combo_" prefix
                self.set_combo_box_value(name, value)
            elif key.startswith("spin_"):
                name = key[5:]  # Remove "spin_" prefix
                self.set_spin_box_value(name, value)
            elif key.startswith("slider_"):
                name = key[7:]  # Remove "slider_" prefix
                self.set_slider_value(name, value)
            elif key.startswith("check_"):
                name = key[6:]  # Remove "check_" prefix
                self.set_checkbox_value(name, value)
            elif key.startswith("edit_"):
                name = key[5:]  # Remove "edit_" prefix
                self.set_line_edit_value(name, value)