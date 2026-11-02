#!/usr/bin/env python3
"""Batch mode for Resume Genie: screen several roles, gate them, file the CVs and track applications.

Claude reads the adverts, runs the fit check and writes each tailored CV. This script does the
parts that must be exact and repeatable:
  - gates every role on the user's own thresholds (fit, ATS after tailoring, a clean audit)
  - refuses salary "ask" figures that have no advert range or cited source behind them
  - flags likely duplicate adverts (the same role posted by several agencies)
  - creates one folder per company and names the CV files consistently
  - prints the summary table with apply links, file links and salary
  - holds back the next batch until every ready role is marked as applied

batch.json:
  {"settings": {"output_dir": "Claude CVs", "candidate": "Alex Morgan",
                "fit_threshold": 70, "ats_target": 80, "batch_size": 10},
   "jobs": [{"company": "Acme", "role": "Data Engineer", "location": "Dublin",
             "apply_url": "https://...", "fit": 84, "ats_before": 62, "ats_after": 91,
             "audit": "clean", "placeholders": 1,
             "salary": {"advert": "EUR 90,000-110,000", "sources": [{"name": "...", "url": "...", "range": "..."}],
                        "ask": "EUR 105,000-110,000"},
             "flags": ["5 days on site"], "status": "new"}]}

Usage:
  python batch_tracker.py check   batch.json   # gate roles, flag duplicates and unsupported salary asks
  python batch_tracker.py folders batch.json   # create company folders, set file paths
  python batch_tracker.py pdf     batch.json   # convert each Word CV to PDF (needs LibreOffice)
  python batch_tracker.py table   batch.json   # markdown summary of the current batch
  python batch_tracker.py applied batch.json all|N[,N...]
  python batch_tracker.py next    batch.json   # exit 1 until every ready role is applied

Author: Rahul Kashyap. MIT licence.
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import quote

DEFAULTS = {'output_dir': 'Resume Genie CVs', 'candidate': 'Candidate', 'fit_threshold': 70,
            'ats_target': 80, 'batch_size': 10}
READY, SKIPPED, APPLIED, NEW = 'ready', 'skipped', 'applied', 'new'


def load(path):
    data = json.load(open(path, encoding='utf-8'))
    data['settings'] = {**DEFAULTS, **(data.get('settings') or {})}
    data.setdefault('jobs', [])
    return data


def save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def safe_name(text):
    """Folder and file safe on Windows, macOS and Linux."""
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', ' ', str(text or '')).strip().strip('.')
    return re.sub(r'\s+', ' ', s) or 'Unknown'


def file_stem(candidate, company, role):
    slug = lambda t: re.sub(r'[^A-Za-z0-9]+', '_', t).strip('_')
    return '_'.join(p for p in (slug(candidate), 'CV', slug(company), slug(role)) if p)


def _norm_role(text):
    t = re.sub(r'[^a-z0-9 ]+', ' ', str(text or '').lower())
    return re.sub(r'\s+', ' ', t).strip()


def salary_problem(salary):
    """An ask needs an advert range or at least one source with a link behind it."""
    salary = salary or {}
    ask = str(salary.get('ask') or '').strip()
    if not ask or ask.lower().startswith('no reliable data'):
        return None
    sources = [s for s in salary.get('sources') or [] if isinstance(s, dict) and s.get('url')]
    if not str(salary.get('advert') or '').strip() and not sources:
        return 'salary ask has no advert range or cited source'
    return None


def check(data):
    """Apply the gates in place. Returns a list of (index, message) notes."""
    s = data['settings']
    notes = []
    for i, job in enumerate(data['jobs'], 1):
        if job.get('status') == APPLIED:
            continue
        reasons = []
        if (job.get('fit') or 0) < s['fit_threshold']:
            reasons.append(f"fit {job.get('fit', 0)} below {s['fit_threshold']}")
        if job.get('ats_after') is not None and job['ats_after'] < s['ats_target']:
            reasons.append(f"ATS {job['ats_after']} below {s['ats_target']}")
        if job.get('ats_after') is not None and job.get('audit') != 'clean':
            reasons.append('fabrication audit not clean')
        problem = salary_problem(job.get('salary'))
        if problem:
            job.setdefault('salary', {})['ask'] = 'No reliable data'
            notes.append((i, problem + '; ask cleared'))
        job['status'] = SKIPPED if reasons else READY
        job['skip_reason'] = '; '.join(reasons)
        if reasons:
            notes.append((i, 'skipped: ' + job['skip_reason']))
    # Same role in the same place from different advertisers is usually one vacancy.
    open_jobs = [(i, j) for i, j in enumerate(data['jobs'], 1) if j.get('status') == READY]
    for a in range(len(open_jobs)):
        for b in range(a + 1, len(open_jobs)):
            (ia, ja), (ib, jb) = open_jobs[a], open_jobs[b]
            same_place = _norm_role(ja.get('location')) == _norm_role(jb.get('location'))
            ratio = difflib.SequenceMatcher(None, _norm_role(ja.get('role')), _norm_role(jb.get('role'))).ratio()
            if same_place and ratio >= 0.85 and ja.get('company') != jb.get('company'):
                flag = f'possible duplicate of #{ia}'
                if flag not in jb.setdefault('flags', []):
                    jb['flags'].append(flag)
                notes.append((ib, flag))
    return notes


def folders(data):
    s = data['settings']
    made = []
    for job in data['jobs']:
        if job.get('status') != READY:
            continue
        folder = os.path.join(s['output_dir'], safe_name(job.get('company')))
        os.makedirs(folder, exist_ok=True)
        stem = file_stem(s['candidate'], job.get('company', ''), job.get('role', ''))
        job['files'] = {'docx': os.path.join(folder, stem + '.docx'), 'pdf': os.path.join(folder, stem + '.pdf')}
        made.append(folder)
    return made


def pdf(data):
    office = shutil.which('soffice') or shutil.which('libreoffice')
    if not office:
        return None
    done = []
    for job in data['jobs']:
        files = job.get('files') or {}
        if job.get('status') == READY and os.path.exists(files.get('docx', '')):
            out = os.path.dirname(files['docx']) or '.'
            subprocess.run([office, '--headless', '--convert-to', 'pdf', '--outdir', out, files['docx']],
                           capture_output=True, timeout=180)
            if os.path.exists(files['pdf']):
                done.append(files['pdf'])
    return done


def _link(label, target):
    if not target:
        return '-'
    if re.match(r'^[a-z]+://', target):
        return f'[{label}]({target})'
    return f'[{label}](file:///{quote(os.path.abspath(target).replace(os.sep, "/").lstrip("/"))})'


def table(data):
    s = data['settings']
    ready = [(i, j) for i, j in enumerate(data['jobs'], 1) if j.get('status') == READY][:s['batch_size']]
    rows = ['| # | Company and role | Fit | ATS | Apply | CV | Salary | Ask for | Flags |',
            '|---|---|---|---|---|---|---|---|---|']
    for i, j in ready:
        sal = j.get('salary') or {}
        found = sal.get('advert') or ', '.join(f"[{x.get('name', 'source')}]({x['url']}) {x.get('range', '')}".strip()
                                               for x in sal.get('sources') or [] if x.get('url')) or '-'
        files = j.get('files') or {}
        cv = ', '.join(x for x in (_link('Word', files.get('docx')), _link('PDF', files.get('pdf'))) if x != '-') or '-'
        ats = f"{j.get('ats_before', '-')} to {j.get('ats_after', '-')}"
        rows.append(f"| {i} | {j.get('company', '')}, {j.get('role', '')} ({j.get('location', '')}) | {j.get('fit', '-')} | {ats} "
                    f"| {_link('Apply', j.get('apply_url'))} | {cv} | {found} | {sal.get('ask') or '-'} "
                    f"| {'; '.join(j.get('flags') or []) or '-'} |")
    skipped = [(i, j) for i, j in enumerate(data['jobs'], 1) if j.get('status') == SKIPPED]
    out = '\n'.join(rows)
    if skipped:
        out += '\n\nSkipped: ' + '; '.join(f"#{i} {j.get('company', '')} ({j.get('skip_reason')})" for i, j in skipped)
    return out


def mark_applied(data, which):
    picks = None if which == 'all' else {int(x) for x in which.split(',') if x.strip()}
    count = 0
    for i, job in enumerate(data['jobs'], 1):
        if job.get('status') == READY and (picks is None or i in picks):
            job['status'] = APPLIED
            count += 1
    return count


def pending(data):
    return [i for i, j in enumerate(data['jobs'], 1) if j.get('status') == READY]


def _main(argv):
    if len(argv) < 3 or argv[1] not in ('check', 'folders', 'pdf', 'table', 'applied', 'next'):
        print(__doc__)
        return 2
    cmd, path = argv[1], argv[2]
    data = load(path)
    if cmd == 'check':
        notes = check(data)
        save(path, data)
        ready = len(pending(data))
        print(f'{ready} role(s) ready, {sum(1 for j in data["jobs"] if j.get("status") == SKIPPED)} skipped.')
        for i, msg in notes:
            print(f'- #{i}: {msg}')
        return 0
    if cmd == 'folders':
        made = folders(data)
        save(path, data)
        print(f'{len(made)} company folder(s) under {data["settings"]["output_dir"]}')
        return 0
    if cmd == 'pdf':
        done = pdf(data)
        if done is None:
            print('LibreOffice not found: PDFs skipped. The Word files are ready.')
            return 1
        print(f'{len(done)} PDF(s) written.')
        return 0
    if cmd == 'table':
        print(table(data))
        return 0
    if cmd == 'applied':
        n = mark_applied(data, argv[3] if len(argv) > 3 else 'all')
        save(path, data)
        print(f'{n} role(s) marked as applied.')
        return 0
    left = pending(data)
    if left:
        print('Not yet applied: ' + ', '.join(f'#{i}' for i in left) + '. Finish these before the next batch.')
        return 1
    print('All ready roles are applied. Start the next batch.')
    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
