# Project brief

Filled in by `/new-project`. Agents read this before every task. Update it whenever the scope changes, and log why in `docs/decisions.md`.

## 1. Name
{{Repo name, e.g. etf-domicile-tax-drag}}

## 2. Type
{{Research (answers a question once) or Tool (runs repeatedly)}}

## 3. Goal
{{In plain language: what question does this answer, or what problem does it solve?}}

## 4. Audience
{{Who uses the output? Default: recruiters and hiring managers reading the README.}}

## 5. Hypothesis (research only)
{{What you expect to find, and why. Written before seeing any results.}}

## 6. Universe, period, frequency, currency
- Universe: {{e.g. Irish- and US-domiciled S&P 500 ETFs}}
- Period: {{start}} to {{end}}
- Frequency: {{daily / monthly}}
- Currency: {{SGD / USD}} · Returns: {{total / price-only}}

## 7. Benchmark
{{What results are compared against.}}

## 8. Data and sources
One source per line, with whether results derived from it can be published.

| Data | Source | Publishable? |
|---|---|---|
| {{Daily prices}} | {{yfinance}} | {{Yes, derived results}} |

## 9. Processing steps
1. {{Step}}
2. {{Step}}

## 10. Outputs
{{e.g. README with headline chart; reports/figures/*.png; summary table}}

## 11. Run cadence (tool only)
{{How often it runs and who starts it, e.g. "by hand, quarterly".}}

## 12. Limits, assumptions and things to avoid
- Transaction costs: {{10 bps per side}}
- Risk-free rate: {{3M SORA / 3M T-bill}}
- {{Other constraints}}

## 13. How we know the code is correct
{{e.g. metrics match a hand calculation on a 3-row example; totals reconcile to source}}

## 14. What would show the hypothesis is wrong
{{The specific result that would change your conclusion.}}

## 15. Open questions
- {{Anything still undecided. Agents add to this list instead of assuming.}}
