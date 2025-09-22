"""
数据处理自动化工作流应用 - 属性编辑面板UI组件

文档版本：V1.0
创建日期：2025-09-06
依据文档：《用户需求说明书》FR-004、《UI界面设计》第3章
适用范围：Stage 2 前端开发 - 节点属性配置编辑器

核心功能：
- 节点参数编辑
- 动态表单生成
- 参数验证
- 实时预览
- 参数表达式支持
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QComboBox, QPushButton, QFileDialog,
                             QDateEdit, QTimeEdit, QGroupBox, QScrollArea,
                             QSplitter, QTabWidget, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QFont, QPalette, QColor

from ..common.contracts import NodeInfo, ParameterInfo, ParameterType


class ParameterWidget(QObject):
    """参数编辑器基类"""
    
    value_changed = pyqtSignal(str, object)  # 参数名, 新值
    
    def __init__(self, param_info: ParameterInfo, parent=None):
        super().__init__(parent)
        self.param_info = param_info
        self.widget: Optional[QWidget] = None
    
    def get_value(self) -> Any:
        """获取当前值"""
        raise NotImplementedError
    
    def set_value(self, value: Any):
        """设置值"""
        raise NotImplementedError
    
    def validate(self) -> Tuple[bool, str]:
        """验证当前值"""
        value = self.get_value()
        
        # 必填检查
        if self.param_info.required and (value is None or value == ""):
            return False, f"参数 '{self.param_info.name}' 是必填项"
        
        # 验证规则检查
        if self.param_info.validation_rules and value is not None:
            for rule, rule_value in self.param_info.validation_rules.items():
                if rule == "min_length" and len(str(value)) < rule_value:
                    return False, f"最小长度: {rule_value}"
                elif rule == "max_length" and len(str(value)) > rule_value:
                    return False, f"最大长度: {rule_value}"
                elif rule == "min_value" and float(value) < rule_value:
                    return False, f"最小值: {rule_value}"
                elif rule == "max_value" and float(value) > rule_value:
                    return False, f"最大值: {rule_value}"
        
        return True, ""


class TextParameterWidget(ParameterWidget):
    """文本参数编辑器"""
    
    def __init__(self, param_info: ParameterInfo, multiline: bool = False, parent=None):
        super().__init__(param_info, parent)
        
        if multiline:
            self.widget = QTextEdit()
            self.widget.textChanged.connect(self._on_text_changed)
            if param_info.validation_rules and "max_length" in param_info.validation_rules:
                self.widget.setMaximumHeight(120)
        else:
            self.widget = QLineEdit()
            self.widget.textChanged.connect(self._on_text_changed)
            if param_info.validation_rules and "max_length" in param_info.validation_rules:
                self.widget.setMaxLength(param_info.validation_rules["max_length"])
        
        # 设置默认值
        if param_info.default_value:
            self.set_value(param_info.default_value)
        
        # 设置占位符
        if hasattr(self.widget, 'setPlaceholderText'):
            self.widget.setPlaceholderText(param_info.description or f"请输入{param_info.name}")
    
    def _on_text_changed(self):
        """文本变化时触发"""
        self.value_changed.emit(self.param_info.name, self.get_value())
    
    def get_value(self) -> str:
        if isinstance(self.widget, QTextEdit):
            return self.widget.toPlainText()
        else:
            return self.widget.text()
    
    def set_value(self, value: Any):
        text_value = str(value) if value is not None else ""
        if isinstance(self.widget, QTextEdit):
            self.widget.setPlainText(text_value)
        else:
            self.widget.setText(text_value)


class NumberParameterWidget(ParameterWidget):
    """数值参数编辑器"""
    
    def __init__(self, param_info: ParameterInfo, is_integer: bool = False, parent=None):
        super().__init__(param_info, parent)
        
        if is_integer:
            self.widget = QSpinBox()
            self.widget.setRange(-2147483648, 2147483647)
            self.widget.valueChanged.connect(self._on_value_changed)
        else:
            self.widget = QDoubleSpinBox()
            self.widget.setRange(-999999999.0, 999999999.0)
            self.widget.setDecimals(6)
            self.widget.valueChanged.connect(self._on_value_changed)
        
        # 设置范围
        if param_info.validation_rules:
            if "min_value" in param_info.validation_rules:
                min_val = param_info.validation_rules["min_value"]
                if is_integer:
                    self.widget.setMinimum(int(min_val))
                else:
                    self.widget.setMinimum(float(min_val))
            
            if "max_value" in param_info.validation_rules:
                max_val = param_info.validation_rules["max_value"]
                if is_integer:
                    self.widget.setMaximum(int(max_val))
                else:
                    self.widget.setMaximum(float(max_val))
        
        # 设置默认值
        if param_info.default_value is not None:
            self.set_value(param_info.default_value)
    
    def _on_value_changed(self):
        """数值变化时触发"""
        self.value_changed.emit(self.param_info.name, self.get_value())
    
    def get_value(self) -> Union[int, float]:
        return self.widget.value()
    
    def set_value(self, value: Any):
        if value is not None:
            try:
                if isinstance(self.widget, QSpinBox):
                    self.widget.setValue(int(value))
                else:
                    self.widget.setValue(float(value))
            except (ValueError, TypeError):
                pass  # 忽略无效值


class BooleanParameterWidget(ParameterWidget):
    """布尔参数编辑器"""
    
    def __init__(self, param_info: ParameterInfo, parent=None):
        super().__init__(param_info, parent)
        
        self.widget = QCheckBox(param_info.description or param_info.name)
        self.widget.stateChanged.connect(self._on_state_changed)
        
        # 设置默认值
        if param_info.default_value is not None:
            self.set_value(param_info.default_value)
    
    def _on_state_changed(self):
        """状态变化时触发"""
        self.value_changed.emit(self.param_info.name, self.get_value())
    
    def get_value(self) -> bool:
        return self.widget.isChecked()
    
    def set_value(self, value: Any):
        if isinstance(value, bool):
            self.widget.setChecked(value)
        elif isinstance(value, str):
            self.widget.setChecked(value.lower() in ['true', '1', 'yes', 'on'])


class ChoiceParameterWidget(ParameterWidget):
    """选择参数编辑器"""
    
    def __init__(self, param_info: ParameterInfo, parent=None):
        super().__init__(param_info, parent)
        
        self.widget = QComboBox()
        self.widget.currentTextChanged.connect(self._on_selection_changed)
        
        # 添加选择项
        if param_info.choices:
            self.widget.addItems(param_info.choices)
        
        # 设置默认值
        if param_info.default_value is not None:
            self.set_value(param_info.default_value)
    
    def _on_selection_changed(self):
        """选择变化时触发"""
        self.value_changed.emit(self.param_info.name, self.get_value())
    
    def get_value(self) -> str:
        return self.widget.currentText()
    
    def set_value(self, value: Any):
        if value is not None:
            text_value = str(value)
            index = self.widget.findText(text_value)
            if index >= 0:
                self.widget.setCurrentIndex(index)


class FileParameterWidget(ParameterWidget):
    """文件参数编辑器"""
    
    def __init__(self, param_info: ParameterInfo, parent=None):
        super().__init__(param_info, parent)
        
        # 创建布局
        self.widget = QWidget()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 文件路径输入框
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("请选择文件...")
        self.path_edit.textChanged.connect(self._on_path_changed)
        layout.addWidget(self.path_edit)
        
        # 浏览按钮
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self._browse_file)
        layout.addWidget(self.browse_button)
        
        # 设置默认值
        if param_info.default_value:
            self.set_value(param_info.default_value)
    
    def _on_path_changed(self):
        """路径变化时触发"""
        self.value_changed.emit(self.param_info.name, self.get_value())
    
    def _browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.widget, f"选择{self.param_info.name}", "", "所有文件 (*.*)"
        )
        if file_path:
            self.set_value(file_path)
    
    def get_value(self) -> str:
        return self.path_edit.text()
    
    def set_value(self, value: Any):
        if value is not None:
            self.path_edit.setText(str(value))


class PropertyPanel(QWidget):
    """属性编辑面板"""
    
    # 信号定义
    parameter_changed = pyqtSignal(str, str, object)  # node_id, param_name, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.current_node: Optional[Any] = None  # 当前编辑的节点
        self.parameter_widgets: Dict[str, ParameterWidget] = {}
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel("节点属性")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarNever)
        
        # 属性容器
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        self.properties_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.properties_widget)
        layout.addWidget(scroll_area)
        
        # 显示空状态
        self._show_empty_state()
    
    def _show_empty_state(self):
        """显示空状态"""
        self._clear_properties()
        
        empty_label = QLabel("请选择一个节点查看其属性")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("color: #666; font-style: italic;")
        
        self.properties_layout.addWidget(empty_label)
        self.properties_layout.addStretch()
    
    def _clear_properties(self):
        """清空属性编辑器"""
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.parameter_widgets.clear()
    
    def set_node(self, node: Any):
        """设置当前编辑的节点"""
        self.current_node = node
        self._build_property_form()
    
    def _build_property_form(self):
        """构建属性表单"""
        if not self.current_node or not hasattr(self.current_node, 'node_info'):
            self._show_empty_state()
            return
        
        self._clear_properties()
        
        node_info: NodeInfo = self.current_node.node_info
        
        # 节点信息
        info_group = QGroupBox("节点信息")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("名称:", QLabel(node_info.name))
        info_layout.addRow("类型:", QLabel(node_info.node_type.value if hasattr(node_info.node_type, 'value') else str(node_info.node_type)))
        info_layout.addRow("描述:", QLabel(node_info.description or "无描述"))
        
        self.properties_layout.addWidget(info_group)
        
        # 参数编辑
        if node_info.inputs:
            params_group = QGroupBox("参数")
            params_layout = QFormLayout(params_group)
            
            for param_info in node_info.inputs:
                widget = self._create_parameter_widget(param_info)
                if widget:
                    self.parameter_widgets[param_info.name] = widget
                    widget.value_changed.connect(self._on_parameter_changed)
                    
                    # 添加到表单
                    label = QLabel(f"{param_info.name}:")
                    if param_info.required:
                        label.setText(f"{param_info.name} *:")
                        label.setStyleSheet("color: #d32f2f;")
                    
                    params_layout.addRow(label, widget.widget)
            
            self.properties_layout.addWidget(params_group)
        
        self.properties_layout.addStretch()
    
    def _create_parameter_widget(self, param_info: ParameterInfo) -> Optional[ParameterWidget]:
        """创建参数编辑器"""
        param_type = param_info.parameter_type
        
        if param_type == ParameterType.TEXT:
            # 判断是否需要多行文本
            multiline = (param_info.validation_rules and 
                        param_info.validation_rules.get("max_length", 0) > 100)
            return TextParameterWidget(param_info, multiline)
        
        elif param_type == ParameterType.NUMBER:
            # 判断是否为整数
            is_integer = (param_info.validation_rules and 
                         param_info.validation_rules.get("integer", False))
            return NumberParameterWidget(param_info, is_integer)
        
        elif param_type == ParameterType.BOOLEAN:
            return BooleanParameterWidget(param_info)
        
        elif param_type == ParameterType.CHOICE:
            return ChoiceParameterWidget(param_info)
        
        elif param_type == ParameterType.FILE:
            return FileParameterWidget(param_info)
        
        else:
            # 默认使用文本编辑器
            return TextParameterWidget(param_info)
    
    def _on_parameter_changed(self, param_name: str, value: Any):
        """参数变化时触发"""
        if self.current_node and hasattr(self.current_node, 'node_info'):
            node_id = self.current_node.node_info.id
            self.parameter_changed.emit(node_id, param_name, value)
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取所有参数值"""
        parameters = {}
        for param_name, widget in self.parameter_widgets.items():
            parameters[param_name] = widget.get_value()
        return parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """设置参数值"""
        for param_name, value in parameters.items():
            if param_name in self.parameter_widgets:
                self.parameter_widgets[param_name].set_value(value)
    
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """验证所有参数"""
        errors = []
        
        for param_name, widget in self.parameter_widgets.items():
            is_valid, error_msg = widget.validate()
            if not is_valid:
                errors.append(f"{param_name}: {error_msg}")
        
        return len(errors) == 0, errors
