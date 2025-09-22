"""
数据工作流自动化项目 - 数据层模块

版本：V1.0
创建日期：2025-09-21
依据文档：《8层架构设计》数据层规范

数据层负责：
1. 数据模型定义和管理
2. 数据持久化操作
3. 数据验证和转换
4. 数据缓存和索引
5. 数据生命周期管理
"""

import logging
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
import json

# 配置日志
logger = logging.getLogger(__name__)

# 数据类型定义
DataValue = Union[str, int, float, bool, list, dict, None]
DataRow = Dict[str, DataValue]
DataSet = List[DataRow]

@dataclass
class DataSchema:
    """数据模式定义"""
    name: str
    fields: Dict[str, str]  # field_name -> field_type
    required_fields: List[str]
    validation_rules: Dict[str, Any]
    created_at: datetime
    version: str = "1.0"

@dataclass
class DataMetadata:
    """数据元数据"""
    source: str
    created_at: datetime
    row_count: int
    column_count: int
    schema: Optional[DataSchema] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class DataInterface(ABC):

    @abstractmethod
    def read(self, source: str, **kwargs) -> DataSet:
        pass

    @abstractmethod
    def write(self, data: DataSet, destination: str, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def validate(self, data: DataSet, schema: DataSchema) -> bool:
        pass

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataProcessor")
    
    def transform(self, data: DataSet, transformations: List[Dict[str, Any]]) -> DataSet:
        try:
            result = data.copy()
            # 循环处理逻辑
            for transform in transformations:
                result = self._apply_transformation(result, transform)
            return result
        except Exception as e:
            self.logger.error(f"数据转换失败: {str(e)}")
            raise
    
    def _apply_transformation(self, data: DataSet, transform: Dict[str, Any]) -> DataSet:
        transform_type = transform.get('type', '')
        
        # 复杂条件判断逻辑
        if transform_type == 'filter':
            return self._filter_data(data, transform.get('condition', {}))
        elif transform_type == 'map':
            return self._map_data(data, transform.get('mapping', {}))
        elif transform_type == 'aggregate':
            return self._aggregate_data(data, transform.get('group_by', []), transform.get('aggregations', {}))
        else:
            self.logger.warning(f"未知的转换类型: {transform_type}")
            return data
    
    def _filter_data(self, data: DataSet, condition: Dict[str, Any]) -> DataSet:
        # 简化的过滤实现
        return [row for row in data if self._evaluate_condition(row, condition)]
    
    def _map_data(self, data: DataSet, mapping: Dict[str, str]) -> DataSet:
        result = []
        # 循环处理逻辑
        for row in data:
            new_row = {}
            # 循环处理逻辑
            for old_field, new_field in mapping.items():
                if old_field in row:
                    new_row[new_field] = row[old_field]
            result.append(new_row)
        return result
    
    def _aggregate_data(self, data: DataSet, group_by: List[str], aggregations: Dict[str, str]) -> DataSet:
        # 简化的聚合实现
        if not group_by:
            return data
        
        groups = {}
        # 循环处理逻辑
        for row in data:
            key = tuple(row.get(field, '') for field in group_by)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)
        
        result = []
        for key, group_data in groups.items():
            agg_row = {}
            for i, field in enumerate(group_by):
                agg_row[field] = key[i]
            
            for field, agg_type in aggregations.items():
                if agg_type == 'count':
                    agg_row[f"{field}_count"] = len(group_data)
                elif agg_type == 'sum':
                    agg_row[f"{field}_sum"] = sum(row.get(field, 0) for row in group_data)
                elif agg_type == 'avg':
                    values = [row.get(field, 0) for row in group_data]
                    agg_row[f"{field}_avg"] = sum(values) / len(values) if values else 0
            
            result.append(agg_row)
        
        return result
    
    def _evaluate_condition(self, row: DataRow, condition: Dict[str, Any]) -> bool:
        # 简化的条件评估
        for field, expected in condition.items():
            if field not in row:
                return False
            if row[field] != expected:
                return False
        return True

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataValidator")
    
    def validate_schema(self, data: DataSet, schema: DataSchema) -> Dict[str, Any]:
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            if not data:
                validation_result['errors'].append("数据集为空")
                validation_result['valid'] = False
                return validation_result
            
            # 检查必需字段
            for row_idx, row in enumerate(data):
                for required_field in schema.required_fields:
                    if required_field not in row or row[required_field] is None:
                        validation_result['errors'].append(
                            f"第{row_idx + 1}行缺少必需字段: {required_field}"
                        )
                        validation_result['valid'] = False
                
                # 检查字段类型
                for field, expected_type in schema.fields.items():
                    if field in row and row[field] is not None:
                        if not self._validate_field_type(row[field], expected_type):
                            validation_result['errors'].append(
                                f"第{row_idx + 1}行字段{field}类型错误，期望: {expected_type}"
                            )
                            validation_result['valid'] = False
            
        except Exception as e:
            self.logger.error(f"数据验证失败: {str(e)}")
            validation_result['valid'] = False
            validation_result['errors'].append(f"验证过程异常: {str(e)}")
        
        return validation_result
    
    def _validate_field_type(self, value: DataValue, expected_type: str) -> bool:
        type_map = {
            'string': str,
            'integer': int,
            'float': float,
            'boolean': bool,
            'list': list,
            'dict': dict
        }
        
        expected_python_type = type_map.get(expected_type.lower())
        if expected_python_type is None:
            return True  # 未知类型通过验证
        
        return isinstance(value, expected_python_type)

class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, max_size: int = 1000):
        """初始化数据缓存管理器
        
        Args:
            max_size: 缓存最大条目数
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.access_order = []
        self.logger = logging.getLogger(f"{__name__}.DataCache")
    
    def get(self, key: str) -> Optional[DataSet]:
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]['data']
        return None
    
    def put(self, key: str, data: DataSet, metadata: Optional[DataMetadata] = None) -> None:
        # 检查缓存大小限制
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_oldest()
        
        self.cache[key] = {
            'data': data,
            'metadata': metadata,
            'cached_at': datetime.now()
        }
        
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        self.logger.debug(f"缓存数据: {key}, 行数: {len(data)}")
    
    def remove(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)
            return True
        return False
    
    def clear(self) -> None:
        self.cache.clear()
        self.access_order.clear()
        self.logger.info("缓存已清空")
    
    def _evict_oldest(self) -> None:
        if self.access_order:
            oldest_key = self.access_order[0]
            self.remove(oldest_key)
            self.logger.debug(f"淘汰最旧缓存: {oldest_key}")

# 全局实例
default_processor = DataProcessor()
default_validator = DataValidator()
default_cache = DataCache()

# 导出的公共接口
__all__ = [
    'DataValue',
    'DataRow', 
    'DataSet',
    'DataSchema',
    'DataMetadata',
    'DataInterface',
    'DataProcessor',
    'DataValidator',
    'DataCache',
    'default_processor',
    'default_validator',
    'default_cache'
]
