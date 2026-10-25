"""Tracking difference from calendar-year NAV returns, by benchmark variant (rules R2, R16)."""

from datetime import date

import pandas as pd

from analysis import metrics


def last_complete_years(as_of: date, n: int = 3) -> list[int]:
    """The n most recent complete calendar years before as_of, oldest first."""
    return list(range(as_of.year - n, as_of.year))


def tracking_difference_table(
    candidates: pd.DataFrame,
    annual_returns: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
    years: list[int],
) -> pd.DataFrame:
    """Annualised NAV return, benchmark return and tracking difference over the given years.

    One row per candidate. A candidate missing any of the years is measured over the years it
    has and marked incomplete; one with none of them gets NaN. Within a benchmark variant,
    ranking by nav_annualised gives the same order as ranking by tracking difference.
    """
    # pivot (not pivot_table) so a duplicated year in the hand-entered data raises, not averages
    nav = annual_returns.pivot(index="year", columns="isin", values="nav_return")  # noqa: PD010
    bench = benchmark_returns.pivot(  # noqa: PD010
        index="year", columns="benchmark_variant", values="index_return"
    )
    rows = []
    for row in candidates.itertuples():
        fund = nav[row.isin].reindex(years).dropna() if row.isin in nav else pd.Series(dtype=float)
        index = bench.get(row.benchmark_variant, pd.Series(dtype=float)).reindex(fund.index)
        covered = list(fund.index)
        nav_ann = metrics.annualised_return(fund, 1) if covered else float("nan")
        index_ann = (
            metrics.annualised_return(index, 1) if covered and index.notna().all() else float("nan")
        )
        rows.append(
            {
                "isin": row.isin,
                "ticker": row.ticker,
                "benchmark_variant": row.benchmark_variant,
                "years_covered": len(covered),
                "complete": len(covered) == len(years),
                "nav_annualised": nav_ann,
                "index_annualised": index_ann,
                "tracking_difference": nav_ann - index_ann,
            }
        )
    return pd.DataFrame(rows)
