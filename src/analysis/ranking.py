"""Tracking difference from issuer-published 12-month NAV returns (rules R2, R16)."""

from datetime import date

import pandas as pd

from analysis import metrics


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
