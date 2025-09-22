"""
数据工作流自动化项目 - UI主题系统

版本：V1.0
创建日期：2025-09-21
功能：统一的UI视觉设计系统，包含颜色主题、字体样式、组件样式等
"""

from typing import Dict, Any
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPalette

class ThemeMode(Enum):
    """主题模式枚举"""
    LIGHT = "light"
    DARK = "dark" 
    AUTO = "auto"

class UITheme:
    """主题定义类"""
    
    # 基础颜色配置
    COLORS = {
        'light': {
            'primary': '#2196F3',
            'primary_dark': '#1976D2', 
            'primary_light': '#BBDEFB',
            'secondary': '#FF9800',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'info': '#2196F3',
            'background': '#FFFFFF',
            'surface': '#F5F5F5',
            'surface_variant': '#E0E0E0',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'text_disabled': '#BDBDBD',
            'border': '#E0E0E0',
            'shadow': 'rgba(0, 0, 0, 0.1)'
        },
        'dark': {
            'primary': '#64B5F6',
            'primary_dark': '#1976D2',
            'primary_light': '#E3F2FD', 
            'secondary': '#FFB74D',
            'success': '#81C784',
            'warning': '#FFB74D',
            'error': '#E57373',
            'info': '#64B5F6',
            'background': '#121212',
            'surface': '#1E1E1E',
            'surface_variant': '#2C2C2C',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0',
            'text_disabled': '#666666',
            'border': '#333333',
            'shadow': 'rgba(0, 0, 0, 0.3)'
        }
    }
    
    # 字体配置
    FONTS = {
        'primary': 'Microsoft YaHei UI',
        'monospace': 'Consolas',
        'sizes': {
            'xs': 10,
            'sm': 11, 
            'md': 12,
            'lg': 14,
            'xl': 16,
            'xxl': 18
        }
    }
    
    # 间距配置
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48
    }
    
    # 圆角配置
    RADIUS = {
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16
    }
    
    # 阴影配置
    SHADOWS = {
        'sm': '0 1px 3px rgba(0, 0, 0, 0.12)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 25px rgba(0, 0, 0, 0.15)',
        'xl': '0 20px 40px rgba(0, 0, 0, 0.2)'
    }

class StyleSheetGenerator:
    """样式表生成器"""
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.LIGHT):
        self.theme_mode = theme_mode
        self.colors = UITheme.COLORS[theme_mode.value]
    
    def generate_main_window_style(self) -> str:
        """生成主窗口样式"""
        return f"""
        QMainWindow {{
            background-color: {self.colors['background']};
            color: {self.colors['text_primary']};
            font-family: {UITheme.FONTS['primary']};
            font-size: {UITheme.FONTS['sizes']['md']}px;
        }}
        
        QMenuBar {{
            background-color: {self.colors['surface']};
            color: {self.colors['text_primary']};
            border-bottom: 1px solid {self.colors['border']};
            padding: {UITheme.SPACING['xs']}px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: {UITheme.SPACING['sm']}px {UITheme.SPACING['md']}px;
            border-radius: {UITheme.RADIUS['sm']}px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors['primary_light']};
        }}
        
        QStatusBar {{
            background-color: {self.colors['surface']};
            color: {self.colors['text_secondary']};
            border-top: 1px solid {self.colors['border']};
        }}
        """
    
    def generate_button_style(self) -> str:
        """生成按钮样式"""
        return f"""
        QPushButton {{
            background-color: {self.colors['primary']};
            color: white;
            border: none;
            padding: {UITheme.SPACING['sm']}px {UITheme.SPACING['md']}px;
            border-radius: {UITheme.RADIUS['md']}px;
            font-weight: 500;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {self.colors['primary_dark']};
        }}
        
        QPushButton:pressed {{
            background-color: {self.colors['primary_dark']};
            transform: translateY(1px);
        }}
        
        QPushButton:disabled {{
            background-color: {self.colors['text_disabled']};
            color: {self.colors['text_secondary']};
        }}
        
        QPushButton.secondary {{
            background-color: {self.colors['surface_variant']};
            color: {self.colors['text_primary']};
            border: 1px solid {self.colors['border']};
        }}
        
        QPushButton.secondary:hover {{
            background-color: {self.colors['surface']};
        }}
        """
    
    def generate_panel_style(self) -> str:
        """生成面板样式"""
        return f"""
        QWidget.panel {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: {UITheme.RADIUS['lg']}px;
        }}
        
        QGroupBox {{
            font-weight: 600;
            color: {self.colors['text_primary']};
            border: 2px solid {self.colors['border']};
            border-radius: {UITheme.RADIUS['md']}px;
            margin: {UITheme.SPACING['md']}px 0;
            padding-top: {UITheme.SPACING['md']}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {UITheme.SPACING['md']}px;
            padding: 0 {UITheme.SPACING['sm']}px;
            background-color: {self.colors['surface']};
        }}
        """
    
    def generate_input_style(self) -> str:
        """生成输入控件样式"""
        return f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.colors['background']};
            color: {self.colors['text_primary']};
            border: 1px solid {self.colors['border']};
            border-radius: {UITheme.RADIUS['sm']}px;
            padding: {UITheme.SPACING['sm']}px;
            font-size: {UITheme.FONTS['sizes']['md']}px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {self.colors['primary']};
        }}
        
        QComboBox {{
            background-color: {self.colors['background']};
            color: {self.colors['text_primary']};
            border: 1px solid {self.colors['border']};
            border-radius: {UITheme.RADIUS['sm']}px;
            padding: {UITheme.SPACING['sm']}px;
            min-width: 100px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: url(down_arrow.png);
            width: 12px;
            height: 12px;
        }}
        """
    
    def generate_tree_style(self) -> str:
        """生成树形控件样式"""
        return f"""
        QTreeWidget, QTreeView {{
            background-color: {self.colors['background']};
            color: {self.colors['text_primary']};
            border: 1px solid {self.colors['border']};
            border-radius: {UITheme.RADIUS['md']}px;
            outline: none;
        }}
        
        QTreeWidget::item, QTreeView::item {{
            padding: {UITheme.SPACING['sm']}px;
            border-bottom: 1px solid {self.colors['surface_variant']};
        }}
        
        QTreeWidget::item:selected, QTreeView::item:selected {{
            background-color: {self.colors['primary_light']};
            color: {self.colors['text_primary']};
        }}
        
        QTreeWidget::item:hover, QTreeView::item:hover {{
            background-color: {self.colors['surface_variant']};
        }}
        
        QHeaderView::section {{
            background-color: {self.colors['surface']};
            color: {self.colors['text_primary']};
            padding: {UITheme.SPACING['sm']}px;
            border: none;
            border-bottom: 1px solid {self.colors['border']};
            font-weight: 600;
        }}
        """
    
    def generate_scroll_style(self) -> str:
        """生成滚动条样式"""
        return f"""
        QScrollBar:vertical {{
            background-color: {self.colors['surface_variant']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.colors['text_disabled']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.colors['surface_variant']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.colors['text_disabled']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.colors['text_secondary']};
        }}
        """
    
    def generate_complete_stylesheet(self) -> str:
        """生成完整样式表"""
        return f"""
        /* 数据工作流自动化项目 - 统一UI样式表 */
        
        {self.generate_main_window_style()}
        {self.generate_button_style()}
        {self.generate_panel_style()}
        {self.generate_input_style()}
        {self.generate_tree_style()}
        {self.generate_scroll_style()}
        """

class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = pyqtSignal(str)  # 主题变更信号
    
    def __init__(self):
        super().__init__()
        self._current_theme = ThemeMode.LIGHT
        self._style_generator = StyleSheetGenerator(self._current_theme)
    
    def set_theme(self, theme_mode: ThemeMode) -> None:
        """设置主题模式"""
        if self._current_theme != theme_mode:
            self._current_theme = theme_mode
            self._style_generator = StyleSheetGenerator(theme_mode)
            self.theme_changed.emit(theme_mode.value)
    
    def get_current_theme(self) -> ThemeMode:
        """获取当前主题"""
        return self._current_theme
    
    def get_stylesheet(self) -> str:
        """获取当前样式表"""
        return self._style_generator.generate_complete_stylesheet()
    
    def get_color(self, color_name: str) -> str:
        """获取主题颜色"""
        return self._style_generator.colors.get(color_name, '#000000')
    
    def get_font(self, size: str = 'md') -> QFont:
        """获取主题字体"""
        font = QFont(UITheme.FONTS['primary'])
        font.setPointSize(UITheme.FONTS['sizes'][size])
        return font

# 全局主题管理器实例
theme_manager = ThemeManager()

# 导出接口
__all__ = [
    'ThemeMode',
    'UITheme', 
    'StyleSheetGenerator',
    'ThemeManager',
    'theme_manager'
]