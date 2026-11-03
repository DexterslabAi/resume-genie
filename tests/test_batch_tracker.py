import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tests.helpers import ROOT
import batch_tracker as bt


def job(**kw):
    base = {'company': 'Acme Analytics', 'role': 'Data Engineer', 'location': 'Dublin',
            'apply_url': 'https://example.com/jobs/1', 'fit': 82, 'ats_before': 60, 'ats_after': 88,
            'audit': 'clean', 'placeholders': 1,
            'salary': {'advert': 'EUR 80,000-95,000', 'ask': 'EUR 90,000-95,000'}}
    base.update(kw)
    return base


def batch(jobs, **settings):
    return {'settings': {**bt.DEFAULTS, 'candidate': 'Alex Morgan', **settings}, 'jobs': jobs}


class BatchTrackerTest(unittest.TestCase):
    def test_gates(self):
        d = batch([job(), job(company='Low Fit Ltd', fit=55), job(company='Short Ltd', ats_after=72),
                   job(company='Dirty Ltd', audit='failed')])
        bt.check(d)
        status = [j['status'] for j in d['jobs']]
        self.assertEqual(status, ['ready', 'skipped', 'skipped', 'skipped'])
        self.assertIn('fit 55 below 70', d['jobs'][1]['skip_reason'])
        self.assertIn('ATS 72 below 80', d['jobs'][2]['skip_reason'])
        self.assertIn('audit not clean', d['jobs'][3]['skip_reason'])

    def test_thresholds_come_from_settings(self):
        d = batch([job(fit=65)], fit_threshold=60)
        bt.check(d)
        self.assertEqual(d['jobs'][0]['status'], 'ready')

    def test_unsupported_salary_ask_is_cleared(self):
        d = batch([job(salary={'ask': 'EUR 120,000'})])
        notes = bt.check(d)
        self.assertEqual(d['jobs'][0]['salary']['ask'], 'No reliable data')
        self.assertTrue(any('no advert range or cited source' in m for _, m in notes))

    def test_cited_salary_ask_is_kept(self):
        sal = {'sources': [{'name': 'Survey', 'url': 'https://example.com/s', 'range': 'EUR 85k-100k'}], 'ask': 'EUR 95,000'}
        d = batch([job(salary=sal)])
        bt.check(d)
        self.assertEqual(d['jobs'][0]['salary']['ask'], 'EUR 95,000')

    def test_duplicate_adverts_flagged(self):
        d = batch([job(company='Agency One', role='AI & Digital Transformation Manager'),
                   job(company='Agency Two', role='AI and Digital Transformation Manager'),
                   job(company='Other Co', role='Finance Systems Analyst')])
        bt.check(d)
        self.assertIn('possible duplicate of #1', d['jobs'][1]['flags'])
        self.assertNotIn('possible duplicate of #1', d['jobs'][2].get('flags', []))

    def test_safe_names(self):
        self.assertEqual(bt.safe_name('Grant Thornton: CFO / Advisory?'), 'Grant Thornton CFO Advisory')
        self.assertEqual(bt.file_stem('Alex Morgan', 'R&D Labs', 'Senior Engineer'), 'Alex_Morgan_CV_R_D_Labs_Senior_Engineer')

    def test_folders_and_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = batch([job(), job(company='Northwind Finance', role='FP&A Manager', fit=50)], output_dir=tmp)
            bt.check(d)
            made = bt.folders(d)
            self.assertEqual(made, [os.path.join(tmp, 'Acme Analytics')])
            self.assertTrue(os.path.isdir(made[0]))
            self.assertTrue(d['jobs'][0]['files']['docx'].endswith('Alex_Morgan_CV_Acme_Analytics_Data_Engineer.docx'))
            out = bt.table(d)
            self.assertIn('| 1 | Acme Analytics, Data Engineer (Dublin) | 82 | 60 to 88 |', out)
            self.assertIn('[Apply](https://example.com/jobs/1)', out)
            self.assertIn('EUR 90,000-95,000', out)
            self.assertIn('Skipped: #2 Northwind Finance (fit 50 below 70)', out)

    def test_batch_size_limits_table(self):
        d = batch([job(company=f'Co {i}', role=f'Role {i} {"x" * i}') for i in range(12)], batch_size=10)
        bt.check(d)
        self.assertEqual(bt.table(d).count('| Co '), 10)

    def test_next_batch_waits_for_applications(self):
        d = batch([job(), job(company='Beta Systems', role='Platform Engineer')])
        bt.check(d)
        self.assertEqual(bt.pending(d), [1, 2])
        self.assertEqual(bt.mark_applied(d, '1'), 1)
        self.assertEqual(bt.pending(d), [2])
        bt.mark_applied(d, 'all')
        self.assertEqual(bt.pending(d), [])
        bt.check(d)  # applied roles are never reopened
        self.assertEqual({j['status'] for j in d['jobs']}, {'applied'})

    def test_declined_roles_count_as_done(self):
        d = batch([job(), job(company='Beta Systems', role='Platform Engineer'), job(company='Gamma Bank', role='FP&A Lead')])
        bt.check(d)
        self.assertEqual(bt.mark_applied(d, '1'), 1)
        self.assertEqual(bt.mark_declined(d, '2', 'prefers hybrid'), 1)
        self.assertEqual(bt.pending(d), [3])
        bt.mark_declined(d, '3')
        self.assertEqual(bt.pending(d), [])
        self.assertEqual(d['jobs'][1]['decline_reason'], 'prefers hybrid')
        self.assertNotIn('decline_reason', d['jobs'][2])
        bt.check(d)  # declined roles are never reopened
        self.assertEqual([j['status'] for j in d['jobs']], ['applied', 'declined', 'declined'])
        out = bt.table(d)
        self.assertIn('Not applying: #2 Beta Systems (prefers hybrid); #3 Gamma Bank', out)
        self.assertIn('Applied: 1. Not applying: 2. Still to decide: 0.', out)

    def test_declined_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'batch.json')
            with open(path, 'w') as f:
                json.dump(batch([job(), job(company='Beta Systems', role='Platform Engineer')]), f)
            script = os.path.join(ROOT, 'shared', 'scripts', 'batch_tracker.py')
            run = lambda *a: subprocess.run([sys.executable, script, a[0], path, *a[1:]], capture_output=True, text=True)
            run('check')
            run('applied', '1')
            self.assertEqual(run('next').returncode, 1)
            self.assertIn('1 role(s) marked as not applying', run('declined', '2', 'not interested').stdout)
            self.assertEqual(run('next').returncode, 0)
            self.assertEqual(run('declined').returncode, 2)

    def test_pdf_without_libreoffice(self):
        d = batch([job()])
        bt.check(d)
        with mock.patch.object(bt.shutil, 'which', return_value=None):
            self.assertIsNone(bt.pdf(d))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'batch.json')
            with open(path, 'w') as f:
                json.dump(batch([job()], output_dir=os.path.join(tmp, 'out')), f)
            script = os.path.join(ROOT, 'shared', 'scripts', 'batch_tracker.py')
            run = lambda *a: subprocess.run([sys.executable, script, *a, path] if len(a) == 1 else [sys.executable, script, a[0], path, *a[1:]],
                                            capture_output=True, text=True)
            self.assertIn('1 role(s) ready', run('check').stdout)
            self.assertEqual(run('next').returncode, 1)
            self.assertEqual(run('applied', 'all').returncode, 0)
            self.assertEqual(run('next').returncode, 0)


if __name__ == '__main__':
    unittest.main()
