"""
数据处理自动化工作流应用 - 引擎层

版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》引擎层、《模块化开发方案》引擎层设计
框架：工作流执行引擎

引擎层模块，负责：
1. 工作流解析、校验、计划和执行
2. 节点调度和并发控制
3. 数据流管理和状态监控
4. 错误处理和恢复机制
"""

from .workflow_engine import WorkflowEngine
from .execution_context import ExecutionContext, ExecutionStatus
from .data_flow import DataFlow, DataFlowService, DataNode, DataLineage
from .scheduler import NodeScheduler, SchedulerStrategy
from .error_handler import ErrorHandler, ErrorLevel, ErrorCategory, RecoveryStrategy
from .execution_plan import ExecutionPlan, ScheduleStrategy as PlanScheduleStrategy, NodeResourceInfo, ExecutionGroup
from .run_handle import RunHandle, RunState, NodeExecutionInfo, ExecutionMetrics
from .workflow_parser import WorkflowParser, WorkflowSchema
from .validation import ParameterValidator
from .data_processor import DataProcessor, DataProfile, ProcessingResult, DataFormat, DataQuality
from .workflow_manager import WorkflowManager, WorkflowTemplate, WorkflowExecutionRecord
from .contracts import (
    NodePlugin,
    NodeInfo,
    ParameterInfo,
    ValidationResult,
    ExecutionResult,
    WorkflowModel,
    WorkflowNode,
    Connection,
    PortInfo,
    PortType,
    ParameterType,
)

__all__ = [
    # 核心引擎
    "WorkflowEngine",
    "ExecutionContext",
    "ExecutionStatus",
    # 执行计划和控制
    "ExecutionPlan",
    "PlanScheduleStrategy",
    "NodeResourceInfo",
    "ExecutionGroup",
    "RunHandle",
    "RunState",
    "NodeExecutionInfo",
    "ExecutionMetrics",
    # 数据流管理
    "DataFlow",
    "DataFlowService",
    "DataNode",
    "DataLineage",
    "DataProcessor",
    "DataProfile",
    "ProcessingResult",
    "DataFormat",
    "DataQuality",
    # 调度和错误处理
    "NodeScheduler",
    "SchedulerStrategy",
    "ErrorHandler",
    "ErrorLevel",
    "ErrorCategory",
    "RecoveryStrategy",
    # 工作流管理
    "WorkflowParser",
    "WorkflowSchema",
    "WorkflowManager",
    "WorkflowTemplate",
    "WorkflowExecutionRecord",
    "ParameterValidator",
    # 数据契约
    "NodePlugin",
    "NodeInfo",
    "ParameterInfo",
    "ValidationResult",
    "ExecutionResult",
    "WorkflowModel",
    "WorkflowNode",
    "Connection",
    "PortInfo",
    "PortType",
    "ParameterType",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "Data Workflow Automation Team"
__description__ = "Workflow execution engine for data processing automation"
