#!/usr/bin/env python3
"""Deterministic ATS keyword scoring for Resume Genie.

Scores are calculated, never estimated by the model:
  score = 75% weighted keyword coverage + 25% format hygiene
Required keywords count double. Plurals, simple stems and listed synonyms match.
Matching is literal, the way an applicant tracking system search works.

Usage:
  python ats_score.py CV.txt KEYWORDS.json            # score one CV
  python ats_score.py --compare ORIGINAL.txt OUTPUT.json   # before/after from a Resume Genie output

KEYWORDS.json: [{"term": "P2P", "importance": "required", "synonyms": ["procure-to-pay"]}, ...]

Author: Rahul Kashyap. MIT licence.
"""
import json
import re
import sys

BULLET_RE = re.compile(r'^\s*([-\u2022*\u25aa\u25cf\u25e6\u2013]|\d+[.)])\s+')


def _norm(text):
    t = str(text or '').lower()
    t = t.replace('\u2018', "'").replace('\u2019', "'").replace('\u2013', '-').replace('\u2014', '-')
    t = re.sub(r"[^a-z0-9+#&/.\-' ]+", ' ', t)
    t = re.sub(r'(\w)\.(\s|$)', r'\1 ', t)
    return ' ' + re.sub(r'\s+', ' ', t).strip() + ' '


def _variants(term):
    t = term.lower().strip()
    out = {t}
    if len(t) > 4:
        if t.endswith('ies'):
            out.add(t[:-3] + 'y')
        elif t.endswith('es'):
            out.add(t[:-2])
        if t.endswith('s') and not t.endswith('ss'):
            out.add(t[:-1])
        else:
            out.add(t + 's')
        if t.endswith('ing'):
            out.add(t[:-3])
        if t.endswith('ed'):
            out.add(t[:-2])
    return out


def contains_term(normalised_text, term):
    return any(
        re.search(r'(^|[^a-z0-9])' + re.escape(_norm(v).strip()) + r'([^a-z0-9]|$)', normalised_text)
        for v in _variants(term)
    )


def keyword_coverage(cv_text, keywords):
    text = _norm(cv_text)
    seen, matched, missing = set(), [], []
    got = total = 0
    for k in keywords or []:
        term = (k.get('term') if isinstance(k, dict) else str(k)).strip()
        if not term or term.lower() in seen:
            continue
        seen.add(term.lower())
        importance = k.get('importance', 'preferred') if isinstance(k, dict) else 'preferred'
        weight = 2 if importance == 'required' else 1
        total += weight
        synonyms = [term] + list(k.get('synonyms', []) if isinstance(k, dict) else [])
        if any(contains_term(text, s) for s in synonyms):
            matched.append(term)
            got += weight
        else:
            missing.append({'term': term, 'importance': importance})
    return {'score': round(got / total * 100) if total else 0, 'matched': matched, 'missing': missing}


def format_checks(cv_text):
    raw = str(cv_text or '')
    words = len(raw.split())
    bullets = [line for line in raw.split('\n') if BULLET_RE.match(line)]
    quantified = [line for line in bullets if re.search(r'\d|%|\u00a3|\u20ac|\$', line)]

    def section(pattern):
        return bool(re.search(pattern, raw, re.I | re.M))

    checks = {
        'email address present': bool(re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', raw)),
        'phone number present': bool(re.search(r'\+?\d[\d\s().-]{7,}\d', raw)),
        'experience heading': section(r'(^|\n)\s*(professional |work |career )?(experience|employment|work history|career history)\b'),
        'education heading': section(r'(^|\n)\s*(education|qualifications|academic)'),
        'skills heading': section(r'(^|\n)\s*((core |key |technical )?skills|competencies|expertise|technologies)'),
        'summary heading': section(r'(^|\n)\s*(professional |career )?(summary|profile|about me|objective)'),
        'length 350-1,100 words': 350 <= words <= 1100,
        '40%+ of bullets show a number': bool(bullets) and len(quantified) / len(bullets) >= 0.4,
        'no unusual characters': not re.search('[\u2600-\u27bf\ue000-\uf8ff]', raw),
    }
    return {'score': round(sum(checks.values()) / len(checks) * 100), 'checks': checks, 'words': words}


def ats_score(cv_text, keywords):
    coverage = keyword_coverage(cv_text, keywords)
    fmt = format_checks(cv_text)
    return {
        'score': round(coverage['score'] * 0.75 + fmt['score'] * 0.25),
        'keyword_score': coverage['score'],
        'format_score': fmt['score'],
        'matched': coverage['matched'],
        'missing': coverage['missing'],
        'format_checks': fmt['checks'],
        'words': fmt['words'],
    }


def cv_to_text(cv):
    """Plain-text rendering of a structured CV, used to score it exactly like the original."""
    out = [cv.get('name', ''), cv.get('headline', ''), ' | '.join(cv.get('contact', [])), '']
    if cv.get('summary'):
        out += ['Professional Summary', cv['summary'], '']
    if cv.get('skills'):
        out.append('Skills')
        for g in cv['skills']:
            out.append((f"{g['group']}: " if g.get('group') else '') + ', '.join(g.get('items', [])))
        out.append('')
    if cv.get('experience'):
        out.append('Professional Experience')
        for job in cv['experience']:
            out.append(' | '.join(x for x in [job.get('title'), job.get('company'), job.get('location'), job.get('dates')] if x))
            for b in job.get('bullets', []):
                out.append('- ' + (b['text'] if isinstance(b, dict) else b))
            out.append('')
    for label, key in [('Projects', 'projects'), ('Education', 'education'), ('Certifications', 'certifications')]:
        items = cv.get(key) or []
        if not items:
            continue
        out.append(label)
        for it in items:
            if isinstance(it, str):
                out.append('- ' + it)
            else:
                out.append(' | '.join(x for x in [it.get('title') or it.get('degree') or it.get('name'), it.get('org') or it.get('institution'), it.get('dates')] if x))
                if it.get('details'):
                    out.append('- ' + it['details'])
        out.append('')
    return '\n'.join(out).strip()


def compare(original_text, output):
    keywords = output['analysis']['keywords']
    before = ats_score(original_text, keywords)
    after = ats_score(cv_to_text(output['cv']), keywords)
    return {'before': before, 'after': after, 'gain': after['score'] - before['score']}


def _main(argv):
    if len(argv) == 4 and argv[1] == '--compare':
        original = open(argv[2], encoding='utf-8').read()
        output = json.load(open(argv[3], encoding='utf-8'))
        r = compare(original, output)
        print(f"ATS score: {r['before']['score']} -> {r['after']['score']} ({r['gain']:+d})")
        missing = [m['term'] for m in r['after']['missing'] if m['importance'] == 'required']
        print('Required keywords still missing:', ', '.join(missing) or 'none')
        print(json.dumps(r, indent=2))
        return 0
    if len(argv) == 3:
        r = ats_score(open(argv[1], encoding='utf-8').read(), json.load(open(argv[2], encoding='utf-8')))
        print(json.dumps(r, indent=2))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
