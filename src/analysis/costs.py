"""Total cost of ownership and the switch rule (rules R3-R8 in docs/decisions.md).

All rates and costs are decimals of position value per year or per trade: 0.0005 = 5 bps.
"""

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from analysis.config import HORIZON_YEARS


def investor_withholding_drag(distribution_yield: float, withholding_rate: float) -> float:
    """Annual cost of tax withheld on distributions paid to the investor (rule R4).

    Use a distribution_yield of 0 for accumulating share classes.
    """
    return distribution_yield * withholding_rate


def annual_holding_cost(tracking_difference: float, withholding_drag: float) -> float:
    """Annual cost of holding a fund: lag behind the net index plus investor withholding (R3)."""
    return -tracking_difference + withholding_drag


def percent_commission(
    trade_value: float, rate: float, minimum: float, maximum: float | None = None
) -> float:
    """Commission charged as a percentage of trade value, with a per-order minimum and cap (R8).

    IBKR Pro Tiered, USD-traded on LSE: rate=0.0005, minimum=1.70, maximum=39.00 (USD).
    """
    fee = max(trade_value * rate, minimum)
    return fee if maximum is None else min(fee, maximum)


def per_share_commission(
    shares: float,
    trade_value: float,
    per_share: float = 0.0035,
    minimum: float = 0.35,
    max_fraction: float = 0.01,
) -> float:
    """Commission charged per share, with a minimum and a cap as a fraction of trade value (R8).

    Defaults are IBKR Pro Tiered for US-listed ETFs (lowest volume tier): USD 0.0035/share,
    min USD 0.35, max 1% of value. Exchange and regulatory fees are extra.
    """
    return min(max(shares * per_share, minimum), trade_value * max_fraction)


def fx_conversion_cost(trade_value: float, rate: float = 0.00002, minimum: float = 2.0) -> float:
    """Cost of a currency conversion: IBKR 0.2 bps of value, min USD 2 (R8)."""
    return max(trade_value * rate, minimum)


def one_way_trading_cost(
    trade_value: float, spread: float, commission: float, fx_cost: float = 0.0
) -> float:
    """Cost of one buy or sell as a fraction of trade value: half the spread plus fees (R8).

    spread is the full bid-ask spread as a fraction of price; commission and fx_cost are in
    currency units.
    """
    return spread / 2 + (commission + fx_cost) / trade_value


def remaining_horizon_years(
    portfolio_start: date, as_of: date, horizon_years: float = HORIZON_YEARS
) -> float:
    """Years left of the investment horizon counted from the portfolio start, floored at 0 (R6)."""
    elapsed = (as_of - portfolio_start).days / 365.25
    return max(horizon_years - elapsed, 0.0)


@dataclass(frozen=True)
class PastSwitch:
    """One switch-log entry: its date, its cost and the annual saving expected when made."""

    switch_date: date
    cost: float
    annual_saving: float


def unrecovered_cost(switch_log: list[PastSwitch], as_of: date) -> float:
    """Switching costs not yet earned back by the savings they bought, carried forward (R7).

    Each switch's saving accrues from its date until the next switch (or as_of), at the
    annual_saving recorded when it was made.
    """
    if not switch_log:
        return 0.0
    log = sorted(switch_log, key=lambda s: s.switch_date)
    total_cost = sum(s.cost for s in log)
    ends = [s.switch_date for s in log[1:]] + [as_of]
    total_saved = sum(
        s.annual_saving * max((end - s.switch_date).days, 0) / 365.25
        for s, end in zip(log, ends, strict=True)
    )
    return max(total_cost - total_saved, 0.0)


def breakeven_years(annual_saving: float, switch_cost: float, unrecovered: float = 0.0) -> float:
    """Years of saving needed to pay back this switch plus earlier unrecovered costs (R6)."""
    if annual_saving <= 0:
        return float("inf")
    return (switch_cost + unrecovered) / annual_saving


def should_switch(
    annual_saving: float, switch_cost: float, unrecovered: float, remaining_years: float
) -> bool:
    """Switch only if the saving over the remaining horizon beats all costs to recover (R6)."""
    return annual_saving * remaining_years > switch_cost + unrecovered


def abdi_ranaldo_spread(high: pd.Series, low: pd.Series, close: pd.Series) -> float:
    """Bid-ask spread estimated from daily close, high and low prices (rule R10).

    Abdi & Ranaldo (2017, Review of Financial Studies 30(12)): with c the log close and eta the
    log mid-range (log high + log low) / 2, spread^2 = 4 * mean((c_t - eta_t)(c_t - eta_t+1)).
    Days with high == low (no trades) are dropped first. A negative mean is set to 0, as in the
    paper. Returns the full spread as a fraction of price.
    """
    traded = high > low
    high, low, close = high[traded], low[traded], close[traded]
    c = np.log(close)
    eta = (np.log(high) + np.log(low)) / 2
    products = (c - eta) * (c - eta.shift(-1))
    mean = products.dropna().mean()
    return float(np.sqrt(max(4 * mean, 0.0))) if pd.notna(mean) else float("nan")


def trailing_distribution_yield(dividends: pd.Series, close: pd.Series, as_of: date) -> float:
    """Distributions paid in the 12 months to as_of divided by the latest close (rule R4)."""
    start = pd.Timestamp(as_of) - pd.DateOffset(years=1)
    window = (dividends.index > start) & (dividends.index <= pd.Timestamp(as_of))
    latest = close[close.index <= pd.Timestamp(as_of)].iloc[-1]
    return float(dividends[window].sum() / latest)


def trade_cost_usd(
    value_usd: float,
    market: str,
    trading_currency: str,
    price: float,
    spread: float,
    broker_fees: pd.DataFrame,
    eur_per_usd: float,
) -> float:
    """USD cost of one buy or sell of value_usd: half spread + commission + FX if needed (R8).

    broker_fees rows are matched on market and trading_currency (FX on market "FX"). Amounts in
    EUR (minimums, caps, per-execution fees) are converted with eur_per_usd. price is the
    share price in the trading currency, used for per-share commissions.
    """
    fees = broker_fees[
        (broker_fees["market"] == market) & (broker_fees["trading_currency"] == trading_currency)
    ]
    if len(fees) != 1:
        raise ValueError(f"expected one fee row for {market}/{trading_currency}, got {len(fees)}")
    fee = fees.iloc[0]
    to_usd = 1 / eur_per_usd if fee["currency"] == "EUR" else 1.0
    local_value = value_usd * eur_per_usd if trading_currency == "EUR" else value_usd
    if fee["fee_type"] == "per_share":
        commission = per_share_commission(
            local_value / price, value_usd, fee["per_share"], fee["minimum"], fee["max_fraction"]
        )
    else:
        maximum = fee["maximum"] * to_usd if pd.notna(fee["maximum"]) else None
        commission = percent_commission(value_usd, fee["rate"], fee["minimum"] * to_usd, maximum)
    if pd.notna(fee.get("third_party_per_execution")):
        commission += fee["third_party_per_execution"] * to_usd
    fx = 0.0
    if trading_currency != "USD":
        fx_row = broker_fees[broker_fees["market"] == "FX"].iloc[0]
        fx = fx_conversion_cost(value_usd, fx_row["rate"], fx_row["minimum"])
    return value_usd * spread / 2 + commission + fx
