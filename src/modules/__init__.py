"""
数据处理自动化工作流应用 - 功能模块

版本：V1.0
创建日期：2025-09-06
依据文档：《技术架构设计》模块化架构
框架：功能模块统一导出

功能模块层，提供：
1. 金融专业功能模块
2. 性能优化模块
3. 数据处理模块
4. 其他专业功能模块
"""

from .financial_professional import (
    FinancialProfessionalModule,
    FinancialIndicatorCalculator,
    TechnicalAnalysisCalculator,
    RiskAnalysisCalculator,
    PortfolioAnalyzer,
    OptionPricingCalculator,
    FinancialIndicatorType,
    RiskMetricType,
    CalculationResult,
)

from .performance_optimization import (
    PerformanceOptimizationManager,
    PerformanceMonitor,
    MemoryOptimizer,
    CacheManager,
    ResourceScheduler,
    PerformanceAnalyzer,
    PerformanceProfile,
    PerformanceMetricType,
    OptimizationStrategy,
    OptimizationRecommendation,
)

__all__ = [
    # 金融专业功能
    "FinancialProfessionalModule",
    "FinancialIndicatorCalculator",
    "TechnicalAnalysisCalculator",
    "RiskAnalysisCalculator",
    "PortfolioAnalyzer",
    "OptionPricingCalculator",
    "FinancialIndicatorType",
    "RiskMetricType",
    "CalculationResult",
    # 性能优化
    "PerformanceOptimizationManager",
    "PerformanceMonitor",
    "MemoryOptimizer",
    "CacheManager",
    "ResourceScheduler",
    "PerformanceAnalyzer",
    "PerformanceProfile",
    "PerformanceMetricType",
    "OptimizationStrategy",
    "OptimizationRecommendation",
]
