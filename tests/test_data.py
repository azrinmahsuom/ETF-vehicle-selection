import pandas as pd
import pytest

from analysis import data


def test_yahoo_symbol():
    assert data.yahoo_symbol("ISAC", "LSE") == "ISAC.L"
    assert data.yahoo_symbol("ACWIA", "SIX") == "ACWIA.SW"
    assert data.yahoo_symbol("ACWI", "NASDAQ") == "ACWI"


def test_yahoo_symbol_unknown_exchange_fails_loudly():
    with pytest.raises(KeyError):
        data.yahoo_symbol("XXX", "Mars")


def test_parse_msci_levels_sorts_by_date():
    payload = {
        "indexes": {
            "INDEX_LEVELS": [
                {"level_eod": 101.0, "calc_date": 20260902},
                {"level_eod": 100.0, "calc_date": 20260901},
            ]
        }
    }
    levels = data.parse_msci_levels(payload)
    assert list(levels.index) == list(pd.to_datetime(["2026-09-01", "2026-09-02"]))
    assert levels.tolist() == [100.0, 101.0]
