from datetime import date

import pandas as pd

from analysis import reference


def _candidates(**overrides):
    row = {
        "ticker": "AAA",
        "isin": "IE0000000001",
        "exchange": "LSE",
        "domicile": "IE",
        "distribution": "acc",
        "hedged": "no",
        "inception": "2020-01-01",
        "status": "verified",
    }
    row.update(overrides)
    return pd.DataFrame([row])


WHT = pd.DataFrame({"fund_domicile": ["IE", "US"]})
FEES = pd.DataFrame({"market": ["LSE", "US"]})


def test_short_history():
    c = pd.concat(
        [_candidates(inception="2020-01-01"), _candidates(inception="2025-01-01")],
        ignore_index=True,
    )
    assert reference.short_history(c, date(2026, 10, 25)).tolist() == [False, True]


def test_short_history_missing_inception_counts_as_short():
    assert reference.short_history(_candidates(inception=None), date(2026, 10, 25)).tolist() == [
        True
    ]


def test_coverage_gaps_none():
    assert reference.coverage_gaps(_candidates(), WHT, FEES) == []


def test_coverage_gaps_finds_each_problem():
    c = _candidates(
        distribution="dist", domicile="LU", exchange="SIX", hedged="unknown", status="to_verify"
    )
    gaps = reference.coverage_gaps(c, WHT, FEES)
    assert len(gaps) == 4
    assert "LU-domiciled" in gaps[0]
    assert "SIX" in gaps[1]
    assert "hedging" in gaps[2]
    assert "1 of 1" in gaps[3]


def test_accumulating_class_needs_no_withholding_rate():
    assert reference.coverage_gaps(_candidates(domicile="LU"), WHT, FEES) == []
