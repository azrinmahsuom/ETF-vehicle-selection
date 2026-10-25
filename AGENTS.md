# AGENTS.md

Shared instructions for any coding agent working in this repository (Claude Code reads this through `CLAUDE.md`; Codex reads it directly). Read it at the start of every session, then read `docs/brief.md`.

## What this repo is

A public investment project by Azrin Mahsuom, CFA. The README must stand on its own for anyone reading it on GitHub, and every number in it must be reproducible from the code.

`docs/brief.md` is the source of truth for this project's goal, scope, method and success criteria. If it still contains `{{placeholders}}`, stop and suggest running `/new-project` before writing any analysis code.

## Hard rules

1. **Public data only.** Never use files that look like they came from an employer, client or internal system (client names, account numbers, internal identifiers, firm templates or letterheads). If unsure, stop and ask.
2. **No secrets in code, output or commits.** API keys come from `.env` via `analysis.config.get_secret`. Never print, log or hardcode them, and never read `.env` directly.
3. **Never commit data files.** Everything under `data/` is git-ignored. Code must be able to re-download or regenerate it.
4. **No look-ahead bias.** A signal at time t uses only data available at t. Lag fundamentals by their publication delay. If you can't guarantee this, say so explicitly.
5. **No survivorship bias without disclosure.** If the universe is today's constituents, state it in the README's Limitations.
6. **Never fabricate numbers.** Every figure in the README or reports must come from running the code. If it hasn't been computed, write `TBD`.
7. **Every decision is rule-based and evidence-backed.** Each methodology choice, threshold and default is written as an explicit rule the code applies mechanically (no case-by-case judgement), and cites the research or data that supports it in `docs/decisions.md`. If no evidence has been found yet, mark the rule `Evidence: pending` and add it to the brief's "Open questions"; never present an unsupported choice as settled.
8. **Stay within the brief.** If a request goes beyond `docs/brief.md`, point it out and ask whether to update the brief first. Add anything unresolved to its "Open questions" section rather than silently assuming.

## How to work with the owner

- The owner reads Python but writes little of it. After each change, explain in two or three plain sentences what changed and why, and point to the file and function.
- Run tests and lint freely. **Ask before** installing packages, downloading large datasets, committing, or pushing.
- When making a methodology choice, add a dated entry to `docs/decisions.md`.

## Layout

The root `README.md` is the only README. Folder rules live here.

- `src/analysis/`: all reusable logic. Small functions, type hints, docstrings.
  - `config.py` paths and settings · `data.py` downloads and loading · `reference.py` reference inputs and gap checks · `metrics.py` returns and tracking difference · `costs.py` cost model and switch rule · `ranking.py` tracking-difference table · `pipeline.py` end-to-end run
- `reference/` (committed): hand-researched inputs that code can't download (R13): `candidates.csv`, `excluded_candidates.csv`, `withholding_rates.csv`, `broker_fees.csv`, `annual_returns.csv`, `benchmark_returns.csv`.
  - Every row cites a source and the date it was checked, with `status` `verified` (primary document) or `to_verify` (secondary source).
  - When a value changes, update the row, its date and its source; git history keeps the old value.
- `data/` (not committed): `raw/` downloads exactly as received, never edited by hand · `external/` the owner's personal inputs (portfolio, holdings, switch log) · `processed/` outputs written only by `src/analysis/`. Folders are created by the code.
- `notebooks/`: exploration only, named `NN-short-description.ipynb`. Import from `src/analysis`; code used twice moves to `src/` with a test. Clear large outputs before committing. Start with `uv run jupyter lab`.
- `reports/figures/`: final charts as PNG (150–200 dpi, 1200px wide), committed and referenced from the README. Final results belong here, not in notebooks.
- `docs/brief.md` project intake · `docs/decisions.md` methodology log.
- `tests/`: a test for every function in `src/analysis/`, using small hand-checkable inputs.

## Commands

```bash
uv sync                         # install / update environment
uv add <package>                # add a dependency (never pip install)
uv run pytest                   # tests
uv run ruff check . --fix       # lint
uv run ruff format .            # format
uv run python -m analysis.pipeline
```

Run tests and lint before saying any task is done.

## Finance conventions

- Simple returns for portfolio aggregation; log returns only when stated. Annualise with the right periods (252 daily, 52 weekly, 12 monthly).
- State the currency, whether returns are total or price-only, and the risk-free rate and its source. Defaults unless the brief says otherwise: SGD with 3M SORA, or USD with 3M T-bill.
- Backtests include transaction costs (default 10 bps per side) and state the rebalancing rule.
- Always compare against the benchmark named in the brief.
- Charts: a title that states the takeaway, labelled axes with units, the period, and a source line.

## Git

- Small commits with imperative messages: `Add drawdown metric`, `Fix dividend adjustment in loader`.
- While the repo is private, commit to `main`. Once public, use a branch and pull request for anything beyond a small fix.
- Never force-push to `main`.
