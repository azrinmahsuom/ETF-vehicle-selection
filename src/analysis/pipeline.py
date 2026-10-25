"""Quarterly run: refresh prices -> tracking difference -> cost of ownership -> switch review.

Run with: uv run python -m analysis.pipeline            (downloads fresh prices)
          uv run python -m analysis.pipeline --offline  (uses data/raw as it is)

Writes the public ranking to reports/<YYYY-QN>/ and the personal switch review (holdings,
values) to data/processed/, which is not committed (rule R13).
"""

import sys
import tomllib
from datetime import date

import pandas as pd

from analysis import charts, costs, data, ranking, reference
from analysis.config import DATA_EXTERNAL, DATA_PROCESSED, DEFAULT_SPREAD, FIGURES, ROOT

FX_SYMBOLS = ["SGD=X", "EURUSD=X"]  # SGD per USD; USD per EUR


def quarter_label(as_of: date) -> str:
    """Quarter of the run date, e.g. 2026-10-25 -> "2026-Q4"."""
    return f"{as_of.year}-Q{(as_of.month - 1) // 3 + 1}"


def markdown_table(df: pd.DataFrame) -> str:
    """Render a small DataFrame as a GitHub markdown table (no extra dependency)."""
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def pct(value: float, digits: int = 2) -> str:
    """Format a decimal as a percentage, or "TBD" when it hasn't been computed."""
    return "TBD" if pd.isna(value) else f"{value * 100:.{digits}f}%"


def latest(prices: pd.DataFrame, symbol: str, column: str = "close") -> float:
    """Most recent value of a column for one symbol."""
    rows = prices[prices["symbol"] == symbol].sort_values("date")
    return float(rows[column].iloc[-1])


PERSONAL_FILES = ["portfolio.toml", "holdings.csv", "switch_log.csv"]


def load_personal() -> tuple[dict, pd.DataFrame, list[costs.PastSwitch]] | None:
    """Portfolio settings, holdings and switch log from data/external (not committed).

    Returns None when any file is missing (e.g. a fresh clone), so only the public ranking runs.
    """
    if not all((DATA_EXTERNAL / f).exists() for f in PERSONAL_FILES):
        return None
    with open(DATA_EXTERNAL / "portfolio.toml", "rb") as f:
        portfolio = tomllib.load(f)
    holdings = pd.read_csv(DATA_EXTERNAL / "holdings.csv", dtype={"isin": str})
    log = pd.read_csv(DATA_EXTERNAL / "switch_log.csv", parse_dates=["switch_date"])
    switches = [
        costs.PastSwitch(r.switch_date.date(), float(r.cost), float(r.annual_saving))
        for r in log.itertuples()
    ]
    return portfolio, holdings, switches


def run(as_of: date, download: bool = True) -> None:
    candidates = reference.load_reference("candidates")
    withholding = reference.load_reference("withholding_rates")
    fees = reference.load_reference("broker_fees")
    annual = reference.load_reference("annual_returns")
    spreads = reference.load_reference("spreads")
    near = reference.load_reference("near_equivalents")
    personal = load_personal()

    candidates["symbol"] = [
        data.yahoo_symbol(t, e)
        for t, e in zip(candidates["ticker"], candidates["exchange"], strict=True)
    ]
    if download:
        start = date(as_of.year - 5, 1, 1)
        data.download_prices([*candidates["symbol"], *FX_SYMBOLS], start, as_of)
    prices = data.load_prices()
    prices = prices[prices["date"] <= pd.Timestamp(as_of)]

    # Tracking difference, withholding and holding cost (R3, R4, R11, R16)
    td = ranking.tracking_difference_table(candidates, annual, as_of)
    dist_yield = {}
    for row in candidates[candidates["distribution"] == "dist"].itertuples():
        p = prices[prices["symbol"] == row.symbol].set_index("date")
        if len(p):
            dist_yield[row.isin] = costs.trailing_distribution_yield(
                p["dividends"], p["close"], as_of
            )
    short = reference.short_history(candidates, as_of)
    table = ranking.cost_table(candidates, td, withholding, dist_yield, short)

    # Spreads (R10): published where available, otherwise the default, flagged
    published = spreads.set_index(["ticker", "exchange"])["spread"]
    keys = list(zip(table["ticker"], table["exchange"], strict=True))
    table["spread"] = [published.get(k, DEFAULT_SPREAD) for k in keys]
    table["spread_source"] = ["published" if k in published.index else "default" for k in keys]

    quarter = quarter_label(as_of)
    gaps = reference.coverage_gaps(candidates, withholding, fees, annual)
    write_public_ranking(table, near, gaps, as_of, quarter)
    charts.holding_cost_chart(table, quarter, FIGURES / "headline.png")
    charts.yearly_td_chart(
        annual,
        {"IE00B44Z5B48": "ACWD (SPDR)", "IE00B6R52259": "ISAC (iShares)"},
        FIGURES / "acwi_yearly_tracking_difference.png",
    )
    if personal is None:
        print(
            f"Public ranking written to reports/{quarter}/. No personal inputs in data/external "
            f"({', '.join(PERSONAL_FILES)}), so the switch review was skipped."
        )
        return
    portfolio, holdings, switches = personal

    # Switch review for each holding (R6, R7, R8)
    eur_per_usd = 1 / latest(prices, "EURUSD=X")
    sgd_per_usd = latest(prices, "SGD=X")
    start = portfolio["portfolio_start"]
    remaining = costs.remaining_horizon_years(start, as_of)
    unrecovered = costs.unrecovered_cost(switches, as_of)
    decisions, one_way_by_holding = [], {}
    for h in holdings.itertuples():
        one_way = {}
        for r in table.itertuples():
            market = reference.FEE_MARKET[r.exchange]
            price = latest(prices, r.symbol)
            usd = costs.trade_cost_usd(
                h.value_usd, market, r.trading_currency, price, r.spread, fees, eur_per_usd
            )
            one_way[r.isin] = usd / h.value_usd
        one_way_by_holding[h.isin] = one_way
        decisions.append(ranking.switch_decision(h.isin, table, one_way, unrecovered, remaining))

    write_switch_review(
        table,
        holdings,
        decisions,
        one_way_by_holding,
        sgd_per_usd,
        remaining,
        unrecovered,
        prices,
        as_of,
        quarter,
    )


def write_public_ranking(
    table: pd.DataFrame, near: pd.DataFrame, gaps: list[str], as_of: date, quarter: str
) -> None:
    """reports/<quarter>/ranking.csv and ranking.md: no personal data."""
    out = ROOT / "reports" / quarter
    out.mkdir(parents=True, exist_ok=True)
    cols = [
        "sleeve",
        "benchmark_variant",
        "rank",
        "ticker",
        "exchange",
        "isin",
        "domicile",
        "distribution",
        "expense_ratio",
        "tracking_difference",
        "periods",
        "window_end",
        "distribution_yield",
        "withholding_rate",
        "withholding_drag",
        "annual_holding_cost",
        "spread",
        "spread_source",
        "short_history",
        "eligible",
        "us_situs",
        "status",
    ]
    ordered = table.sort_values(["benchmark_variant", "rank", "annual_holding_cost"])
    ordered[cols].to_csv(out / "ranking.csv", index=False)

    lines = [
        f"# ETF ranking, {quarter}",
        "",
        f"Run on {as_of.isoformat()}. Annual holding cost = expense ratio + tax withheld on "
        "distributions for a Singapore resident (rules R3, R4); both are fixed, published "
        "figures. Tracking difference (each share class's latest three 12-month periods from "
        "issuer factsheets, R16) is shown for information only: three years of it are too "
        "noisy to separate close funds. Candidates under 3 years old or not yet verified at "
        "source are listed but not ranked (R11).",
        "",
    ]
    for variant, g in ordered.groupby("benchmark_variant", sort=False):
        view = pd.DataFrame(
            {
                "Rank": g["rank"].map(lambda v: "—" if pd.isna(v) else str(int(v))),
                "ETF": g["ticker"] + " (" + g["exchange"] + ")",
                "Domicile": g["domicile"],
                "Expense ratio": g["expense_ratio"].map(pct),
                "Withholding drag": g["withholding_drag"].map(pct),
                "Annual holding cost": g["annual_holding_cost"].map(pct),
                "Tracking difference (info)": g["tracking_difference"].map(pct),
                "Window end": g["window_end"].map(
                    lambda d: "—" if pd.isna(d) else d.strftime("%Y-%m")
                ),
                "Notes": [
                    ", ".join(
                        n
                        for n, flag in [
                            ("under 3 years", s),
                            ("incomplete window", not s and not c and pd.notna(td_)),
                            ("US estate tax", u),
                            ("not verified", st != "verified"),
                        ]
                        if flag
                    )
                    for s, u, st, c, td_ in zip(
                        g["short_history"],
                        g["us_situs"],
                        g["status"],
                        g["complete"],
                        g["tracking_difference"],
                        strict=True,
                    )
                ],
            }
        )
        lines += [f"## {variant}", "", markdown_table(view), ""]

    lines += [
        "## Near-equivalents (separate comparison, not ranked; R17)",
        "",
        markdown_table(
            pd.DataFrame(
                {
                    "ETF": near["ticker"] + " (" + near["exchange"] + ")",
                    "Index tracked": near["index_tracked"],
                    "Compares with": near["compares_with"],
                    "Expense ratio": near["expense_ratio"].map(pct),
                    "3y tracking difference vs own index": (
                        (1 + near["nav_3y_annualised"]) - (1 + near["index_3y_annualised"])
                    ).map(pct),
                    "Window end": near["window_end"],
                }
            )
        ),
        "",
        "## Data gaps",
        "",
        *[f"- {g}" for g in gaps],
        "",
        "Not investment advice. Source data: issuer factsheets and IBKR's published fees, "
        "listed per row in `reference/`.",
    ]
    (out / "ranking.md").write_text("\n".join(lines) + "\n")


def write_switch_review(
    table: pd.DataFrame,
    holdings: pd.DataFrame,
    decisions: list[ranking.SwitchDecision],
    one_way_by_holding: dict[str, dict[str, float]],
    sgd_per_usd: float,
    remaining: float,
    unrecovered: float,
    prices: pd.DataFrame,
    as_of: date,
    quarter: str,
) -> None:
    """data/processed/<quarter>_switch_review.md: holdings, costs in USD and SGD, decisions."""
    by_isin = table.set_index("isin")
    fx = prices[prices["symbol"] == "SGD=X"].set_index("date")["close"]
    years = [as_of.year - 3, as_of.year - 1]
    fx_start = fx[fx.index <= pd.Timestamp(f"{years[0] - 1}-12-31")].iloc[-1]
    fx_end = fx[fx.index <= pd.Timestamp(f"{years[1]}-12-31")].iloc[-1]
    fx_ann = (fx_end / fx_start) ** (1 / 3) - 1

    rows = []
    for h, d in zip(holdings.itertuples(), decisions, strict=True):
        r = by_isin.loc[h.isin]
        cost_usd = r["annual_holding_cost"] * h.value_usd
        nav_usd = r["nav_annualised"]
        rows.append(
            {
                "Holding": f"{h.ticker} ({h.exchange})",
                "Value": f"USD {h.value_usd:,.0f} / SGD {h.value_usd * sgd_per_usd:,.0f}",
                "Annual holding cost": f"{pct(r['annual_holding_cost'])} = USD {cost_usd:,.2f} / "
                f"SGD {cost_usd * sgd_per_usd:,.2f}",
                "3y NAV return, USD": pct(nav_usd),
                "Same in SGD": pct((1 + nav_usd) * (1 + fx_ann) - 1),
                "Rank in variant": "—" if pd.isna(r["rank"]) else str(int(r["rank"])),
                "Best alternative": d.best_candidate or "—",
                "Saving/yr": pct(d.annual_saving, 3),
                "Switch cost": pct(d.switch_cost, 3),
                "Breakeven (yrs)": "—"
                if d.breakeven_years == float("inf")
                else f"{d.breakeven_years:.1f}",
                "Decision": d.reason,
            }
        )
    lines = [
        f"# Switch review, {quarter} (private, not committed)",
        "",
        f"Run on {as_of.isoformat()}. Horizon left: {remaining:.1f} years (20 years from the "
        f"portfolio start, R6). Unrecovered cost from past switches: {pct(unrecovered, 3)} (R7). "
        f"USD/SGD {sgd_per_usd:.4f}; USD/SGD change over {years[0]}–{years[1]}: "
        f"{pct(fx_ann)} a year (FX impact on an SGD investor).",
        "",
        "Rule (R6): switch only if annual saving × years left > switch cost + unrecovered cost. "
        "Switch cost = selling the holding + buying the alternative, each = half spread + IBKR "
        "Pro Tiered commission + FX conversion where needed (R8, R10).",
        "",
        markdown_table(pd.DataFrame(rows)),
        "",
    ]
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    (DATA_PROCESSED / f"{quarter}_switch_review.md").write_text("\n".join(lines) + "\n")
    summary = pd.DataFrame([d.__dict__ for d in decisions])
    summary.to_csv(DATA_PROCESSED / f"{quarter}_switch_review.csv", index=False)
    print("\n".join(lines))


def main() -> None:
    run(date.today(), download="--offline" not in sys.argv)


if __name__ == "__main__":
    main()
