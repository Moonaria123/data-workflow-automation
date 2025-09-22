"""
数据处理自动化工作流应用 - 节点库

版本：V1.0
创建日期：2025-09-11
依据文档：《模块化开发方案》第9章节点开发手册、《节点清单_v2.md》
框架：95种节点插件库

节点库模块，提供：
1. 95种节点实现（输入17+处理40+财务8+输出20+工具10）
2. 统一节点插件接口
3. 节点注册与发现机制
4. 节点执行沙箱环境
"""

from typing import Dict, List, Type, Optional
import logging
from pathlib import Path

from ..engine.contracts import NodePlugin, NodeInfo
from ..common.contracts import NodeType

# 节点注册表
_node_registry: Dict[str, Type[NodePlugin]] = {}

logger = logging.getLogger(__name__)


def register_node(node_class: Type[NodePlugin]) -> None:
    """注册节点插件"""
    if not issubclass(node_class, NodePlugin):
        raise ValueError(f"节点类 {node_class.__name__} 必须继承自 NodePlugin")

    # 创建实例获取节点信息
    instance = node_class()
    node_info = instance.node_info

    if node_info.node_id in _node_registry:
        logger.warning(f"节点 {node_info.node_id} 已存在，将被覆盖")

    _node_registry[node_info.node_id] = node_class
    logger.debug(f"注册节点插件：{node_info.name} ({node_info.node_id})")


def get_node_class(node_id: str) -> Optional[Type[NodePlugin]]:
    """获取节点类"""
    return _node_registry.get(node_id)


def get_available_nodes() -> List[NodeInfo]:
    """获取所有可用节点信息"""
    nodes = []
    for node_class in _node_registry.values():
        try:
            instance = node_class()
            nodes.append(instance.node_info)
        except Exception as e:
            logger.error(f"获取节点信息失败 {node_class.__name__}: {e}")
    
    return nodes


def get_nodes_by_type(node_type: NodeType) -> List[NodeInfo]:
    """根据类型获取节点列表"""
    nodes = []
    for node_class in _node_registry.values():
        try:
            instance = node_class()
            if instance.node_info.node_type == node_type:
                nodes.append(instance.node_info)
        except Exception as e:
            logger.error(f"获取节点信息失败 {node_class.__name__}: {e}")
    
    return nodes


def get_all_registered_nodes() -> Dict[str, NodeInfo]:
    """获取所有已注册节点的信息字典"""
    nodes = {}
    for node_id, node_class in _node_registry.items():
        try:
            instance = node_class()
            nodes[node_id] = instance.node_info
        except Exception as e:
            logger.error(f"获取节点信息失败 {node_class.__name__}: {e}")
    
    return nodes


def load_all_nodes() -> None:
    """加载所有节点插件"""
    logger.info("开始加载节点插件...")
    
    try:
        # 导入输入节点模块 - 自动注册17个输入节点
        from . import input
        
        # 导入处理节点模块 - 自动注册40个处理节点
        from . import processing
        
        # 导入输出节点模块 - 自动注册20个输出节点
        from . import output
        
        # 导入财务节点模块 - 自动注册8个财务节点
        from . import finance
        
        # 导入工具节点模块 - 自动注册10个工具节点
        from . import tools
        
        # 导入可视化节点模块 - 分析和图表节点
        from . import visualization
        from . import analysis
        
        logger.info(f"节点插件加载完成，共 {len(_node_registry)} 个节点")
        
    except ImportError as e:
        logger.error(f"加载节点模块失败: {e}")
        # 如果无法加载某些模块，继续加载其他模块
    except Exception as e:
        logger.error(f"节点插件加载异常: {e}")


# 自动加载节点
# load_all_nodes()

__all__ = [
    "register_node",
    "get_node_class", 
    "get_available_nodes",
    "get_nodes_by_type",
    "get_all_registered_nodes",
    "load_all_nodes",
]
