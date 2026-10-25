# Decision log

Append an entry whenever a methodology choice is made. Newest at the bottom.

Every decision must state the **rule** the code applies and the **evidence** behind it (see AGENTS.md rule 7). Use this format:

```
### YYYY-MM-DD — Decision title
**Context:** What prompted the choice
**Rule:** The exact rule the code applies, with thresholds
**Evidence:** Sources (paper, data, regulator/issuer document) with links, or "pending"
**Alternatives considered:** What was rejected and why
**Effect on results:** If known
```

---

### 2026-10-24 — Initial scope
**Context:** Project intake via `/new-project`.
**Decision:** Build a quarterly tool, run by hand, that ranks ETFs tracking MSCI ACWI (global equity) and the Bloomberg Global Aggregate (global bonds) by total cost of ownership for a Singapore tax-resident investor. Total cost of ownership = expense ratio + tracking difference + dividend withholding tax drag + bid-ask spread + FX conversion cost. Daily total-return data. Trailing 3-year main window, with 1- and 5-year context. USD base currency, SGD shown alongside with the FX impact separated. US estate-tax exposure is a flag, not a cost. Two switch-rule branches: ≥0.15% a year cheaper after all costs including switching, and cost saving net positive since the last switch. *(Cost formula superseded by R3; switch rule superseded by R6/R7.)*
**Rule:** As above. Each component becomes its own rule entry, with thresholds, once evidence is cited.
**Evidence:** Pending for each component (listed in the brief's "Open questions").
**Alternatives considered:** A one-off research comparison (rejected: the owner wants a repeatable quarterly review). SGD as the base currency (rejected for now: both benchmarks are quoted in USD and most candidates trade in USD, so measuring in USD keeps FX out of the cost comparison; supporting sources still to be cited).
**Effect on results:** Defines the universe and the cost model; no results computed yet.

### 2026-10-24 — Bond sleeve currency hedging (pending)
**Context:** The owner prefers the unhedged Global Aggregate on the view that hedging doesn't help returns, and asked for that view to be checked against research.
**Decision:** Decided by owner 2026-10-25: rank **both**. The bond sleeve has two rankings shown side by side, unhedged (vs BBGATR) and USD-hedged (vs BBGATRH). Hedged and unhedged share classes are never ranked against each other (R12), and a switch only compares candidates within the same variant.
**Rule:** Two bond rankings, each against its own index variant.
**Evidence:** Reviewed 2026-10-24:
- Perold & Schulman (1988): hedging cuts risk at no loss of expected return over the long run.
- Campbell, Serfaty-de Medeiros & Viceira (*Journal of Finance*, 2010): the risk-minimising position for a global bond investor is close to a full hedge.
- Vanguard: 5.81% hedged vs 8.20% unhedged volatility for global bonds over the 2022 period. T. Rowe Price (Global Agg, EUR base): 2.5% vs 6.4%. BNY (USD): 10-year drawdown −13.6% hedged vs −24.2% unhedged.
- Against: MSCI (1987–2008) found the "free lunch" did not hold consistently, and unhedged beat hedged in periods of USD weakness. Vanguard (May 2026) favours unhedged for equity-oriented investors and higher hedge ratios for fixed-income-oriented ones.
- Conclusion: hedging's return effect depends on the period (roughly the rate differential plus FX surprises); its reliable effect is lower volatility.
**Alternatives considered:** Unhedged only (owner's preference), hedged only, or ranking both variants side by side.
**Effect on results:** Determines which bond ETFs are in the candidate set and which benchmark variant tracking difference is measured against.

---

## Evidence review — 2026-10-25

One entry per rule. **Status** is one of: *Supported* (evidence backs the rule as written), *Revised* (evidence backs a changed rule, pending owner approval), *Owner's call* (evidence informs it but the parameter is a preference), *Pending* (more evidence needed). Most sources are secondary; primary documents still to check are listed under each entry.

### 2026-10-25 — R1 Base currency: USD
**Status:** Supported
**Rule:** Tracking difference and total cost of ownership are computed in USD, against the USD variant of each benchmark. SGD figures are the USD figures converted at the daily USD/SGD rate. FX impact = SGD return − USD return.
**Evidence:** MSCI's flagship ACWI factsheet reports net returns in USD ([MSCI ACWI Net factsheet](https://www.msci.com/documents/10199/255599/msci-acwi-net.pdf)). The flagship Bloomberg Global Aggregate (BBGATR) is a USD-denominated unhedged total return index, with a separate USD-hedged series (BBGATRH) ([YCharts BBGATR](https://ycharts.com/indices/^BBGATR), [BBGATRH](https://ycharts.com/indices/^BBGATRH)). Measuring the fund and index in the same currency keeps FX out of tracking difference; FX is reported separately, as the owner asked.
**To verify:** Bloomberg's official index factsheet (only a data aggregator was found).
**Alternatives considered:** SGD base, rejected because neither benchmark's flagship series is in SGD, and SGD-converted tracking difference would mix FX into cost.

### 2026-10-25 — R2 Measurement window: trailing 3 years, with 1 and 5 years shown
**Status:** Supported as convention; statistical stability still to be tested on our data
**Rule:** Rank on trailing 3-year annualised tracking difference. Show 1-year and 5-year figures, plus each calendar year's tracking difference, so consistency is visible.
**Evidence:** Multi-window disclosure is the regulatory norm. India's SEBI requires tracking difference for 1, 3, 5 and 10 years and since inception ([Bajaj Finserv summary](https://www.bajajfinserv.in/investments/what-is-tracking-difference)). Morningstar requires a 3-year record before rating a fund ([Morningstar](https://morningstar.co.uk/uk/news/68360/funds-whats-behind-the-morningstar-ratings.aspx)), though it gives no statistical rationale. Counterpoint: 3-year performance can mean-revert ([Validea](https://blog.validea.com/?p=18804)), which matters less for tracking difference than for returns, since tracking difference is dominated by persistent costs.
**To verify:** No study was found that quantifies how many years tracking difference needs to stabilise. Once data is in, test it: if the spread of annual tracking differences between two candidates is larger than the gap between them, the ranking is not reliable at 3 years.

### 2026-10-25 — R3 Total cost of ownership components
**Status:** Approved by owner 2026-10-25. Fixes double counting of withholding tax.
**Rule:** Annual total cost of ownership = −(tracking difference vs the benchmark's **net** total return variant) + investor-level withholding tax on distributions + annualised trading costs (spread + commission + FX conversion). The expense ratio is shown for information but **not added**, because it's already inside tracking difference.
**Evidence:** HKEX's TCO framework splits costs into trading costs (commission, spread) and holding costs (tracking difference, taxes, withholding) ([HKEX TCO primer](https://www.HKEX.com.hk/-/media/HKEX-Market/Products/Securities/Exchange-Traded-Products/Launch/ETF-Total-Cost-of-Ownership-primer-(for-Australia-investors).pdf)). Morningstar treats the expense ratio as one part of tracking difference ([Morningstar](https://morningstar.co.uk/uk/news/66096/the-total-cost-of-etf-ownership.aspx)). MSCI net indexes deduct withholding tax at the maximum rate for non-resident institutional investors without treaty benefits ([MSCI](https://www.msci.com/documents/1296102/7573199/WMA+PRIVATE+INVESTOR+INCOME.pdf/e13418a8-6e7a-4db7-86e4-dfa24be2ab88)), and funds paying lower treaty rates can beat the index as a result ([iShares SEC filing](https://www.sec.gov/Archives/edgar/data/930667/000119312525327007/R421.htm)). So fund-level withholding is already in tracking difference; adding it again double-counts.
**Alternatives considered:** Sum of expense ratio + withholding drag + spread + FX (the original step 3). Rejected because it counts both the expense ratio and fund-level withholding twice.
**To verify:** Withholding on bond ETF distributions (interest vs dividends) for a Singapore investor. The US portfolio-interest exemption may apply to some US-domiciled bond ETF payouts; this is unconfirmed.

### 2026-10-25 — R4 Dividend withholding tax rates by domicile
**Status:** Supported (secondary sources; primary check pending)
**Rule:** Investor-level withholding on distributions: US-domiciled ETF → 30% (Singapore has no US income tax treaty). Irish-domiciled UCITS → 0% (Ireland doesn't withhold on UCITS distributions to non-residents). Fund-level withholding (e.g. 15% on US dividends inside an Irish fund) is captured by tracking difference (R3). Accumulating share classes have no investor-level distributions.
**Evidence:** IRS Publication 515 default 30% rate, US–Ireland treaty 15%, no Irish withholding to non-residents, and Singapore not taxing foreign dividends for individuals ([POEMS](https://www.poems.com.sg/market-journal/us-domiciled-etfs-vs-ireland-domiciled-ucits-etfs-which-is-better-for-singapore-investors/), [Paasa](https://paasa.com/blog/dividend-withholding-tax-on-irish-ucits), [Paasa](https://paasa.com/blog/us-dividend-withholding-tax-singapore)).
**To verify:** IRS Publication 515 and IRAS guidance directly; record the rates with document dates in `data/external/withholding_rates.csv`.

### 2026-10-25 — R5 US estate tax: flag, not cost
**Status:** Supported
**Rule:** Flag every US-domiciled ETF as "US-situs: estate tax exposure", and show the holding value above USD 60,000. Not added to annual cost, because the expected cost depends on mortality and the size of holdings, not on the fund's annual operation.
**Evidence:** Non-resident non-citizens' US-situs assets above USD 60,000 require Form 706-NA ([IRS](https://irs.gov/individuals/international-taxpayers/some-nonresidents-with-u-s-assets-must-file-estate-tax-returns)), with rates of 18–40% ([Taxes for Expats](https://www.taxesforexpats.com/articles/non-us-citizens/nonresident-alien-estate-tax-exemption-us-situs-assets.html)). Singapore is not on the IRS list of US estate tax treaty countries ([IRS](https://www.irs.gov/node/7770)). Irish-domiciled UCITS shares are generally treated as non-US-situs ([Taxes for Expats](https://www.taxesforexpats.com/articles/investments/ucits-etf-withholding-tax.html), [StashAway](https://www.stashaway.sg/r/guide-ireland-domiciled-etfs-singapore)); this is commentary, not IRS guidance.

### 2026-10-25 — R6 Switch rule: breakeven over a 20-year horizon (replaces 0.15% a year)
**Status:** Decided by owner 2026-10-25. The fixed 0.15% threshold is replaced by a breakeven rule based on trading cost. R6 and R7 now form one rule.
**Rule:** All amounts are in bps of the position value.
- `S` = annual holding-cost saving of the candidate vs the current holding (R3 total cost of ownership, excluding trading costs).
- `C` = one-off cost of the new switch (spread + commission + FX conversion + any tax; R8).
- `U` = cost still unrecovered from previous switches (R7).
- `H` = remaining investment horizon = **20 years from the portfolio start date, minus years elapsed** (decided by owner 2026-10-25). As the horizon shrinks, a switch needs a faster breakeven; once the horizon is used up, no switch passes.
- **Switch if `S × H > C + U`**, i.e. breakeven years `(C + U) / S` < `H`. Otherwise hold.
- Owner's example: S = 5 bps a year and C = 50 bps gives breakeven in 10 years.
- The two rule branches from the goal are covered by this one formula: a first switch (`U = 0`), and a switch made while earlier switch costs are still unrecovered (`U > 0`).
**Evidence:** Practitioner analyses frame switching as a breakeven: a 40 bps switching cost is small against a 25 bps a year fee gap over 20 years ([Avantis](https://avantisinvestors.com/avantis-insights/penny-saved-is-a-dollar-earned)), and round-trip trading costs can be recovered within days to months depending on spread ([Nasdaq / Morningstar data](https://www.nasdaq.com/articles/how-benefits-low-etf-expense-ratios-expand-over-time)). Frequent trading erodes returns, mainly through trading costs ([Barber & Odean 2000](https://faculty.haas.berkeley.edu/odean/papers/returns/returns.html)).
**Note:** Economically, unrecovered past costs are sunk. Including `U` is a deliberate, conservative anti-churn rule chosen by the owner, consistent with the evidence that trading frequency erodes returns.
**Inputs:** Portfolio start January 2026 (taken as 2026-01-01), so the horizon ends 2046-01-01. Stored in `data/external/portfolio.toml`, which is not committed.

### 2026-10-25 — R7 "Net positive since last switch"
**Status:** Decided by owner 2026-10-25 (feeds `U` in R6)
**Rule:** After each switch, record its cost `C` and expected annual saving `S` in a switch log. Unrecovered cost `U = max(0, Σ C of previous switches − Σ (S × years held since each switch))`, carried forward across switches. The next switch must recover `C_new + U` within the horizon (R6). Owner's example: a 50 bps switch saving 10 bps a year, held 3 years, leaves U = 50 − 30 = 20 bps to be covered by the next switch.
**Evidence:** An anti-churn rule is supported by the evidence that trading frequency and its costs, not selection, drive underperformance ([Barber & Odean 2000](https://faculty.haas.berkeley.edu/odean/papers/returns/returns.html)). Note the rational-model view that adjustment costs alone can explain this ([Bonaparte, Cooper & Sha, NBER w16022](https://www.nber.org/papers/w16022.pdf)), which still supports including switching costs explicitly.
**Implementation choice:** Savings accrue at the `S` recorded at the time of the switch (as in the owner's example), not at a re-measured figure, so `U` is deterministic and auditable.

### 2026-10-25 — R8 Default switching cost: 10 bps per side
**Status:** Decided by owner 2026-10-25. Broker: Interactive Brokers (IBKR), Pro Tiered plan.
**Rule:** Switching cost per side = half the measured spread (R10) + IBKR commission for the trade size + FX conversion cost (if a currency conversion is needed). Commission and FX are computed from a dated fee schedule in `data/external/broker_fees.csv`, so they scale with the position size. Use 10 bps per side only if a measured figure is missing, and flag it.
**IBKR Pro Tiered schedule (owner's plan, confirmed 2026-10-25; verified on IBKR Singapore's public pricing pages):**
- US-listed: USD 0.0035 per share, min USD 0.35, max 1% of trade value, plus regulatory, exchange and clearing fees.
- USD-traded on LSE, SIX and Euronext Amsterdam: 0.05% of value, min USD 1.70, max USD 39 per order, plus exchange and clearing fees. Euronext also passes through EUR 0.75 per execution on ETFs.
- EUR-traded on Euronext and XETRA: 0.05%, min EUR 1.25, max EUR 29 per order (plus EUR 0.75 per execution on Euronext ETFs).
- FX: 0.2 bps of value, min USD 2 per conversion.
- Sources: [IBKR SG stocks](https://www.interactivebrokers.com.sg/en/pricing/commissions-stocks.php), [IBKR SG spot currencies](https://www.interactivebrokers.com.sg/en/pricing/commissions-spot-currencies.php). All rows are in `reference/broker_fees.csv`.
- Note: IBKR Lite offers zero-commission US trades to Singapore retail investors. That only matters for US-listed candidates (ACWI).
**Pending:** Third-party exchange and clearing fees under Tiered aren't itemised on the main page and are not yet modelled. They're expected to be small relative to the commission; check the IBKR knowledge base.

### 2026-10-25 — R9 Risk-free rate
**Status:** Approved by owner 2026-10-25. Not needed for ranking.
**Rule:** Total cost of ownership ranking uses no risk-free rate. If R6 discounts future savings, use the 3M US T-bill (FRED `DTB3`) as the discount rate.
**Evidence:** Source: [FRED DTB3](https://fred.stlouisfed.org/series/dtb3) (Federal Reserve H.15, daily since 1954). Cost comparison doesn't involve excess returns, so a risk-free rate has no role there.

### 2026-10-25 — R10 Bid-ask spread estimate
**Status:** Supported
**Rule:** Use quoted spread data where available. Otherwise estimate from daily close/high/low with the Abdi–Ranaldo estimator, cross-checked against Corwin–Schultz, and validate against quoted spreads where both exist.
**Evidence:** Peer-reviewed estimators: Corwin & Schultz (2012), *Journal of Finance* 67(2), 719–760, and Abdi & Ranaldo (2017), *Review of Financial Studies* 30(12), 4437–4480. A reference implementation is in R `bidask` ([CRAN docs](https://search.r-project.org/CRAN/packages/bidask/bidask.pdf)).

### 2026-10-25 — R11 Short-history ETFs
**Status:** Approved by owner 2026-10-25
**Rule:** ETFs with less than 3 years of history are ranked on their available window but flagged "insufficient history", and **cannot trigger a switch** until they reach 3 years.
**Evidence:** Morningstar's 3-year minimum before rating a fund ([Morningstar](https://morningstar.co.uk/uk/news/68360/funds-whats-behind-the-morningstar-ratings.aspx)); R2's window choice.

### 2026-10-25 — R12 Hedged and unhedged share classes ranked separately
**Status:** Supported
**Rule:** Each candidate is matched to the exact index variant it tracks (e.g. BBGATR unhedged or BBGATRH USD-hedged). Rankings are only within the same variant.
**Evidence:** Bloomberg publishes the hedged and unhedged variants as separate indexes ([YCharts BBGATR](https://ycharts.com/indices/^BBGATR), [BBGATRH](https://ycharts.com/indices/^BBGATRH)). Tracking difference is defined against the fund's own benchmark (ESMA ETF guidelines consultation, [ESMA/2012/44](https://www.esma.europa.eu/sites/default/files/library/2015/11/2012-44_0.pdf)), and the variants differ by FX return and hedging cost, not by fund cost.

### 2026-10-25 — R13 Where inputs live: committed reference data vs private personal data
**Status:** Decided (structural)
**Context:** The template excludes everything under `data/external/` from git. But the candidate list, withholding rates and broker fees are researched by hand and can't be regenerated by code. Excluded from git, the results couldn't be reproduced (AGENTS.md rules 3 and 6).
**Rule:** Hand-researched inputs go in `reference/` (committed), with a source, a checked-on date and a `verified`/`to_verify` status on every row. Personal inputs (portfolio start, portfolio value, holdings, switch log) go in `data/external/` (not committed).
**Evidence:** Reproducibility requirement in AGENTS.md; keeping personal financial details out of a public repo.
**Alternatives considered:** Committing `data/external/` (rejected: it would also publish personal inputs). Keeping everything uncommitted (rejected: not reproducible).

### 2026-10-25 — R14 Candidate matching: exact index only
**Status:** Decided (applies the owner's "whichever ETFs track those indices count as candidates")
**Rule:** A share class is a candidate only if its stated benchmark is the exact index: MSCI ACWI (equity), or the Bloomberg Global Aggregate unhedged or USD-hedged (bonds). Any replication method (physical or swap), domicile, or distribution policy qualifies. Excluded: index variants (float-adjusted, ESG, IMI), different index families (e.g. FTSE All-World, so VWRA is out), and classes hedged to a currency other than USD. Each exclusion is listed with its reason in `reference/excluded_candidates.csv`.
**Evidence:** Tracking difference is only meaningful against the fund's own benchmark (R12). A different index differs in constituents and returns, not just in cost.
**Alternatives considered:** Include close equivalents such as VWRA or VAGU. Rejected as candidates because their tracking difference is measured against another index. They could be shown in a separate "near-equivalents" table if the owner wants.
**First pass (2026-10-25):** 13 equity, 5 bond unhedged and 6 bond USD-hedged candidates, mostly from justETF (data dated 2026-10-23) and so marked `to_verify` until checked against issuer factsheets. Gaps: tickers and exchanges for most rows; hedging status of the two Amundi Core Global Aggregate classes (LU1437024729, LU1737654019); withholding rates for Luxembourg- and France-domiciled distributing classes (R4).

### 2026-10-25 — R15 Which listing to use for each share class
**Status:** Decided
**Rule:** Use a USD-traded listing where one exists, because it avoids an FX conversion on every trade (R8). Among USD listings, prefer LSE, then Euronext Amsterdam, SIX, XETRA, Euronext Paris. If there's no USD listing, use the main EUR listing; FX conversion cost is then added to its trading cost.
**Evidence:** IBKR charges 0.2 bps (min USD 2) per FX conversion (R8). The USD base currency is set by R1. LSE comes first because its IBKR fee schedule is the best documented of the venues (`reference/broker_fees.csv`).
**Result (2026-10-25):** 20 of 24 candidates have a USD listing; 4 trade in EUR only (LU1829220216, FR0014017NX3, LU3243907741, LU1737654019). 8 candidates are under 3 years old and can't trigger a switch (R11): SCWX, ACSW, GPEA, ALLCE, ALLC, ISDA, AGAC, HGAD.

### 2026-10-25 — R16 Tracking difference from NAV, using issuer-published calendar-year returns
**Status:** Decided (follows the owner's instruction to use open sources; replaces measuring tracking difference from daily market prices)
**Context:** Open daily index data exists for MSCI ACWI only: MSCI's end-of-day data, free for informational, non-commercial use, with redistribution prohibited ([MSCI index terms](https://www.msci.com/legal/index-terms)). No free daily history was found for the Bloomberg Global Aggregate; Bloomberg's quote pages show snapshots only ([Bloomberg LEGATRUU](https://www.bloomberg.com/professional/products/indices/quote/LEGATRUU:IND)).
**Evidence (own test, 2026-10-25, Yahoo prices vs MSCI ACWI Net USD, trailing 3 years):**
- US-listed ACWI correlates 0.95 with the index on the same day, so the dates are aligned.
- LSE listings split between the same day (0.69) and the next (0.33), because they close hours before MSCI's index close.
- Annualised monthly tracking error from market prices was 2.4% for LSE listings, and calendar-year tracking differences swung by about ±2%. That's 10–20 times the cost differences being ranked.
- Yahoo also had a bad print: ISDA.AS +35% on 2025-12-31.
- Conclusion: market prices can't rank tracking difference. The standard measure uses NAV, struck at the same closing prices as the index (issuers and the ESMA guidelines report NAV-based tracking difference).
**Rule:**
- Tracking difference = annualised fund NAV total return − annualised benchmark return over the last 3 complete calendar years (R2), from the calendar-year figures in the issuer's factsheet or KID.
- These go in `reference/annual_returns.csv` with source and date.
- A share class with fewer than 3 complete calendar years is ranked on what it has and flagged (R11).
- Daily MSCI and Yahoo data are still used for spreads (R10), FX (R1), and as a cross-check on the factsheet figures.
**Alternatives considered:** Daily market-price tracking difference (rejected: evidence above). Scraping issuer NAV history (rejected for now: each issuer's site differs and loads data in the browser, so it would be fragile). Paid index data (rejected: the owner asked for open sources).
**Effect:** Tracking difference is now annual rather than daily. Calendar-year results lag by up to one year; the factsheet is updated monthly, but its calendar-year table only changes in January.

**Update 2026-10-25:**
- iShares factsheets compare USD-hedged share classes against the fund's *unhedged* benchmark (AGGU 2022: −11.65% vs −16.25%), so a factsheet's benchmark column can't always be used as-is.
- Benchmark returns are therefore stored once per variant in `reference/benchmark_returns.csv`, taken from a factsheet whose benchmark matches the variant. SPDR's hedged factsheets print the USD-hedged index LEGATRUH.
- Within a variant, ranking by annualised NAV return gives the same order as ranking by tracking difference, because the index return is common to all of them.
- First result (2023–2025, 10 verified classes): every tracking difference is between −0.21% and +0.05% a year, consistent with the funds' 0.10–0.32% expense ratios after withholding effects.

### 2026-10-25 — R17 Near-equivalents shown in a separate comparison table
**Status:** Decided by owner 2026-10-25 ("separate comparison")
**Rule:** Funds tracking a close but different index (currently VWRA on FTSE All-World and VAGU on Bloomberg Global Aggregate Float Adjusted and Scaled) are listed in `reference/near_equivalents.csv`. They are shown in a separate table with expense ratio, tracking difference against their *own* index, withholding and trading costs. They are never ranked against the candidates and can't trigger a switch (R14).
**Evidence:** Vanguard factsheets (as at 2026-09-30): VWRA OCF 0.14%, 3-year NAV return 21.65% a year vs FTSE All-World 21.65%; VAGU OCF 0.08%, 3.97% vs 4.07%. Vanguard reports trailing periods to quarter-end, not calendar years, so the window differs from the candidates' (R16) and is labelled in the table.

### 2026-10-25 — R14 refinement: only count years when the fund tracked the exact index
**Status:** Decided (follows R14)
**Rule:** Calendar years before a share class switched to the exact benchmark are excluded from its tracking difference.
**Evidence:** Amundi switched LU1437024729 (GAGU) from the Bloomberg Barclays Global Aggregate 500M index on 2024-01-17 ([LSE RNS, 14 Dec 2023](https://lse.co.uk/rns/GAGG/amundi-etf-8211-important-information-8211-index-and-name-change-8211-17012024-71bseuis9tjm7zy.html?page=22)). Its 2024–2025 returns qualify; 2023 does not.
