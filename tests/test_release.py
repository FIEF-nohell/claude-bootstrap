import json
import re
import subprocess
import sys
import unittest

from helpers import PROMPT, REPO, prompt_text

EM_DASH = '—'


def readme_status_version():
    text = (REPO / 'README.md').read_text(encoding='utf-8')
    match = re.search(r'^## Status\s*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    assert match, 'README has no Status section'
    versions = [int(v) for v in re.findall(r'\bV(\d+)\b', match.group(1), re.I)]
    assert versions, 'README Status mentions no version'
    return max(versions)


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prompt = prompt_text()

    def test_versions_agree(self):
        markers = set(int(v) for v in re.findall(r'nohell v(\d+)', self.prompt))
        self.assertEqual(len(markers), 1, f'prompt has differing nohell vN strings: {sorted(markers)}')
        prompt_v = markers.pop()
        manifest_versions = set(int(v) for v in re.findall(r'"bootstrap-version": (\d+)', self.prompt))
        release = json.loads((REPO / 'bootstrap-release.json').read_text())['version']
        readme = readme_status_version()
        with self.subTest('prompt manifest bootstrap-version'):
            self.assertEqual(manifest_versions, {prompt_v})
        with self.subTest('bootstrap-release.json version'):
            self.assertEqual(release, prompt_v)
        with self.subTest('README Status version'):
            self.assertEqual(readme, prompt_v)

    def test_no_em_dash(self):
        for path in (PROMPT, REPO / 'README.md', REPO / 'CLAUDE.md'):
            with self.subTest(file=path.name):
                lines = [i + 1 for i, line in enumerate(path.read_text(encoding='utf-8').splitlines()) if EM_DASH in line]
                self.assertEqual(lines, [], f'{path.name} has em dashes on lines {lines[:10]}')

    def test_json_blocks_parse(self):
        blocks = re.findall(r'```json\n(.*?)\n```', self.prompt, re.S)
        self.assertTrue(blocks)
        checked = 0
        for i, block in enumerate(blocks):
            if '<' in block:
                continue
            checked += 1
            with self.subTest(block=i):
                json.loads(block)
        self.assertGreater(checked, 0)

    def test_module_source_pin(self):
        match = re.search(r'```json\n(\{\s*"schema-version".*?)\n```', self.prompt, re.S)
        data = json.loads(match.group(1))
        ref = data['module-source']['ref']
        self.assertRegex(ref, r'^[0-9a-f]{40}$')
        self.assertIn(ref, data['module-source']['registry-url'])
        self.assertIn('/' + data['module-source']['repository'] + '/', data['module-source']['registry-url'])
        self.assertIn('/master/', data['update-source']['metadata-url'])

    def test_archive_matches_master(self):
        # Archive numbers are an edit counter, so the invariant is that master's prompt is preserved somewhere.
        have = subprocess.run(['git', 'rev-parse', '--verify', '-q', 'refs/heads/master'], cwd=REPO, capture_output=True)
        if have.returncode != 0:
            self.skipTest('no local master branch')
        shown = subprocess.run(['git', 'show', 'master:claude-bootstrap-prompt.md'], cwd=REPO, capture_output=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        if shown.stdout == (REPO / 'claude-bootstrap-prompt.md').read_bytes():
            return  # master already is the current prompt
        archives = sorted((REPO / 'old-versions').glob('claude-bootstrap-prompt-v*.md'))
        self.assertTrue(any(a.read_bytes() == shown.stdout for a in archives),
                        'master:claude-bootstrap-prompt.md is not preserved in old-versions/')

    def test_module_pin_is_current(self):
        pin = subprocess.run([sys.executable, str(REPO / 'tools' / 'pin_modules.py'), '--check'],
                             cwd=REPO, capture_output=True, text=True)
        self.assertEqual(pin.returncode, 0, pin.stdout + pin.stderr + ' (run python3 tools/pin_modules.py)')


if __name__ == '__main__':
    unittest.main()
