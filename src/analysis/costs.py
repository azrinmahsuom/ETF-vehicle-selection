"""Total cost of ownership and the switch rule (rules R3-R8 in docs/decisions.md).

All rates and costs are decimals of position value per year or per trade: 0.0005 = 5 bps.
"""

from dataclasses import dataclass
from datetime import date

from analysis.config import HORIZON_YEARS


def investor_withholding_drag(distribution_yield: float, withholding_rate: float) -> float:
    """Annual cost of tax withheld on distributions paid to the investor (rule R4).

    Use a distribution_yield of 0 for accumulating share classes.
    """
    return distribution_yield * withholding_rate


def annual_holding_cost(tracking_difference: float, withholding_drag: float) -> float:
    """Annual cost of holding a fund: lag behind the net index plus investor withholding (R3)."""
    return -tracking_difference + withholding_drag


def percent_commission(trade_value: float, rate: float, minimum: float) -> float:
    """Commission charged as a percentage of trade value with a per-order minimum (R8).

    IBKR Fixed on LSE: rate=0.0005, minimum=4.0 (USD).
    """
    return max(trade_value * rate, minimum)


def per_share_commission(
    shares: float,
    trade_value: float,
    per_share: float = 0.005,
    minimum: float = 1.0,
    max_fraction: float = 0.01,
) -> float:
    """Commission charged per share, with a minimum and a cap as a fraction of trade value (R8).

    Defaults are IBKR Fixed for US-listed ETFs: USD 0.005/share, min USD 1, max 1% of value.
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
