"""
财务工作流基础框架

提供工作流模板的核心抽象类和通用组件，支持：
- 工作流步骤定义和执行
- 工作流上下文管理
- 错误处理和日志记录
- 状态跟踪和进度管理
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import traceback

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepStatus(Enum):
    """工作流步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowContext:
    """工作流执行上下文
    
    存储工作流执行过程中的共享数据、配置参数和状态信息
    """
    # 基本信息
    workflow_id: str
    workflow_name: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # 执行状态
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    
    # 数据存储
    data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # 配置参数
    config: Dict[str, Any] = field(default_factory=dict)
    
    # 执行统计
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step_count: int = 0
    completed_count: int = 0
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any) -> None:
        """设置上下文数据"""
        self.data[key] = value
    
    def add_result(self, step_name: str, result: Any) -> None:
        """添加步骤执行结果"""
        self.results[step_name] = result
    
    def add_error(self, step_name: str, error: Exception) -> None:
        """添加错误信息"""
        error_info = {
            'step': step_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now(),
            'traceback': traceback.format_exc()
        }
        self.errors.append(error_info)
    
    def get_progress(self) -> float:
        """获取执行进度百分比"""
        if self.step_count == 0:
            return 0.0
        return (self.completed_count / self.step_count) * 100.0

@dataclass
class WorkflowStep:
    """工作流步骤定义
    
    定义单个工作流步骤的名称、描述、执行函数和依赖关系
    """
    name: str
    description: str
    execute_func: Callable[[WorkflowContext], Any]
    
    # 步骤属性
    required: bool = True
    retry_count: int = 0
    timeout: Optional[int] = None
    
    # 依赖关系
    depends_on: List[str] = field(default_factory=list)
    
    # 执行状态
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[Exception] = None
    
    def can_execute(self, context: WorkflowContext) -> bool:
        """检查步骤是否可以执行"""
        # 检查依赖步骤是否已完成
        for dep_step in self.depends_on:
            if dep_step not in context.completed_steps:
                return False
        return True
    
    def execute(self, context: WorkflowContext) -> Any:
        """执行工作流步骤"""
        try:
            self.status = StepStatus.RUNNING
            self.start_time = datetime.now()
            context.current_step = self.name
            
            logger.info(f"开始执行步骤: {self.name}")
            
            # 执行步骤函数
            result = self.execute_func(context)
            
            # 记录结果
            self.result = result
            self.status = StepStatus.COMPLETED
            self.end_time = datetime.now()
            
            # 更新上下文
            context.completed_steps.append(self.name)
            context.add_result(self.name, result)
            context.completed_count += 1
            
            logger.info(f"步骤执行完成: {self.name}")
            return result
            
        except Exception as e:
            self.error = e
            self.status = StepStatus.FAILED
            self.end_time = datetime.now()
            
            # 更新上下文
            context.failed_steps.append(self.name)
            context.add_error(self.name, e)
            
            logger.error(f"步骤执行失败: {self.name}, 错误: {str(e)}")
            
            if self.required:
                raise e
            else:
                # 可选步骤失败时跳过
                self.status = StepStatus.SKIPPED
                return None

class WorkflowTemplate(ABC):
    """工作流模板抽象基类
    
    定义财务工作流的通用结构和执行逻辑
    """
    
    def __init__(self, workflow_name: str, workflow_id: Optional[str] = None):
        self.workflow_name = workflow_name
        self.workflow_id = workflow_id or f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.steps: List[WorkflowStep] = []
        self.context: Optional[WorkflowContext] = None
    
    @abstractmethod
    def define_steps(self) -> List[WorkflowStep]:
        """定义工作流步骤
        
        子类必须实现此方法来定义具体的业务步骤
        """
        pass
    
    def initialize_context(self, initial_data: Optional[Dict[str, Any]] = None, 
                          config: Optional[Dict[str, Any]] = None) -> WorkflowContext:
        """初始化工作流上下文"""
        self.context = WorkflowContext(
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            data=initial_data or {},
            config=config or {}
        )
        return self.context
    
    def prepare_workflow(self, initial_data: Optional[Dict[str, Any]] = None, 
                        config: Optional[Dict[str, Any]] = None) -> None:
        """准备工作流执行"""
        # 初始化上下文
        self.initialize_context(initial_data, config)
        
        # 定义步骤
        self.steps = self.define_steps()
        self.context.step_count = len(self.steps)
        
        logger.info(f"工作流准备完成: {self.workflow_name}, 步骤数量: {len(self.steps)}")
    
    def validate_workflow(self) -> List[str]:
        """验证工作流定义的正确性"""
        errors = []
        
        # 检查步骤依赖关系
        step_names = {step.name for step in self.steps}
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_names:
                    errors.append(f"步骤 '{step.name}' 依赖的步骤 '{dep}' 不存在")
        
        # 检查循环依赖
        # TODO: 实现循环依赖检测算法
        
        return errors
    
    def execute(self, initial_data: Optional[Dict[str, Any]] = None, 
               config: Optional[Dict[str, Any]] = None) -> WorkflowContext:
        """执行工作流
        
        Args:
            initial_data: 初始数据
            config: 配置参数
            
        Returns:
            执行完成后的工作流上下文
        """
        try:
            # 准备工作流
            self.prepare_workflow(initial_data, config)
            
            # 验证工作流
            validation_errors = self.validate_workflow()
            if validation_errors:
                raise ValueError(f"工作流验证失败: {', '.join(validation_errors)}")
            
            # 开始执行
            self.context.status = WorkflowStatus.RUNNING
            self.context.start_time = datetime.now()
            
            logger.info(f"开始执行工作流: {self.workflow_name}")
            
            # 执行步骤
            self._execute_steps()
            
            # 完成执行
            self.context.status = WorkflowStatus.COMPLETED
            self.context.end_time = datetime.now()
            
            logger.info(f"工作流执行完成: {self.workflow_name}")
            
        except Exception as e:
            self.context.status = WorkflowStatus.FAILED
            self.context.end_time = datetime.now()
            logger.error(f"工作流执行失败: {self.workflow_name}, 错误: {str(e)}")
            raise e
        
        return self.context
    
    def _execute_steps(self) -> None:
        """执行工作流步骤"""
        remaining_steps = self.steps.copy()
        
        while remaining_steps:
            # 找到可以执行的步骤
            executable_steps = [step for step in remaining_steps if step.can_execute(self.context)]
            
            if not executable_steps:
                # 检查是否有失败的必需步骤
                failed_required_steps = [
                    step.name for step in self.steps 
                    if step.status == StepStatus.FAILED and step.required
                ]
                if failed_required_steps:
                    raise RuntimeError(f"必需步骤执行失败: {', '.join(failed_required_steps)}")
                
                # 检查是否存在循环依赖
                pending_steps = [step.name for step in remaining_steps]
                raise RuntimeError(f"存在循环依赖或无法满足的依赖关系: {', '.join(pending_steps)}")
            
            # 执行可执行的步骤
            for step in executable_steps:
                try:
                    step.execute(self.context)
                except Exception as e:
                    if step.required:
                        # 必需步骤失败，终止执行
                        raise e
                    else:
                        # 可选步骤失败，继续执行
                        logger.warning(f"可选步骤执行失败，继续执行: {step.name}")
                
                # 从待执行列表中移除
                remaining_steps.remove(step)
    
    def get_step_by_name(self, step_name: str) -> Optional[WorkflowStep]:
        """根据名称获取步骤"""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        if not self.context:
            return {"error": "工作流尚未执行"}
        
        return {
            "workflow_name": self.workflow_name,
            "workflow_id": self.workflow_id,
            "status": self.context.status.value,
            "progress": self.context.get_progress(),
            "total_steps": self.context.step_count,
            "completed_steps": len(self.context.completed_steps),
            "failed_steps": len(self.context.failed_steps),
            "start_time": self.context.start_time,
            "end_time": self.context.end_time,
            "duration": (
                (self.context.end_time - self.context.start_time).total_seconds()
                if self.context.start_time and self.context.end_time
                else None
            ),
            "errors": self.context.errors
        }
