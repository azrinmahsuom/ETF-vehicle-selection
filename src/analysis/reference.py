"""Load the hand-researched inputs in reference/ and report what is missing (rule R13)."""

from datetime import date

import pandas as pd

from analysis.config import REFERENCE

# Exchanges that share one fee schedule in broker_fees.csv
FEE_MARKET = {
    "LSE": "LSE",
    "NASDAQ": "US",
    "NYSE": "US",
    "Euronext Paris": "Euronext",
    "Euronext Amsterdam": "Euronext",
    "XETRA": "XETRA",
    "SIX": "SIX",
}


def load_reference(name: str) -> pd.DataFrame:
    """Read one reference CSV, e.g. load_reference("candidates")."""
    return pd.read_csv(REFERENCE / f"{name}.csv", dtype={"isin": str, "ticker": str})


def short_history(candidates: pd.DataFrame, as_of: date, min_years: float = 3.0) -> pd.Series:
    """True for share classes younger than min_years at as_of; they can't trigger a switch (R11).

    A missing inception date counts as short history, so it can't trigger a switch by accident.
    """
    inception = pd.to_datetime(candidates["inception"], errors="coerce")
    age_years = (pd.Timestamp(as_of) - inception).dt.days / 365.25
    return ~(age_years >= min_years)


def coverage_gaps(
    candidates: pd.DataFrame, withholding: pd.DataFrame, broker_fees: pd.DataFrame
) -> list[str]:
    """List every candidate input the cost model would have to guess at.

    Checks: a withholding rate for each distributing class's domicile (R4), a fee schedule for
    each exchange (R8), a known hedging status (R12), and rows not yet verified at source.
    """
    gaps = []
    domiciles = set(withholding["fund_domicile"])
    markets = set(broker_fees["market"])
    for row in candidates.itertuples():
        label = f"{row.ticker} ({row.isin})"
        if row.distribution == "dist" and row.domicile not in domiciles:
            gaps.append(f"{label}: no withholding rate for {row.domicile}-domiciled distributions")
        market = FEE_MARKET.get(row.exchange)
        if market not in markets:
            gaps.append(f"{label}: no broker fee schedule for {row.exchange}")
        if row.hedged == "unknown":
            gaps.append(f"{label}: hedging status unknown")
    unverified = int((candidates["status"] != "verified").sum())
    if unverified:
        gaps.append(f"{unverified} of {len(candidates)} candidates not yet verified at source")
    return gaps
