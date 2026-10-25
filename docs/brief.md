# Project brief

Filled in by `/new-project`. Agents read this before every task. Update it whenever the scope changes, and log why in `docs/decisions.md`.

## 1. Name
etf-vehicle-selection

## 2. Type
Tool (runs repeatedly)

## 3. Goal
I am choosing between ETFs, and will use this tool to assist in my decision making. Each quarter it ranks the candidate ETFs tracking a given index by total cost of ownership, and the ranking helps determine whether the portfolio's ETF allocations need to be moved around.

**Switch rule** (R6/R7 in `docs/decisions.md`): the threshold is based on trading cost, over a 20-year investment horizon counted from the portfolio start, and accumulates costs left uncovered by previous switches. Switch only if annual saving × remaining years of the horizon > cost of this switch + cost still unrecovered from previous switches. Example: saving 5 bps a year against 50 bps of switching fees breaks even in 10 years. Example of unrecovered cost: a 50 bps switch saving 10 bps a year, held 3 years, leaves 20 bps that the next switch must also recover.

**Investor:** Singapore tax-resident.

## 4. Audience
Me, as part of my quarterly portfolio review.

## 5. Hypothesis (research only)
Not applicable (Tool).

## 6. Universe, period, frequency, currency
- Universe: two sleeves.
  - Global equity: every ETF that tracks MSCI ACWI.
  - Global bonds: every ETF that tracks the Bloomberg Global Aggregate.
- Period: trailing 3 years as the main measurement window, with 1 and 5 years shown for context, rolled forward each quarter. ETFs with less than 3 years of history are flagged, not dropped.
- Frequency: daily
- Currency: USD base, with SGD shown alongside and the FX impact broken out · Returns: total return only

## 7. Benchmark
- Global equity: MSCI ACWI (total return, USD)
- Global bonds: Bloomberg Global Aggregate (total return, USD): both unhedged (BBGATR) and USD-hedged (BBGATRH), ranked separately side by side

## 8. Data and sources
One source per line, with whether results derived from it can be published.

| Data | Source | Publishable? |
|---|---|---|
| ETF daily prices and dividends | yfinance | Yes, derived results |
| Expense ratio, domicile, share class, hedging | Issuer factsheets and KIIDs (manual entry, dated) | Yes |
| Benchmark index levels (MSCI ACWI, Bloomberg Global Agg) | Index provider or issuer factsheets | Derived results only (licensed index data; publish tracking differences, not raw index series) |
| USD/SGD FX | MAS published rates, or yfinance `SGD=X` | Yes |
| Dividend withholding tax rates | Tax treaty rates, documented in `data/external/` | Yes |
| Bid-ask spreads | Exchange or issuer data, or estimated from daily high/low | Yes, derived results |

## 9. Processing steps
1. Build the candidate list: ETFs tracking each benchmark, with domicile, listing, share class and hedging. Maintained by hand in `reference/candidates.csv`, with sources and dates (R13).
2. Download daily total-return prices, dividends and USD/SGD FX.
3. Calculate each candidate's costs (R3): tracking difference against the benchmark's net total return variant over 1, 3 and 5 years (this already includes the expense ratio and fund-level withholding), investor-level withholding on distributions, and trading costs (bid-ask spread, commission, FX conversion). The expense ratio is shown for information only.
4. Total cost of ownership = −tracking difference + investor-level withholding + annualised trading costs, in USD. Convert to SGD and break out the FX impact.
5. Rank candidates within each sleeve and flag US estate-tax exposure.
6. Compare against current holdings and apply the breakeven switch rule (R6/R7), using the switch log for unrecovered costs. Each candidate is marked "switch" or "hold", with the breakeven years and the reason. ETFs with less than 3 years of history cannot trigger a switch (R11).
7. Write the outputs: ranking table, charts, and a quarterly summary.

## 10. Outputs
- Quarterly ranking table per sleeve: `reports/YYYY-QN/ranking.csv`, plus a readable markdown version. One row per ETF, with each cost component, total cost of ownership in USD and SGD, FX impact, US estate-tax flag, and rank.
- Switch recommendation for each current holding: switch or hold, breakeven years, the numbers behind it (S, C, U), and the estimated cost of switching.
- Charts in `reports/figures/`: cost breakdown per candidate (stacked bars), tracking difference over time against the benchmark, and USD vs SGD returns showing the FX effect.
- README with the latest headline chart and a short summary of the method, updated after each run.
- No Excel export for now.

## 11. Run cadence (tool only)
By hand, quarterly, started by me as part of my portfolio review.

## 12. Limits, assumptions and things to avoid
- Transaction costs: 10 bps per side, used as the switching cost when actual spread and commission data is missing
- Risk-free rate: 3M US T-bill (USD base)
- Tracking difference is measured in USD, against the index variant the ETF tracks. Hedged and unhedged share classes are not ranked against each other.
- US estate-tax exposure for US-domiciled ETFs is shown as a flag, not added to the annual cost.
- Public data only; no look-ahead in any time series.
- Every decision is an explicit rule applied mechanically by the code, backed by cited research or data in `docs/decisions.md` (AGENTS.md rule 7).

## 13. How we know the code is correct
- Each cost metric matches a hand calculation on a 3-row example.
- Computed tracking differences reconcile to the issuer's published figures within a stated tolerance.
- Totals reconcile to source data (sum of cost components equals total cost of ownership).

## 14. What would show the hypothesis is wrong
Not applicable (Tool).

## 15. Open questions
- **Candidate data gaps** (run `analysis.reference.coverage_gaps` for the current list): no withholding rate for Luxembourg-domiciled distributions (1 candidate); most rows still `to_verify`.
- **Current holdings and switch log:** where the tool reads current holdings and the switch log (date, cost `C` and expected saving `S` of each past switch) from. Default: manual files in `data/external/` (not committed, R13).
- **Evidence review (2026-10-25, rules R1–R12 in `docs/decisions.md`).**
  - Supported: R1 USD base, R2 3-year window (as convention), R4 withholding rates, R5 estate-tax flag, R10 spread estimator, R12 hedged/unhedged separation.
  - Decided by owner 2026-10-25: R3 cost formula, R6/R7 breakeven switch rule with a 20-year horizon and unrecovered costs, R9 no risk-free rate, R11 short-history ETFs cannot trigger a switch.
  - Also decided 2026-10-25: R8 broker is IBKR; bond sleeve ranks both unhedged and USD-hedged variants side by side.
  - Still to verify against primary documents: Bloomberg index factsheet (R1), IRS Publication 515 and IRAS (R4), withholding on bond ETF distributions (R3), and the stability of 3-year tracking difference on our own data (R2).
