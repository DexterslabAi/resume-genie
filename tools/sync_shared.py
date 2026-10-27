#!/usr/bin/env python3
"""Copy shared scripts and references into each skill, as listed in tools/manifest.json.

Every skill must be self-contained (each is installed on its own), but the code and
guidance live once in shared/. Run this after editing anything in shared/.
  python tools/sync_shared.py          # write copies
  python tools/sync_shared.py --check  # fail if any copy is out of date (used in CI)

Author: Rahul Kashyap. MIT licence.
"""
import filecmp
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def plan():
    manifest = json.load(open(os.path.join(ROOT, 'tools', 'manifest.json')))
    for skill, parts in manifest.items():
        for kind in ('scripts', 'references'):
            for name in parts.get(kind, []):
                yield os.path.join(ROOT, 'shared', kind, name), os.path.join(ROOT, 'skills', skill, kind, name)


def main(argv):
    check = '--check' in argv
    stale = []
    for src, dst in plan():
        if not os.path.exists(dst) or not filecmp.cmp(src, dst, shallow=False):
            stale.append(os.path.relpath(dst, ROOT))
            if not check:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
    if check and stale:
        print('Out of date (run python tools/sync_shared.py):\n' + '\n'.join(f'- {s}' for s in stale))
        return 1
    print('Checked' if check else 'Synced', f'{len(list(plan()))} shared files across skills.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
