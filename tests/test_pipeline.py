from datetime import date

import pandas as pd

from analysis import pipeline


def test_quarter_label():
    assert pipeline.quarter_label(date(2026, 10, 25)) == "2026-Q4"
    assert pipeline.quarter_label(date(2026, 3, 31)) == "2026-Q1"


def test_markdown_table():
    md = pipeline.markdown_table(pd.DataFrame({"a": [1], "b": ["x"]}))
    assert md == "| a | b |\n|---|---|\n| 1 | x |"


def test_pct_marks_missing_as_tbd():
    assert pipeline.pct(0.0123) == "1.23%"
    assert pipeline.pct(float("nan")) == "TBD"
