"""
数据处理自动化工作流应用 - 工具库

版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》工具层
框架：通用工具和优化组件

工具库模块，提供：
1. 性能监控和优化
2. 资源管理和优化
3. UI响应优化
4. 用户体验优化
5. 懒加载和启动优化
"""

from .performance_monitor import PerformanceMonitor, MemoryMonitor, ExecutionTimer
from .resource_optimizer import ResourceOptimizer, MemoryOptimizer, ThreadPoolOptimizer
from .ui_performance_monitor import UIPerformanceMonitor, RenderingMetrics, InteractionMetrics
from .ui_response_optimizer import UIResponseOptimizer, ComponentOptimizer, EventOptimizer
from .user_experience_optimizer import UserExperienceOptimizer, InteractionOptimizer
from .startup_optimizer import StartupOptimizer, ModuleLoadOptimizer, ConfigurationOptimizer
from .lazy_imports import LazyImportManager, ImportOptimizer
from .runtime_optimizer import RuntimeOptimizer, ExecutionOptimizer, DataFlowOptimizer

__all__ = [
    # 性能监控
    "PerformanceMonitor",
    "MemoryMonitor", 
    "ExecutionTimer",
    # 资源优化
    "ResourceOptimizer",
    "MemoryOptimizer",
    "ThreadPoolOptimizer",
    # UI性能优化
    "UIPerformanceMonitor",
    "RenderingMetrics",
    "InteractionMetrics",
    "UIResponseOptimizer",
    "ComponentOptimizer",
    "EventOptimizer",
    # 用户体验优化
    "UserExperienceOptimizer",
    "InteractionOptimizer",
    # 启动优化
    "StartupOptimizer",
    "ModuleLoadOptimizer",
    "ConfigurationOptimizer",
    # 懒加载优化
    "LazyImportManager",
    "ImportOptimizer",
    # 运行时优化
    "RuntimeOptimizer",
    "ExecutionOptimizer",
    "DataFlowOptimizer",
]

__version__ = "1.0.0"
__author__ = "Data Workflow Automation Team"
__description__ = "Utility tools and optimization components"
