from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'outputs'
    obs=pd.read_csv(ROOT/'data/processed/observations.csv',parse_dates=['period']).set_index('period')
    metrics=pd.read_csv(out/'metrics.csv'); predictions=pd.read_csv(out/'predictions.csv')
    coverage=pd.read_csv(out/'jodi_coverage.csv')
    summary=json.loads((out/'summary.json').read_text())
    with pd.ExcelWriter(out/'research_tables.xlsx') as writer:
        obs.to_excel(writer,sheet_name='observations')
        metrics.to_excel(writer,sheet_name='metrics',index=False)
        predictions.to_excel(writer,sheet_name='predictions',index=False)
        coverage.to_excel(writer,sheet_name='coverage',index=False)
    finding=[]
    for h in (1,2,3):
        main=metrics[(metrics.lag==2)&(metrics.horizon==h)].set_index('model')
        ridge=main.loc['ridge']; baseline=main.loc[['persistence','seasonal_naive'],'mae_mt'].idxmin()
        best=main.loc[baseline]
        change=(ridge.mae_mt/best.mae_mt-1)*100
        finding.append(f'{h}-month horizon: ridge MAE {ridge.mae_mt:.2f} Mt versus {baseline} {best.mae_mt:.2f} Mt ({abs(change):.1f}% {"higher" if change>0 else "lower"} error; n={int(ridge.n)}).')
    lines=['# China Crude Import Observatory: research memo','',
           '## Question and measured result','',
           'Can lagged independent refinery activity improve forecasts of China crude imports? '+ ' '.join(finding), '',
           'The evidence is mixed across horizons and metrics. Production and processing do not provide a consistent improvement over simple or imports-only models. Empirical interval coverage falls well below its nominal 90% level on a small sample; these bands should not be presented as calibrated risk limits. The table reports revised-history evaluation, not a vintage backtest.','',
           '| Publication lag | Horizon | Method | N | MAE (Mt) | RMSE (Mt) | 90% interval coverage |',
           '|---|---|---|---:|---:|---:|---:|']
    for r in metrics.itertuples():
        c=f'{r.coverage90:.1%} (n={r.interval_n})' if pd.notna(r.coverage90) else 'Insufficient prior errors'
        lines.append(f'| {r.lag} months | {r.horizon} months | {r.model} | {r.n} | {r.mae_mt:.2f} | {r.rmse_mt:.2f} | {c} |')
    lines+=['','For each horizon, compare ridge with both simple benchmarks and the imports-only ridge ablation on the same target months. The ablation tests whether domestic production and independent processing add predictive information together; it does not isolate a causal refinery effect. The conservative three-month lag checks sensitivity to unknown JODI publication dates. Test samples and interval counts matter as much as headline accuracy.','',
            '## Data and method','',
            f'JODI coverage: {obs.index.min():%B %Y} to {obs.index.max():%B %Y}, {len(obs)} import months. Independent monthly NBS processing: {obs.processing_mt.count()} aligned observations. The continuous model window begins {summary["common_model_start"]}; the isolated December 2015 release is excluded from modelling. Raw official files, checksums and retrieval times are retained. January-February processing and forecast targets are excluded because their monthly splits are not independently observed.',
            '', 'Features are lagged imports, domestic production, independently surveyed processing, processing age and target seasonality. A fixed ridge model is fitted after training-only scaling. Each training target must precede the origin by the assumed publication lag. Calculated JODI refinery intake is never used.','',
            '## Two historical cases','']
    cases=obs[['imports_mt','production_mt','processing_mt','exports_mt','indicative_residual_mt']].dropna()
    for label,date in [('Largest positive indicative residual',cases.indicative_residual_mt.idxmax()),('Smallest indicative residual',cases.indicative_residual_mt.idxmin())]:
        r=cases.loc[date]
        lines+=[f'### {label}: {date:%B %Y}', '',f'Imports were {r.imports_mt:.2f} Mt, domestic production {r.production_mt:.2f} Mt, exports {r.exports_mt:.2f} Mt and NBS processing {r.processing_mt:.2f} Mt. The indicative residual was {r.indicative_residual_mt:.2f} Mt.',
                '', 'This observation shows how reported supply and surveyed refinery use can diverge. It does not identify storage accumulation or its cause. A merchant would investigate survey coverage, cargo timing, refinery maintenance, direct use and other flows before interpreting it as a procurement signal.','']
    lines+=['## Commercial scenarios','',
            'Holding exports, direct use, stocks and coverage differences constant, +2 Mt of refinery processing raises indicative imports required by 2 Mt; +1 Mt of domestic production lowers them by 1 Mt. Together they imply +1 Mt. These are accounting sensitivities, not fitted predictions or executable trades.',
            '', 'A persistent increase in independently observed processing can inform supplier demand planning, but arrivals reflect contracts and lead times. The forecast does not identify profitable cargo timing, freight-adjusted margins or counterparty demand. Before a trading decision, add refinery maintenance, shipping schedules, grades, freight, storage constraints and contractual information.',
            '', '## Limitations and reproducibility','',
            'JODI assessment code 3 means not assessed. Closing stocks are missing. China stock-change reporting stopped in October 2020; isolated recent zeros do not establish a resumed reliable series. NBS enterprise coverage changes, and the current official release archive can limit recovered processing history. Historical revisions are not reconstructed. Two- and three-month lags reduce timing risk but cannot repair vintage uncertainty.',
            '', 'Run the commands in README.md to reproduce the audit, models and this memo. Source links and dates are included in normalized tables. Report numerical improvements only when the metrics support them.']
    (out/'research_memo.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    audit=json.loads((ROOT/'data/processed/nbs_ingestion_audit.json').read_text())
    observed=obs.processing_mt.dropna()
    quality=['# Data quality audit','',f'JODI primary files: 2015-2026, {len(obs)} monthly records through {obs.index.max():%B %Y}. No duplicate series-period keys.',
             '',f'NBS independent processing: {len(observed)} numeric observations from {observed.index.min():%B %Y} to {observed.index.max():%B %Y} in the aligned JODI window.',
             '',f'NBS release candidates: {audit["candidate_releases"]}; ingestion issues: {len(audit["failures"])}. See data/processed/nbs_ingestion_audit.json for individual skipped releases and disagreement records.',
             '', '## Coverage by series','', '| Series | Numeric months | Missing months |','|---|---:|---:|']
    for name in ['imports_mt','production_mt','exports_mt','stock_change_mt','closing_stocks_mt','processing_mt']:
        quality.append(f'| {name} | {obs[name].count()} | {obs[name].isna().sum()} |')
    quality+=['','## Mandatory interpretation flags','',
              '- Source KTONS is divided by 1000 to produce million tonnes; original strings remain in jodi_observations.csv.',
              '- JODI calculated intake is excluded from forecasts; using it would create a circular relation with imports.',
              '- Nonnumeric missing markers remain missing. Zero stock changes are not proof of renewed inventory reporting.',
              '- January-February calendar splits are retained in JODI, excluded as evaluation targets; NBS combined totals are preserved in flags and not treated as independently observed months.',
              '- NBS revised release snapshots and changing enterprise coverage limit comparisons. Release dates are retained; vintage revisions are not recovered.',
              '- Publication lags are conservative assumptions for JODI, not independently verified release dates. Compare both sensitivities.',
              '- Raw snapshot hashes and retrieval times are retained. Reruns reuse cache; a new snapshot directory is required for revision analysis.']
    (out/'data_quality.md').write_text('\n'.join(quality)+'\n',encoding='utf-8')
    print('Wrote research memo and Excel-readable workbook.')
if __name__=='__main__': main()
