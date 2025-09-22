"""
数据处理自动化工作流应用 - 性能优化模块

版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》性能优化、《模块化开发方案》性能监控
框架：性能监控、优化和调优

性能优化模块，提供：
1. 性能监控和指标收集
2. 内存管理和优化
3. 计算资源调度优化
4. 缓存策略和管理
5. 并发执行优化
6. 性能分析和建议
"""

import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import gc
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import weakref
from collections import defaultdict, deque
import statistics


class PerformanceMetricType(Enum):
    """性能指标类型"""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    EXECUTION_TIME = "execution_time"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"
    CONCURRENT_TASKS = "concurrent_tasks"


class OptimizationStrategy(Enum):
    """优化策略"""

    MEMORY_OPTIMIZATION = "memory_optimization"
    CPU_OPTIMIZATION = "cpu_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    PARALLEL_OPTIMIZATION = "parallel_optimization"
    RESOURCE_BALANCING = "resource_balancing"


@dataclass
class PerformanceMetric:
    """性能指标"""

    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceProfile:
    """性能配置文件"""

    profile_name: str
    cpu_cores: int
    memory_limit_mb: int
    cache_size_mb: int
    thread_pool_size: int
    process_pool_size: int
    enable_parallel: bool = True
    enable_caching: bool = True
    gc_threshold: int = 1000
    metrics_interval: int = 5


@dataclass
class OptimizationRecommendation:
    """优化建议"""

    strategy: OptimizationStrategy
    description: str
    expected_improvement: float
    implementation_complexity: str
    priority: int
    details: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, monitoring_interval: int = 5):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitor_thread = None

        # 性能指标存储
        self.metrics_history: Dict[PerformanceMetricType, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )

        # 系统信息
        self.system_info = self._get_system_info()

        # 监控回调
        self.metric_callbacks: List[Callable[[PerformanceMetric], None]] = []

        # 性能阈值
        self.thresholds = {
            PerformanceMetricType.CPU_USAGE: 80.0,
            PerformanceMetricType.MEMORY_USAGE: 85.0,
            PerformanceMetricType.ERROR_RATE: 5.0,
        }

    def start_monitoring(self):
        """开始性能监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitor_thread.start()
            self.logger.info("性能监控已启动")

    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.logger.info("性能监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                self._collect_system_metrics()

                # 等待下一次监控
                time.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"性能监控错误: {e}")

    def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            timestamp = datetime.now()

            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._record_metric(PerformanceMetricType.CPU_USAGE, cpu_percent, timestamp)

            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self._record_metric(
                PerformanceMetricType.MEMORY_USAGE, memory_percent, timestamp
            )

            # 进程特定指标
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            self._record_metric(
                PerformanceMetricType.MEMORY_USAGE,
                process_memory,
                timestamp,
                context={"type": "process"},
            )

        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")

    def _record_metric(
        self,
        metric_type: PerformanceMetricType,
        value: float,
        timestamp: datetime,
        context: Optional[Dict[str, Any]] = None,
    ):
        """记录性能指标"""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            context=context or {},
        )

        # 存储指标
        self.metrics_history[metric_type].append(metric)

        # 检查阈值
        self._check_threshold(metric)

        # 触发回调
        for callback in self.metric_callbacks:
            try:
                callback(metric)
            except Exception as e:
                self.logger.error(f"性能指标回调执行失败: {e}")

    def _check_threshold(self, metric: PerformanceMetric):
        """检查性能阈值"""
        threshold = self.thresholds.get(metric.metric_type)
        if threshold and metric.value > threshold:
            self.logger.warning(
                f"性能指标超过阈值: {metric.metric_type.value} = {metric.value} > {threshold}"
            )

    def record_execution_time(
        self,
        operation: str,
        execution_time: float,
        context: Optional[Dict[str, Any]] = None,
    ):
        """记录执行时间"""
        self._record_metric(
            PerformanceMetricType.EXECUTION_TIME,
            execution_time,
            datetime.now(),
            context={"operation": operation, **(context or {})},
        )

    def record_throughput(
        self,
        operation: str,
        items_processed: int,
        time_window: float,
        context: Optional[Dict[str, Any]] = None,
    ):
        """记录吞吐量"""
        throughput = items_processed / time_window if time_window > 0 else 0
        self._record_metric(
            PerformanceMetricType.THROUGHPUT,
            throughput,
            datetime.now(),
            context={
                "operation": operation,
                "items": items_processed,
                **(context or {}),
            },
        )

    def get_metric_statistics(
        self,
        metric_type: PerformanceMetricType,
        time_window: Optional[timedelta] = None,
    ) -> Dict[str, float]:
        """获取指标统计"""
        try:
            metrics = self.metrics_history[metric_type]

            if time_window:
                cutoff_time = datetime.now() - time_window
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]

            if not metrics:
                return {}

            values = [m.value for m in metrics]

            return {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            }

        except Exception as e:
            self.logger.error(f"获取指标统计失败: {e}")
            return {}

    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total": psutil.virtual_memory().total,
                "platform": sys.platform,
                "python_version": sys.version,
            }
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}

    def add_metric_callback(self, callback: Callable[[PerformanceMetric], None]):
        """添加指标回调"""
        self.metric_callbacks.append(callback)

    def remove_metric_callback(self, callback: Callable[[PerformanceMetric], None]):
        """移除指标回调"""
        try:
            self.metric_callbacks.remove(callback)
        except ValueError:
            pass


class MemoryOptimizer:
    """内存优化器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.gc_threshold = 1000
        self.object_tracking = {}
        self.memory_pools = defaultdict(list)

        # 弱引用追踪
        self.tracked_objects = weakref.WeakSet()

    def optimize_memory_usage(self):
        """优化内存使用"""
        try:
            initial_memory = psutil.Process().memory_info().rss

            # 强制垃圾回收
            collected = gc.collect()

            # 清理内存池
            self._cleanup_memory_pools()

            # 优化对象引用
            self._optimize_object_references()

            final_memory = psutil.Process().memory_info().rss
            memory_saved = initial_memory - final_memory

            self.logger.info(
                f"内存优化完成: 回收对象 {collected}, 节省内存 {memory_saved / 1024 / 1024:.2f} MB"
            )

            return {
                "objects_collected": collected,
                "memory_saved_bytes": memory_saved,
                "memory_saved_mb": memory_saved / 1024 / 1024,
            }

        except Exception as e:
            self.logger.error(f"内存优化失败: {e}")
            return {}

    def _cleanup_memory_pools(self):
        """清理内存池"""
        try:
            total_cleaned = 0
            for pool_name, pool_objects in self.memory_pools.items():
                cleaned = len(pool_objects)
                pool_objects.clear()
                total_cleaned += cleaned

            self.logger.debug(f"清理内存池: {total_cleaned} 个对象")

        except Exception as e:
            self.logger.error(f"清理内存池失败: {e}")

    def _optimize_object_references(self):
        """优化对象引用"""
        try:
            # 清理已失效的弱引用
            dead_refs = []
            for obj in self.tracked_objects:
                try:
                    # 触发垃圾回收检查
                    ref_count = sys.getrefcount(obj)
                    if ref_count <= 2:  # 只有weakref和当前引用
                        dead_refs.append(obj)
                except ReferenceError:
                    pass

            # 移除死引用
            for obj in dead_refs:
                try:
                    self.tracked_objects.remove(obj)
                except KeyError:
                    pass

            self.logger.debug(f"优化对象引用: 清理 {len(dead_refs)} 个死引用")

        except Exception as e:
            self.logger.error(f"优化对象引用失败: {e}")

    def track_object(self, obj: Any, category: str = "default"):
        """跟踪对象"""
        try:
            self.tracked_objects.add(obj)
            self.object_tracking[id(obj)] = {
                "category": category,
                "created_at": datetime.now(),
                "size": sys.getsizeof(obj),
            }
        except Exception as e:
            self.logger.error(f"跟踪对象失败: {e}")

    def get_memory_usage_report(self) -> Dict[str, Any]:
        """获取内存使用报告"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            # 按类别统计对象
            category_stats = defaultdict(lambda: {"count": 0, "total_size": 0})
            for obj_id, info in self.object_tracking.items():
                category = info["category"]
                category_stats[category]["count"] += 1
                category_stats[category]["total_size"] += info["size"]

            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "tracked_objects": len(self.object_tracking),
                "gc_counts": gc.get_count(),
                "category_stats": dict(category_stats),
            }

        except Exception as e:
            self.logger.error(f"获取内存使用报告失败: {e}")
            return {}

    def configure_gc(
        self, generation0: int = 700, generation1: int = 10, generation2: int = 10
    ):
        """配置垃圾回收"""
        try:
            gc.set_threshold(generation0, generation1, generation2)
            self.logger.info(
                f"垃圾回收阈值已设置: {generation0}, {generation1}, {generation2}"
            )
        except Exception as e:
            self.logger.error(f"配置垃圾回收失败: {e}")


class CacheManager:
    """缓存管理器"""

    def __init__(self, max_size_mb: int = 100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0

        # 多级缓存
        self.l1_cache = {}  # 最近使用
        self.l2_cache = {}  # 频繁使用
        self.cache_stats = defaultdict(int)

        # 访问统计
        self.access_counts = defaultdict(int)
        self.access_times = defaultdict(float)

        # LRU链表
        self.lru_order = deque()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        try:
            # L1缓存命中
            if key in self.l1_cache:
                self._update_access_stats(key, hit=True, level=1)
                self._update_lru_order(key)
                return self.l1_cache[key]

            # L2缓存命中
            if key in self.l2_cache:
                self._update_access_stats(key, hit=True, level=2)
                # 提升到L1缓存
                value = self.l2_cache.pop(key)
                self.l1_cache[key] = value
                self._update_lru_order(key)
                return value

            # 缓存未命中
            self._update_access_stats(key, hit=False)
            return None

        except Exception as e:
            self.logger.error(f"获取缓存失败 {key}: {e}")
            return None

    def put(self, key: str, value: Any, priority: int = 1):
        """放入缓存"""
        try:
            value_size = sys.getsizeof(value)

            # 检查空间
            if not self._ensure_space(value_size):
                self.logger.warning(f"缓存空间不足，无法存储: {key}")
                return False

            # 根据优先级选择缓存级别
            if priority >= 2:
                self.l1_cache[key] = value
            else:
                self.l2_cache[key] = value

            self.current_size += value_size
            self._update_lru_order(key)

            self.cache_stats["puts"] += 1
            self.logger.debug(f"缓存存储: {key} ({value_size} bytes)")

            return True

        except Exception as e:
            self.logger.error(f"存储缓存失败 {key}: {e}")
            return False

    def _ensure_space(self, needed_size: int) -> bool:
        """确保有足够空间"""
        while self.current_size + needed_size > self.max_size_bytes:
            if not self._evict_least_recently_used():
                return False
        return True

    def _evict_least_recently_used(self) -> bool:
        """驱逐最近最少使用的项"""
        try:
            if not self.lru_order:
                return False

            # 从最旧的开始驱逐
            lru_key = self.lru_order.popleft()

            # 从缓存中移除
            evicted_size = 0
            if lru_key in self.l1_cache:
                evicted_size = sys.getsizeof(self.l1_cache.pop(lru_key))
            elif lru_key in self.l2_cache:
                evicted_size = sys.getsizeof(self.l2_cache.pop(lru_key))

            self.current_size -= evicted_size
            self.cache_stats["evictions"] += 1

            self.logger.debug(f"驱逐缓存项: {lru_key} ({evicted_size} bytes)")
            return True

        except Exception as e:
            self.logger.error(f"驱逐缓存项失败: {e}")
            return False

    def _update_lru_order(self, key: str):
        """更新LRU顺序"""
        # 移除旧位置
        try:
            self.lru_order.remove(key)
        except ValueError:
            pass

        # 添加到末尾（最新）
        self.lru_order.append(key)

    def _update_access_stats(self, key: str, hit: bool, level: int = 0):
        """更新访问统计"""
        self.access_counts[key] += 1
        self.access_times[key] = time.time()

        if hit:
            self.cache_stats["hits"] += 1
            self.cache_stats[f"l{level}_hits"] += 1
        else:
            self.cache_stats["misses"] += 1

    def get_cache_statistics(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_accesses = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            (self.cache_stats["hits"] / total_accesses * 100)
            if total_accesses > 0
            else 0
        )

        return {
            "hit_rate": hit_rate,
            "total_accesses": total_accesses,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "l1_hits": self.cache_stats["l1_hits"],
            "l2_hits": self.cache_stats["l2_hits"],
            "evictions": self.cache_stats["evictions"],
            "puts": self.cache_stats["puts"],
            "current_size_mb": self.current_size / 1024 / 1024,
            "max_size_mb": self.max_size_bytes / 1024 / 1024,
            "utilization": (
                (self.current_size / self.max_size_bytes * 100)
                if self.max_size_bytes > 0
                else 0
            ),
            "l1_items": len(self.l1_cache),
            "l2_items": len(self.l2_cache),
        }

    def clear(self):
        """清空缓存"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.lru_order.clear()
        self.current_size = 0
        self.access_counts.clear()
        self.access_times.clear()
        self.cache_stats.clear()

        self.logger.info("缓存已清空")


class ResourceScheduler:
    """资源调度器"""

    def __init__(self, performance_profile: PerformanceProfile):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.profile = performance_profile

        # 线程池
        self.thread_pool = ThreadPoolExecutor(
            max_workers=performance_profile.thread_pool_size,
            thread_name_prefix="DWA-Worker",
        )

        # 进程池
        self.process_pool = (
            ProcessPoolExecutor(max_workers=performance_profile.process_pool_size)
            if performance_profile.enable_parallel
            else None
        )

        # 资源使用统计
        self.resource_stats = {
            "active_threads": 0,
            "active_processes": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
        }

        # 任务队列
        self.task_queue = deque()
        self.priority_queue = deque()

        # 资源锁
        self.resource_lock = threading.Lock()

    def submit_task(
        self,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict = None,
        priority: int = 1,
        use_process: bool = False,
    ):
        """提交任务"""
        try:
            kwargs = kwargs or {}

            if use_process and self.process_pool and self.profile.enable_parallel:
                future = self.process_pool.submit(func, *args, **kwargs)
                with self.resource_lock:
                    self.resource_stats["active_processes"] += 1
            else:
                future = self.thread_pool.submit(func, *args, **kwargs)
                with self.resource_lock:
                    self.resource_stats["active_threads"] += 1

            # 添加完成回调
            future.add_done_callback(self._task_completed)

            self.logger.debug(f"任务已提交: {'进程' if use_process else '线程'} 模式")
            return future

        except Exception as e:
            self.logger.error(f"提交任务失败: {e}")
            with self.resource_lock:
                self.resource_stats["failed_tasks"] += 1
            return None

    def _task_completed(self, future):
        """任务完成回调"""
        try:
            with self.resource_lock:
                if future.exception():
                    self.resource_stats["failed_tasks"] += 1
                else:
                    self.resource_stats["completed_tasks"] += 1

                # 更新活跃计数（简化处理）
                if self.resource_stats["active_threads"] > 0:
                    self.resource_stats["active_threads"] -= 1
                if self.resource_stats["active_processes"] > 0:
                    self.resource_stats["active_processes"] -= 1

        except Exception as e:
            self.logger.error(f"任务完成回调失败: {e}")

    def get_resource_utilization(self) -> Dict[str, float]:
        """获取资源利用率"""
        try:
            with self.resource_lock:
                thread_utilization = (
                    self.resource_stats["active_threads"]
                    / self.profile.thread_pool_size
                    * 100
                )

                process_utilization = 0
                if self.profile.process_pool_size > 0:
                    process_utilization = (
                        self.resource_stats["active_processes"]
                        / self.profile.process_pool_size
                        * 100
                    )

                return {
                    "thread_utilization": thread_utilization,
                    "process_utilization": process_utilization,
                    "total_tasks": (
                        self.resource_stats["completed_tasks"]
                        + self.resource_stats["failed_tasks"]
                    ),
                    "success_rate": (
                        self.resource_stats["completed_tasks"]
                        / max(
                            1,
                            self.resource_stats["completed_tasks"]
                            + self.resource_stats["failed_tasks"],
                        )
                        * 100
                    ),
                }

        except Exception as e:
            self.logger.error(f"获取资源利用率失败: {e}")
            return {}

    def shutdown(self, wait: bool = True):
        """关闭调度器"""
        try:
            self.thread_pool.shutdown(wait=wait)
            if self.process_pool:
                self.process_pool.shutdown(wait=wait)

            self.logger.info("资源调度器已关闭")

        except Exception as e:
            self.logger.error(f"关闭资源调度器失败: {e}")


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, monitor: PerformanceMonitor):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.monitor = monitor

    def analyze_performance(
        self, time_window: timedelta = timedelta(minutes=30)
    ) -> List[OptimizationRecommendation]:
        """分析性能并生成优化建议"""
        recommendations = []

        try:
            # 分析CPU使用情况
            cpu_recommendations = self._analyze_cpu_usage(time_window)
            recommendations.extend(cpu_recommendations)

            # 分析内存使用情况
            memory_recommendations = self._analyze_memory_usage(time_window)
            recommendations.extend(memory_recommendations)

            # 分析执行时间
            execution_recommendations = self._analyze_execution_times(time_window)
            recommendations.extend(execution_recommendations)

            # 按优先级排序
            recommendations.sort(key=lambda x: x.priority, reverse=True)

            self.logger.info(f"性能分析完成，生成 {len(recommendations)} 条建议")

        except Exception as e:
            self.logger.error(f"性能分析失败: {e}")

        return recommendations

    def _analyze_cpu_usage(
        self, time_window: timedelta
    ) -> List[OptimizationRecommendation]:
        """分析CPU使用情况"""
        recommendations = []

        try:
            cpu_stats = self.monitor.get_metric_statistics(
                PerformanceMetricType.CPU_USAGE, time_window
            )

            if not cpu_stats:
                return recommendations

            # 高CPU使用率
            if cpu_stats["mean"] > 80:
                recommendations.append(
                    OptimizationRecommendation(
                        strategy=OptimizationStrategy.CPU_OPTIMIZATION,
                        description="CPU使用率过高，建议优化计算密集型操作",
                        expected_improvement=15.0,
                        implementation_complexity="中等",
                        priority=8,
                        details={
                            "current_usage": cpu_stats["mean"],
                            "max_usage": cpu_stats["max"],
                            "suggestions": [
                                "使用更高效的算法",
                                "启用并行处理",
                                "优化循环和计算",
                            ],
                        },
                    )
                )

            # CPU使用率不稳定
            if cpu_stats.get("std_dev", 0) > 20:
                recommendations.append(
                    OptimizationRecommendation(
                        strategy=OptimizationStrategy.RESOURCE_BALANCING,
                        description="CPU使用率波动较大，建议进行负载均衡",
                        expected_improvement=10.0,
                        implementation_complexity="简单",
                        priority=5,
                        details={
                            "std_dev": cpu_stats["std_dev"],
                            "suggestions": [
                                "调整任务调度策略",
                                "优化线程池配置",
                                "实现负载均衡",
                            ],
                        },
                    )
                )

        except Exception as e:
            self.logger.error(f"分析CPU使用情况失败: {e}")

        return recommendations

    def _analyze_memory_usage(
        self, time_window: timedelta
    ) -> List[OptimizationRecommendation]:
        """分析内存使用情况"""
        recommendations = []

        try:
            memory_stats = self.monitor.get_metric_statistics(
                PerformanceMetricType.MEMORY_USAGE, time_window
            )

            if not memory_stats:
                return recommendations

            # 高内存使用率
            if memory_stats["mean"] > 85:
                recommendations.append(
                    OptimizationRecommendation(
                        strategy=OptimizationStrategy.MEMORY_OPTIMIZATION,
                        description="内存使用率过高，建议进行内存优化",
                        expected_improvement=20.0,
                        implementation_complexity="中等",
                        priority=9,
                        details={
                            "current_usage": memory_stats["mean"],
                            "max_usage": memory_stats["max"],
                            "suggestions": [
                                "启用对象池化",
                                "优化数据结构",
                                "增加垃圾回收频率",
                                "使用生成器替代列表",
                            ],
                        },
                    )
                )

            # 内存持续增长
            if memory_stats["max"] - memory_stats["min"] > 30:
                recommendations.append(
                    OptimizationRecommendation(
                        strategy=OptimizationStrategy.MEMORY_OPTIMIZATION,
                        description="检测到内存泄漏迹象，建议检查对象引用",
                        expected_improvement=25.0,
                        implementation_complexity="复杂",
                        priority=10,
                        details={
                            "memory_growth": memory_stats["max"] - memory_stats["min"],
                            "suggestions": [
                                "检查循环引用",
                                "清理未使用的对象",
                                "使用弱引用",
                                "定期执行垃圾回收",
                            ],
                        },
                    )
                )

        except Exception as e:
            self.logger.error(f"分析内存使用情况失败: {e}")

        return recommendations

    def _analyze_execution_times(
        self, time_window: timedelta
    ) -> List[OptimizationRecommendation]:
        """分析执行时间"""
        recommendations = []

        try:
            execution_stats = self.monitor.get_metric_statistics(
                PerformanceMetricType.EXECUTION_TIME, time_window
            )

            if not execution_stats:
                return recommendations

            # 执行时间过长
            if execution_stats["mean"] > 5.0:  # 5秒
                recommendations.append(
                    OptimizationRecommendation(
                        strategy=OptimizationStrategy.PARALLEL_OPTIMIZATION,
                        description="执行时间过长，建议启用并行处理",
                        expected_improvement=30.0,
                        implementation_complexity="中等",
                        priority=7,
                        details={
                            "avg_execution_time": execution_stats["mean"],
                            "max_execution_time": execution_stats["max"],
                            "suggestions": [
                                "将任务分解为并行子任务",
                                "使用异步处理",
                                "优化I/O操作",
                                "启用缓存机制",
                            ],
                        },
                    )
                )

            # 执行时间不稳定
            if execution_stats.get("std_dev", 0) > execution_stats["mean"] * 0.5:
                recommendations.append(
                    OptimizationRecommendation(
                        strategy=OptimizationStrategy.CACHE_OPTIMIZATION,
                        description="执行时间波动较大，建议优化缓存策略",
                        expected_improvement=15.0,
                        implementation_complexity="简单",
                        priority=6,
                        details={
                            "time_variation": execution_stats["std_dev"],
                            "suggestions": [
                                "增加缓存命中率",
                                "预加载常用数据",
                                "优化数据访问模式",
                            ],
                        },
                    )
                )

        except Exception as e:
            self.logger.error(f"分析执行时间失败: {e}")

        return recommendations


class PerformanceOptimizationManager:
    """性能优化管理器主类"""

    def __init__(self, performance_profile: PerformanceProfile):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.profile = performance_profile

        # 初始化各个组件
        self.monitor = PerformanceMonitor(
            monitoring_interval=performance_profile.metrics_interval
        )
        self.memory_optimizer = MemoryOptimizer()
        self.cache_manager = CacheManager(max_size_mb=performance_profile.cache_size_mb)
        self.resource_scheduler = ResourceScheduler(performance_profile)
        self.analyzer = PerformanceAnalyzer(self.monitor)

        # 自动优化配置
        self.auto_optimization_enabled = True
        self.optimization_interval = 300  # 5分钟
        self.last_optimization = datetime.now()

        self.logger.info(
            f"性能优化管理器初始化完成: {performance_profile.profile_name}"
        )

    def start(self):
        """启动性能优化管理器"""
        try:
            # 启动性能监控
            self.monitor.start_monitoring()

            # 配置垃圾回收
            self.memory_optimizer.configure_gc(
                self.profile.gc_threshold,
                self.profile.gc_threshold // 10,
                self.profile.gc_threshold // 100,
            )

            # 添加监控回调
            self.monitor.add_metric_callback(self._on_metric_received)

            self.logger.info("性能优化管理器已启动")

        except Exception as e:
            self.logger.error(f"启动性能优化管理器失败: {e}")

    def stop(self):
        """停止性能优化管理器"""
        try:
            # 停止监控
            self.monitor.stop_monitoring()

            # 关闭资源调度器
            self.resource_scheduler.shutdown()

            self.logger.info("性能优化管理器已停止")

        except Exception as e:
            self.logger.error(f"停止性能优化管理器失败: {e}")

    def _on_metric_received(self, metric: PerformanceMetric):
        """性能指标接收回调"""
        try:
            # 检查是否需要自动优化
            if (
                self.auto_optimization_enabled
                and datetime.now() - self.last_optimization
                > timedelta(seconds=self.optimization_interval)
            ):

                # 执行自动优化
                self._perform_auto_optimization()
                self.last_optimization = datetime.now()

        except Exception as e:
            self.logger.error(f"性能指标处理失败: {e}")

    def _perform_auto_optimization(self):
        """执行自动优化"""
        try:
            # 内存优化
            if self._should_optimize_memory():
                self.memory_optimizer.optimize_memory_usage()

            # 缓存优化
            cache_stats = self.cache_manager.get_cache_statistics()
            if cache_stats.get("hit_rate", 0) < 70:  # 命中率低于70%
                self.logger.info("缓存命中率较低，考虑调整缓存策略")

            self.logger.debug("自动优化执行完成")

        except Exception as e:
            self.logger.error(f"自动优化执行失败: {e}")

    def _should_optimize_memory(self) -> bool:
        """判断是否应该进行内存优化"""
        try:
            memory_stats = self.monitor.get_metric_statistics(
                PerformanceMetricType.MEMORY_USAGE, timedelta(minutes=5)
            )

            # 内存使用率超过阈值
            return memory_stats.get("mean", 0) > 80

        except Exception as e:
            self.logger.error(f"检查内存优化条件失败: {e}")
            return False

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        try:
            return {
                "profile": self.profile.profile_name,
                "monitoring": {
                    "cpu_stats": self.monitor.get_metric_statistics(
                        PerformanceMetricType.CPU_USAGE, timedelta(hours=1)
                    ),
                    "memory_stats": self.monitor.get_metric_statistics(
                        PerformanceMetricType.MEMORY_USAGE, timedelta(hours=1)
                    ),
                    "execution_stats": self.monitor.get_metric_statistics(
                        PerformanceMetricType.EXECUTION_TIME, timedelta(hours=1)
                    ),
                },
                "memory": self.memory_optimizer.get_memory_usage_report(),
                "cache": self.cache_manager.get_cache_statistics(),
                "resources": self.resource_scheduler.get_resource_utilization(),
                "recommendations": self.analyzer.analyze_performance(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"获取性能报告失败: {e}")
            return {}

    def apply_optimization_recommendations(
        self, recommendations: List[OptimizationRecommendation]
    ) -> Dict[str, bool]:
        """应用优化建议"""
        results = {}

        for recommendation in recommendations:
            try:
                success = False

                if recommendation.strategy == OptimizationStrategy.MEMORY_OPTIMIZATION:
                    self.memory_optimizer.optimize_memory_usage()
                    success = True

                elif recommendation.strategy == OptimizationStrategy.CACHE_OPTIMIZATION:
                    # 清理缓存以优化性能
                    self.cache_manager.clear()
                    success = True

                elif recommendation.strategy == OptimizationStrategy.CPU_OPTIMIZATION:
                    # CPU优化通常需要代码层面的改动，这里只是标记
                    self.logger.info(f"CPU优化建议: {recommendation.description}")
                    success = True

                results[recommendation.strategy.value] = success

            except Exception as e:
                self.logger.error(f"应用优化建议失败 {recommendation.strategy}: {e}")
                results[recommendation.strategy.value] = False

        return results