#!/usr/bin/env python3
"""
数据处理自动化工作流应用 - 主程序入口

文档版本：V1.0
创建日期：2025-09-06
依据文档：《用户需求说明书》、《技术架构设计》、《PROJECT_SETUP.md》
技术栈：Python 3.9+ + PyQt6 + Polars

应用程序主入口，负责：
1. 环境检查和初始化
2. 依赖库加载和版本验证
3. 主窗口启动和异常处理
4. 命令行参数解析
5. 日志系统初始化
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

# 添加src目录到Python路径
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 导入版本检查和环境验证
try:
    from common.environment import EnvironmentChecker, setup_logging
    from ui.main_window import MainWindow
    from app.application import Application
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog="数据工作流自动化平台",
        description="可视化数据处理工作流设计和执行平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 正常启动
  python main.py --debug            # 调试模式启动
  python main.py --log-level DEBUG  # 设置日志级别
  python main.py --config custom.ini # 使用自定义配置文件
        """,
    )

    parser.add_argument(
        "--debug", action="store_true", help="启用调试模式（详细日志、错误堆栈跟踪）"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="设置日志级别 (default: INFO)",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/app.ini",
        help="配置文件路径 (default: config/app.ini)",
    )

    parser.add_argument("--data-dir", type=str, help="数据目录路径 (覆盖配置文件设置)")

    parser.add_argument(
        "--max-memory", type=int, default=2048, help="最大内存使用量 (MB, default: 2048)"
    )

    parser.add_argument(
        "--version", action="version", version="数据工作流自动化平台 v1.0.0"
    )

    return parser.parse_args()


def validate_environment(args: argparse.Namespace) -> bool:
    """验证运行环境"""
    checker = EnvironmentChecker()

    print("🔍 检查运行环境...")

    # 检查Python版本
    if not checker.check_python_version():
        print("❌ Python版本不符合要求 (需要3.9+)")
        return False

    # 检查关键依赖
    required_packages = [
        ("PyQt6", "6.6.0"),
        ("polars", "0.19.0"),
        ("numpy", "1.24.0"),
        ("openpyxl", "3.1.0"),
    ]

    for package, min_version in required_packages:
        if not checker.check_package_version(package, min_version):
            print(f"❌ {package} 版本不符合要求 (需要>={min_version})")
            return False

    # 检查系统资源
    if not checker.check_system_resources(min_memory_gb=2, min_disk_gb=1):
        print("⚠️  系统资源可能不足，但可以尝试运行")

    # 检查配置文件
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"⚠️  配置文件不存在: {config_path}，将使用默认配置")

    print("✅ 环境检查完成")
    return True


def setup_application_environment(args: argparse.Namespace) -> None:
    """设置应用程序环境"""

    # 设置日志系统
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(level=log_level, debug_mode=args.debug, log_dir=PROJECT_ROOT / "logs")

    # 创建必要的目录
    directories = [
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "temp",
        PROJECT_ROOT / "config",
        PROJECT_ROOT / "data",
    ]

    for directory in directories:
        directory.mkdir(exist_ok=True)

    # 设置环境变量
    os.environ["DWA_PROJECT_ROOT"] = str(PROJECT_ROOT)
    os.environ["DWA_DATA_DIR"] = args.data_dir or str(PROJECT_ROOT / "data")
    os.environ["DWA_MAX_MEMORY_MB"] = str(args.max_memory)

    if args.debug:
        os.environ["DWA_DEBUG"] = "1"
        os.environ["PYTHONPATH"] = str(SRC_DIR)


def main() -> int:
    """主函数"""

    # 解析命令行参数
    args = parse_arguments()

    try:
        # 环境验证
        if not validate_environment(args):
            return 1

        # 设置应用环境
        setup_application_environment(args)

        # 获取logger
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("🚀 启动数据工作流自动化平台")
        logger.info("=" * 60)
        logger.info(f"📂 项目根目录: {PROJECT_ROOT}")
        logger.info(f"🔧 配置文件: {args.config}")
        logger.info(f"📊 最大内存: {args.max_memory}MB")
        logger.info(f"🐞 调试模式: {'开启' if args.debug else '关闭'}")

        # 创建并启动应用程序
        logger.info("🎨 初始化用户界面...")

        app = Application(sys.argv)
        app.setApplicationName("数据工作流自动化平台")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("DWA Development Team")

        # 设置应用程序配置
        app.configure(
            config_path=args.config,
            debug_mode=args.debug,
            max_memory_mb=args.max_memory,
        )

        # 创建并显示主窗口
        logger.info("🖥️  创建主窗口...")
        main_window = MainWindow()
        main_window.show()

        logger.info("✅ 应用程序启动成功")

        # 运行事件循环
        return app.exec()

    except KeyboardInterrupt:
        print("\n⚠️  用户中断，正在退出...")
        return 0

    except Exception as e:
        error_msg = f"❌ 应用程序启动失败: {e}"
        print(error_msg)

        if args.debug:
            import traceback

            traceback.print_exc()

        # 尝试记录错误到日志文件
        try:
            logger = logging.getLogger(__name__)
            logger.critical(error_msg, exc_info=True)
        except:
            pass

        return 1

    finally:
        # 清理工作
        try:
            logger = logging.getLogger(__name__)
            logger.info("🔄 应用程序正在关闭...")

            # 清理临时文件
            temp_dir = PROJECT_ROOT / "temp"
            if temp_dir.exists():
                import shutil

                try:
                    shutil.rmtree(temp_dir)
                    logger.info("🗑️  临时文件清理完成")
                except Exception as e:
                    logger.warning(f"临时文件清理失败: {e}")

            logger.info("👋 再见！")

        except:
            pass


if __name__ == "__main__":
    # 设置异常处理
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = f"未捕获的异常: {exc_type.__name__}: {exc_value}"
        print(f"❌ {error_msg}")

        # 尝试记录到日志
        try:
            logger = logging.getLogger("uncaught_exception")
            logger.critical(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        except:
            pass

    sys.excepthook = handle_exception

    # 运行主函数
    exit_code = main()
    sys.exit(exit_code)
