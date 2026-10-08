# Data quality audit

JODI primary files: 2015-2026, 139 monthly records through July 2026. No duplicate series-period keys.

NBS independent processing: 71 numeric observations from December 2015 to July 2026 in the aligned JODI window.

NBS release candidates: 110; ingestion issues: 106. See data/processed/nbs_ingestion_audit.json for individual skipped releases and disagreement records.

## Coverage by series

| Series | Numeric months | Missing months |
|---|---:|---:|
| imports_mt | 139 | 0 |
| production_mt | 139 | 0 |
| exports_mt | 135 | 4 |
| stock_change_mt | 73 | 66 |
| closing_stocks_mt | 0 | 139 |
| processing_mt | 71 | 68 |

## Mandatory interpretation flags

- Source KTONS is divided by 1000 to produce million tonnes; original strings remain in jodi_observations.csv.
- JODI calculated intake is excluded from forecasts; using it would create a circular relation with imports.
- Nonnumeric missing markers remain missing. Zero stock changes are not proof of renewed inventory reporting.
- January-February calendar splits are retained in JODI, excluded as evaluation targets; NBS combined totals are preserved in flags and not treated as independently observed months.
- NBS revised release snapshots and changing enterprise coverage limit comparisons. Release dates are retained; vintage revisions are not recovered.
- Publication lags are conservative assumptions for JODI, not independently verified release dates. Compare both sensitivities.
- Raw snapshot hashes and retrieval times are retained. Reruns reuse cache; a new snapshot directory is required for revision analysis.
