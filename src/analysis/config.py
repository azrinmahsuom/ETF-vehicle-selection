"""Project paths and settings. Import from here rather than hardcoding paths."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_EXTERNAL = ROOT / "data" / "external"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"

load_dotenv(ROOT / ".env")

TRADING_DAYS = 252
TRANSACTION_COST_BPS = 10  # per side; fallback only when measured costs are missing (R8)
DEFAULT_SPREAD = 0.0010  # full bid-ask spread when no published figure exists (R10)
HORIZON_YEARS = 20  # investment horizon counted from the portfolio start (R6)
REFERENCE = ROOT / "reference"  # hand-researched inputs with sources, committed


def get_secret(name: str) -> str:
    """Return an API key from the environment, failing clearly if it's missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set. Copy .env.example to .env and add it.")
    return value
