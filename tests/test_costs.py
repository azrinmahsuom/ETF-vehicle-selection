from datetime import date

import pytest

from analysis import costs


def test_investor_withholding_drag():
    # 1.5% yield, 30% US withholding -> 0.45% a year
    assert costs.investor_withholding_drag(0.015, 0.30) == pytest.approx(0.0045)


def test_investor_withholding_drag_accumulating_is_zero():
    assert costs.investor_withholding_drag(0.0, 0.30) == 0.0


def test_annual_holding_cost():
    # Fund lags net index by 0.20% and loses 0.45% to withholding -> 0.65% a year
    assert costs.annual_holding_cost(-0.0020, 0.0045) == pytest.approx(0.0065)


def test_annual_holding_cost_fund_beats_index():
    # Irish fund beating the net index by 0.10%, accumulating -> negative cost
    assert costs.annual_holding_cost(0.0010, 0.0) == pytest.approx(-0.0010)


def test_percent_commission_minimum_and_cap():
    # Tiered USD on LSE: 0.05% of 12,000 = 6.00; of 2,000 = 1.00 -> min 1.70
    # and of 100,000 = 50 -> cap 39
    assert costs.percent_commission(12_000, 0.0005, 1.70, 39.0) == pytest.approx(6.0)
    assert costs.percent_commission(2_000, 0.0005, 1.70, 39.0) == pytest.approx(1.70)
    assert costs.percent_commission(100_000, 0.0005, 1.70, 39.0) == pytest.approx(39.0)


def test_percent_commission_no_cap():
    assert costs.percent_commission(100_000, 0.0005, 1.70) == pytest.approx(50.0)


def test_per_share_commission_minimum_and_cap():
    # Tiered US: 50 shares x 0.0035 = 0.175 -> minimum 0.35
    assert costs.per_share_commission(50, 5_000) == pytest.approx(0.35)
    # 1,000 shares x 0.0035 = 3.50, under the 1% cap of 100
    assert costs.per_share_commission(1_000, 10_000) == pytest.approx(3.5)
    # 10 shares of a 2-dollar stock: min 0.35 but cap 1% of 20 = 0.20
    assert costs.per_share_commission(10, 20) == pytest.approx(0.2)


def test_fx_conversion_cost():
    # 0.2 bps of 12,500 = 0.25 -> minimum 2.00; of 20m = 400
    assert costs.fx_conversion_cost(12_500) == pytest.approx(2.0)
    assert costs.fx_conversion_cost(20_000_000) == pytest.approx(400.0)


def test_one_way_trading_cost():
    # 6 bps spread -> 3 bps; 6.00 commission + 2.00 FX on 10,000 -> 8 bps; total 11 bps
    assert costs.one_way_trading_cost(10_000, 0.0006, 6.0, 2.0) == pytest.approx(0.0011)


def test_remaining_horizon_years():
    start = date(2026, 1, 1)
    assert costs.remaining_horizon_years(start, start) == pytest.approx(20.0)
    assert costs.remaining_horizon_years(start, date(2031, 1, 1)) == pytest.approx(
        20 - 1826 / 365.25
    )
    assert costs.remaining_horizon_years(start, date(2050, 1, 1)) == 0.0


def test_breakeven_owner_example():
    # Owner's example: save 5 bps a year, pay 50 bps to switch -> 10 years
    assert costs.breakeven_years(0.0005, 0.0050) == pytest.approx(10.0)


def test_breakeven_no_saving_is_infinite():
    assert costs.breakeven_years(0.0, 0.0050) == float("inf")


def test_unrecovered_cost_owner_example():
    # Owner's example: 50 bps switch saving 10 bps a year, held 3 years -> 20 bps left
    log = [costs.PastSwitch(date(2026, 1, 1), cost=0.0050, annual_saving=0.0010)]
    as_of = date(2029, 1, 1)  # 1096 days
    expected = 0.0050 - 0.0010 * 1096 / 365.25
    assert costs.unrecovered_cost(log, as_of) == pytest.approx(expected)
    assert costs.unrecovered_cost(log, as_of) == pytest.approx(0.0020, abs=1e-6)


def test_unrecovered_cost_carries_across_switches():
    # Switch 1: 50 bps, saves 10 bps/yr, held 1 year until switch 2 -> 40 bps left
    # Switch 2: 30 bps, saves 20 bps/yr, held 1 year -> 40 + 30 - 20 = 50 bps left
    log = [
        costs.PastSwitch(date(2027, 1, 1), cost=0.0030, annual_saving=0.0020),
        costs.PastSwitch(date(2026, 1, 1), cost=0.0050, annual_saving=0.0010),
    ]
    result = costs.unrecovered_cost(log, date(2028, 1, 1))
    expected = 0.0080 - 0.0010 * 365 / 365.25 - 0.0020 * 365 / 365.25
    assert result == pytest.approx(expected)


def test_unrecovered_cost_floored_at_zero():
    log = [costs.PastSwitch(date(2026, 1, 1), cost=0.0010, annual_saving=0.0010)]
    assert costs.unrecovered_cost(log, date(2036, 1, 1)) == 0.0


def test_unrecovered_cost_empty_log():
    assert costs.unrecovered_cost([], date(2026, 10, 25)) == 0.0


def test_should_switch():
    # 5 bps/yr saving, 50 bps cost: passes with 19 years left, fails with 9
    assert costs.should_switch(0.0005, 0.0050, 0.0, remaining_years=19)
    assert not costs.should_switch(0.0005, 0.0050, 0.0, remaining_years=9)
    # Unrecovered 20 bps pushes breakeven to 14 years: fails with 13 left
    assert not costs.should_switch(0.0005, 0.0050, 0.0020, remaining_years=13)
