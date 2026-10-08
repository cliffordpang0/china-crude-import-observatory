import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nbs_ingest import parse_release
class NbsParser(unittest.TestCase):
    def fixture(self,title,monthly,cumulative):
        return f'<html><title>{title}</title><meta name="PubDate" content="2026-04-16"><table><tr><td>\u539f\u6cb9\u52a0\u5de5\u91cf(\u4e07\u5428)</td><td>{monthly}</td><td>2.0</td><td>{cumulative}</td></tr></table></html>'
    def test_monthly_not_cumulative(self):
        html=self.fixture('2026\u5e743\u6708\u4efd\u80fd\u6e90\u751f\u4ea7\u60c5\u51b5',6306,18225)
        row=parse_release(html,'https://www.stats.gov.cn/test')[0]
        self.assertEqual(row['processing_mt'],63.06)
        self.assertEqual(row['period'],'2026-03-01')
        self.assertEqual(row['publication_date'],'2026-04-16')
    def test_combined_monthly_missing(self):
        html=self.fixture('2026\u5e741-2\u6708\u4efd\u80fd\u6e90\u751f\u4ea7\u60c5\u51b5',11919,11919)
        rows=parse_release(html,'https://www.stats.gov.cn/test')
        self.assertEqual(len(rows),2)
        self.assertTrue(all(r['processing_mt']=='' for r in rows))
        self.assertTrue(all('119.19' in r['flags'] for r in rows))
    def test_challenge_not_observation(self):
        self.assertEqual(parse_release('<html><title>Access challenge</title></html>','https://www.stats.gov.cn/test'),[])
if __name__=='__main__': unittest.main()
