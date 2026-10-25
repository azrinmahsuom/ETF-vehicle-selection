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


def _table():
    candidates = pd.DataFrame(
        {
            "isin": ["H", "C1", "C2", "N"],
            "ticker": ["HHH", "CC1", "CC2", "NEW"],
            "benchmark_variant": ["X"] * 4,
            "distribution": ["acc", "dist", "acc", "acc"],
            "domicile": ["IE", "US", "IE", "IE"],
        }
    )
    td = pd.DataFrame(
        {
            "isin": ["H", "C1", "C2", "N"],
            "ticker": ["HHH", "CC1", "CC2", "NEW"],
            "benchmark_variant": ["X"] * 4,
            "complete": [True, True, True, True],
            "tracking_difference": [-0.0020, 0.0010, -0.0015, 0.0050],
        }
    )
    wht = pd.DataFrame({"fund_domicile": ["IE", "US"], "withholding_rate": [0.0, 0.30]})
    short = pd.Series([False, False, False, True])
    return ranking.cost_table(candidates, td, wht, {"C1": 0.02}, short)


def test_cost_table_holding_cost_and_eligibility():
    t = _table().set_index("isin")
    # US dist beating its index by 0.10%: cost = -0.0010 + 2% yield x 30% = 0.0050
    assert t.loc["C1", "annual_holding_cost"] == pytest.approx(0.0050)
    assert t.loc["C2", "annual_holding_cost"] == pytest.approx(0.0015)
    assert t.loc["C1", "us_situs"]
    # Short history can't be ranked or trigger a switch, even though it looks cheapest
    assert not t.loc["N", "eligible"]
    assert pd.isna(t.loc["N", "rank"])
    assert t.loc["C2", "rank"] == 1


def test_switch_decision_picks_cheapest_eligible_and_applies_breakeven():
    t = _table()
    one_way = {"H": 0.0010, "C1": 0.0010, "C2": 0.0010, "N": 0.0010}
    # H costs 0.20%/yr, C2 0.15%/yr -> saving 5 bps; switch cost 20 bps -> breakeven 4 years
    d = ranking.switch_decision("H", t, one_way, unrecovered=0.0, remaining_years=19.2)
    assert d.best_candidate == "CC2 (C2)"
    assert d.annual_saving == pytest.approx(0.0005)
    assert d.breakeven_years == pytest.approx(4.0)
    assert d.switch
    # With only 3 years left the same switch fails
    assert not ranking.switch_decision("H", t, one_way, 0.0, remaining_years=3.0).switch


def test_switch_decision_holds_when_already_cheapest():
    d = ranking.switch_decision("C2", _table(), {i: 0.001 for i in ["H", "C1", "C2", "N"]}, 0.0, 19)
    assert not d.switch
    assert d.reason.startswith("hold: already")
