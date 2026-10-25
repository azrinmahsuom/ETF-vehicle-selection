"""Download and load prices, FX and index levels (brief section 8).

Raw downloads go to data/raw as CSV and are never committed; rerun the download to rebuild them.
"""

from datetime import date

import pandas as pd
import requests
import yfinance as yf

from analysis.config import DATA_PROCESSED, DATA_RAW

# Yahoo Finance suffix for each exchange in reference/candidates.csv
YAHOO_SUFFIX = {
    "LSE": ".L",
    "SIX": ".SW",
    "Euronext Amsterdam": ".AS",
    "Euronext Paris": ".PA",
    "XETRA": ".DE",
    "NASDAQ": "",
    "NYSE": "",
}

MSCI_URL = "https://app2.msci.com/products/service/index/indexmaster/getLevelDataForGraph"
MSCI_ACWI = "892400"  # MSCI index code for MSCI ACWI

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15"


def yahoo_symbol(ticker: str, exchange: str) -> str:
    """Yahoo Finance symbol for a listing, e.g. ("ISAC", "LSE") -> "ISAC.L"."""
    return ticker + YAHOO_SUFFIX[exchange]


def download_prices(symbols: list[str], start: date, end: date) -> pd.DataFrame:
    """Daily prices for each Yahoo symbol, in long format, saved to data/raw/prices.csv.

    Columns: date, symbol, open, high, low, close, adj_close, dividends. adj_close includes
    reinvested distributions, so it is the total-return price series.
    """
    frames = []
    for symbol in symbols:
        hist = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=False, actions=True)
        if hist.empty:
            continue
        hist = hist.rename(columns=lambda c: c.lower().replace(" ", "_"))
        hist.index = hist.index.tz_localize(None).normalize()
        hist = hist[["open", "high", "low", "close", "adj_close", "dividends"]]
        frames.append(hist.rename_axis("date").reset_index().assign(symbol=symbol))
    prices = pd.concat(frames, ignore_index=True)
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    prices.to_csv(DATA_RAW / "prices.csv", index=False)
    return prices


def parse_msci_levels(payload: dict) -> pd.Series:
    """Daily index levels from an MSCI end-of-day response, indexed by date."""
    rows = payload["indexes"]["INDEX_LEVELS"]
    dates = pd.to_datetime([str(r["calc_date"]) for r in rows], format="%Y%m%d")
    return pd.Series([r["level_eod"] for r in rows], index=dates, name="level").sort_index()


def download_msci_index(
    start: date,
    end: date,
    index_code: str = MSCI_ACWI,
    variant: str = "NETR",
    currency: str = "USD",
) -> pd.Series:
    """Daily MSCI index levels from MSCI's public end-of-day data, saved to data/raw.

    MSCI's terms allow informational, non-commercial use and prohibit redistribution, so the
    series stays in data/raw (not committed) and only derived results are published.
    """
    params = {
        "currency_symbol": currency,
        "index_variant": variant,
        "start_date": start.strftime("%Y%m%d"),
        "end_date": end.strftime("%Y%m%d"),
        "data_frequency": "DAILY",
        "index_codes": index_code,
    }
    response = requests.get(MSCI_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    levels = parse_msci_levels(response.json())
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    levels.rename_axis("date").to_csv(DATA_RAW / f"msci_{index_code}_{variant}_{currency}.csv")
    return levels


def load_prices() -> pd.DataFrame:
    """Load data/raw/prices.csv written by download_prices."""
    path = DATA_RAW / "prices.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run the download step first.")
    return pd.read_csv(path, parse_dates=["date"])


def load_msci_index(
    index_code: str = MSCI_ACWI, variant: str = "NETR", currency: str = "USD"
) -> pd.Series:
    """Load an MSCI index series written by download_msci_index."""
    path = DATA_RAW / f"msci_{index_code}_{variant}_{currency}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run the download step first.")
    return pd.read_csv(path, index_col="date", parse_dates=["date"])["level"]


def save_processed(df: pd.DataFrame, filename: str) -> None:
    """Write an analysis-ready table to data/processed as CSV."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PROCESSED / filename, index=False)
