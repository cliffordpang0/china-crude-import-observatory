# China Crude Import Observatory: research memo

## Question and measured result

Can lagged independent refinery activity improve forecasts of China crude imports? 1-month horizon: ridge MAE 4.34 Mt versus seasonal_naive 4.62 Mt (6.2% lower error; n=29). 2-month horizon: ridge MAE 4.71 Mt versus seasonal_naive 4.55 Mt (3.5% higher error; n=27). 3-month horizon: ridge MAE 4.33 Mt versus seasonal_naive 4.73 Mt (8.4% lower error; n=25).

The evidence is mixed across horizons and metrics. Production and processing do not provide a consistent improvement over simple or imports-only models. Empirical interval coverage falls well below its nominal 90% level on a small sample; these bands should not be presented as calibrated risk limits. The table reports revised-history evaluation, not a vintage backtest.

| Publication lag | Horizon | Method | N | MAE (Mt) | RMSE (Mt) | 90% interval coverage |
|---|---|---|---:|---:|---:|---:|
| 2 months | 1 months | persistence | 29 | 4.66 | 6.49 | 42.9% (n=7) |
| 2 months | 1 months | ridge | 29 | 4.34 | 5.94 | 28.6% (n=7) |
| 2 months | 1 months | ridge_imports_only | 29 | 4.55 | 5.87 | 28.6% (n=7) |
| 2 months | 1 months | seasonal_naive | 29 | 4.62 | 6.41 | 28.6% (n=7) |
| 2 months | 2 months | persistence | 27 | 5.29 | 7.48 | 20.0% (n=5) |
| 2 months | 2 months | ridge | 27 | 4.71 | 6.60 | 20.0% (n=5) |
| 2 months | 2 months | ridge_imports_only | 27 | 4.92 | 6.44 | 20.0% (n=5) |
| 2 months | 2 months | seasonal_naive | 27 | 4.55 | 6.46 | 20.0% (n=5) |
| 2 months | 3 months | persistence | 25 | 4.82 | 7.79 | 0.0% (n=3) |
| 2 months | 3 months | ridge | 25 | 4.33 | 6.53 | 0.0% (n=3) |
| 2 months | 3 months | ridge_imports_only | 25 | 5.09 | 6.71 | 0.0% (n=3) |
| 2 months | 3 months | seasonal_naive | 25 | 4.73 | 6.66 | 0.0% (n=3) |
| 3 months | 1 months | persistence | 27 | 5.29 | 7.48 | 20.0% (n=5) |
| 3 months | 1 months | ridge | 27 | 4.73 | 6.55 | 20.0% (n=5) |
| 3 months | 1 months | ridge_imports_only | 27 | 4.86 | 6.34 | 20.0% (n=5) |
| 3 months | 1 months | seasonal_naive | 27 | 4.55 | 6.46 | 20.0% (n=5) |
| 3 months | 2 months | persistence | 25 | 4.82 | 7.79 | 0.0% (n=3) |
| 3 months | 2 months | ridge | 25 | 4.21 | 6.45 | 0.0% (n=3) |
| 3 months | 2 months | ridge_imports_only | 25 | 5.08 | 6.69 | 0.0% (n=3) |
| 3 months | 2 months | seasonal_naive | 25 | 4.73 | 6.66 | 0.0% (n=3) |
| 3 months | 3 months | persistence | 25 | 5.85 | 8.36 | 0.0% (n=2) |
| 3 months | 3 months | ridge | 25 | 4.94 | 6.80 | 0.0% (n=2) |
| 3 months | 3 months | ridge_imports_only | 25 | 5.17 | 6.82 | 0.0% (n=2) |
| 3 months | 3 months | seasonal_naive | 25 | 4.73 | 6.66 | 0.0% (n=2) |

For each horizon, compare ridge with both simple benchmarks and the imports-only ridge ablation on the same target months. The ablation tests whether domestic production and independent processing add predictive information together; it does not isolate a causal refinery effect. The conservative three-month lag checks sensitivity to unknown JODI publication dates. Test samples and interval counts matter as much as headline accuracy.

## Data and method

JODI coverage: January 2015 to July 2026, 139 import months. Independent monthly NBS processing: 71 aligned observations. The continuous model window begins 2019-08-01; the isolated December 2015 release is excluded from modelling. Raw official files, checksums and retrieval times are retained. January-February processing and forecast targets are excluded because their monthly splits are not independently observed.

Features are lagged imports, domestic production, independently surveyed processing, processing age and target seasonality. A fixed ridge model is fitted after training-only scaling. Each training target must precede the origin by the assumed publication lag. Calculated JODI refinery intake is never used.

## Two historical cases

### Largest positive indicative residual: June 2020

Imports were 53.18 Mt, domestic production 16.24 Mt, exports 0.07 Mt and NBS processing 57.87 Mt. The indicative residual was 11.48 Mt.

This observation shows how reported supply and surveyed refinery use can diverge. It does not identify storage accumulation or its cause. A merchant would investigate survey coverage, cargo timing, refinery maintenance, direct use and other flows before interpreting it as a procurement signal.

### Smallest indicative residual: December 2020

Imports were 38.47 Mt, domestic production 16.27 Mt, exports 0.25 Mt and NBS processing 60.00 Mt. The indicative residual was -5.51 Mt.

This observation shows how reported supply and surveyed refinery use can diverge. It does not identify storage accumulation or its cause. A merchant would investigate survey coverage, cargo timing, refinery maintenance, direct use and other flows before interpreting it as a procurement signal.

## Commercial scenarios

Holding exports, direct use, stocks and coverage differences constant, +2 Mt of refinery processing raises indicative imports required by 2 Mt; +1 Mt of domestic production lowers them by 1 Mt. Together they imply +1 Mt. These are accounting sensitivities, not fitted predictions or executable trades.

A persistent increase in independently observed processing can inform supplier demand planning, but arrivals reflect contracts and lead times. The forecast does not identify profitable cargo timing, freight-adjusted margins or counterparty demand. Before a trading decision, add refinery maintenance, shipping schedules, grades, freight, storage constraints and contractual information.

## Limitations and reproducibility

JODI assessment code 3 means not assessed. Closing stocks are missing. China stock-change reporting stopped in October 2020; isolated recent zeros do not establish a resumed reliable series. NBS enterprise coverage changes, and the current official release archive can limit recovered processing history. Historical revisions are not reconstructed. Two- and three-month lags reduce timing risk but cannot repair vintage uncertainty.

Run the commands in README.md to reproduce the audit, models and this memo. Source links and dates are included in normalized tables. Report numerical improvements only when the metrics support them.
