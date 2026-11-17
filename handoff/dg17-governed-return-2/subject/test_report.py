import unittest
from projection import render_report
from storage import report_key

class ReportTests(unittest.TestCase):
    def test_projection(self):
        self.assertEqual(render_report([{'id':'A','label':'Check','state':'ready'}], {'heading':'Tasks','separator':' / '}), 'Tasks\n\nA / Check / ready\n')
    def test_key_is_stable(self):
        rows = [{'id':'A','label':'Check','state':'ready'}]
        self.assertEqual(report_key(rows, 'compact'), report_key(rows, 'compact'))
    def test_changed_jobs_change_key(self):
        self.assertNotEqual(report_key([{'id':'A'}], 'compact'), report_key([{'id':'B'}], 'compact'))

if __name__ == '__main__':
    unittest.main()
