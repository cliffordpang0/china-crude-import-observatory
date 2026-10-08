"""Discover official annual primary files and audit full China crude history."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
PAGE = 'https://www.jodidata.org/oil/database/data-downloads.aspx'
FLOWS = {'TOTIMPSB':'imports_mt','TOTEXPSB':'exports_mt','INDPROD':'production_mt',
         'REFINOBS':'calculated_intake_mt','STOCKCH':'stock_change_mt','CLOSTLV':'closing_stocks_mt'}
def main():
    raw, processed, outputs = ROOT/'data/raw/jodi', ROOT/'data/processed', ROOT/'outputs'
    for p in (raw, processed, outputs): p.mkdir(parents=True, exist_ok=True)
    response = requests.get(PAGE, timeout=60); response.raise_for_status()
    (raw/'download-page.html').write_text(response.text, encoding='utf-8')
    links = {}
    for a in BeautifulSoup(response.text,'html.parser').find_all('a',href=True):
        label, url = a.get_text(strip=True), urljoin(PAGE,a['href'])
        if re.fullmatch(r'20\d\d',label) and int(label)>=2015 and '.csv' in url.lower() and 'secondary' not in url.lower():
            links.setdefault(label,url)
    if len(links)<10: raise ValueError(f'Incomplete discovered links: {links}')
    frames, manifest = [], []
    for year,url in sorted(links.items()):
        path = raw/f'{year}.csv'
        if not path.exists():
            r=requests.get(url,timeout=120); r.raise_for_status(); path.write_bytes(r.content)
        df=pd.read_csv(path,dtype=str)
        df=df.loc[(df.REF_AREA=='CN')&(df.ENERGY_PRODUCT=='CRUDEOIL')&(df.UNIT_MEASURE=='KTONS')&df.FLOW_BREAKDOWN.isin(FLOWS)].copy()
        df['value_mt']=pd.to_numeric(df.OBS_VALUE,errors='coerce')/1000
        df['series']=df.FLOW_BREAKDOWN.map(FLOWS); df['period']=pd.to_datetime(df.TIME_PERIOD)
        df['source_url']=url; df['retrieved_at']=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()
        df['publication_date']=''
        df['normalized_unit']='million_tonnes'
        df['flags']=df.period.dt.month.map(lambda m:'jan_feb_calendar_disaggregated' if m<=2 else '')
        df.loc[df.series=='calculated_intake_mt','flags']+=';supply_derived_excluded_from_model'
        df.loc[df.ASSESSMENT_CODE=='3','flags']+=';not_assessed'
        df['flags']+=';historical_publication_date_unknown'
        frames.append(df)
        manifest.append({'url':url,'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'retrieved_at':df.retrieved_at.iloc[0]})
        print(f'{year}: {len(df)} China observations',flush=True)
    df=pd.concat(frames,ignore_index=True)
    duplicates=int(df.duplicated(['period','series']).sum())
    if duplicates: raise ValueError(f'{duplicates} duplicate observations')
    df.to_csv(processed/'jodi_observations.csv',index=False)
    wide=df.pivot(index='period',columns='series',values='value_mt').sort_index(); wide.to_csv(processed/'jodi_monthly.csv')
    df.assign(year=df.period.dt.year).groupby(['year','series']).agg(rows=('value_mt','size'),numeric=('value_mt','count'),not_assessed=('ASSESSMENT_CODE',lambda x:(x=='3').sum())).to_csv(outputs/'jodi_coverage.csv')
    (raw/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Full audit: {len(wide)} months, {duplicates} duplicates; latest {wide.index.max()}')
if __name__=='__main__': main()
