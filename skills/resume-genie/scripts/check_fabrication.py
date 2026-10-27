#!/usr/bin/env python3
"""Guardrail check: did the tailored CV invent anything?

Compares a Resume Genie output against the candidate's original CV (and any extra
facts they supplied) and reports:
  - numbers in the tailored CV that appear nowhere in the source and can't be derived
    from it (simple percentage change between two source numbers is allowed)
  - employers that don't appear in the source CV
  - dates whose years don't appear in the source CV
  - bullets containing a [placeholder] that aren't marked needs_confirmation
Text inside [placeholders] is ignored: placeholders are how Resume Genie asks the
candidate for numbers instead of inventing them.

Usage:
  python check_fabrication.py ORIGINAL_CV.txt OUTPUT.json [EXTRA_FACTS.txt]
Exit code 0 = clean, 1 = issues found.

Author: Rahul Kashyap. MIT licence.
"""
import json
import re
import sys

NUM_RE = re.compile(r'(?<![\w.])\d+(?:[.,]\d+)*(?:%|k|m|bn)?', re.I)
PLACEHOLDER_RE = re.compile(r'\[[^\]]*\]')


def _numbers(text):
    """Numeric tokens as normalised strings ('1,200' -> '1200', '56%' -> '56')."""
    out = set()
    for tok in NUM_RE.findall(PLACEHOLDER_RE.sub(' ', str(text or ''))):
        core = re.sub(r'(%|k|m|bn)$', '', tok, flags=re.I).replace(',', '')
        try:
            value = float(core)
        except ValueError:
            continue
        out.add(f'{value:g}')
    return out


def _derived(source_numbers):
    """Percentage changes and ratios between source numbers, so '9 days -> 4 days (56% faster)' is fine."""
    vals = sorted({float(n) for n in source_numbers if 0 < float(n) < 1_000_000})[:200]
    derived = set()
    for a in vals:
        for b in vals:
            if a == b:
                continue
            for pct in ((a - b) / a * 100, (b - a) / a * 100, b / a * 100):
                if 0 < pct <= 1000:
                    for r in (round(pct), int(pct)):
                        derived.add(f'{float(r):g}')
            if a and b / a == int(b / a):
                derived.add(f'{b / a:g}')  # "doubled", "3x"
    return derived


def _cv_lines(cv):
    yield 'headline', cv.get('headline', '')
    yield 'summary', cv.get('summary', '')
    for g in cv.get('skills', []):
        yield 'skills', ', '.join(g.get('items', []))
    for i, job in enumerate(cv.get('experience', [])):
        for j, b in enumerate(job.get('bullets', [])):
            yield f"experience[{i}] {job.get('company', '')} bullet {j + 1}", b['text'] if isinstance(b, dict) else b
    for p in cv.get('projects', []):
        yield 'projects', f"{p.get('title', '')} {p.get('details', '')}"
    for c in cv.get('certifications', []):
        yield 'certifications', c


def check(original_cv, output, extra_facts=''):
    source = f'{original_cv}\n{extra_facts}'
    source_lower = source.lower()
    allowed = _numbers(source)
    allowed |= _derived(allowed)
    issues = []
    cv = output.get('cv', {})

    for where, text in _cv_lines(cv):
        for n in sorted(_numbers(text) - allowed, key=float):
            issues.append({'type': 'invented_number', 'where': where, 'value': n, 'text': text})

    for job in cv.get('experience', []):
        company = (job.get('company') or '').strip()
        if company and company.lower() not in source_lower:
            core = re.sub(r'\b(ltd|limited|inc|llc|plc|gmbh|group|co)\.?$', '', company, flags=re.I).strip().lower()
            if not core or core not in source_lower:
                issues.append({'type': 'unknown_employer', 'where': 'experience', 'value': company})
        # Years must match this employer's own entry in the source CV, not just appear somewhere in it.
        lines = original_cv.splitlines()
        hits = [i for i, line in enumerate(lines) if company and company.lower() in line.lower()]
        window = ' '.join(' '.join(lines[i:i + 2]) for i in hits) if hits else source
        for year in re.findall(r'(?:19|20)\d{2}', job.get('dates', '')):
            if year not in window:
                issues.append({'type': 'changed_date', 'where': company or 'experience', 'value': year})

    for i, job in enumerate(cv.get('experience', [])):
        for j, b in enumerate(job.get('bullets', [])):
            if isinstance(b, dict) and PLACEHOLDER_RE.search(b.get('text', '')) and not b.get('needs_confirmation'):
                issues.append({'type': 'unflagged_placeholder', 'where': f"experience[{i}] bullet {j + 1}", 'value': b['text']})

    placeholders = sum(len(PLACEHOLDER_RE.findall(t)) for _, t in _cv_lines(cv))
    return {'clean': not issues, 'issues': issues, 'placeholders': placeholders}


def _main(argv):
    if len(argv) not in (3, 4):
        print(__doc__)
        return 2
    original = open(argv[1], encoding='utf-8').read()
    output = json.load(open(argv[2], encoding='utf-8'))
    extra = open(argv[3], encoding='utf-8').read() if len(argv) == 4 else ''
    r = check(original, output, extra)
    if r['clean']:
        print(f"Clean: nothing invented. {r['placeholders']} placeholder(s) for the candidate to fill in.")
        return 0
    print(f"{len(r['issues'])} issue(s) found:")
    for i in r['issues']:
        print(f"- {i['type']} in {i['where']}: {i['value']}")
    return 1


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
