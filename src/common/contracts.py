"""
数据处理自动化工作流应用 - 核心数据契约

文档版本：V1.0
创建日期：2025-09-06
依据文档：《用户需求说明书》、《模块化开发方案》、《技术架构设计》
适用范围：所有模块间的数据传输和接口定义

统一数据模型与节点接口契约定义，确保模块间数据传递的类型安全和一致性。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Type
from uuid import UUID, uuid4

import polars as pl
import pandas as pd


# =============================================================================
# 1. 基础数据类型和枚举
# =============================================================================


@dataclass
class ParameterInfo:
    """参数信息定义 - 节点参数接口契约"""
    
    name: str  # 参数名称
    parameter_type: 'ParameterType'  # 参数类型
    required: bool = True  # 是否必需
    default_value: Any = None  # 默认值
    description: str = ""  # 参数描述
    choices: Optional[List[str]] = None  # 选择项（用于CHOICE类型）
    validation_rules: Optional[Dict[str, Any]] = None  # 验证规则
    
    def __post_init__(self):
        """初始化后处理"""
        if self.validation_rules is None:
            self.validation_rules = {}


@dataclass
class NodeInfo:
    """节点信息定义 - 节点元数据契约"""
    
    id: str  # 节点唯一标识
    name: str  # 节点显示名称
    category: str  # 节点分类
    node_type: 'NodeType'  # 节点类型
    description: str = ""  # 节点描述
    version: str = "1.0.0"  # 节点版本
    author: str = ""  # 作者信息
    inputs: List[ParameterInfo] = field(default_factory=list)  # 输入参数
    outputs: List[ParameterInfo] = field(default_factory=list)  # 输出参数
    tags: List[str] = field(default_factory=list)  # 标签
    
    def get_input_by_name(self, name: str) -> Optional[ParameterInfo]:
        """根据名称获取输入参数"""
        return next((inp for inp in self.inputs if inp.name == name), None)
    
    def get_output_by_name(self, name: str) -> Optional[ParameterInfo]:
        """根据名称获取输出参数"""
        return next((out for out in self.outputs if out.name == name), None)


@dataclass
class ExecutionResult:
    """执行结果契约 - 节点执行状态和输出"""
    
    success: bool  # 执行是否成功
    node_id: str  # 节点ID
    execution_time: float = 0.0  # 执行耗时(秒)
    memory_usage: int = 0  # 内存使用(MB)
    output_data: Dict[str, Any] = field(default_factory=dict)  # 输出数据
    error_message: str = ""  # 错误信息
    warning_messages: List[str] = field(default_factory=list)  # 警告信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    
    def add_warning(self, message: str):
        """添加警告信息"""
        self.warning_messages.append(message)
    
    def set_error(self, message: str):
        """设置错误信息"""
        self.success = False
        self.error_message = message
    
    def get_output(self, name: str, default: Any = None) -> Any:
        """获取指定输出数据"""
        return self.output_data.get(name, default)


class NodeType(Enum):
    """节点类型枚举 - 对应95种节点分类"""

    # 输入节点 (17种)
    INPUT = "input"
    INPUT_FILE = "input_file"
    INPUT_DATABASE = "input_database"
    INPUT_API = "input_api"
    INPUT_MANUAL = "input_manual"

    # 处理节点 (40种)
    PROCESSING = "processing"
    PROCESS_CLEAN = "process_clean"
    PROCESS_TRANSFORM = "process_transform"
    PROCESS_AGGREGATE = "process_aggregate"
    PROCESS_FILTER = "process_filter"
    PROCESS_CALCULATE = "process_calculate"
    PROCESS_FINANCE = "process_finance"

    # 输出节点 (20种)
    OUTPUT = "output"
    OUTPUT_FILE = "output_file"
    OUTPUT_DATABASE = "output_database"
    OUTPUT_REPORT = "output_report"
    OUTPUT_CHART = "output_chart"
    OUTPUT_EMAIL = "output_email"

    # 工具节点 (10种)
    TOOL = "tool"
    TOOL_CONDITION = "tool_condition"
    TOOL_LOOP = "tool_loop"
    TOOL_SCRIPT = "tool_script"
    TOOL_VARIABLE = "tool_variable"


class ExecutionStatus(Enum):
    """工作流和节点执行状态"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消
    PAUSED = "paused"  # 已暂停


class DataType(Enum):
    """数据类型枚举 - 支持的数据格式"""

    DATAFRAME = "dataframe"  # Polars/Pandas DataFrame
    TEXT = "text"  # 字符串文本
    NUMBER = "number"  # 数值类型
    BOOLEAN = "boolean"  # 布尔类型
    DATE = "date"  # 日期类型
    FILE = "file"  # 文件路径
    JSON = "json"  # JSON对象
    LIST = "list"  # 列表数据
    DICT = "dict"  # 字典数据


class ParameterType(Enum):
    """参数类型枚举 - 节点参数配置"""
    
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    FILE = "file"
    DATE = "date"
    JSON = "json"


class PortType(Enum):
    """端口类型枚举"""
    
    DATA = "data"
    CONTROL = "control"
    EVENT = "event"


class LogLevel(Enum):
    """日志级别"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# =============================================================================
# 2. 核心数据结构
# =============================================================================


@dataclass
class NodeParameter:
    """节点参数定义 - FR-004工作流参数配置系统"""

    name: str  # 参数名称
    param_type: str  # 参数类型：text/number/date/file/select/boolean
    default_value: Any = None  # 默认值
    required: bool = False  # 是否必填
    description: str = ""  # 参数描述
    validation_rules: Dict[str, Any] = field(default_factory=dict)  # 验证规则
    options: List[str] = field(default_factory=list)  # 选择参数的选项列表

    def validate(self, value: Any) -> bool:
        """验证参数值是否符合规则"""
        if self.required and value is None:
            return False

        # 类型验证
        if value is not None:
            if self.param_type == "number" and not isinstance(value, (int, float)):
                return False
            elif self.param_type == "boolean" and not isinstance(value, bool):
                return False
            elif self.param_type == "select" and value not in self.options:
                return False

        # 自定义验证规则
        for rule, rule_value in self.validation_rules.items():
            if rule == "min_length" and len(str(value)) < rule_value:
                return False
            elif rule == "max_length" and len(str(value)) > rule_value:
                return False
            elif rule == "min_value" and value < rule_value:
                return False
            elif rule == "max_value" and value > rule_value:
                return False

        return True


@dataclass
class DataPortSchema:
    """数据端口模式定义 - 节点输入输出接口"""

    name: str  # 端口名称
    data_type: DataType  # 数据类型
    required: bool = True  # 是否必需
    description: str = ""  # 端口描述
    schema: Optional[Dict[str, Any]] = None  # 数据模式（如DataFrame列定义）


@dataclass
class ExecutionContext:
    """执行上下文 - 工作流运行时环境"""

    run_id: str  # 运行实例ID
    workflow_id: str  # 工作流ID
    started_at: datetime  # 开始时间
    global_parameters: Dict[str, Any] = field(default_factory=dict)  # 全局参数
    temp_dir: str = ""  # 临时目录
    log_level: LogLevel = LogLevel.INFO  # 日志级别
    max_memory_mb: int = 2048  # 最大内存限制(MB)
    timeout_seconds: int = 3600  # 超时时间(秒)

    def resolve_parameter(self, expression: str) -> Any:
        """解析参数表达式，支持${parameter_name}语法"""
        if not expression.startswith("${") or not expression.endswith("}"):
            return expression

        param_name = expression[2:-1]
        return self.global_parameters.get(param_name, expression)


@dataclass
class NodeResult:
    """节点执行结果"""

    node_id: str  # 节点ID
    status: ExecutionStatus  # 执行状态
    data: Optional[Any] = None  # 输出数据
    error_message: str = ""  # 错误消息
    execution_time_ms: int = 0  # 执行耗时(毫秒)
    memory_usage_mb: float = 0.0  # 内存使用量(MB)
    output_count: int = 0  # 输出记录数

    def is_success(self) -> bool:
        """判断是否执行成功"""
        return self.status == ExecutionStatus.COMPLETED

    def get_dataframe(self) -> Optional[pl.DataFrame]:
        """获取DataFrame数据，自动转换格式"""
        if self.data is None:
            return None

        if isinstance(self.data, pl.DataFrame):
            return self.data
        elif isinstance(self.data, pd.DataFrame):
            return pl.from_pandas(self.data)
        else:
            return None


@dataclass
class LogEntry:
    """日志条目"""

    timestamp: datetime  # 时间戳
    level: LogLevel  # 日志级别
    node_id: str  # 节点ID
    message: str  # 日志消息
    extra: Dict[str, Any] = field(default_factory=dict)  # 额外信息


# =============================================================================
# 3. 节点基类和接口
# =============================================================================


class IProcessingNode(ABC):
    """数据处理节点接口 - FR-001数据处理节点系统"""

    @abstractmethod
    def get_node_info(self) -> NodeInfo:
        """获取节点信息"""
        pass

    @abstractmethod
    def execute(
        self, inputs: Dict[str, Any], parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """执行节点逻辑"""
        pass

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入数据"""
        pass

    def cleanup(self, context: ExecutionContext) -> None:
        """清理资源（可选实现）"""
        pass


class BaseProcessingNode(IProcessingNode):
    """数据处理节点基类 - 通用实现"""

    def __init__(self, node_id: str, display_name: str):
        self.node_id = node_id
        self.display_name = display_name
        self._node_info: Optional[NodeInfo] = None

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """默认输入验证 - 子类可重写"""
        return True

    def create_execution_result(
        self, success: bool = True, output_data: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """创建执行结果对象"""
        return ExecutionResult(
            success=success,
            node_id=self.node_id,
            output_data=output_data or {},
        )


# =============================================================================
# 4. 工作流定义
# =============================================================================


@dataclass
class WorkflowNode:
    """工作流中的节点定义"""

    node_id: str  # 节点唯一ID
    node_type: str  # 节点类型名称
    display_name: str  # 显示名称
    position: Dict[str, float]  # 位置坐标 {x, y}
    parameters: Dict[str, Any] = field(default_factory=dict)  # 节点参数
    enabled: bool = True  # 是否启用


@dataclass
class WorkflowConnection:
    """工作流连接定义"""

    connection_id: str  # 连接唯一ID
    from_node_id: str  # 源节点ID
    to_node_id: str  # 目标节点ID
    from_port: str  # 源端口名称
    to_port: str  # 目标端口名称
    enabled: bool = True  # 是否启用


@dataclass
class WorkflowDefinition:
    """工作流定义 - FR-002可视化工作流设计器"""

    workflow_id: str  # 工作流唯一ID
    name: str  # 工作流名称
    description: str = ""  # 描述
    version: str = "1.0.0"  # 版本号
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    nodes: List[WorkflowNode] = field(default_factory=list)  # 节点列表
    connections: List[WorkflowConnection] = field(default_factory=list)  # 连接列表
    global_parameters: List[NodeParameter] = field(default_factory=list)  # 全局参数

    def add_node(self, node: WorkflowNode) -> None:
        """添加节点"""
        self.nodes.append(node)

    def add_connection(self, connection: WorkflowConnection) -> None:
        """添加连接"""
        self.connections.append(connection)

    def get_node_by_id(self, node_id: str) -> Optional[WorkflowNode]:
        """根据ID获取节点"""
        return next((node for node in self.nodes if node.node_id == node_id), None)

    def get_connections_from_node(self, node_id: str) -> List[WorkflowConnection]:
        """获取从指定节点出发的连接"""
        return [conn for conn in self.connections if conn.from_node_id == node_id]

    def get_connections_to_node(self, node_id: str) -> List[WorkflowConnection]:
        """获取连接到指定节点的连接"""
        return [conn for conn in self.connections if conn.to_node_id == node_id]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "display_name": node.display_name,
                    "position": node.position,
                    "parameters": node.parameters,
                }
                for node in self.nodes
            ],
            "connections": [
                {
                    "connection_id": conn.connection_id,
                    "from_node_id": conn.from_node_id,
                    "to_node_id": conn.to_node_id,
                    "from_port": conn.from_port,
                    "to_port": conn.to_port,
                }
                for conn in self.connections
            ],
            "global_parameters": [
                {
                    "name": param.name,
                    "param_type": param.param_type,
                    "default_value": param.default_value,
                    "required": param.required,
                    "description": param.description,
                    "validation_rules": param.validation_rules,
                    "options": param.options,
                }
                for param in self.global_parameters
            ],
        }


# =============================================================================
# 5. 异常定义
# =============================================================================


class WorkflowException(Exception):
    """工作流异常基类"""

    pass


class NodeExecutionException(WorkflowException):
    """节点执行异常"""

    def __init__(
        self, node_id: str, message: str, original_exception: Optional[Exception] = None
    ):
        self.node_id = node_id
        self.original_exception = original_exception
        super().__init__(f"节点 {node_id} 执行失败: {message}")


class ParameterValidationException(WorkflowException):
    """参数验证异常"""

    def __init__(self, parameter_name: str, message: str):
        self.parameter_name = parameter_name
        super().__init__(f"参数 {parameter_name} 验证失败: {message}")


class DataValidationException(WorkflowException):
    """数据验证异常"""

    def __init__(self, data_type: str, message: str):
        self.data_type = data_type
        super().__init__(f"数据类型 {data_type} 验证失败: {message}")


# =============================================================================
# 6. 工具函数
# =============================================================================


def generate_node_id() -> str:
    """生成唯一的节点ID"""
    return f"node_{uuid4().hex[:8]}"


def generate_workflow_id() -> str:
    """生成唯一的工作流ID"""
    return f"workflow_{uuid4().hex[:8]}"


def generate_run_id() -> str:
    """生成唯一的运行实例ID"""
    return f"run_{uuid4().hex[:8]}"


def create_execution_context(
    workflow_id: str, global_parameters: Optional[Dict[str, Any]] = None
) -> ExecutionContext:
    """创建执行上下文"""
    return ExecutionContext(
        run_id=generate_run_id(),
        workflow_id=workflow_id,
        started_at=datetime.now(),
        global_parameters=global_parameters or {},
        temp_dir=f"temp/run_{uuid4().hex[:8]}",
        log_level=LogLevel.INFO,
        max_memory_mb=2048,
        timeout_seconds=3600,
    )


# =============================================================================
# 7. 版本信息
# =============================================================================

__version__ = "1.0.0"
__author__ = "Data Workflow Automation Team"
__description__ = (
    "Core contracts and data models for the Data Workflow Automation Application"
)
