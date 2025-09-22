"""
数据处理自动化工作流应用 - 应用程序主类

文档版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》应用层、《模块化开发方案》第3章
框架：PyQt6应用程序架构

应用程序主类，负责：
1. PyQt6应用程序生命周期管理
2. 全局配置和状态管理
3. 事件总线初始化
4. 服务层初始化和依赖注入
5. 异常处理和崩溃恢复
"""

import sys
import os
import logging
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QSettings, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

from src.common.contracts import ExecutionContext, LogLevel


class ApplicationEventBus(QObject):
    """应用程序事件总线"""

    # 工作流事件
    workflow_loaded = pyqtSignal(str)  # 工作流已加载
    workflow_started = pyqtSignal(str)  # 工作流开始执行
    workflow_completed = pyqtSignal(str)  # 工作流执行完成
    workflow_failed = pyqtSignal(str, str)  # 工作流执行失败

    # 节点事件
    node_started = pyqtSignal(str, str)  # 节点开始执行
    node_completed = pyqtSignal(str, str)  # 节点执行完成
    node_failed = pyqtSignal(str, str, str)  # 节点执行失败

    # 数据事件
    data_changed = pyqtSignal(str, str)  # 数据变更
    data_cached = pyqtSignal(str)  # 数据已缓存

    # 应用事件
    config_changed = pyqtSignal(str, str)  # 配置变更
    memory_warning = pyqtSignal(float)  # 内存使用警告
    performance_warning = pyqtSignal(str)  # 性能警告


class Application(QApplication):
    """应用程序主类"""

    def __init__(self, argv: list):
        super().__init__(argv)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.event_bus = ApplicationEventBus()
        self.config: Optional[configparser.ConfigParser] = None
        self.settings: Optional[QSettings] = None

        # 应用程序状态
        self.is_configured = False
        self.debug_mode = False
        self.max_memory_mb = 2048
        self.config_path = ""

        # 性能监控定时器
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._check_performance)

        # 设置应用程序基本信息
        self.setApplicationName("数据工作流自动化平台")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("DWA Development Team")
        self.setOrganizationDomain("github.com/dwa-team")

        # 设置图标
        self._setup_application_icon()

        # 设置异常处理
        sys.excepthook = self._handle_exception

        self.logger.info("应用程序初始化完成")

    def configure(
        self, config_path: str, debug_mode: bool = False, max_memory_mb: int = 2048
    ) -> bool:
        """配置应用程序"""
        try:
            self.config_path = config_path
            self.debug_mode = debug_mode
            self.max_memory_mb = max_memory_mb

            # 加载配置文件
            if not self._load_config():
                return False

            # 初始化设置
            self._init_settings()

            # 启动性能监控
            if self.debug_mode:
                self.performance_timer.start(5000)  # 5秒间隔
            else:
                self.performance_timer.start(30000)  # 30秒间隔

            self.is_configured = True
            self.logger.info("应用程序配置完成")
            return True

        except Exception as e:
            self.logger.error(f"应用程序配置失败: {e}")
            return False

    def _load_config(self) -> bool:
        """加载配置文件"""
        config_path = Path(self.config_path)

        if not config_path.exists():
            self.logger.warning(f"配置文件不存在: {config_path}")
            # 创建默认配置
            from common.environment import create_default_config

            create_default_config(config_path)
            self.logger.info(f"已创建默认配置文件: {config_path}")

        try:
            self.config = configparser.ConfigParser()
            self.config.read(config_path, encoding="utf-8")

            # 验证配置文件
            required_sections = ["application", "performance", "ui", "data"]
            for section in required_sections:
                if not self.config.has_section(section):
                    self.logger.warning(f"配置文件缺少节: {section}")

            self.logger.info(f"配置文件加载成功: {config_path}")
            return True

        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            return False

    def _init_settings(self) -> None:
        """初始化应用程序设置"""
        self.settings = QSettings()

        # 设置默认值
        defaults = {
            "ui/theme": self.get_config_value("ui", "theme", "auto"),
            "ui/language": self.get_config_value("ui", "language", "zh_CN"),
            "ui/auto_save_interval": self.get_config_value(
                "ui", "auto_save_interval", 300
            ),
            "performance/max_memory_mb": self.max_memory_mb,
            "data/default_encoding": self.get_config_value(
                "data", "default_encoding", "utf-8"
            ),
        }

        for key, value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)

        self.logger.debug("应用程序设置初始化完成")

    def _setup_application_icon(self) -> None:
        """设置应用程序图标"""
        try:
            icon_path = Path("resources/icons/app.ico")
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            self.logger.debug(f"设置应用程序图标失败: {e}")

    def _check_performance(self) -> None:
        """检查性能指标"""
        try:
            import psutil

            process = psutil.Process()

            # 检查内存使用
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)

            if memory_mb > self.max_memory_mb * 0.8:  # 80%警告阈值
                self.event_bus.memory_warning.emit(memory_mb)
                self.logger.warning(
                    f"内存使用率过高: {memory_mb:.1f}MB / {self.max_memory_mb}MB"
                )

            # 检查CPU使用率
            cpu_percent = process.cpu_percent()
            if cpu_percent > 80:  # 80%警告阈值
                self.event_bus.performance_warning.emit(
                    f"CPU使用率过高: {cpu_percent:.1f}%"
                )
                self.logger.warning(f"CPU使用率过高: {cpu_percent:.1f}%")

        except ImportError:
            # psutil未安装，停止性能监控
            self.performance_timer.stop()
            self.logger.debug("psutil未安装，性能监控已停止")
        except Exception as e:
            self.logger.debug(f"性能检查失败: {e}")

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 用户中断，正常处理
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 记录异常
        error_msg = f"未捕获的异常: {exc_type.__name__}: {exc_value}"
        self.logger.critical(error_msg, exc_info=(exc_type, exc_value, exc_traceback))

        # 在调试模式下显示详细错误
        if self.debug_mode:
            import traceback

            detailed_error = "\n".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )
            QMessageBox.critical(
                None,
                "程序错误",
                f"程序遇到未处理的错误：\n\n{error_msg}\n\n详细信息：\n{detailed_error}",
            )
        else:
            QMessageBox.critical(
                None,
                "程序错误",
                f"程序遇到未处理的错误：\n{error_msg}\n\n请检查日志文件获取详细信息。",
            )

    def get_config_value(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if not self.config:
            return default

        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set_config_value(self, section: str, key: str, value: Any) -> None:
        """设置配置值"""
        if not self.config:
            return

        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, str(value))
        self.event_bus.config_changed.emit(section, key)

    def save_config(self) -> bool:
        """保存配置文件"""
        if not self.config or not self.config_path:
            return False

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                self.config.write(f)
            self.logger.info("配置文件已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取应用程序设置"""
        if not self.settings:
            return default
        return self.settings.value(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """设置应用程序设置"""
        if self.settings:
            self.settings.setValue(key, value)

    def create_execution_context(self, workflow_id: str = None) -> ExecutionContext:
        """创建执行上下文"""
        from common.contracts import create_execution_context

        context = create_execution_context(workflow_id or "unknown")
        context.max_memory_mb = self.max_memory_mb
        context.log_level = LogLevel.DEBUG if self.debug_mode else LogLevel.INFO

        # 添加应用程序配置到上下文
        if self.config:
            context.global_parameters.update(
                {
                    "app.data_dir": self.get_config_value("data", "temp_dir", "data"),
                    "app.temp_dir": self.get_config_value("data", "temp_dir", "temp"),
                    "app.encoding": self.get_config_value(
                        "data", "default_encoding", "utf-8"
                    ),
                    "app.max_memory_mb": self.max_memory_mb,
                    "app.debug": self.debug_mode,
                }
            )

        return context

    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """显示消息对话框"""
        if msg_type == "error":
            QMessageBox.critical(None, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(None, title, message)
        else:
            QMessageBox.information(None, title, message)

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            if self.performance_timer.isActive():
                self.performance_timer.stop()

            # 保存配置
            self.save_config()

            # 清理临时文件
            temp_dir = Path(self.get_config_value("data", "temp_dir", "temp"))
            if temp_dir.exists():
                import shutil

                try:
                    shutil.rmtree(temp_dir)
                    self.logger.info("临时文件清理完成")
                except Exception as e:
                    self.logger.warning(f"临时文件清理失败: {e}")

            self.logger.info("应用程序清理完成")

        except Exception as e:
            self.logger.error(f"应用程序清理失败: {e}")

    def quit(self) -> None:
        """退出应用程序"""
        self.cleanup()
        super().quit()


# 全局应用程序实例访问
_app_instance: Optional[Application] = None


def get_application() -> Optional[Application]:
    """获取应用程序实例"""
    return _app_instance


def set_application(app: Application) -> None:
    """设置应用程序实例"""
    global _app_instance
    _app_instance = app
