#!/usr/bin/env python3
"""Package each skill as an upload-ready zip in dist/ (Claude app: Settings > Capabilities > Skills > Upload skill).

  python tools/package_skills.py

Author: Rahul Kashyap. MIT licence.
"""
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    skills_dir = os.path.join(ROOT, 'skills')
    dist = os.path.join(ROOT, 'dist')
    os.makedirs(dist, exist_ok=True)
    built = []
    for skill in sorted(os.listdir(skills_dir)):
        folder = os.path.join(skills_dir, skill)
        if not os.path.isdir(folder):
            continue
        target = os.path.join(dist, f'{skill}.zip')
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
            for base, _, files in os.walk(folder):
                for f in sorted(files):
                    if f.endswith('.pyc') or f == '.DS_Store':
                        continue
                    full = os.path.join(base, f)
                    z.write(full, os.path.relpath(full, skills_dir))
        built.append(target)
    for b in built:
        print('Built', os.path.relpath(b, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
