"""
数据处理自动化工作流应用 - 节点基础类

版本：V1.0
创建日期：2025-09-11
依据文档：《模块化开发方案》第5章核心接口定义、《引擎合约接口》
框架：节点插件基础抽象类

节点基础类，提供：
1. 统一的NodePlugin实现基础
2. 通用的参数验证机制
3. 标准的错误处理流程
4. 性能监控和资源控制
"""

import time
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

try:
    import polars as pl
    DataFrame = pl.DataFrame
except ImportError:
    DataFrame = Any

from ..engine.contracts import (
    NodePlugin, NodeInfo, ExecutionResult, ExecutionContext, 
    ValidationResult, ParameterInfo, PortInfo, PortType
)
from ..common.contracts import NodeType


class BaseNodePlugin(NodePlugin):
    """
    节点插件基础类
    
    提供通用的节点实现基础，所有具体节点应继承此类
    按照《模块化开发方案》第9章NodePlugin模板规范实现
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._node_info: Optional[NodeInfo] = None
    
    @property
    def node_info(self) -> NodeInfo:
        """获取节点信息（缓存）"""
        if self._node_info is None:
            # 将PortInfo列表转换为字符串列表
            input_ports = self.get_input_ports()
            output_ports = self.get_output_ports()
            
            # 处理端口信息类型转换
            if input_ports and hasattr(input_ports[0], 'name'):
                input_port_names = [port.name for port in input_ports]
            else:
                input_port_names = input_ports if isinstance(input_ports, list) else []
                
            if output_ports and hasattr(output_ports[0], 'name'):
                output_port_names = [port.name for port in output_ports]
            else:
                output_port_names = output_ports if isinstance(output_ports, list) else []
            
            self._node_info = NodeInfo(
                node_id=self.get_node_id(),
                name=self.get_display_name(),
                description=self.get_description(),
                node_type=self.get_node_type(),
                category=self.get_category(),
                version=self.get_version(),
                author=self.get_author(),
                input_ports=input_port_names,
                output_ports=output_port_names,
                parameters=self.get_parameter_definitions(),
                tags=self.get_tags(),
                icon=self.get_icon()
            )
        return self._node_info
    
    @abstractmethod
    def get_node_id(self) -> str:
        """获取节点唯一ID"""
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """获取节点显示名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取节点功能描述"""
        pass
    
    @abstractmethod
    def get_node_type(self) -> NodeType:
        """获取节点类型"""
        pass
    
    def get_category(self) -> str:
        """获取节点分类"""
        return self.get_node_type().value
    
    def get_version(self) -> str:
        """获取节点版本"""
        return "1.0.0"
    
    def get_author(self) -> str:
        """获取节点作者"""
        return "DWA Team"
    
    def get_tags(self) -> List[str]:
        """获取节点标签"""
        return [self.get_category()]
    
    def get_icon(self) -> Optional[str]:
        """获取节点图标"""
        return None
    
    @abstractmethod
    def get_input_ports(self) -> List[PortInfo]:
        """获取输入端口定义"""
        pass
    
    @abstractmethod
    def get_output_ports(self) -> List[PortInfo]:
        """获取输出端口定义"""
        pass
    
    @abstractmethod
    def get_parameter_definitions(self) -> List[ParameterInfo]:
        """获取参数定义"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any], context: ExecutionContext) -> ValidationResult:
        """验证参数"""
        errors = []
        warnings = []
        
        param_defs = self.get_parameter_definitions()
        param_dict = {p.name: p for p in param_defs}
        
        # 检查必需参数
        for param_def in param_defs:
            if param_def.required and param_def.name not in parameters:
                errors.append(f"缺少必需参数: {param_def.name}")
        
        # 验证参数值
        for param_name, param_value in parameters.items():
            if param_name in param_dict:
                param_def = param_dict[param_name]
                try:
                    self._validate_parameter_value(param_def, param_value)
                except ValueError as e:
                    errors.append(f"参数 {param_name} 验证失败: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_parameter_value(self, param_def: ParameterInfo, value: Any) -> None:
        """验证单个参数值"""
        if value is None and param_def.required:
            raise ValueError("参数不能为空")
        
        if value is None:
            return
        
        # 类型验证
        param_type = param_def.parameter_type
        if param_type == "text" and not isinstance(value, str):
            raise ValueError("参数必须是字符串类型")
        elif param_type == "number" and not isinstance(value, (int, float)):
            raise ValueError("参数必须是数值类型")
        elif param_type == "boolean" and not isinstance(value, bool):
            raise ValueError("参数必须是布尔类型")
        
        # 自定义验证规则
        if hasattr(param_def, 'validation_rules') and param_def.validation_rules:
            for rule_name, rule_value in param_def.validation_rules.items():
                if rule_name == "min_length" and len(str(value)) < rule_value:
                    raise ValueError(f"参数长度不能小于 {rule_value}")
                elif rule_name == "max_length" and len(str(value)) > rule_value:
                    raise ValueError(f"参数长度不能大于 {rule_value}")
                elif rule_name == "min_value" and float(value) < rule_value:
                    raise ValueError(f"参数值不能小于 {rule_value}")
                elif rule_name == "max_value" and float(value) > rule_value:
                    raise ValueError(f"参数值不能大于 {rule_value}")
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any], parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """执行节点逻辑"""
        pass
    
    def create_success_result(self, outputs: Dict[str, Any], execution_time: float = 0.0, 
                            memory_usage: int = 0) -> ExecutionResult:
        """创建成功结果"""
        return ExecutionResult(
            success=True,
            node_id=self.get_node_id(),
            outputs=outputs,
            execution_time=execution_time,
            memory_usage=memory_usage,
            error_message="",
            logs=[]
        )
    
    def create_error_result(self, error_message: str, execution_time: float = 0.0) -> ExecutionResult:
        """创建错误结果"""
        return ExecutionResult(
            success=False,
            node_id=self.get_node_id(),
            outputs={},
            execution_time=execution_time,
            memory_usage=0,
            error_message=error_message,
            logs=[]
        )
    
    def log_execution_start(self, parameters: Dict[str, Any]) -> None:
        """记录执行开始"""
        self.logger.info(f"节点 {self.get_display_name()} 开始执行")
        self.logger.debug(f"执行参数: {parameters}")
    
    def log_execution_end(self, result: ExecutionResult) -> None:
        """记录执行结束"""
        if result.success:
            self.logger.info(f"节点 {self.get_display_name()} 执行成功，耗时 {result.execution_time:.2f}秒")
        else:
            self.logger.error(f"节点 {self.get_display_name()} 执行失败: {result.error_message}")
