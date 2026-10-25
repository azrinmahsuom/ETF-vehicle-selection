# reference/

Hand-researched inputs that can't be downloaded by code. Unlike `data/`, these files **are committed**, so every result can be reproduced from a fresh clone. Personal inputs (portfolio size, holdings, switch log) go in `data/external/`, which is not committed.

Rules (AGENTS.md rule 7):
- Every row cites a source and the date it was checked.
- `status` is `verified` (checked against a primary document) or `to_verify` (secondary source only). The pipeline warns when it uses a `to_verify` row.
- When a value changes, update the row, its date and its source. Git history keeps the old value.

| File | Contents | Rule |
|---|---|---|
| `candidates.csv` | ETFs tracking each benchmark: ticker, ISIN, listing, domicile, share class, hedging, index variant, expense ratio | R12, R11 |
| `withholding_rates.csv` | Investor-level withholding on distributions by fund domicile, for a Singapore tax resident | R4 |
| `broker_fees.csv` | IBKR commission and FX schedules by market | R8 |
| `annual_returns.csv` | Calendar-year NAV total return of each share class and its benchmark, from issuer factsheets/KIDs | R16 |
| `excluded_candidates.csv` | Funds excluded from candidates and why | R14 |
