import pandas as pd
import pytest

from analysis import metrics


def test_simple_returns():
    prices = pd.Series([100.0, 110.0, 99.0])
    assert metrics.simple_returns(prices).tolist() == pytest.approx([0.10, -0.10])


def test_annualised_return_one_year_of_monthly():
    # 12 months of 1% -> (1.01^12 - 1)
    rets = pd.Series([0.01] * 12)
    assert metrics.annualised_return(rets, periods_per_year=12) == pytest.approx(1.01**12 - 1)


def test_max_drawdown():
    # 100 -> 120 -> 90 -> 130: trough 90 from peak 120 = -25%
    rets = pd.Series([0.20, -0.25, 130 / 90 - 1])
    assert metrics.max_drawdown(rets) == pytest.approx(-0.25)


def test_sharpe_is_finite():
    rets = pd.Series([0.01, -0.005, 0.02, 0.0])
    assert pd.notna(metrics.sharpe_ratio(rets, periods_per_year=12))


def test_tracking_difference_one_year_monthly():
    # Fund 12 x 0.9%, index 12 x 1%: TD = (1.009^12 - 1) - (1.01^12 - 1)
    fund = pd.Series([0.009] * 12)
    index = pd.Series([0.01] * 12)
    expected = 1.009**12 - 1.01**12
    assert metrics.tracking_difference(fund, index, periods_per_year=12) == pytest.approx(expected)


def test_tracking_difference_uses_common_dates_only():
    dates = pd.date_range("2025-01-31", periods=3, freq="ME")
    fund = pd.Series([0.01, 0.02, 0.03], index=dates)
    index = pd.Series([0.01, 0.02], index=dates[:2])
    # Only the two shared months count, and they match exactly -> TD 0
    assert metrics.tracking_difference(fund, index, periods_per_year=12) == pytest.approx(0.0)


def test_calendar_year_tracking_difference():
    # 2024: fund +10% vs index +12% -> -2%; 2025: fund 1.05*1.05 vs index 1.10 -> +0.25%
    dates = pd.to_datetime(["2024-06-30", "2025-03-31", "2025-09-30"])
    fund = pd.Series([0.10, 0.05, 0.05], index=dates)
    index = pd.Series([0.12, 0.10, 0.0], index=dates)
    result = metrics.calendar_year_tracking_difference(fund, index)
    assert result.loc[2024] == pytest.approx(-0.02)
    assert result.loc[2025] == pytest.approx(1.05 * 1.05 - 1.10)


def test_tracking_difference_from_calendar_years():
    # R16: 3 calendar years, fund 10%/-5%/20% vs benchmark 10.2%/-4.8%/20.1%
    years = [2023, 2024, 2025]
    fund = pd.Series([0.10, -0.05, 0.20], index=years)
    bench = pd.Series([0.102, -0.048, 0.201], index=years)
    expected = (1.10 * 0.95 * 1.20) ** (1 / 3) - (1.102 * 0.952 * 1.201) ** (1 / 3)
    assert metrics.tracking_difference(fund, bench, periods_per_year=1) == pytest.approx(expected)
