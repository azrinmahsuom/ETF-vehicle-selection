from datetime import date

import pandas as pd
import pytest

from analysis import ranking

CANDIDATES = pd.DataFrame(
    {
        "isin": ["A", "B", "C", "D"],
        "ticker": ["AAA", "BBB", "CCC", "DDD"],
        "benchmark_variant": ["X"] * 4,
    }
)
ANNUAL = pd.DataFrame(
    {
        "isin": ["A", "A", "A", "B", "D"],
        "period_end": ["2023-12-31", "2024-12-31", "2025-12-31", "2025-12-31", "2025-09-30"],
        "nav_return": [0.50, 0.099, 0.198, 0.201, 0.05],
        "benchmark_return": [0.50, 0.10, 0.20, 0.20, None],
    }
)


def test_uses_latest_periods_up_to_as_of():
    t = ranking.tracking_difference_table(CANDIDATES, ANNUAL, date(2026, 10, 25), n_periods=2)
    a = t.set_index("isin").loc["A"]
    # Latest two periods only (2024, 2025); 2023 is dropped
    assert a["tracking_difference"] == pytest.approx((1.099 * 1.198) ** 0.5 - (1.10 * 1.20) ** 0.5)
    assert a["complete"]
    assert a["window_end"] == pd.Timestamp("2025-12-31")


def test_partial_missing_and_no_benchmark():
    t = ranking.tracking_difference_table(CANDIDATES, ANNUAL, date(2026, 10, 25), n_periods=2)
    t = t.set_index("isin")
    assert t.loc["B", "tracking_difference"] == pytest.approx(0.001)
    assert t.loc["B", "periods"] == 1
    assert not t.loc["B", "complete"]
    assert pd.isna(t.loc["C", "tracking_difference"])
    assert t.loc["C", "periods"] == 0
    # D has a return but no benchmark -> NAV known, tracking difference unknown
    assert t.loc["D", "nav_annualised"] == pytest.approx(0.05)
    assert pd.isna(t.loc["D", "tracking_difference"])


def test_periods_after_as_of_are_ignored():
    t = ranking.tracking_difference_table(CANDIDATES, ANNUAL, date(2025, 6, 30), n_periods=3)
    assert t.set_index("isin").loc["A", "periods"] == 2
