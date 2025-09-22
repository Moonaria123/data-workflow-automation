#!/usr/bin/env python3
"""
数据处理自动化工作流应用 - 安装配置

文档版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》、《PROJECT_SETUP.md》
用途：项目打包、分发、依赖管理
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# 读取依赖
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                requirements.append(line)

# 读取开发依赖
dev_requirements = []
dev_requirements_file = this_directory / "requirements-dev.txt"
if dev_requirements_file.exists():
    with open(dev_requirements_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if (
                line
                and not line.startswith("#")
                and not line.startswith("-r")
                and not line.startswith("-")
            ):
                dev_requirements.append(line)

setup(
    name="data-workflow-automation",
    version="1.0.0",
    author="DWA Development Team",
    author_email="dev@dwa-platform.com",
    description="专为个人用户设计的桌面可视化数据处理工作流平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Moonaria123/data-workflow-automation",
    project_urls={
        "Bug Reports": "https://github.com/Moonaria123/data-workflow-automation/issues",
        "Source": "https://github.com/Moonaria123/data-workflow-automation",
        "Documentation": "https://github.com/Moonaria123/data-workflow-automation/docs",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "resources": ["*.qss", "*.png", "*.ico", "*.json"],
        "config": ["*.ini", "*.json", "*.yaml"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: Chinese (Simplified)",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
        ],
        "build": [
            "PyInstaller>=5.13.0",
            "build>=0.10.0",
            "wheel>=0.41.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dwa=main:main",
            "data-workflow-automation=main:main",
        ],
        "gui_scripts": [
            "dwa-gui=main:main",
        ],
    },
    keywords=[
        "data-processing",
        "workflow",
        "automation",
        "excel",
        "finance",
        "pyqt6",
        "polars",
        "visual-programming",
        "drag-and-drop",
        "data-analysis",
    ],
    zip_safe=False,
    platforms=["any"],
)
