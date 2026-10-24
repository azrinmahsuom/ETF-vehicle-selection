# ETF Vehicle Selection

> **One line:** A quarterly tool that ranks the ETFs tracking MSCI ACWI and the Bloomberg Global Aggregate by total cost of ownership for a Singapore tax-resident investor, and flags when a holding should be switched.

![CI](https://github.com/azrinmahsuom/ETF-vehicle-selection/actions/workflows/ci.yml/badge.svg)

## Summary

| | |
|---|---|
| **Question** | Each quarter: which ETF is the cheapest way to hold each index, and should any current holding be switched? |
| **Universe / period** | ETFs tracking MSCI ACWI (global equity) and the Bloomberg Global Aggregate (global bonds); daily total returns, trailing 3 years (1- and 5-year context), USD base with SGD shown |
| **Method** | Total cost of ownership = tracking difference vs the net index (includes expense ratio and fund-level withholding) + investor-level withholding + trading costs; rank within each sleeve; switch only if the annual saving over a 20-year horizon exceeds this switch's cost plus any cost not yet recovered from earlier switches; flag US estate-tax exposure |
| **Headline result** | TBD |
| **Status** | In progress |

## Key findings

TBD

<!-- Headline chart goes here once reports/figures/headline.png exists. -->

## Limitations

- TBD. Expected so far:
  - The candidate list is maintained by hand, so newly launched ETFs only appear once they're added.
  - Bid-ask spreads may be estimated from daily high/low where actual quotes aren't available.
  - Benchmark index data is licensed, so only derived tracking differences are published.

## Reproduce it

Requires [uv](https://docs.astral.sh/uv/) (installs Python for you).

```bash
git clone https://github.com/azrinmahsuom/ETF-vehicle-selection.git
cd ETF-vehicle-selection
uv sync                  # create the environment
cp .env.example .env     # add any API keys (never committed)
uv run pytest            # check everything works
uv run python -m analysis.pipeline   # run the analysis end to end
```

## Repository layout

```
├── AGENTS.md          Rules for AI coding agents working in this repo (CLAUDE.md points here)
├── data/              Raw, external and processed data (contents git-ignored)
├── docs/              Project brief and methodology decision log
├── notebooks/         Exploration only; anything reusable moves to src/
├── reports/           Final write-up and figures (committed)
├── src/analysis/      Reusable code: loading, cleaning, metrics, pipeline
└── tests/             Tests for the code in src/
```

## Data sources

| Source | What | Licence / terms |
|---|---|---|
| Yahoo Finance via yfinance | ETF daily prices and dividends | Personal, non-commercial use |
| Issuer factsheets and KIIDs | Expense ratio, domicile, share class, hedging | Public documents |
| MSCI, Bloomberg (via index provider or issuer factsheets) | Benchmark index levels | Licensed; derived results only |
| MAS, or yfinance `SGD=X` | USD/SGD exchange rates | Public |
| Tax treaty rates | Dividend withholding tax by domicile | Public |
| Exchange or issuer data | Bid-ask spreads | Public; derived results |

## Disclaimer

This is a personal research project built on publicly available data. It is not investment advice, not a recommendation to buy or sell any security, and does not represent the views of any employer.
