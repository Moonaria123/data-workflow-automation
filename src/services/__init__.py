"""
数据处理自动化工作流应用 - 服务层模块

版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》服务层架构
框架：服务层统一导出

服务层模块，提供：
1. 工作流序列化服务
2. 节点连接管理服务
3. 参数系统集成服务
4. 数据预览服务
5. 其他核心业务服务
"""

from .workflow_serialization import WorkflowSerializer, WorkflowFileManager

from .node_connection import (
    NodeConnectionManager,
    ConnectionStatus,
    PortTypeCompatibilityRule,
    CycleDetectionRule,
    DuplicateConnectionRule,
    SingleInputPortRule,
)

from .parameter_integration import (
    ParameterManager,
    ParameterSystemIntegration,
    ParameterScope,
    ParameterSource,
    ParameterBinding,
    ParameterDependency,
    ParameterTemplate,
    ExpressionEvaluator,
)

__all__ = [
    # 工作流序列化
    "WorkflowSerializer",
    "WorkflowFileManager",
    # 节点连接管理
    "NodeConnectionManager",
    "ConnectionStatus",
    "PortTypeCompatibilityRule",
    "CycleDetectionRule",
    "DuplicateConnectionRule",
    "SingleInputPortRule",
    # 参数系统集成
    "ParameterManager",
    "ParameterSystemIntegration",
    "ParameterScope",
    "ParameterSource",
    "ParameterBinding",
    "ParameterDependency",
    "ParameterTemplate",
    "ExpressionEvaluator",
]
