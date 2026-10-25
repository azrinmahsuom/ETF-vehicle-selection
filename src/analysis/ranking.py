"""Tracking difference from issuer-published 12-month NAV returns (rules R2, R16)."""

from dataclasses import dataclass
from datetime import date

import pandas as pd

from analysis import costs, metrics


def tracking_difference_table(
    candidates: pd.DataFrame, annual_returns: pd.DataFrame, as_of: date, n_periods: int = 3
) -> pd.DataFrame:
    """Annualised NAV return, benchmark return and tracking difference per candidate.

    Uses each candidate's n_periods most recent 12-month periods ending on or before as_of
    (calendar years, or the issuer's own 12-month periods when it doesn't publish calendar
    years). Fund and benchmark are in the share class's currency, so tracking difference is
    comparable across currencies. A candidate with fewer periods is measured over what it has
    and marked incomplete; a missing benchmark for any period leaves tracking difference NaN.
    """
    periods = annual_returns.assign(period_end=pd.to_datetime(annual_returns["period_end"]))
    periods = periods[periods["period_end"] <= pd.Timestamp(as_of)]
    rows = []
    for row in candidates.itertuples():
        own = periods[periods["isin"] == row.isin].sort_values("period_end").tail(n_periods)
        nav_ann = metrics.annualised_return(own["nav_return"], 1) if len(own) else float("nan")
        bench_ok = len(own) and own["benchmark_return"].notna().all()
        bench_ann = (
            metrics.annualised_return(own["benchmark_return"], 1) if bench_ok else float("nan")
        )
        rows.append(
            {
                "isin": row.isin,
                "ticker": row.ticker,
                "benchmark_variant": row.benchmark_variant,
                "periods": len(own),
                "complete": len(own) == n_periods,
                "window_end": own["period_end"].max() if len(own) else pd.NaT,
                "nav_annualised": nav_ann,
                "index_annualised": bench_ann,
                "tracking_difference": nav_ann - bench_ann,
            }
        )
    return pd.DataFrame(rows)


def cost_table(
    candidates: pd.DataFrame,
    td: pd.DataFrame,
    withholding: pd.DataFrame,
    dist_yield: dict[str, float],
    short_history: pd.Series,
) -> pd.DataFrame:
    """Annual holding cost per candidate, and whether it may trigger a switch (R3, R4, R11).

    annual_holding_cost = -tracking difference + investor withholding on distributions.
    eligible means a complete tracking-difference window and at least 3 years of history.
    The rank is within each benchmark variant, cheapest first, among eligible candidates.
    """
    rates = withholding.set_index("fund_domicile")["withholding_rate"]
    t = candidates.merge(td.drop(columns=["ticker", "benchmark_variant"]), on="isin", how="left")
    t["short_history"] = short_history.to_numpy()
    t["distribution_yield"] = [
        dist_yield.get(i, float("nan")) if d == "dist" else 0.0
        for i, d in zip(t["isin"], t["distribution"], strict=True)
    ]
    t["withholding_rate"] = t["domicile"].map(rates)
    t["withholding_drag"] = [
        costs.investor_withholding_drag(y, r) if y else 0.0
        for y, r in zip(t["distribution_yield"], t["withholding_rate"], strict=True)
    ]
    t["annual_holding_cost"] = [
        costs.annual_holding_cost(td_, w)
        for td_, w in zip(t["tracking_difference"], t["withholding_drag"], strict=True)
    ]
    t["us_situs"] = t["domicile"] == "US"
    t["eligible"] = (
        t["complete"].fillna(False).astype(bool)
        & ~t["short_history"]
        & t["annual_holding_cost"].notna()
    )
    t["rank"] = (
        t[t["eligible"]].groupby("benchmark_variant")["annual_holding_cost"].rank(method="min")
    )
    return t


@dataclass(frozen=True)
class SwitchDecision:
    """Outcome of the switch rule for one holding (R6, R7)."""

    holding: str
    best_candidate: str | None
    annual_saving: float
    switch_cost: float
    unrecovered: float
    breakeven_years: float
    remaining_years: float
    switch: bool
    reason: str


def switch_decision(
    holding_isin: str,
    table: pd.DataFrame,
    one_way_cost: dict[str, float],
    unrecovered: float,
    remaining_years: float,
) -> SwitchDecision:
    """Apply the breakeven switch rule to one holding against eligible same-variant candidates.

    one_way_cost maps ISIN to the cost of one trade of this holding's value, as a fraction.
    Switch cost = selling the holding + buying the candidate.
    """
    current = table.set_index("isin").loc[holding_isin]
    peers = table[
        (table["benchmark_variant"] == current["benchmark_variant"])
        & table["eligible"]
        & (table["isin"] != holding_isin)
    ]
    label = f"{current['ticker']} ({holding_isin})"
    if pd.isna(current["annual_holding_cost"]):
        return SwitchDecision(
            label,
            None,
            float("nan"),
            float("nan"),
            unrecovered,
            float("nan"),
            remaining_years,
            False,
            "hold: current holding's cost is unknown",
        )
    if peers.empty:
        return SwitchDecision(
            label,
            None,
            0.0,
            0.0,
            unrecovered,
            float("inf"),
            remaining_years,
            False,
            "hold: no eligible candidate",
        )
    best = peers.loc[peers["annual_holding_cost"].idxmin()]
    saving = current["annual_holding_cost"] - best["annual_holding_cost"]
    cost = one_way_cost[holding_isin] + one_way_cost[best["isin"]]
    years = costs.breakeven_years(saving, cost, unrecovered)
    go = costs.should_switch(saving, cost, unrecovered, remaining_years)
    if saving <= 0:
        reason = "hold: already the cheapest eligible candidate"
    elif go:
        reason = f"switch: breakeven {years:.1f} years < {remaining_years:.1f} years left"
    else:
        reason = f"hold: breakeven {years:.1f} years >= {remaining_years:.1f} years left"
    best_label = f"{best['ticker']} ({best['isin']})"
    return SwitchDecision(
        label, best_label, saving, cost, unrecovered, years, remaining_years, go, reason
    )
