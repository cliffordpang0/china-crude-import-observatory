import sys
from pathlib import Path
import unittest
import pandas as pd
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evaluate import features, load
class Integrity(unittest.TestCase):
    def test_missing_and_units(self):
        x=pd.to_numeric(pd.Series(['-','0','1000']),errors='coerce')/1000
        self.assertTrue(pd.isna(x.iloc[0])); self.assertEqual(x.iloc[1],0); self.assertEqual(x.iloc[2],1)
    def test_no_future_features(self):
        ix=pd.date_range('2015-01-01',periods=60,freq='MS')
        df=pd.DataFrame({'imports_mt':np.arange(60.),'production_mt':20.,'processing_mt':50.,'publication_date':ix+pd.DateOffset(months=1,days=15)},index=ix)
        origin=ix[40]; target=ix[43]
        before=features(df,origin,target,2)
        df.loc[origin:,'imports_mt']=9999; df.loc[origin:,'processing_mt']=9999
        self.assertEqual(before,features(df,origin,target,2))
        self.assertGreaterEqual(before['processing_age'],2)
        self.assertNotIn('calculated_intake_mt',before)
    def test_observations(self):
        df=load(); self.assertTrue(df.index.is_unique)
        self.assertTrue(df.loc[df.index.month<=2,'processing_mt'].isna().all())
        self.assertTrue(df.imports_mt.notna().all())
if __name__=='__main__': unittest.main()
