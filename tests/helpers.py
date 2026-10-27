import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'shared', 'scripts'))
CASE1 = os.path.join(ROOT, 'evals', 'cases', '01-finance-automation-po-dublin')
CASE2 = os.path.join(ROOT, 'evals', 'cases', '02-procurement-manager-dubai')
PHOTO = os.path.join(ROOT, 'tests', 'fixtures', 'photo.jpg')


def load_case(path):
    read = lambda f: open(os.path.join(path, f), encoding='utf-8').read() if os.path.exists(os.path.join(path, f)) else ''
    return read('cv.md'), json.load(open(os.path.join(path, 'output.json'))), read('notes.md')
