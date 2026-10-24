"""Core performance and risk metrics. Every function here should have a test."""

import numpy as np
import pandas as pd

from analysis.config import TRADING_DAYS


def simple_returns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Period-over-period simple returns; first row dropped."""
    return prices.pct_change().iloc[1:]


def annualised_return(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    """Geometric annualised return from periodic simple returns."""
    growth = (1 + returns).prod()
    years = len(returns) / periods_per_year
    return float(growth ** (1 / years) - 1)


def annualised_volatility(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    """Annualised standard deviation of periodic returns."""
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series, risk_free_annual: float = 0.0, periods_per_year: int = TRADING_DAYS
) -> float:
    """Annualised Sharpe ratio. risk_free_annual is a decimal (0.03 = 3%)."""
    rf_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1
    excess = returns - rf_period
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(periods_per_year))


def max_drawdown(returns: pd.Series) -> float:
    """Largest peak-to-trough decline of the cumulative return path, as a negative decimal."""
    wealth = (1 + returns).cumprod()
    peak = wealth.cummax()
    return float((wealth / peak - 1).min())


def tracking_difference(
    fund_returns: pd.Series, index_returns: pd.Series, periods_per_year: int = TRADING_DAYS
) -> float:
    """Annualised fund return minus annualised index return over their common dates (rule R3).

    Negative means the fund lagged its index. Measured against the index's net total return
    variant, it already includes the expense ratio and fund-level withholding tax.
    """
    fund, index = fund_returns.align(index_returns, join="inner")
    return annualised_return(fund, periods_per_year) - annualised_return(index, periods_per_year)


def calendar_year_tracking_difference(
    fund_returns: pd.Series, index_returns: pd.Series
) -> pd.Series:
    """Tracking difference for each calendar year, not annualised (rule R2 consistency check).

    Both inputs need a DatetimeIndex. Partial years are included as they stand.
    """
    fund, index = fund_returns.align(index_returns, join="inner")
    fund_growth = (1 + fund).groupby(fund.index.year).prod()
    index_growth = (1 + index).groupby(index.index.year).prod()
    return fund_growth - index_growth
