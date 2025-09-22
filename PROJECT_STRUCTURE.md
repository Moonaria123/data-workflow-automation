# 数据工作流自动化平台 - 项目结构

## 项目概述

本项目是一个专为个人用户设计的桌面可视化数据处理工作流平台，基于Python 3.9+ + PyQt6 + Polars技术栈开发。

## 技术架构

### 核心技术栈
- **前端框架**: PyQt6 6.6+
- **数据处理**: Polars 0.19+ (主要), Pandas 2.0+ (兼容)
- **数据库**: SQLite (内置), 支持Excel/CSV/JSON等格式
- **可视化**: Plotly 5.15+, Matplotlib
- **异步处理**: asyncio, 多线程支持

### 8层架构设计

```
┌─────────────────────────────────────┐
│            用户界面层 (UI)            │  ← PyQt6主窗口、工作流画布、属性面板
├─────────────────────────────────────┤
│           应用控制层 (App)            │  ← 应用程序生命周期、事件总线、配置管理
├─────────────────────────────────────┤
│           业务逻辑层 (Business)        │  ← 工作流管理、节点调度、数据验证
├─────────────────────────────────────┤
│           服务层 (Services)           │  ← 序列化服务、连接管理、参数系统
├─────────────────────────────────────┤
│           引擎层 (Engine)             │  ← 工作流执行引擎、调度器、数据流管理
├─────────────────────────────────────┤
│           节点层 (Nodes)              │  ← 87种数据处理节点插件实现
├─────────────────────────────────────┤
│           数据层 (Data)               │  ← 数据模型、持久化、缓存管理
├─────────────────────────────────────┤
│           基础设施层 (Infrastructure)  │  ← 通用工具、性能优化、日志系统
└─────────────────────────────────────┘
```

## 项目结构

```
data-workflow-automation/
├── README.md                    # 项目说明文档
├── LICENSE                      # MIT开源许可证
├── main.py                      # 应用程序入口点
├── setup.py                     # 项目打包配置
├── requirements.txt             # 生产环境依赖
├── requirements-dev.txt         # 开发环境依赖
├── .gitignore                   # Git忽略规则
├── config/
│   └── app_config.json         # 应用程序配置文件
└── src/                        # 源代码目录
    ├── __init__.py
    ├── common/                 # 公共模块
    │   ├── contracts.py        # 核心数据契约和接口定义
    │   ├── config.py          # 配置管理
    │   └── environment.py     # 环境检查和日志系统
    ├── app/                   # 应用程序层
    │   ├── application.py     # PyQt6应用程序主类
    │   ├── controllers/       # 控制器组件
    │   ├── commands/          # 命令模式实现
    │   └── viewmodels/        # 视图模型
    ├── ui/                    # 用户界面层
    │   ├── main_window.py     # 主窗口 (1178行)
    │   ├── canvas.py          # 工作流画布组件
    │   ├── property_panel.py  # 属性编辑面板
    │   ├── components/        # UI组件库
    │   ├── dialogs/           # 对话框组件
    │   ├── panels/            # 面板组件
    │   ├── widgets/           # 自定义控件
    │   └── themes/            # 主题和样式
    ├── engine/                # 执行引擎层
    │   ├── workflow_engine.py # 工作流执行引擎 (1105行)
    │   ├── scheduler.py       # 智能节点调度器 (1114行)
    │   ├── data_flow.py       # 数据流管理
    │   ├── execution_plan.py  # 执行计划管理
    │   ├── error_handler.py   # 错误处理机制
    │   └── contracts.py       # 引擎层接口契约
    ├── nodes/                 # 节点插件库 (87种节点)
    │   ├── __init__.py        # 节点注册和发现
    │   ├── base.py           # 节点插件基础类
    │   ├── input/            # 输入节点 (17种)
    │   ├── processing/       # 处理节点 (40种)
    │   ├── output/           # 输出节点 (20种)
    │   ├── finance/          # 财务节点 (8种)
    │   ├── tools/            # 工具节点 (10种)
    │   ├── analysis/         # 分析节点
    │   └── visualization/    # 可视化节点
    ├── services/             # 服务层
    │   ├── workflow_serialization.py # 工作流序列化
    │   ├── node_connection.py        # 节点连接管理
    │   ├── parameter_integration.py  # 参数系统集成
    │   └── storage_service.py        # 存储服务
    ├── models/               # 数据模型层
    │   └── finance/          # 财务数据模型
    ├── persistence/          # 持久化层
    ├── utils/                # 工具库
    │   ├── performance_monitor.py    # 性能监控
    │   ├── resource_optimizer.py     # 资源优化
    │   ├── ui_optimizer.py           # UI优化
    │   └── startup_optimizer.py      # 启动优化
    └── workflows/            # 工作流模板
```

## 核心功能模块

### 1. 用户界面层 (UI)
- **主窗口**: 1178行代码，完整的PyQt6主窗口实现
- **工作流画布**: 支持拖拽式节点编排和连接管理
- **属性面板**: 动态参数编辑和实时验证
- **组件库**: 丰富的UI组件和自定义控件

### 2. 执行引擎层 (Engine)
- **工作流引擎**: 1105行代码，支持并行执行和错误恢复
- **智能调度器**: 1114行代码，7种调度策略，负载均衡
- **数据流管理**: 数据传递、转换和血缘追踪
- **错误处理**: 完善的异常处理和恢复机制

### 3. 节点插件库 (Nodes)
- **87种节点**: 覆盖输入、处理、输出、财务、工具等领域
- **统一接口**: BaseNodePlugin抽象类，标准化节点开发
- **插件系统**: 自动注册和发现机制
- **沙箱执行**: 安全的节点执行环境

### 4. 数据契约层 (Contracts)
- **核心契约**: 725行代码，完整的数据模型定义
- **类型安全**: 强类型接口，确保模块间数据一致性
- **参数验证**: 完善的参数验证和错误处理
- **版本管理**: 接口版本控制和兼容性管理

## 性能特性

### 内存管理
- 最大内存使用: 2GB (可配置)
- 智能内存监控和警告机制
- 数据流优化，减少内存占用

### 执行性能
- 启动时间: ≤5秒
- 100MB数据处理: ≤10秒
- 支持多线程并行执行
- 智能调度和负载均衡

### 可扩展性
- 模块化架构，易于扩展
- 插件化节点系统
- 支持自定义节点开发
- 热插拔组件支持

## 开发规范

### 代码质量
- 完整的类型注解支持
- 统一的错误处理机制
- 详细的代码文档和注释
- 模块化设计，低耦合高内聚

### 测试覆盖
- 目标代码覆盖率: 90%+
- 单元测试、集成测试支持
- 性能测试和压力测试
- 自动化测试流水线

### 文档体系
- 用户手册和开发文档
- API接口文档
- 节点开发指南
- 部署和维护文档

## 构建和部署

### 开发环境
```bash
# 克隆仓库
git clone https://github.com/Moonaria123/data-workflow-automation.git
cd data-workflow-automation

# 安装依赖
pip install -r requirements-dev.txt

# 运行应用
python main.py
```

### 生产部署
```bash
# 安装生产依赖
pip install -r requirements.txt

# 构建可执行文件
pyinstaller --windowed main.py

# 或使用setup.py安装
python setup.py install
```

## 贡献指南

本项目采用MIT开源许可证，欢迎社区贡献。

### 开发流程
1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request
5. 代码审查和合并

### 问题反馈
- GitHub Issues: 报告Bug和功能请求
- 技术讨论: GitHub Discussions
- 文档完善: Wiki贡献

---

**项目状态**: 生产就绪 ✅  
**最后更新**: 2025-09-22  
**维护团队**: DWA Development Team
