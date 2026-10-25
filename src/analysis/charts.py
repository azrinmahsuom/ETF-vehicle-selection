"""README charts (AGENTS.md: a title that states the takeaway, labelled axes, period, source).

Colours are slots 1-2 of the reference data-viz palette (validated as a pair), on its light
chart surface; text uses the palette's text tokens, never a series colour.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SERIES = ["#2a78d6", "#eb6834"]  # blue, orange

VARIANT_TITLES = {
    "MSCI ACWI Net USD": "Global equity (MSCI ACWI)",
    "Bloomberg Global Aggregate USD unhedged": "Global bonds, unhedged",
    "Bloomberg Global Aggregate USD hedged": "Global bonds, USD-hedged",
}


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def holding_cost_chart(table: pd.DataFrame, quarter: str, path: Path) -> None:
    """Annual holding cost of each ranked ETF, one panel per benchmark variant."""
    ranked = table[table["eligible"]].copy()
    ranked["label"] = (
        ranked["ticker"] + " (" + ranked["exchange"].str.replace("Euronext ", "") + ")"
    )
    variants = [v for v in VARIANT_TITLES if v in set(ranked["benchmark_variant"])]
    heights = [len(ranked[ranked["benchmark_variant"] == v]) + 0.9 for v in variants]
    fig, axes = plt.subplots(
        len(variants),
        1,
        figsize=(8, 0.45 * sum(heights) + 1.6),
        sharex=True,
        gridspec_kw={"height_ratios": heights},
        facecolor=SURFACE,
    )
    lo = min(ranked["annual_holding_cost"].min(), 0) * 100
    hi = ranked["annual_holding_cost"].max() * 100
    for ax, variant in zip(axes, variants, strict=True):
        g = ranked[ranked["benchmark_variant"] == variant].sort_values(
            "annual_holding_cost", ascending=False
        )
        values = g["annual_holding_cost"] * 100
        ax.barh(g["label"], values, color=SERIES[0], height=0.55, edgecolor=SURFACE, linewidth=2)
        for y, v in enumerate(values):
            ax.text(
                v + (hi - lo) * 0.015 if v >= 0 else v - (hi - lo) * 0.015,
                y,
                f"{v:.2f}%",
                va="center",
                ha="left" if v >= 0 else "right",
                fontsize=9,
                color=TEXT,
            )
        ax.axvline(0, color=TEXT_SECONDARY, linewidth=0.8)
        ax.set_title(VARIANT_TITLES[variant], loc="left", fontsize=10, color=TEXT, pad=4)
        ax.tick_params(axis="y", labelcolor=TEXT)
        _style(ax)
    axes[-1].set_xlim(lo - (hi - lo) * 0.15, hi * 1.18)
    axes[-1].set_xlabel(
        "Annual holding cost (% of position a year; below 0 = beats its index)",
        fontsize=9,
        color=TEXT_SECONDARY,
    )
    fig.suptitle(
        "Within each index, the cheapest ETFs cost under 0.2% a year to hold",
        x=0.01,
        ha="left",
        fontsize=12,
        fontweight="bold",
        color=TEXT,
    )
    fig.text(
        0.01,
        0.005,
        f"Ranked ETFs only ({quarter} run). Holding cost = −tracking difference over the "
        "latest three 12-month periods + investor withholding tax.\nSource: issuer "
        "factsheets (NAV returns); IRS / issuer tax documents. Not investment advice.",
        fontsize=7.5,
        color=TEXT_SECONDARY,
        va="bottom",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def yearly_td_chart(annual_returns: pd.DataFrame, funds: dict[str, str], path: Path) -> None:
    """Calendar-year tracking difference of two funds, to show year-to-year noise (R2)."""
    a = annual_returns.copy()
    a["period_end"] = pd.to_datetime(a["period_end"])
    a = a[a["period_end"].dt.month == 12]
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=SURFACE)
    _style(ax)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.grid(axis="x", visible=False)
    ax.axhline(0, color=TEXT_SECONDARY, linewidth=0.8)
    for colour, (isin, name) in zip(SERIES, funds.items(), strict=False):
        f = a[a["isin"] == isin].sort_values("period_end").tail(3)
        years = f["period_end"].dt.year
        td = (f["nav_return"] - f["benchmark_return"]) * 100
        ax.plot(
            years,
            td,
            color=colour,
            linewidth=2,
            marker="o",
            markersize=8,
            markeredgecolor=SURFACE,
            markeredgewidth=2,
            label=name,
        )
        ax.annotate(
            name,
            (years.iloc[-1], td.iloc[-1]),
            xytext=(10, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=TEXT,
        )
    ax.set_xticks(sorted(set(a["period_end"].dt.year))[-3:])
    ax.set_ylabel("Tracking difference (percentage points)", fontsize=9, color=TEXT_SECONDARY)
    ax.legend(frameon=False, fontsize=9, loc="upper left", labelcolor=TEXT)
    ax.set_xlim(ax.get_xlim()[0] - 0.1, ax.get_xlim()[1] + 0.35)
    fig.suptitle(
        "Year-to-year swings are far larger than the gap between these two ETFs",
        x=0.01,
        ha="left",
        fontsize=12,
        fontweight="bold",
        color=TEXT,
    )
    fig.text(
        0.01,
        0.01,
        "Fund NAV return minus MSCI ACWI Net (USD), by calendar year. Above 0 = beat the "
        "index.\nSource: iShares and SPDR factsheets. Not investment advice.",
        fontsize=7.5,
        color=TEXT_SECONDARY,
        va="bottom",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
