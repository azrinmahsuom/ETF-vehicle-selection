from datetime import date

import pandas as pd
import pytest

from analysis import ranking


def test_last_complete_years():
    assert ranking.last_complete_years(date(2026, 10, 25)) == [2023, 2024, 2025]
    assert ranking.last_complete_years(date(2026, 1, 1), n=2) == [2024, 2025]


CANDIDATES = pd.DataFrame(
    {"isin": ["A", "B", "C"], "ticker": ["AAA", "BBB", "CCC"], "benchmark_variant": ["X"] * 3}
)
BENCH = pd.DataFrame(
    {"benchmark_variant": ["X", "X"], "year": [2024, 2025], "index_return": [0.10, 0.20]}
)


def test_tracking_difference_table_full_and_partial_history():
    annual = pd.DataFrame(
        {
            "isin": ["A", "A", "B"],
            "year": [2024, 2025, 2025],
            "nav_return": [0.099, 0.198, 0.201],
        }
    )
    t = ranking.tracking_difference_table(CANDIDATES, annual, BENCH, [2024, 2025]).set_index("isin")
    # A: two full years
    expected_a = (1.099 * 1.198) ** 0.5 - (1.10 * 1.20) ** 0.5
    assert t.loc["A", "tracking_difference"] == pytest.approx(expected_a)
    assert t.loc["A", "complete"]
    # B: 2025 only, measured against the 2025 index return, marked incomplete
    assert t.loc["B", "tracking_difference"] == pytest.approx(0.001)
    assert t.loc["B", "years_covered"] == 1
    assert not t.loc["B", "complete"]
    # C: no returns at all
    assert pd.isna(t.loc["C", "tracking_difference"])
    assert t.loc["C", "years_covered"] == 0
