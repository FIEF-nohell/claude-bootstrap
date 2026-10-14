#!/usr/bin/env python3
"""Set the module pin in claude-bootstrap-prompt.md to the last commit that touched modules/.

Run after committing any change under modules/. `--check` only reports (exit 1 if stale).
The pinned commit must already be pushed, because installed projects fetch from it.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPT = REPO / 'claude-bootstrap-prompt.md'
PIN = re.compile(r'(?<=/)[0-9a-f]{40}(?=/modules/registry\.json)|(?<="ref": ")[0-9a-f]{40}(?=")')


def last_module_commit():
    out = subprocess.run(['git', 'log', '-1', '--format=%H', '--', 'modules'], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout.strip()
    if not re.fullmatch(r'[0-9a-f]{40}', out):
        sys.exit('no commit touching modules/ found')
    return out


def main():
    want = last_module_commit()
    text = PROMPT.read_text(encoding='utf-8')
    found = set(PIN.findall(text))
    if len(PIN.findall(text)) != 2:
        sys.exit('expected exactly two pin occurrences (registry-url and ref), found %d' % len(PIN.findall(text)))
    if found == {want}:
        print('pin up to date: ' + want)
        return 0
    if '--check' in sys.argv:
        print('pin is stale: %s, last modules commit is %s' % (', '.join(sorted(found)), want))
        return 1
    PROMPT.write_text(PIN.sub(want, text), encoding='utf-8')
    print('pin updated: %s -> %s' % (', '.join(sorted(found)), want))
    print('Push the modules commit before releasing, then commit this change.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
