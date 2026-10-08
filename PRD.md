# China Crude Import Observatory

## Purpose

Build a reproducible research project for an undergraduate or recent graduate applying to Trafigura China and bp China supply, trading and shipping roles. Use real, free official data to explain and forecast China's crude imports. The finished work must demonstrate data sourcing, quantitative analysis, physical-market understanding and clear commercial communication.

## Commercial Question

Can lagged refinery activity, domestic production and seasonality improve forecasts of China's crude import volume at one-, two- and three-month horizons relative to simple benchmarks? What do changes in refinery activity imply for indicative import requirements?

An improvement is a research hypothesis, not an acceptance requirement. Report negative findings honestly.

## Users And Deliverables

The primary user is the applicant; secondary users are interviewers reviewing the analysis. Deliver a working Python project, an inspectable local analytical dashboard, reproducible historical evaluation, a data-quality report, a short commercial research memo and an Excel-readable export of the principal observations and results. Actual results must come before resume claims.

## Data Sources

1. JODI-Oil official annual primary CSVs: https://www.jodidata.org/oil/database/data-downloads.aspx
2. JODI China metadata workbook: https://www.jodidata.org/_resources/files/downloads/oil-data/jodi-oil-country-note.xlsx
3. JODI code definitions: https://www.jodidata.org/_resources/files/downloads/oil-data/jodi-oil-wdb-item-names-ver2017.pdf
4. NBS official crude-processing and domestic-production releases and National Data portal: https://data.stats.gov.cn/english/?cn=C01
5. Confirmed NBS historical release: https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1899018.html (December 2015).
6. Confirmed NBS release: https://www.stats.gov.cn/sj/zxfb/202601/t20260119_1962322.html (December 2025).
7. Confirmed NBS release: https://www.stats.gov.cn/sj/zxfbhjd/202609/t20260915_1965312.html (August 2026).
8. Combined January-February NBS example: https://www.stats.gov.cn/sj/zxfb/202603/t20260316_1962787.html.

Start with CSV downloads, which do not require an account. JODI API access requires registration; no API account is necessary for the first version. Follow links on the download page rather than assuming annual URL patterns: the 2026 filename is primaryyear2026.csv, whereas inspected completed years use YYYY.csv.

## Findings Already Verified On 2026-10-08

An initial audit downloaded the 2015, 2024, 2025 and 2026 JODI primary files and the country notes. China crude imports, exports, production and refinery-intake fields contain 12 numeric monthly observations in each inspected completed year. The inspected 2026 file contains January-July observations. This is a sample-year audit, not proof of complete intervening history.

Filter REF_AREA=CN, ENERGY_PRODUCT=CRUDEOIL and UNIT_MEASURE=KTONS. Imports are TOTIMPSB; exports TOTEXPSB; production INDPROD; refinery intake REFINOBS; stock change STOCKCH; closing stocks CLOSTLV. Convert thousand tonnes to million tonnes consistently. Keep source units and original values in the raw layer.

Critical: JODI's China REFINOBS is calculated from other supply flows, including imports. It is NOT an independently surveyed refinery-throughput feature. Do not use it as evidence that refinery activity predicts imports. Use NBS surveyed crude-processing volume for this purpose.

China closing stocks were missing throughout inspected files. Stock changes were numeric in 2015, missing throughout 2024 and 2025, and missing for March-July 2026; January-February 2026 contain numeric zeros. Metadata says China stopped reporting stock changes from October 2020. Do not infer that reporting resumed from those zeros; preserve the discrepancy in the audit.

JODI metadata says January-February activity has been combined and then calendar-day disaggregated since 2015. NBS directly publishes combined January-February activity. Do not describe imputed splits as independent monthly measurements.

NBS covers industrial enterprises above a revenue threshold; the surveyed enterprise population changes. Differences between JODI and NBS do not measure inventories directly. Assessment code 3 means not assessed, not validated quality.

## Scope

### Data Pipeline

- Discover and ingest official files and archived releases; retain immutable raw snapshots, source URLs, retrieval timestamps and checksums.
- Audit historical coverage before selecting a modelling window. Aim for 2015 onward, but use the verified common window if smaller and explain the reduction.
- Build a normalized observation table containing period, series, value, unit, source, publication date when known, retrieval date and quality or transformation flags.
- Treat nonnumeric missing markers as missing rather than zero. Preserve meaningful zeros and flag uncertain observations.
- Record revisions and duplicate observations. Make repeated ingestion idempotent.
- Parse structured tables or supported exports. Never bypass access restrictions, CAPTCHA or authentication; use readable official archives if a portal cannot be automated.
- Handle January-February through explicit combined-period handling or documented lagged/cumulative features. Any interpolation must be flagged and sensitivity-tested.

### Research And Forecasting

- Descriptive charts: imports, NBS crude processing, domestic production, seasonality and year-on-year changes with coverage annotations.
- Benchmarks: seasonal naive and a simple persistence or historical seasonal-average model.
- Begin with an interpretable regularized linear model and a small feature set. Add complexity only with evidence.
- Use rolling or expanding chronological evaluation at horizons 1, 2 and 3 months; never random train/test splits.
- Restrict every feature to what was available at the forecast origin. Current-month realised refinery throughput is not a valid earlier forecast input.
- Recover release dates where feasible. If vintage history cannot be recovered, label evaluation as using revised historical data; do not claim a fully point-in-time backtest. Show a conservative publication-lag sensitivity.
- Report MAE and RMSE in million tonnes and comparison with benchmarks by horizon. Provide prediction intervals with their empirical coverage if supported by sample size.
- Treat supply-minus-NBS-processing as an indicative residual with explicit coverage and omitted-flow caveats, not measured stock change.

### Commercial Scenarios

- Quantify changes in indicative import requirements under higher or lower independently measured refinery processing and domestic production, holding other assumptions explicit.
- Distinguish forecast estimates from accounting sensitivities and commercial interpretation.
- Discuss supplier-demand implications, timing uncertainty and additional information needed before a trading decision.
- Include two historical case studies using actual observations.

### Interface And Reports

- Prefer a small local Streamlit analytical app over a large web platform. Show real observations on the first screen, with tabs for balances, forecasts, scenarios and data quality.
- Include date and horizon controls, clear units, source links, last observation and forecast origin, missing-data states and downloadable tables.
- Do not fill data gaps with demonstration data. An empty state must explain missing inputs accurately.
- Keep charts and tables readable on desktop and narrow screens. Use restrained styling appropriate to research.
- Export machine-readable results and a two-page Markdown research memo suitable for conversion or further editing.

## Non-Goals

No live trading, investment recommendations, paid data subscriptions, vessel tracking, exact inventory estimation, synthetic trade blotters, guaranteed forecast outperformance or deep-learning-first development.

## Acceptance Criteria

1. A documented command ingests real official data and generates a coverage audit without secrets.
2. Imports and independent NBS processing are separately sourced and traceable.
3. Missing values, units, January-February handling and source discrepancies are visible and validated.
4. Chronological evaluation produces actual results for all supported horizons; unsupported horizons are explained, not fabricated.
5. No circular contemporaneous JODI refinery-intake feature or future information enters the model.
6. The local dashboard runs and displays real data, working filters, scenarios and downloadable results.
7. The memo reports measured results, two historical cases, data limitations and commercial implications.
8. README contains setup, ingestion, evaluation, reporting and dashboard commands, plus the working local URL when the server is started.
9. Focused checks cover parsing, missing markers, units, period alignment and temporal leakage. Verify the dashboard visually where tools permit.

## Implementation Sequence

Audit and ingest data first; select the common modelling window; implement benchmarks and evaluation; add scenarios and dashboard; write the memo from actual outputs; run checks and provide a clear handoff. If a source blocks progress, complete unaffected work and state the exact missing input and supported reduced scope.
