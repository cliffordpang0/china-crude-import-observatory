"""Expanding-window, revised-history evaluation with conservative publication lags."""
from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parents[1]

def features(df, origin, target, lag):
    cutoff=origin-pd.DateOffset(months=lag)
    if cutoff not in df.index: return None
    prior=df.loc[:cutoff]
    processing=prior.processing_mt.dropna()
    if 'publication_date' in prior:
        processing=prior.loc[pd.to_datetime(prior.publication_date,errors='coerce')<=origin,'processing_mt'].dropna()
    if processing.empty: return None
    row={f'imports_lag{k}':df.imports_mt.get(origin-pd.DateOffset(months=k),np.nan) for k in (lag,lag+1,12)}
    row['production']=df.production_mt.get(cutoff,np.nan)
    row['processing']=processing.iloc[-1]
    row['processing_age']=(origin.year-processing.index[-1].year)*12+origin.month-processing.index[-1].month
    if row['processing_age']>lag+2:
        return None
    row['sin']=np.sin(2*np.pi*target.month/12); row['cos']=np.cos(2*np.pi*target.month/12)
    return row if np.isfinite(list(row.values())).all() else None

def load():
    df=pd.read_csv(ROOT/'data/processed/jodi_monthly.csv',parse_dates=['period']).set_index('period')
    nbs=pd.read_csv(ROOT/'data/processed/nbs_processing.csv',parse_dates=['period'])
    nbs=nbs.drop_duplicates('period').set_index('period')
    df=df.join(nbs[['processing_mt','publication_date']])
    # No independent observations exist for these disaggregated months.
    df.loc[df.index.month<=2,'processing_mt']=np.nan
    df['indicative_residual_mt']=df.production_mt+df.imports_mt-df.exports_mt-df.processing_mt
    return df

def main():
    df=load(); out=ROOT/'outputs'; out.mkdir(exist_ok=True)
    df.to_csv(ROOT/'data/processed/observations.csv')
    measured=df.processing_mt.dropna().index
    month_ids=pd.Series(measured.year*12+measured.month,index=measured)
    blocks=month_ids.diff().gt(3).cumsum()
    largest=blocks.value_counts().idxmax()
    common_start=measured[blocks.to_numpy()==largest][0]
    results=[]; forecasts=[]
    for lag in (2,3):
        for h in (1,2,3):
            examples=[]
            for target in df.index:
                if target<common_start: continue
                origin=target-pd.DateOffset(months=h)
                x=features(df,origin,target,lag)
                if x is not None and target.month>2 and pd.notna(df.loc[target,'imports_mt']):
                    examples.append((origin,target,x,float(df.loc[target,'imports_mt'])))
            for origin,target,x,actual in examples:
                training=[e for e in examples if e[1]<=origin-pd.DateOffset(months=lag)]
                if len(training)<36: continue
                model=make_pipeline(StandardScaler(),Ridge(alpha=10.0))
                model.fit(pd.DataFrame([e[2] for e in training]),[e[3] for e in training])
                import_columns=[k for k in x if k.startswith('imports_') or k in ('sin','cos')]
                import_model=make_pipeline(StandardScaler(),Ridge(alpha=10.0))
                import_model.fit(pd.DataFrame([e[2] for e in training])[import_columns],[e[3] for e in training])
                predictions={'ridge':float(model.predict(pd.DataFrame([x]))[0]),
                             'ridge_imports_only':float(import_model.predict(pd.DataFrame([x])[import_columns])[0]),
                             'seasonal_naive':float(df.imports_mt.get(target-pd.DateOffset(years=1),np.nan)),
                             'persistence':float(df.imports_mt.get(origin-pd.DateOffset(months=lag),np.nan))}
                for name,pred in predictions.items():
                    past=[abs(r['actual_mt']-r['prediction_mt']) for r in results if r['model']==name and r['horizon']==h and r['lag']==lag and pd.Timestamp(r['target'])<=origin-pd.DateOffset(months=lag)]
                    radius=float(np.quantile(past,.9)) if len(past)>=20 else np.nan
                    results.append(dict(origin=str(origin.date()),target=str(target.date()),horizon=h,lag=lag,model=name,actual_mt=actual,prediction_mt=pred,lower90=pred-radius,upper90=pred+radius,train_n=len(training)))
            if examples:
                origin=pd.Timestamp(datetime.now(ZoneInfo('Asia/Hong_Kong')).date()).replace(day=1)
                target=origin+pd.DateOffset(months=h)
                x=features(df,origin,target,lag)
                train=[e for e in examples if e[1]<=origin-pd.DateOffset(months=lag)]
                if x is not None and len(train)>=36 and target.month>2:
                    m=make_pipeline(StandardScaler(),Ridge(alpha=10.0)); m.fit(pd.DataFrame([e[2] for e in train]),[e[3] for e in train])
                    forecasts.append(dict(origin=str(origin.date()),snapshot_date=str(datetime.now(ZoneInfo('Asia/Hong_Kong')).date()),target=str(target.date()),horizon=h,lag=lag,prediction_mt=float(m.predict(pd.DataFrame([x]))[0])))
    r=pd.DataFrame(results)
    if r.empty: raise ValueError('Insufficient independent processing history for honest evaluation')
    r['error']=r.prediction_mt-r.actual_mt
    metrics=[]
    for keys,g in r.groupby(['lag','horizon','model']):
        intervals=g.dropna(subset=['lower90','upper90'])
        metrics.append(dict(lag=keys[0],horizon=keys[1],model=keys[2],n=len(g),mae_mt=g.error.abs().mean(),rmse_mt=np.sqrt((g.error**2).mean()),interval_n=len(intervals),coverage90=((intervals.actual_mt>=intervals.lower90)&(intervals.actual_mt<=intervals.upper90)).mean()))
    r.to_csv(out/'predictions.csv',index=False); pd.DataFrame(metrics).to_csv(out/'metrics.csv',index=False)
    pd.DataFrame(forecasts,columns=['origin','snapshot_date','target','horizon','lag','prediction_mt']).to_csv(out/'latest_forecasts.csv',index=False)
    summary={'first_month':str(df.index.min().date()),'last_month':str(df.index.max().date()),'common_model_start':str(common_start.date()),'months':len(df),'independent_processing_months':int(df.processing_mt.count()),'evaluation':'Revised historical snapshots; not a vintage point-in-time backtest. Origins are first day of month. Lags 2 and 3 months. Jan-Feb targets excluded. Fixed ridge alpha=10, no tuning. Isolated historical NBS samples excluded from model window.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(pd.DataFrame(metrics).to_string(index=False))

if __name__=='__main__': main()
