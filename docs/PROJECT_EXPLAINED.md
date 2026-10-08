# China Crude Import Observatory, explained from the beginning

## The question in one sentence

Can information about refinery activity and domestic oil production help forecast how much crude oil China will import, beyond what simple historical patterns already tell us?

## 1. Why crude imports matter

Crude oil is oil before it has been processed into products such as petrol, diesel and jet fuel. Refineries perform that processing. China obtains crude from domestic production and imports.

For a supplier, changes in import demand help frame conversations about how much oil customers might need. For supply and shipping teams, they also provide context for procurement and transport planning. A monthly national forecast is only one input: it does not tell someone which cargo, grade, route or contract will be profitable.

This project connects a physical-market question with a transparent quantitative test. Its value is in the data discipline, benchmark comparisons and honest interpretation as well as the dashboard.

## 2. The physical intuition

Imagine refineries process 60 million tonnes of crude in a month while domestic producers supply 17 million tonnes. Before considering other flows, the remaining requirement is 43 million tonnes.

More refinery processing can raise the requirement for imported crude. More domestic production can reduce it. But arrivals may also reflect contracts agreed earlier, shipment timing and inventory use. The relationship is useful without being an exact forecasting rule.

The dashboard includes accounting scenarios:

| Assumed change | Indicative change in imports required |
|---|---:|
| Processing increases by 2 Mt | +2 Mt |
| Domestic production increases by 1 Mt | -1 Mt |
| Both changes occur together | +1 Mt |

Mt means million tonnes. These scenarios hold exports, direct use, stocks and coverage differences constant. They are accounting sensitivities, not fitted model predictions.

The project also computes imports + domestic production - exports - NBS processing. It calls this an **indicative residual**. It cannot be called measured inventory change because inventories are missing and the supply and processing series do not have identical coverage.

## 3. The evidence

The import and supply observations come from official JODI annual data files. Independent refinery-processing observations come from China's National Bureau of Statistics (NBS).

The saved dataset contains 139 monthly import observations from January 2015 through July 2026. It retains 72 numeric NBS processing observations through August 2026, of which 71 align with the JODI window. The continuous modelling window starts in August 2019. An isolated December 2015 observation is kept for audit and excluded from modelling.

January and February need special treatment. NBS reports combined activity, while JODI's activity figures are calendar-disaggregated. The project does not treat those splits as independently observed monthly processing, and excludes January-February forecast targets.

Official archive access was imperfect. The pipeline records failed retrievals and uses verified transcriptions from readable official releases where needed. Source links and provenance are retained. No demonstration observations fill the gaps.

## 4. The important circular-data problem

JODI publishes a China refinery-intake field, but it is calculated using other supply flows, including imports. If an input already contains part of the quantity being predicted, a model can appear informative for the wrong reason.

For that reason, this project excludes calculated JODI refinery intake from forecasting features. It uses independently surveyed NBS crude processing instead. Checking how a number is constructed is as important as checking whether it is present in a spreadsheet.

## 5. What the forecasts are compared with

| Method | Meaning |
|---|---|
| Seasonal naive | Predict the same imports as the corresponding month last year. |
| Persistence | Predict the latest import observation available under the assumed publication lag. |
| Imports-only ridge | Use previous imports and seasonal patterns in a statistical model. |
| Full ridge | Add domestic production, independent processing and the age of the processing observation. |

Ridge regression is a linear model that penalizes large coefficients. This helps limit overfitting: learning historical quirks that do not predict later observations. The regularization strength is fixed rather than chosen to look best on the test results.

The imports-only comparison asks whether adding production and processing together helps. It does not isolate a causal effect of refineries on imports.

## 6. How the test avoids looking into the future

The project repeatedly trains on earlier observations and evaluates forecasts for later months. This is an expanding chronological backtest. It does not randomly mix past and future data.

Inputs are delayed by at least two months, with a three-month lag tested as a sensitivity. NBS publication dates are respected, and training uses only targets considered observable at the forecast origin under the assumed lag. Scaling is fitted separately inside each training window.

For this project, an origin is the first day of a month. A one-month horizon refers to the subsequent calendar month, two months to the month after that, and so on.

Historical data vintages were not reconstructed. The evaluation uses revised snapshots, not necessarily the exact values available at every historical forecast date. Conservative publication lags reduce timing risk but do not remove revision uncertainty. This is not a fully point-in-time backtest.

## 7. What the results say

Under the two-month publication-lag assumption:

| Horizon | Full model MAE | Seasonal MAE | Evaluated observations |
|---|---:|---:|---:|
| One month | 4.34 Mt | 4.62 Mt | 29 |
| Two months | 4.71 Mt | 4.55 Mt | 27 |
| Three months | 4.33 Mt | 4.73 Mt | 25 |

MAE means **mean absolute error**: the average size of a forecast miss, ignoring whether it was too high or too low. Lower is better. A 4.34 Mt MAE does not mean every forecast missed by 4.34 Mt.

The full model's MAE is about 6.2% lower at one month and 8.4% lower at three months, but about 3.5% higher at two months. This is a conditional result, not consistent outperformance. The three-month publication lag changes the pattern, and other error measures do not always favor the same model.

RMSE means **root mean squared error**. It puts more weight on large misses than MAE. Both measures appear in the saved metrics.

The nominal 90% error bands also performed poorly. For the full model under the two-month lag, observed coverage was 28.6% at one month (7 eligible interval observations), 20.0% at two months (5), and 0% at three months (3). Those samples are tiny, but they do not support treating the bands as calibrated risk limits.

The honest conclusion is that adding physical-market information did not reliably improve every forecast. Negative findings are useful evidence about the limits of this dataset and model.

## 8. What the dashboard lets someone do

- Inspect actual imports, processing and production over a selected date range.
- Compare seasonality and year-on-year changes.
- Compare historical forecasts and errors by horizon and assumed publication lag.
- Explore indicative changes in import requirements under processing and production scenarios.
- Review coverage, missing observations and source caveats.
- Download tables for further inspection.

It runs locally. A localhost link works only on the computer running the app; it is not a public demonstration site.

## 9. What was built and what was established

The project delivers a reproducible pipeline, source audit, model evaluation, dashboard, Excel export and research memo.

It finds some forecast improvements under specific assumptions. It does not establish causality, consistently superior forecasts, measured inventories or profitable trades. NBS enterprise coverage changes over time; JODI assessment code 3 means not assessed, rather than validated quality.

## 10. A recruiter explanation

> I developed a research project to understand China's crude-oil imports using official public data. I tested whether refinery processing and domestic production could improve forecasts beyond simple historical benchmarks. A key finding was that one published refinery-intake series was partly calculated from imports, so I used independently surveyed processing data instead. I evaluated forecasts in chronological order and accounted for publication delays. The results were mixed, which I documented in a dashboard and research memo. The project connects physical oil flows with quantitative analysis and demonstrates careful data interpretation and honest communication of uncertainty.

When discussing personal contribution, describe the work you actually performed and reviewed. If asked, explain how AI assistance was used and which source choices, calculations and results you can independently defend.

## 11. Likely follow-up questions

**Why this project?** It provides a concrete physical-market question that can be investigated with official public data and explained commercially.

**Did the model work?** It produced forecasts and improved some average errors, but did not consistently outperform. That is the research result.

**Why a simple model?** The independent processing sample is modest. An interpretable model and strong simple benchmarks make the added value easier to assess.

**Could it support trading?** It can inform a demand discussion. A trading decision also needs refinery maintenance, cargo schedules, grades, freight, storage and contractual information.

**What would improve the research?** More independently verified processing history, reconstructed data vintages, better publication timing and additional operational information could support stronger tests. Any added complexity would still need to beat benchmarks on later observations.

## Inspect the evidence

- [Research memo and historical cases](../outputs/research_memo.md)
- [Full forecast metrics](../outputs/metrics.csv)
- [Excel research tables](../outputs/research_tables.xlsx)
- [Data-quality report](../outputs/data_quality.md)
- [Setup and reproduction instructions](../README.md#run-on-windows)
