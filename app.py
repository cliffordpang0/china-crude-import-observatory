from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).parent
st.set_page_config(page_title='China Crude Import Observatory',layout='wide')
st.title('China Crude Import Observatory')
path=ROOT/'data/processed/observations.csv'
if not path.exists():
    st.warning('Research outputs are not yet available. Complete data ingestion and evaluation.'); st.stop()
df=pd.read_csv(path,parse_dates=['period']).set_index('period')
metrics=pd.read_csv(ROOT/'outputs/metrics.csv')
pred=pd.read_csv(ROOT/'outputs/predictions.csv',parse_dates=['origin','target'])
summary=json.loads((ROOT/'outputs/summary.json').read_text())
st.caption(f"Official JODI and NBS observations | Million tonnes | Latest import month: {df.index.max():%B %Y}")
cols=st.columns(3)
cols[0].metric('Latest crude imports',f'{df.imports_mt.dropna().iloc[-1]:.2f} Mt')
cols[1].metric('Independent processing observations',int(df.processing_mt.count()))
cols[2].metric('Historical import months',len(df))
start,end=st.select_slider('Balance observation window',options=list(df.index.date),value=(df.index[0].date(),df.index[-1].date()))
view=df.loc[str(start):str(end)]
balance,forecast,scenario,quality=st.tabs(['Balances','Forecasts','Scenarios','Data quality'])
with balance:
    series=st.multiselect('Series', ['imports_mt','processing_mt','production_mt','exports_mt'],default=['imports_mt','processing_mt'])
    if series:
        st.plotly_chart(px.line(view.reset_index(),x='period',y=series,labels={'value':'Million tonnes','period':'Month','variable':'Series'}),width='stretch')
    a,b=st.columns(2)
    seasonal=view.reset_index().assign(month=lambda x:x.period.dt.month,year=lambda x:x.period.dt.year)
    a.plotly_chart(px.line(seasonal,x='month',y='imports_mt',color='year',labels={'imports_mt':'Imports (Mt)','month':'Calendar month'}),width='stretch')
    yoy=df[['imports_mt','processing_mt','production_mt']].pct_change(12,fill_method=None)*100
    b.plotly_chart(px.line(yoy.loc[str(start):str(end)].reset_index(),x='period',y=list(yoy.columns),labels={'value':'Year-on-year (%)','period':'Month'}),width='stretch')
    st.subheader('Indicative supply minus processing residual')
    st.plotly_chart(px.bar(view.reset_index(),x='period',y='indicative_residual_mt',labels={'indicative_residual_mt':'Million tonnes'}),width='stretch')
    st.caption('Imports + production - exports - surveyed processing. Coverage differences and omitted flows mean this is not measured inventory change. January-February processing is omitted.')
    st.download_button('Download observations',df.to_csv().encode(),'observations.csv','text/csv')
with forecast:
    a,b=st.columns(2)
    h=a.selectbox('Forecast horizon (months)',[1,2,3])
    lag=b.selectbox('Conservative publication lag (months)',[2,3])
    m=metrics[(metrics.horizon==h)&(metrics.lag==lag)]
    st.dataframe(m.drop(columns=['horizon','lag']),hide_index=True,width='stretch')
    p=pred[(pred.horizon==h)&(pred.lag==lag)]
    chart=p.pivot(index='target',columns='model',values='prediction_mt')
    chart['actual']=p.drop_duplicates('target').set_index('target').actual_mt
    st.plotly_chart(px.line(chart.reset_index(),x='target',y=list(chart.columns),labels={'value':'Million tonnes','target':'Target month'}),width='stretch')
    st.caption(summary['evaluation'])
    latest=pd.read_csv(ROOT/'outputs/latest_forecasts.csv')
    if not latest.empty:
        st.subheader('Current snapshot forecasts')
        st.dataframe(latest[latest.lag==lag],hide_index=True,width='stretch')
        st.caption('Current forecasts use the snapshot date shown. Their calendar origin is month-start; they are not vintage forecasts issued on that earlier date.')
    st.caption('Current forecasts are omitted when the required lagged import observation is unavailable or the target falls in January-February. Historical horizon evaluation remains available on supported target months.')
    st.caption('90% empirical error bands use only previously observable forecast errors; interval coverage is evaluated separately. Model comparisons use identical target months.')
    st.download_button('Download forecasts and errors',pred.to_csv(index=False).encode(),'predictions.csv','text/csv')
with scenario:
    a,b=st.columns(2)
    processing=a.slider('Change in refinery processing (Mt)',-10.0,10.0,0.0,0.5)
    production=b.slider('Change in domestic production (Mt)',-5.0,5.0,0.0,0.25)
    st.metric('Indicative change in import requirement',f'{processing-production:+.2f} Mt')
    st.caption('Accounting sensitivity, not a fitted forecast: one additional tonne of processing increases required imports by one tonne; one additional tonne of domestic production reduces them by one tonne. Exports, direct use, stocks and coverage differences are held constant.')
    st.download_button('Download scenario',pd.DataFrame([{'processing_change_mt':processing,'production_change_mt':production,'import_requirement_change_mt':processing-production}]).to_csv(index=False).encode(),'scenario.csv','text/csv')
with quality:
    st.dataframe(pd.read_csv(ROOT/'outputs/jodi_coverage.csv'),hide_index=True,width='stretch')
    st.warning('JODI refinery intake is supply-derived and excluded from forecasts. Closing stocks are missing. January-February values are calendar-disaggregated; those target months are excluded. Assessment code 3 means not assessed.')
    st.caption('Historical vintages were not recovered. Results use revised snapshots, conservative release lags and dated NBS releases. These results do not establish executable trading profits.')
    st.markdown('[JODI downloads](https://www.jodidata.org/oil/database/data-downloads.aspx) | [NBS releases](https://www.stats.gov.cn/sj/zxfb/)')
