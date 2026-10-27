import os
import subprocess
import sys
import unittest

from tests.helpers import ROOT


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


class RepoTest(unittest.TestCase):
    def test_skills_pass_lint(self):
        r = run('tools/lint_skills.py')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_shared_files_in_sync(self):
        r = run('tools/sync_shared.py', '--check')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_evals_pass(self):
        r = run('evals/run_evals.py')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_cli_entry_points(self):
        case = os.path.join('evals', 'cases', '01-finance-automation-po-dublin')
        r = run('shared/scripts/ats_score.py', '--compare', f'{case}/cv.md', f'{case}/output.json')
        self.assertIn('ATS score: 57 -> 75', r.stdout)
        r = run('shared/scripts/check_fabrication.py', f'{case}/cv.md', f'{case}/output.json')
        self.assertEqual(r.returncode, 0, r.stdout)
        r = run('shared/scripts/validate_output.py', f'{case}/output.json')
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == '__main__':
    unittest.main()
