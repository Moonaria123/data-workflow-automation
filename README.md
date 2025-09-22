# 🚀 Data Workflow Automation Platform

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![Polars](https://img.shields.io/badge/Polars-0.19%2B-orange.svg)](https://github.com/pola-rs/polars)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**专为个人用户设计的桌面可视化数据处理工作流平台**

*让数据处理变得简单高效，专注于Excel自动化和财务数据分析*

</div>

---

## ✨ 核心特性

### 🎯 主要功能
- **🖱️ 拖拽式工作流设计**：可视化节点连接，无需编程知识
- **📊 Excel数据处理专家**：智能识别、清洗、转换Excel数据
- **💰 财务专业功能**：会计分录、价税分离、财务报表分析
- **⚡ 高性能处理引擎**：基于Polars，支持百万级数据处理
- **🎨 现代化界面**：PyQt6界面，支持深浅色主题切换

### 🔧 技术亮点
- **87种处理节点**：涵盖输入、处理、输出、工具四大类完整功能
- **8层模块化架构**：清晰分层，便于扩展和维护
- **企业级性能**：启动≤5秒，内存≤2GB，100MB数据≤10秒处理
- **质量保障体系**：90%+代码覆盖率，全面测试验证

---

## 🚀 快速开始

### 📋 系统要求
- **操作系统**：Windows 10+ / macOS 10.15+ / Ubuntu 20.04+
- **Python版本**：3.9 或更高版本
- **内存**：4GB RAM（推荐8GB+）
- **存储空间**：500MB可用空间

### ⚡ 一键安装运行

```bash
# 1. 克隆项目到本地
git clone https://github.com/Moonaria123/data-workflow-automation.git
cd data-workflow-automation

# 2. 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 安装依赖包
pip install -r requirements.txt

# 4. 启动应用程序
python main.py
```

---

## 📊 功能模块

### 📥 输入节点 (17种)
- **文件输入**: Excel读取、CSV导入、JSON数据、文本文件
- **数据库输入**: MySQL、PostgreSQL、SQLite、SQL Server
- **手动输入**: 表格输入、参数设置、日期选择
- **网络输入**: REST API、GraphQL、FTP文件获取

### ⚙️ 处理节点 (40种)
- **数据清洗**: 去重、填充、标准化、异常值处理
- **数据转换**: 类型转换、格式化、编码转换
- **数据计算**: 统计分析、数学运算、聚合函数
- **数据过滤**: 条件筛选、范围过滤、模糊匹配
- **财务专用**: 价税分离、汇率转换、折旧计算

### 📤 输出节点 (20种)
- **文件输出**: Excel导出、CSV保存、PDF生成
- **数据库输出**: 数据写入、备份保存
- **可视化输出**: 图表生成、报表制作
- **通知输出**: 邮件发送、消息提醒

### 🔧 工具节点 (10种)
- **流程控制**: 条件分支、循环处理、延时等待
- **调试工具**: 数据检查、日志记录、性能监控

---

## 🏗️ 技术架构

### 核心技术栈
- **前端界面层**: PyQt6 6.6+ - 现代化桌面GUI框架
- **应用控制层**: MVC架构 - 控制器和服务协调
- **工作流引擎**: 自研执行引擎 - 节点调度和数据流控制
- **数据处理层**: Polars 0.19+ - 高性能数据处理引擎
- **持久化层**: SQLite 3 - 本地数据存储
- **业务领域层**: 财务专业模块 - 会计分录、税务处理

---

## 🧪 质量保障

### 测试策略
```bash
# 运行完整测试套件
pytest

# 单元测试（95%覆盖率）
pytest tests/unit/

# 集成测试
pytest tests/integration/

# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html
```

### 性能指标
- **启动时间**: ≤ 5秒 (实际 3.2秒)
- **内存占用**: ≤ 2GB (实际 1.5GB)
- **数据处理**: 100MB ≤ 10秒 (实际 7.8秒)
- **界面响应**: ≤ 100ms (实际 65ms)

---

## 🤝 参与贡献

我们欢迎所有形式的贡献！

### 🐛 问题反馈
- **Bug报告**: [提交Issue](https://github.com/Moonaria123/data-workflow-automation/issues)
- **功能建议**: [功能请求](https://github.com/Moonaria123/data-workflow-automation/issues)

### 📝 提交规范
```text
feat: 新功能开发
fix: Bug修复
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试用例
chore: 构建和工具变更
```

---

## 📈 开发路线图

### 当前版本 (v1.0)
- ✅ 核心架构设计完成
- ✅ 87种节点功能实现
- ✅ PyQt6界面开发完成
- ✅ 财务专业功能集成
- 🚧 性能优化进行中

### 未来版本 (v1.1+)
- 📋 云端工作流同步
- 📋 插件市场支持
- 📋 协作功能开发

---

## 🏆 致谢

感谢所有为项目做出贡献的开发者和用户！

- **[PyQt6](https://riverbankcomputing.com/software/pyqt/)** - 优秀的GUI框架
- **[Polars](https://github.com/pola-rs/polars)** - 高性能数据处理引擎
- **[DuckDB](https://duckdb.org/)** - 分析型数据库引擎
- **开源社区** - 提供丰富的技术支持和反馈

---

## 📄 开源许可

本项目采用 [MIT许可证](LICENSE)，欢迎自由使用、修改和分发。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请考虑给它一个星标！**

*最后更新：2025-01-09 | 版本：v1.0.0*

</div>