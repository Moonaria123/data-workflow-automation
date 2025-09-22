"""
数据处理自动化工作流应用 - 环境检查与初始化

文档版本：V1.0
创建日期：2025-09-06
依据文档：《AI开发代理注意事项》性能需求、《技术架构设计》
用途：运行环境验证、依赖检查、日志系统初始化

环境检查清单：
- Python版本 ≥ 3.9
- 关键依赖库版本验证
- 系统资源检查（内存≥4GB，磁盘≥2GB）
- 权限验证
- 配置文件验证
"""

import sys
import os
import platform
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Tuple
import importlib.util
from packaging import version


class EnvironmentChecker:
    """环境检查器"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_python_version(self, min_version: str = "3.9.0") -> bool:
        """检查Python版本"""
        current_version = platform.python_version()
        try:
            return version.parse(current_version) >= version.parse(min_version)
        except Exception:
            return False

    def check_package_version(self, package_name: str, min_version: str) -> bool:
        """检查包版本"""
        try:
            module = importlib.import_module(package_name)
            if hasattr(module, "__version__"):
                current_version = module.__version__
                return version.parse(current_version) >= version.parse(min_version)
            else:
                # 如果没有版本信息，假设已安装
                return True
        except ImportError:
            return False
        except Exception:
            return False

    def check_system_resources(
        self, min_memory_gb: float = 4.0, min_disk_gb: float = 2.0
    ) -> bool:
        """检查系统资源"""
        try:
            import psutil

            # 检查内存
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)

            # 检查磁盘空间
            disk = psutil.disk_usage("/")
            disk_gb = disk.free / (1024**3)

            memory_ok = memory_gb >= min_memory_gb
            disk_ok = disk_gb >= min_disk_gb

            if not memory_ok:
                self.warnings.append(f"内存不足: {memory_gb:.1f}GB < {min_memory_gb}GB")

            if not disk_ok:
                self.warnings.append(f"磁盘空间不足: {disk_gb:.1f}GB < {min_disk_gb}GB")

            return memory_ok and disk_ok

        except ImportError:
            self.warnings.append("psutil未安装，无法检查系统资源")
            return True
        except Exception as e:
            self.warnings.append(f"资源检查失败: {e}")
            return True

    def check_permissions(self, project_root: Path) -> bool:
        """检查文件权限"""
        try:
            # 检查项目目录写权限
            test_file = project_root / "temp" / "permission_test.tmp"
            test_file.parent.mkdir(exist_ok=True)

            test_file.write_text("test")
            test_file.unlink()

            return True

        except Exception as e:
            self.errors.append(f"权限检查失败: {e}")
            return False

    def get_system_info(self) -> dict:
        """获取系统信息"""
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
        }

        try:
            import psutil

            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            info.update(
                {
                    "memory_total_gb": round(memory.total / (1024**3), 1),
                    "memory_available_gb": round(memory.available / (1024**3), 1),
                    "disk_free_gb": round(disk.free / (1024**3), 1),
                    "cpu_count": psutil.cpu_count(),
                }
            )
        except ImportError:
            pass

        return info


def setup_logging(
    level: int = logging.INFO, debug_mode: bool = False, log_dir: Optional[Path] = None
) -> None:
    """设置日志系统"""

    if log_dir is None:
        log_dir = Path("logs")

    log_dir.mkdir(exist_ok=True)

    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 创建格式器
    if debug_mode:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 错误文件处理器
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # 设置第三方库日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # 记录初始化信息
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成")
    logger.debug(f"日志目录: {log_dir}")
    logger.debug(f"日志级别: {logging.getLevelName(level)}")


def create_default_config(config_path: Path) -> None:
    """创建默认配置文件"""
    config_content = """
# 数据处理自动化工作流应用 - 配置文件
# 文档版本：V1.0
# 创建日期：2025-09-06

[application]
name = 数据工作流自动化平台
version = 1.0.0
debug = false

[performance]
max_memory_mb = 2048
max_cpu_percent = 80
max_file_size_mb = 1024
timeout_seconds = 3600

[ui]
theme = auto
language = zh_CN
auto_save_interval = 300

[data]
default_encoding = utf-8
temp_dir = temp
cache_size_mb = 512
backup_enabled = true

[security]
enable_file_validation = true
allowed_extensions = .csv,.xlsx,.xls,.json,.xml,.txt
max_upload_size_mb = 100

[logging]
level = INFO
max_file_size_mb = 10
backup_count = 5
console_output = true

[database]
type = sqlite
path = data/app.db
connection_pool_size = 5
query_timeout = 30

[plugins]
enabled = true
auto_load = true
plugin_dir = plugins
"""

    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text(config_content.strip(), encoding="utf-8")


def validate_installation() -> Tuple[bool, list, list]:
    """验证完整安装"""
    checker = EnvironmentChecker()
    errors = []
    warnings = []

    # Python版本检查
    if not checker.check_python_version("3.9.0"):
        errors.append("Python版本过低，需要3.9+")

    # 核心依赖检查
    required_packages = [
        ("PyQt6", "6.6.0"),
        ("polars", "0.19.0"),
        ("numpy", "1.24.0"),
        ("openpyxl", "3.1.0"),
    ]

    for package, min_ver in required_packages:
        if not checker.check_package_version(package, min_ver):
            errors.append(f"缺少或版本过低: {package} >= {min_ver}")

    # 可选依赖检查
    optional_packages = [
        ("pandas", "2.0.0"),
        ("duckdb", "0.9.0"),
        ("plotly", "5.15.0"),
        ("requests", "2.31.0"),
    ]

    for package, min_ver in optional_packages:
        if not checker.check_package_version(package, min_ver):
            warnings.append(f"建议安装或升级: {package} >= {min_ver}")

    # 系统资源检查
    if not checker.check_system_resources(4.0, 2.0):
        warnings.extend(checker.warnings)

    errors.extend(checker.errors)
    warnings.extend(checker.warnings)

    return len(errors) == 0, errors, warnings


if __name__ == "__main__":
    """环境检查工具 - 可独立运行"""

    print("🔍 数据工作流自动化平台 - 环境检查工具")
    print("=" * 50)

    success, errors, warnings = validate_installation()

    # 显示系统信息
    checker = EnvironmentChecker()
    sys_info = checker.get_system_info()
    print(f"🖥️  系统平台: {sys_info['platform']}")
    print(f"🐍 Python版本: {sys_info['python_version']}")
    print(f"🏗️  架构: {sys_info['architecture']}")

    if "memory_total_gb" in sys_info:
        print(
            f"💾 内存: {sys_info['memory_available_gb']}/{sys_info['memory_total_gb']} GB 可用"
        )
        print(f"💿 磁盘: {sys_info['disk_free_gb']} GB 可用")
        print(f"⚡ CPU核心: {sys_info['cpu_count']}")

    print()

    # 显示错误
    if errors:
        print("❌ 发现错误:")
        for error in errors:
            print(f"   • {error}")
        print()

    # 显示警告
    if warnings:
        print("⚠️  警告:")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    # 结果
    if success:
        print("✅ 环境检查通过，可以运行应用程序")
    else:
        print("❌ 环境检查失败，请解决上述问题后重试")
        print("💡 提示: pip install -r requirements.txt")

    print("=" * 50)
