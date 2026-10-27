#!/usr/bin/env python3
"""Lint every skill against the Agent Skills format rules.

Checks: SKILL.md exists with YAML front matter; name matches the folder, is kebab-case,
at most 64 characters and doesn't contain reserved words; description is present, under
1,024 characters and free of angle brackets; every scripts/ or references/ file that
SKILL.md mentions actually exists; scripts are pure ASCII and compile.

Author: Rahul Kashyap. MIT licence.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESERVED = ('claude', 'anthropic')


def lint_skill(folder):
    errors = []
    name = os.path.basename(folder)
    path = os.path.join(folder, 'SKILL.md')
    if not os.path.exists(path):
        return [f'{name}: missing SKILL.md']
    text = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return [f'{name}: SKILL.md has no front matter']
    meta = dict(line.split(':', 1) for line in m.group(1).splitlines() if ':' in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    if meta.get('name') != name:
        errors.append(f"{name}: front matter name {meta.get('name')!r} doesn't match the folder")
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name) or len(name) > 64:
        errors.append(f'{name}: name must be kebab-case and at most 64 characters')
    if any(word in name for word in RESERVED):
        errors.append(f'{name}: name contains a reserved word')
    desc = meta.get('description', '')
    if not desc:
        errors.append(f'{name}: missing description')
    if len(desc) > 1024:
        errors.append(f'{name}: description is {len(desc)} characters (max 1024)')
    if '<' in desc or '>' in desc:
        errors.append(f'{name}: description contains angle brackets')
    for ref in sorted(set(re.findall(r'((?:scripts|references)/[\w.\-]+)', text))):
        if not os.path.exists(os.path.join(folder, ref)):
            errors.append(f'{name}: SKILL.md mentions {ref}, which is missing')
    scripts = os.path.join(folder, 'scripts')
    for f in sorted(os.listdir(scripts)) if os.path.isdir(scripts) else []:
        p = os.path.join(scripts, f)
        if f.endswith('.py'):
            if any(ord(c) > 127 for c in open(p, encoding='utf-8').read()):
                errors.append(f'{name}: {f} contains non-ASCII characters')
            try:
                compile(open(p, encoding='utf-8').read(), p, 'exec')
            except SyntaxError as e:
                errors.append(f'{name}: {f} does not compile: {e}')
    return errors


def main():
    skills_dir = os.path.join(ROOT, 'skills')
    folders = sorted(os.path.join(skills_dir, d) for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
    errors = [e for f in folders for e in lint_skill(f)]
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'{len(folders)} skills pass the lint.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
