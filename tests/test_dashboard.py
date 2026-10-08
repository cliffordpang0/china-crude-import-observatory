from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
class Dashboard(unittest.TestCase):
    def test_filters_and_accounting_scenario(self):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        self.assertEqual(len(app.exception),0)
        app.selectbox[0].set_value(3); app.selectbox[1].set_value(3); app.run()
        self.assertEqual(len(app.exception),0)
        app.slider[0].set_value(2.0); app.slider[1].set_value(1.0); app.run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(app.metric[-1].value,'+1.00 Mt')
if __name__=='__main__': unittest.main()
