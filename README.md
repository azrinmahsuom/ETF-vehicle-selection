<!-- START HERE (removed by /new-project)
New project from the template? Open this folder in VS Code, open Claude Code, and run /new-project.
It interviews you, writes docs/brief.md and fills in this README. Delete this block once done. -->

# {{Project Title}}

> **One-line thesis:** {{e.g. "Singapore REITs with sub-35% gearing outperformed the index on a risk-adjusted basis, 2015–2025."}}

![CI](https://github.com/azrinmahsuom/{{repo-name}}/actions/workflows/ci.yml/badge.svg)

## Summary

| | |
|---|---|
| **Question** | {{What are you trying to find out?}} |
| **Universe / period** | {{e.g. SGX-listed REITs, Jan 2015 – Dec 2025, monthly}} |
| **Method** | {{e.g. factor screen + backtest, DCF, regression}} |
| **Headline result** | {{One number with context, e.g. "Sharpe 0.82 vs 0.51 benchmark, net of 20 bps costs"}} |
| **Status** | {{In progress / Complete}} |

## Key findings

1. {{Finding, with the chart that shows it}}
2. {{Finding}}
3. {{What surprised you, or what didn't work}}

![Headline chart](reports/figures/headline.png)

## Limitations

Be specific. Reviewers trust a project more when it names its own weak points.

- {{e.g. Survivorship bias: universe is today's constituents}}
- {{e.g. No transaction costs below monthly rebalancing}}
- {{e.g. Small sample: 11 years, one rate cycle}}

## Reproduce it

Requires [uv](https://docs.astral.sh/uv/) (installs Python for you).

```bash
git clone https://github.com/azrinmahsuom/{{repo-name}}.git
cd {{repo-name}}
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
| {{e.g. Yahoo Finance via yfinance}} | {{Daily prices}} | {{Personal, non-commercial use}} |

## Disclaimer

This is a personal research project built on publicly available data. It is not investment advice, not a recommendation to buy or sell any security, and does not represent the views of any employer.
