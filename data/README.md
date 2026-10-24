# data/

Nothing in here is committed except this file and the `.gitkeep` placeholders. All data must be reproducible by running the code.

| Folder | Contents | Rule |
|---|---|---|
| `raw/` | Downloads exactly as received | Never edit by hand |
| `external/` | Third-party reference data (index constituents, calendars) | Note source + date pulled below |
| `processed/` | Cleaned, analysis-ready outputs | Written only by `src/analysis/` |

## Provenance

| File | Source | Pulled on | Script |
|---|---|---|---|
| {{prices.parquet}} | {{yfinance}} | {{YYYY-MM-DD}} | `analysis.data.download_prices` |
