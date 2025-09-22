"""
数据处理自动化工作流应用 - 金融专业功能模块

版本：V1.0
创建日期：2025-09-06
依据文档：《功能需求分析》金融数据处理、《模块化开发方案》专业函数库
框架：金融分析和计算

金融专业功能模块，提供：
1. 财务指标计算
2. 风险评估模型
3. 投资组合分析
4. 技术分析指标
5. 期权定价模型
6. 时间序列分析
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import math
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize


class FinancialIndicatorType(Enum):
    """财务指标类型"""

    PROFITABILITY = "profitability"  # 盈利能力
    LIQUIDITY = "liquidity"  # 流动性
    LEVERAGE = "leverage"  # 杠杆
    EFFICIENCY = "efficiency"  # 效率
    VALUATION = "valuation"  # 估值
    GROWTH = "growth"  # 成长性


class RiskMetricType(Enum):
    """风险指标类型"""

    VOLATILITY = "volatility"  # 波动率
    VAR = "var"  # 风险价值
    SHARPE = "sharpe"  # 夏普比率
    BETA = "beta"  # 贝塔系数
    DRAWDOWN = "drawdown"  # 回撤
    CORRELATION = "correlation"  # 相关性


@dataclass
class FinancialData:
    """金融数据结构"""

    symbol: str
    data: pd.DataFrame
    metadata: Dict[str, Any]


@dataclass
class CalculationResult:
    """计算结果"""

    indicator: str
    value: Union[float, Dict[str, float]]
    timestamp: datetime
    metadata: Dict[str, Any]


class FinancialIndicatorCalculator:
    """财务指标计算器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_profitability_ratios(
        self, financial_data: Dict[str, float]
    ) -> Dict[str, float]:
        """计算盈利能力指标"""
        try:
            results = {}

            # 净资产收益率 (ROE)
            if (
                "net_income" in financial_data
                and "shareholders_equity" in financial_data
            ):
                roe = (
                    financial_data["net_income"] / financial_data["shareholders_equity"]
                )
                results["roe"] = roe

            # 总资产收益率 (ROA)
            if "net_income" in financial_data and "total_assets" in financial_data:
                roa = financial_data["net_income"] / financial_data["total_assets"]
                results["roa"] = roa

            # 毛利率
            if "gross_profit" in financial_data and "revenue" in financial_data:
                gross_margin = (
                    financial_data["gross_profit"] / financial_data["revenue"]
                )
                results["gross_margin"] = gross_margin

            # 净利率
            if "net_income" in financial_data and "revenue" in financial_data:
                net_margin = financial_data["net_income"] / financial_data["revenue"]
                results["net_margin"] = net_margin

            # 营业利润率
            if "operating_income" in financial_data and "revenue" in financial_data:
                operating_margin = (
                    financial_data["operating_income"] / financial_data["revenue"]
                )
                results["operating_margin"] = operating_margin

            # 息税前利润率 (EBITDA Margin)
            if "ebitda" in financial_data and "revenue" in financial_data:
                ebitda_margin = financial_data["ebitda"] / financial_data["revenue"]
                results["ebitda_margin"] = ebitda_margin

            self.logger.debug(f"计算盈利能力指标: {len(results)} 个指标")
            return results

        except Exception as e:
            self.logger.error(f"计算盈利能力指标失败: {e}")
            return {}

    def calculate_liquidity_ratios(
        self, financial_data: Dict[str, float]
    ) -> Dict[str, float]:
        """计算流动性指标"""
        try:
            results = {}

            # 流动比率
            if (
                "current_assets" in financial_data
                and "current_liabilities" in financial_data
            ):
                current_ratio = (
                    financial_data["current_assets"]
                    / financial_data["current_liabilities"]
                )
                results["current_ratio"] = current_ratio

            # 速动比率
            if (
                "current_assets" in financial_data
                and "inventory" in financial_data
                and "current_liabilities" in financial_data
            ):
                quick_assets = (
                    financial_data["current_assets"] - financial_data["inventory"]
                )
                quick_ratio = quick_assets / financial_data["current_liabilities"]
                results["quick_ratio"] = quick_ratio

            # 现金比率
            if (
                "cash_and_equivalents" in financial_data
                and "current_liabilities" in financial_data
            ):
                cash_ratio = (
                    financial_data["cash_and_equivalents"]
                    / financial_data["current_liabilities"]
                )
                results["cash_ratio"] = cash_ratio

            # 营运资金
            if (
                "current_assets" in financial_data
                and "current_liabilities" in financial_data
            ):
                working_capital = (
                    financial_data["current_assets"]
                    - financial_data["current_liabilities"]
                )
                results["working_capital"] = working_capital

            self.logger.debug(f"计算流动性指标: {len(results)} 个指标")
            return results

        except Exception as e:
            self.logger.error(f"计算流动性指标失败: {e}")
            return {}

    def calculate_leverage_ratios(
        self, financial_data: Dict[str, float]
    ) -> Dict[str, float]:
        """计算杠杆指标"""
        try:
            results = {}

            # 债务权益比
            if (
                "total_debt" in financial_data
                and "shareholders_equity" in financial_data
            ):
                debt_to_equity = (
                    financial_data["total_debt"] / financial_data["shareholders_equity"]
                )
                results["debt_to_equity"] = debt_to_equity

            # 债务资产比
            if "total_debt" in financial_data and "total_assets" in financial_data:
                debt_to_assets = (
                    financial_data["total_debt"] / financial_data["total_assets"]
                )
                results["debt_to_assets"] = debt_to_assets

            # 权益乘数
            if (
                "total_assets" in financial_data
                and "shareholders_equity" in financial_data
            ):
                equity_multiplier = (
                    financial_data["total_assets"]
                    / financial_data["shareholders_equity"]
                )
                results["equity_multiplier"] = equity_multiplier

            # 利息保障倍数
            if (
                "operating_income" in financial_data
                and "interest_expense" in financial_data
            ):
                if financial_data["interest_expense"] != 0:
                    interest_coverage = (
                        financial_data["operating_income"]
                        / financial_data["interest_expense"]
                    )
                    results["interest_coverage"] = interest_coverage

            self.logger.debug(f"计算杠杆指标: {len(results)} 个指标")
            return results

        except Exception as e:
            self.logger.error(f"计算杠杆指标失败: {e}")
            return {}

    def calculate_efficiency_ratios(
        self, financial_data: Dict[str, float]
    ) -> Dict[str, float]:
        """计算效率指标"""
        try:
            results = {}

            # 总资产周转率
            if "revenue" in financial_data and "total_assets" in financial_data:
                asset_turnover = (
                    financial_data["revenue"] / financial_data["total_assets"]
                )
                results["asset_turnover"] = asset_turnover

            # 应收账款周转率
            if "revenue" in financial_data and "accounts_receivable" in financial_data:
                receivables_turnover = (
                    financial_data["revenue"] / financial_data["accounts_receivable"]
                )
                results["receivables_turnover"] = receivables_turnover

                # 应收账款周转天数
                receivables_days = 365 / receivables_turnover
                results["receivables_days"] = receivables_days

            # 存货周转率
            if "cost_of_goods_sold" in financial_data and "inventory" in financial_data:
                inventory_turnover = (
                    financial_data["cost_of_goods_sold"] / financial_data["inventory"]
                )
                results["inventory_turnover"] = inventory_turnover

                # 存货周转天数
                inventory_days = 365 / inventory_turnover
                results["inventory_days"] = inventory_days

            # 权益周转率
            if "revenue" in financial_data and "shareholders_equity" in financial_data:
                equity_turnover = (
                    financial_data["revenue"] / financial_data["shareholders_equity"]
                )
                results["equity_turnover"] = equity_turnover

            self.logger.debug(f"计算效率指标: {len(results)} 个指标")
            return results

        except Exception as e:
            self.logger.error(f"计算效率指标失败: {e}")
            return {}


class TechnicalAnalysisCalculator:
    """技术分析指标计算器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_moving_averages(
        self, prices: pd.Series, periods: List[int]
    ) -> Dict[str, pd.Series]:
        """计算移动平均线"""
        try:
            results = {}

            for period in periods:
                # 简单移动平均 (SMA)
                sma = prices.rolling(window=period).mean()
                results[f"sma_{period}"] = sma

                # 指数移动平均 (EMA)
                ema = prices.ewm(span=period).mean()
                results[f"ema_{period}"] = ema

            self.logger.debug(f"计算移动平均线: {len(periods)} 个周期")
            return results

        except Exception as e:
            self.logger.error(f"计算移动平均线失败: {e}")
            return {}

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算相对强弱指数 (RSI)"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            self.logger.debug(f"计算RSI: 周期={period}")
            return rsi

        except Exception as e:
            self.logger.error(f"计算RSI失败: {e}")
            return pd.Series()

    def calculate_macd(
        self,
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        try:
            # 计算快慢EMA
            ema_fast = prices.ewm(span=fast_period).mean()
            ema_slow = prices.ewm(span=slow_period).mean()

            # MACD线
            macd_line = ema_fast - ema_slow

            # 信号线
            signal_line = macd_line.ewm(span=signal_period).mean()

            # 柱状图
            histogram = macd_line - signal_line

            results = {"macd": macd_line, "signal": signal_line, "histogram": histogram}

            self.logger.debug(f"计算MACD: {fast_period}-{slow_period}-{signal_period}")
            return results

        except Exception as e:
            self.logger.error(f"计算MACD失败: {e}")
            return {}

    def calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """计算布林带"""
        try:
            # 中轨（移动平均）
            middle_band = prices.rolling(window=period).mean()

            # 标准差
            std = prices.rolling(window=period).std()

            # 上轨和下轨
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)

            results = {"upper": upper_band, "middle": middle_band, "lower": lower_band}

            self.logger.debug(f"计算布林带: 周期={period}, 标准差={std_dev}")
            return results

        except Exception as e:
            self.logger.error(f"计算布林带失败: {e}")
            return {}

    def calculate_stochastic(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3,
    ) -> Dict[str, pd.Series]:
        """计算随机指标 (%K, %D)"""
        try:
            # 计算%K
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()

            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))

            # 计算%D（%K的移动平均）
            d_percent = k_percent.rolling(window=d_period).mean()

            results = {"k_percent": k_percent, "d_percent": d_percent}

            self.logger.debug(f"计算随机指标: K={k_period}, D={d_period}")
            return results

        except Exception as e:
            self.logger.error(f"计算随机指标失败: {e}")
            return {}


class RiskAnalysisCalculator:
    """风险分析计算器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_volatility(self, returns: pd.Series, period: str = "daily") -> float:
        """计算波动率"""
        try:
            # 年化因子
            annualization_factor = {
                "daily": 252,
                "weekly": 52,
                "monthly": 12,
                "quarterly": 4,
                "yearly": 1,
            }

            factor = annualization_factor.get(period, 252)
            volatility = returns.std() * np.sqrt(factor)

            self.logger.debug(f"计算波动率: {period} = {volatility:.4f}")
            return volatility

        except Exception as e:
            self.logger.error(f"计算波动率失败: {e}")
            return 0.0

    def calculate_var(
        self, returns: pd.Series, confidence_level: float = 0.05
    ) -> Dict[str, float]:
        """计算风险价值 (VaR)"""
        try:
            # 历史模拟法
            historical_var = np.percentile(returns, confidence_level * 100)

            # 参数法（假设正态分布）
            mean_return = returns.mean()
            std_return = returns.std()
            parametric_var = (
                mean_return - stats.norm.ppf(1 - confidence_level) * std_return
            )

            # 修正的Cornish-Fisher VaR
            skewness = stats.skew(returns)
            kurtosis = stats.kurtosis(returns)

            z_score = stats.norm.ppf(1 - confidence_level)
            modified_z = (
                z_score
                + (z_score**2 - 1) * skewness / 6
                + (z_score**3 - 3 * z_score) * kurtosis / 24
                - (2 * z_score**3 - 5 * z_score) * skewness**2 / 36
            )

            cornish_fisher_var = mean_return - modified_z * std_return

            results = {
                "historical_var": historical_var,
                "parametric_var": parametric_var,
                "cornish_fisher_var": cornish_fisher_var,
            }

            self.logger.debug(f"计算VaR: 置信度={1-confidence_level:.1%}")
            return results

        except Exception as e:
            self.logger.error(f"计算VaR失败: {e}")
            return {}

    def calculate_sharpe_ratio(
        self, returns: pd.Series, risk_free_rate: float = 0.0
    ) -> float:
        """计算夏普比率"""
        try:
            excess_returns = returns - risk_free_rate
            sharpe_ratio = excess_returns.mean() / returns.std()

            # 年化
            sharpe_ratio_annual = sharpe_ratio * np.sqrt(252)

            self.logger.debug(f"计算夏普比率: {sharpe_ratio_annual:.4f}")
            return sharpe_ratio_annual

        except Exception as e:
            self.logger.error(f"计算夏普比率失败: {e}")
            return 0.0

    def calculate_beta(
        self, asset_returns: pd.Series, market_returns: pd.Series
    ) -> Dict[str, float]:
        """计算贝塔系数"""
        try:
            # 确保数据长度一致
            aligned_data = pd.concat([asset_returns, market_returns], axis=1).dropna()
            asset_ret = aligned_data.iloc[:, 0]
            market_ret = aligned_data.iloc[:, 1]

            # 计算贝塔
            covariance = np.cov(asset_ret, market_ret)[0, 1]
            market_variance = np.var(market_ret)
            beta = covariance / market_variance

            # 计算相关系数
            correlation = np.corrcoef(asset_ret, market_ret)[0, 1]

            # 计算阿尔法
            asset_mean = asset_ret.mean()
            market_mean = market_ret.mean()
            alpha = asset_mean - beta * market_mean

            results = {
                "beta": beta,
                "alpha": alpha,
                "correlation": correlation,
                "r_squared": correlation**2,
            }

            self.logger.debug(f"计算贝塔: β={beta:.4f}, α={alpha:.4f}")
            return results

        except Exception as e:
            self.logger.error(f"计算贝塔失败: {e}")
            return {}

    def calculate_max_drawdown(self, prices: pd.Series) -> Dict[str, float]:
        """计算最大回撤"""
        try:
            # 计算累计收益
            cumulative = (1 + prices.pct_change()).cumprod()

            # 计算历史最高点
            running_max = cumulative.expanding().max()

            # 计算回撤
            drawdown = (cumulative - running_max) / running_max

            # 最大回撤
            max_drawdown = drawdown.min()

            # 最大回撤期间
            max_dd_date = drawdown.idxmin()
            recovery_date = None

            # 寻找恢复日期
            recovery_series = cumulative[max_dd_date:] >= running_max[max_dd_date]
            if recovery_series.any():
                recovery_date = recovery_series[recovery_series].index[0]
                drawdown_duration = (recovery_date - max_dd_date).days
            else:
                drawdown_duration = (cumulative.index[-1] - max_dd_date).days

            results = {
                "max_drawdown": max_drawdown,
                "max_drawdown_date": max_dd_date,
                "recovery_date": recovery_date,
                "duration_days": drawdown_duration,
            }

            self.logger.debug(f"计算最大回撤: {max_drawdown:.4f}")
            return results

        except Exception as e:
            self.logger.error(f"计算最大回撤失败: {e}")
            return {}


class PortfolioAnalyzer:
    """投资组合分析器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.risk_calculator = RiskAnalysisCalculator()

    def calculate_portfolio_metrics(
        self, returns: pd.DataFrame, weights: np.array
    ) -> Dict[str, float]:
        """计算投资组合指标"""
        try:
            # 投资组合收益
            portfolio_returns = (returns * weights).sum(axis=1)

            # 基本统计
            expected_return = portfolio_returns.mean() * 252  # 年化
            volatility = portfolio_returns.std() * np.sqrt(252)  # 年化

            # 夏普比率
            sharpe_ratio = self.risk_calculator.calculate_sharpe_ratio(
                portfolio_returns
            )

            # VaR
            var_results = self.risk_calculator.calculate_var(portfolio_returns)

            # 最大回撤
            cumulative_returns = (1 + portfolio_returns).cumprod()
            drawdown_results = self.risk_calculator.calculate_max_drawdown(
                cumulative_returns
            )

            results = {
                "expected_return": expected_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "var_95": var_results.get("historical_var", 0),
                "max_drawdown": drawdown_results.get("max_drawdown", 0),
                "skewness": stats.skew(portfolio_returns),
                "kurtosis": stats.kurtosis(portfolio_returns),
            }

            self.logger.debug(
                f"计算投资组合指标: 收益={expected_return:.4f}, 波动={volatility:.4f}"
            )
            return results

        except Exception as e:
            self.logger.error(f"计算投资组合指标失败: {e}")
            return {}

    def optimize_portfolio(
        self,
        returns: pd.DataFrame,
        risk_aversion: float = 1.0,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """投资组合优化"""
        try:
            n_assets = len(returns.columns)

            # 计算期望收益和协方差矩阵
            expected_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252

            # 目标函数（最大化效用）
            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                return -(portfolio_return - 0.5 * risk_aversion * portfolio_variance)

            # 约束条件
            constraints_list = []

            # 权重和为1
            constraints_list.append({"type": "eq", "fun": lambda x: np.sum(x) - 1})

            # 权重边界
            bounds = [(0, 1) for _ in range(n_assets)]

            # 自定义约束
            if constraints:
                # 最大权重约束
                if "max_weight" in constraints:
                    max_weight = constraints["max_weight"]
                    bounds = [(0, max_weight) for _ in range(n_assets)]

                # 最小权重约束
                if "min_weight" in constraints:
                    min_weight = constraints["min_weight"]
                    bounds = [(min_weight, bounds[i][1]) for i in range(n_assets)]

            # 初始权重（等权重）
            initial_weights = np.array([1 / n_assets] * n_assets)

            # 优化
            result = minimize(
                objective,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints_list,
            )

            if result.success:
                optimal_weights = result.x
                portfolio_metrics = self.calculate_portfolio_metrics(
                    returns, optimal_weights
                )

                optimization_result = {
                    "success": True,
                    "weights": optimal_weights,
                    "metrics": portfolio_metrics,
                    "optimization_info": {
                        "iterations": result.nit,
                        "function_value": -result.fun,
                    },
                }
            else:
                optimization_result = {
                    "success": False,
                    "message": result.message,
                    "weights": initial_weights,
                }

            self.logger.debug(f"投资组合优化: 成功={result.success}")
            return optimization_result

        except Exception as e:
            self.logger.error(f"投资组合优化失败: {e}")
            return {"success": False, "error": str(e)}

    def calculate_efficient_frontier(
        self, returns: pd.DataFrame, num_portfolios: int = 100
    ) -> Dict[str, np.array]:
        """计算有效前沿"""
        try:
            n_assets = len(returns.columns)
            expected_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252

            # 计算最小方差组合
            def min_variance_objective(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))

            constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
            bounds = [(0, 1) for _ in range(n_assets)]
            initial_weights = np.array([1 / n_assets] * n_assets)

            min_var_result = minimize(
                min_variance_objective,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

            min_return = np.dot(min_var_result.x, expected_returns)
            max_return = expected_returns.max()

            # 生成目标收益率序列
            target_returns = np.linspace(min_return, max_return, num_portfolios)

            efficient_portfolios = []
            portfolio_returns = []
            portfolio_volatilities = []

            for target_return in target_returns:
                # 约束条件：权重和为1，目标收益率
                constraints = [
                    {"type": "eq", "fun": lambda x: np.sum(x) - 1},
                    {
                        "type": "eq",
                        "fun": lambda x: np.dot(x, expected_returns) - target_return,
                    },
                ]

                result = minimize(
                    min_variance_objective,
                    initial_weights,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints,
                )

                if result.success:
                    weights = result.x
                    port_return = np.dot(weights, expected_returns)
                    port_volatility = np.sqrt(
                        np.dot(weights.T, np.dot(cov_matrix, weights))
                    )

                    efficient_portfolios.append(weights)
                    portfolio_returns.append(port_return)
                    portfolio_volatilities.append(port_volatility)

            frontier_results = {
                "returns": np.array(portfolio_returns),
                "volatilities": np.array(portfolio_volatilities),
                "weights": np.array(efficient_portfolios),
            }

            self.logger.debug(f"计算有效前沿: {len(portfolio_returns)} 个组合")
            return frontier_results

        except Exception as e:
            self.logger.error(f"计算有效前沿失败: {e}")
            return {}


class OptionPricingCalculator:
    """期权定价计算器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def black_scholes_price(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str = "call",
    ) -> Dict[str, float]:
        """Black-Scholes期权定价"""
        try:
            # 计算d1和d2
            d1 = (
                np.log(spot_price / strike_price)
                + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry
            ) / (volatility * np.sqrt(time_to_expiry))
            d2 = d1 - volatility * np.sqrt(time_to_expiry)

            # 标准正态分布CDF
            N_d1 = stats.norm.cdf(d1)
            N_d2 = stats.norm.cdf(d2)
            N_neg_d1 = stats.norm.cdf(-d1)
            N_neg_d2 = stats.norm.cdf(-d2)

            # 计算期权价格
            if option_type.lower() == "call":
                option_price = (
                    spot_price * N_d1
                    - strike_price * np.exp(-risk_free_rate * time_to_expiry) * N_d2
                )
            else:  # put
                option_price = (
                    strike_price * np.exp(-risk_free_rate * time_to_expiry) * N_neg_d2
                    - spot_price * N_neg_d1
                )

            # 计算希腊字母
            greeks = self._calculate_greeks(
                spot_price,
                strike_price,
                time_to_expiry,
                risk_free_rate,
                volatility,
                option_type,
                d1,
                d2,
            )

            results = {
                "option_price": option_price,
                "delta": greeks["delta"],
                "gamma": greeks["gamma"],
                "theta": greeks["theta"],
                "vega": greeks["vega"],
                "rho": greeks["rho"],
            }

            self.logger.debug(f"Black-Scholes定价: {option_type} = {option_price:.4f}")
            return results

        except Exception as e:
            self.logger.error(f"Black-Scholes定价失败: {e}")
            return {}

    def _calculate_greeks(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str,
        d1: float,
        d2: float,
    ) -> Dict[str, float]:
        """计算希腊字母"""
        try:
            # 标准正态分布PDF和CDF
            n_d1 = stats.norm.pdf(d1)
            N_d1 = stats.norm.cdf(d1)
            N_d2 = stats.norm.cdf(d2)
            N_neg_d1 = stats.norm.cdf(-d1)
            N_neg_d2 = stats.norm.cdf(-d2)

            # Delta
            if option_type.lower() == "call":
                delta = N_d1
            else:
                delta = -N_neg_d1

            # Gamma
            gamma = n_d1 / (spot_price * volatility * np.sqrt(time_to_expiry))

            # Theta
            theta_term1 = -(spot_price * n_d1 * volatility) / (
                2 * np.sqrt(time_to_expiry)
            )
            theta_term2 = (
                risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry)
            )

            if option_type.lower() == "call":
                theta = theta_term1 - theta_term2 * N_d2
            else:
                theta = theta_term1 + theta_term2 * N_neg_d2

            theta = theta / 365  # 转换为每日theta

            # Vega
            vega = (
                spot_price * n_d1 * np.sqrt(time_to_expiry) / 100
            )  # 转换为1%波动率变化的影响

            # Rho
            if option_type.lower() == "call":
                rho = (
                    strike_price
                    * time_to_expiry
                    * np.exp(-risk_free_rate * time_to_expiry)
                    * N_d2
                    / 100
                )
            else:
                rho = (
                    -strike_price
                    * time_to_expiry
                    * np.exp(-risk_free_rate * time_to_expiry)
                    * N_neg_d2
                    / 100
                )

            return {
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega,
                "rho": rho,
            }

        except Exception as e:
            self.logger.error(f"计算希腊字母失败: {e}")
            return {}

    def implied_volatility(
        self,
        market_price: float,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str = "call",
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> float:
        """计算隐含波动率"""
        try:
            # 使用牛顿-拉夫逊方法
            volatility = 0.2  # 初始猜测值

            for i in range(max_iterations):
                # 计算当前波动率下的期权价格
                bs_result = self.black_scholes_price(
                    spot_price,
                    strike_price,
                    time_to_expiry,
                    risk_free_rate,
                    volatility,
                    option_type,
                )

                if not bs_result:
                    break

                theoretical_price = bs_result["option_price"]
                vega = bs_result["vega"] * 100  # 转换回原始vega

                # 价格差异
                price_diff = theoretical_price - market_price

                # 检查收敛
                if abs(price_diff) < tolerance:
                    self.logger.debug(
                        f"隐含波动率收敛: {volatility:.4f}, 迭代次数: {i+1}"
                    )
                    return volatility

                # 更新波动率
                if vega != 0:
                    volatility = volatility - price_diff / vega
                    volatility = max(0.001, min(5.0, volatility))  # 限制范围
                else:
                    break

            self.logger.warning(f"隐含波动率未收敛，返回最后值: {volatility:.4f}")
            return volatility

        except Exception as e:
            self.logger.error(f"计算隐含波动率失败: {e}")
            return 0.0


class FinancialProfessionalModule:
    """金融专业功能模块主类"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # 初始化各个计算器
        self.indicator_calculator = FinancialIndicatorCalculator()
        self.technical_calculator = TechnicalAnalysisCalculator()
        self.risk_calculator = RiskAnalysisCalculator()
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.option_calculator = OptionPricingCalculator()

        self.logger.info("金融专业功能模块初始化完成")

    def get_available_functions(self) -> Dict[str, List[str]]:
        """获取可用功能列表"""
        return {
            "financial_indicators": [
                "profitability_ratios",
                "liquidity_ratios",
                "leverage_ratios",
                "efficiency_ratios",
            ],
            "technical_analysis": [
                "moving_averages",
                "rsi",
                "macd",
                "bollinger_bands",
                "stochastic",
            ],
            "risk_analysis": [
                "volatility",
                "var",
                "sharpe_ratio",
                "beta",
                "max_drawdown",
            ],
            "portfolio_analysis": [
                "portfolio_metrics",
                "portfolio_optimization",
                "efficient_frontier",
            ],
            "option_pricing": ["black_scholes", "implied_volatility", "greeks"],
        }

    def execute_financial_function(
        self, function_name: str, parameters: Dict[str, Any]
    ) -> CalculationResult:
        """执行金融计算功能"""
        try:
            result_value = None
            metadata = {"function": function_name, "parameters": parameters}

            # 财务指标计算
            if function_name == "profitability_ratios":
                result_value = self.indicator_calculator.calculate_profitability_ratios(
                    parameters.get("financial_data", {})
                )
            elif function_name == "liquidity_ratios":
                result_value = self.indicator_calculator.calculate_liquidity_ratios(
                    parameters.get("financial_data", {})
                )
            elif function_name == "leverage_ratios":
                result_value = self.indicator_calculator.calculate_leverage_ratios(
                    parameters.get("financial_data", {})
                )
            elif function_name == "efficiency_ratios":
                result_value = self.indicator_calculator.calculate_efficiency_ratios(
                    parameters.get("financial_data", {})
                )

            # 技术分析
            elif function_name == "moving_averages":
                prices = parameters.get("prices")
                periods = parameters.get("periods", [5, 10, 20, 50])
                result_value = self.technical_calculator.calculate_moving_averages(
                    prices, periods
                )

            elif function_name == "rsi":
                prices = parameters.get("prices")
                period = parameters.get("period", 14)
                result_value = self.technical_calculator.calculate_rsi(prices, period)

            elif function_name == "macd":
                prices = parameters.get("prices")
                fast = parameters.get("fast_period", 12)
                slow = parameters.get("slow_period", 26)
                signal = parameters.get("signal_period", 9)
                result_value = self.technical_calculator.calculate_macd(
                    prices, fast, slow, signal
                )

            # 风险分析
            elif function_name == "volatility":
                returns = parameters.get("returns")
                period = parameters.get("period", "daily")
                result_value = self.risk_calculator.calculate_volatility(
                    returns, period
                )

            elif function_name == "var":
                returns = parameters.get("returns")
                confidence = parameters.get("confidence_level", 0.05)
                result_value = self.risk_calculator.calculate_var(returns, confidence)

            elif function_name == "sharpe_ratio":
                returns = parameters.get("returns")
                risk_free_rate = parameters.get("risk_free_rate", 0.0)
                result_value = self.risk_calculator.calculate_sharpe_ratio(
                    returns, risk_free_rate
                )

            # 投资组合分析
            elif function_name == "portfolio_optimization":
                returns = parameters.get("returns")
                risk_aversion = parameters.get("risk_aversion", 1.0)
                constraints = parameters.get("constraints")
                result_value = self.portfolio_analyzer.optimize_portfolio(
                    returns, risk_aversion, constraints
                )

            # 期权定价
            elif function_name == "black_scholes":
                spot = parameters.get("spot_price")
                strike = parameters.get("strike_price")
                time_to_expiry = parameters.get("time_to_expiry")
                risk_free_rate = parameters.get("risk_free_rate")
                volatility = parameters.get("volatility")
                option_type = parameters.get("option_type", "call")
                result_value = self.option_calculator.black_scholes_price(
                    spot,
                    strike,
                    time_to_expiry,
                    risk_free_rate,
                    volatility,
                    option_type,
                )

            else:
                raise ValueError(f"未知的金融功能: {function_name}")

            # 创建计算结果
            calculation_result = CalculationResult(
                indicator=function_name,
                value=result_value,
                timestamp=datetime.now(),
                metadata=metadata,
            )

            self.logger.debug(f"执行金融功能: {function_name}")
            return calculation_result

        except Exception as e:
            self.logger.error(f"执行金融功能失败 {function_name}: {e}")
            error_result = CalculationResult(
                indicator=function_name,
                value={"error": str(e)},
                timestamp=datetime.now(),
                metadata={"function": function_name, "error": True},
            )
            return error_result