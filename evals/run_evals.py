#!/usr/bin/env python3
"""Resume Genie evaluation suite.

For every case in evals/cases/<id>/ (cv.md, jd.md, optional notes.md, output.json, case.json):
  1. the output matches the schema
  2. the fabrication check is clean: no invented numbers, employers or dates
  3. the ATS score (calculated) rises by at least the expected amount
  4. placeholders are used where the candidate must supply numbers
  5. Word files build in all four templates, with the case's regional extras

Then the adversarial suite takes a clean output, injects fabrications (an invented metric,
a fake employer, a shifted date, an unflagged placeholder, an inflated percentage) and
confirms the guardrail catches every one.

  python evals/run_evals.py            # print a report; exit 1 on any failure
  python evals/run_evals.py --write    # also save evals/RESULTS.md

Author: Rahul Kashyap. MIT licence.
"""
import copy
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'shared', 'scripts'))

from ats_score import compare  # noqa: E402
from check_fabrication import check  # noqa: E402
from validate_output import validate  # noqa: E402

SCHEMA = json.load(open(os.path.join(ROOT, 'shared', 'references', 'output-schema.json')))
CASES = os.path.join(ROOT, 'evals', 'cases')


def read(path, default=''):
    return open(path, encoding='utf-8').read() if os.path.exists(path) else default


def run_case(case_id):
    d = os.path.join(CASES, case_id)
    meta = json.load(open(os.path.join(d, 'case.json')))
    cv, notes = read(os.path.join(d, 'cv.md')), read(os.path.join(d, 'notes.md'))
    output = json.load(open(os.path.join(d, 'output.json')))
    exp = meta.get('expect', {})
    schema_errors = validate(output, SCHEMA)
    fab = check(cv, output, notes)
    ats = compare(cv, output)
    built = build_all_templates(output, meta.get('build', {}))
    checks = {
        'schema valid': not schema_errors,
        'nothing invented': fab['clean'] == exp.get('fabrication_clean', True),
        f"ATS gain >= {exp.get('min_ats_gain', 0)}": ats['gain'] >= exp.get('min_ats_gain', 0),
        f"placeholders >= {exp.get('min_placeholders', 0)}": fab['placeholders'] >= exp.get('min_placeholders', 0),
        'Word files build': built is True,
    }
    return {
        'id': case_id, 'title': meta['title'], 'region': meta.get('region'), 'checks': checks,
        'ats': f"{ats['before']['score']} -> {ats['after']['score']} ({ats['gain']:+d})",
        'placeholders': fab['placeholders'], 'issues': fab['issues'] + [{'type': 'schema', 'value': e} for e in schema_errors],
        'build_error': None if built is True else built,
    }


def build_all_templates(output, extras):
    try:
        from build_docx import TEMPLATES, build_cv, build_letter
    except ImportError:
        return True  # python-docx not installed: skip the build step rather than fail the eval
    try:
        with tempfile.TemporaryDirectory() as tmp:
            for t in TEMPLATES:
                build_cv(output['cv'], os.path.join(tmp, f'{t}.docx'), template=t,
                         header_lines=extras.get('header', []), details=[tuple(x) for x in extras.get('details', [])],
                         languages=extras.get('languages', ''))
            build_letter(output['cover_letter'], os.path.join(tmp, 'letter.docx'), name=output['cv']['name'])
        return True
    except Exception as e:  # report, don't crash the whole suite
        return f'{type(e).__name__}: {e}'


# Each mutation injects one kind of fabrication into a clean output.
def _bullet(o):
    return o['cv']['experience'][0]['bullets']


MUTATIONS = [
    ('invented team size', 'invented_number', lambda o: _bullet(o).append({'text': 'Managed a team of 14 analysts across Europe.'})),
    ('inflated percentage', 'invented_number', lambda o: _bullet(o).__setitem__(0, {'text': 'Cut invoice processing time by 85% across 6 countries.'})),
    ('invented revenue', 'invented_number', lambda o: o['cv'].__setitem__('summary', o['cv']['summary'] + ' Delivered EUR 3.2m in annual savings.')),
    ('fake employer', 'unknown_employer', lambda o: o['cv']['experience'][0].__setitem__('company', 'Google')),
    ('shifted dates', 'changed_date', lambda o: o['cv']['experience'][-1].__setitem__('dates', '2012 - 2017')),
    ('unflagged placeholder', 'unflagged_placeholder', lambda o: _bullet(o).append({'text': 'Saved [X%] on supplier spend.', 'needs_confirmation': False})),
]


def run_adversarial(case_id='01-finance-automation-po-dublin'):
    d = os.path.join(CASES, case_id)
    cv, notes = read(os.path.join(d, 'cv.md')), read(os.path.join(d, 'notes.md'))
    clean = json.load(open(os.path.join(d, 'output.json')))
    results = []
    for name, expected_type, mutate in MUTATIONS:
        o = copy.deepcopy(clean)
        mutate(o)
        found = {i['type'] for i in check(cv, o, notes)['issues']}
        results.append({'mutation': name, 'expected': expected_type, 'caught': expected_type in found})
    return results


def report(cases, adversarial):
    lines = ['# Evaluation results', '',
             'Generated by `python evals/run_evals.py --write`. The scores are calculated by `ats_score.py`, not estimated by a model.', '',
             '## Cases', '', '| Case | Region | ATS before -> after | Placeholders | Checks |', '|---|---|---|---|---|']
    for c in cases:
        passed = sum(c['checks'].values())
        lines.append(f"| {c['title']} | {c['region']} | {c['ats']} | {c['placeholders']} | {passed}/{len(c['checks'])} pass |")
    lines += ['', '## Adversarial: injected fabrications the guardrail must catch', '', '| Injected | Expected flag | Caught |', '|---|---|---|']
    for a in adversarial:
        lines.append(f"| {a['mutation']} | `{a['expected']}` | {'yes' if a['caught'] else '**NO**'} |")
    total = sum(len(c['checks']) for c in cases) + len(adversarial)
    passed = sum(sum(c['checks'].values()) for c in cases) + sum(a['caught'] for a in adversarial)
    lines += ['', f'**{passed}/{total} checks passed.**', '']
    return '\n'.join(lines), passed == total


def main(argv):
    cases = [run_case(c) for c in sorted(os.listdir(CASES)) if os.path.isdir(os.path.join(CASES, c))]
    adversarial = run_adversarial()
    text, ok = report(cases, adversarial)
    print(text)
    for c in cases:
        for name, passed in c['checks'].items():
            if not passed:
                print(f"FAIL {c['id']}: {name}", c['issues'] or c['build_error'] or '')
    if '--write' in argv:
        open(os.path.join(ROOT, 'evals', 'RESULTS.md'), 'w').write(text)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
