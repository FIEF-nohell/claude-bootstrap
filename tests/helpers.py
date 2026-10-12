"""Shared fixtures for the bootstrap test suite (stdlib only, PyYAML needed by the helper)."""
import contextlib
import datetime as dt
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest.mock as mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPT = REPO / 'claude-bootstrap-prompt.md'
SENTENCE = 'Write the following helper under the ownership contract:'


def ensure_yaml():
    try:
        import yaml  # noqa: F401
        return
    except ImportError:
        pass
    if subprocess.run([sys.executable, '-c', 'import yaml']).returncode != 0:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--break-system-packages', 'pyyaml'], check=True)


ensure_yaml()


def prompt_text():
    return PROMPT.read_text(encoding='utf-8')


def helper_source():
    text = prompt_text()
    idx = text.index(SENTENCE)
    match = re.search(r'```python\n(.*?)\n```', text[idx:], re.S)
    if not match:
        raise RuntimeError('helper python block not found after sentence')
    return match.group(1) + '\n'


def prompt_version():
    match = re.search(r'This bootstrap is `nohell v(\d+)`', prompt_text())
    return int(match.group(1))


def prompt_manifest_block():
    for block in re.findall(r'```json\n(.*?)\n```', prompt_text(), re.S):
        if '"schema-version"' in block and '"module-source"' in block:
            return json.loads(block)
    raise RuntimeError('manifest block not found')


def today():
    return dt.date.today().isoformat()


def rule_text(ident, scope='**', status='active', priority='required', body='Rule body.', extra=''):
    return (f'---\nid: {ident}\nstatus: {status}\nscope: "{scope}"\npriority: {priority}\nowner: team\n'
            f'confidence: verified\nlast-reviewed: {today()}\n{extra}---\n{body}\n')


def learning_text(ident, scope='src/**', status='active', tags=(), severity='medium', applies_to=(),
                  invalidates_when=(), extra=''):
    def lst(v):
        return json.dumps(list(v))
    return (f'---\nid: {ident}\nstatus: {status}\nscope: "{scope}"\npriority: preferred\nowner: team\n'
            f'confidence: supported\nlast-reviewed: {today()}\ndate: {today()}\ntags: {lst(tags)}\n'
            f'severity: {severity}\napplies-to: {lst(applies_to)}\nevidence-refs: []\nvalidates-with: []\n'
            f'invalidates-when: {lst(invalidates_when)}\n{extra}---\nLesson body.\n')


def plan_text(goal='Ship the thing', base='deadbeef', status='in-progress'):
    return (f'---\nstatus: {status}\ncreated: {today()}\nupdated: {today()}\nbase: {base}\ngoal: {goal}\n---\n'
            '# Plan\n- [x] first\n- [ ] second task\n\n## Log\n- started\n- did first\n')


class Fixture:
    """A disposable project plus a separate cache directory outside the project root."""

    def __init__(self, version=None):
        self.version = prompt_version() if version is None else version
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix='bootstrap-fx-')))
        self.root = self.tmp / 'proj'
        self.cache = self.tmp / 'cache'
        self.cache.mkdir()
        self.root.mkdir()
        self.hook = self.root / '.claude' / 'hooks' / 'bootstrap-runtime.py'
        self.write('.claude/hooks/bootstrap-runtime.py', helper_source())
        for folder in ('rules', 'learnings', 'plans', 'decisions', 'evidence'):
            (self.root / '.docs' / folder).mkdir(parents=True)
        manifest = prompt_manifest_block()
        manifest['bootstrap-version'] = self.version
        manifest['artifacts'] = []
        self.manifest = manifest
        self.write_manifest()
        marker = f'> Bootstrapped by nohell v{self.version}'
        self.write('AGENTS.md',
                   f'# Project\n\n{marker}\n\n## Available agents\n\n| Agent | Description | Output |\n|---|---|---|\n'
                   '| `reviewer` | Reviews code | Report |\n\n### Routing heuristics\n\n- Use reviewer.\n')
        self.write('CLAUDE.md', f'# Project\n\n{marker}\n\n@AGENTS.md\n')
        self.write('.claude/agents/reviewer.md',
                   '---\nname: reviewer\ndescription: Reviews code\n---\nYou review code.\n')
        self.write('.claude/settings.json', json.dumps({
            'permissions': {'allow': ['Bash(git status:*)'], 'deny': [], 'ask': ['Bash(git push:*)']},
            'hooks': {'SessionStart': [{'matcher': 'startup', 'hooks': [
                {'type': 'command', 'command': 'sh .claude/hooks/session-start.sh'}]}]},
        }, indent=2))

    # file helpers
    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def write_manifest(self):
        self.write('.claude/bootstrap-manifest.json', json.dumps(self.manifest, indent=2))

    def add_rule(self, name, ident=None, **kw):
        return self.write(f'.docs/rules/{name}.md', rule_text(ident or name, **kw))

    def add_learning(self, name, ident=None, **kw):
        return self.write(f'.docs/learnings/{name}.md', learning_text(ident or name, **kw))

    def add_plan(self, name='current', **kw):
        return self.write(f'.docs/plans/{name}.md', plan_text(**kw))

    # git
    def git(self, *args):
        env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull}
        return subprocess.run(
            ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false', *args],
            cwd=self.root, check=True, capture_output=True, text=True, env=env).stdout.strip()

    def git_init(self, commit=True):
        self.git('init', '-q', '-b', 'main')
        if commit:
            self.git_commit('initial')

    def git_commit(self, message):
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)
        return self.git('rev-parse', 'HEAD')

    # environment and execution
    def env(self, **extra):
        env = {k: v for k, v in os.environ.items()
               if k not in ('LOCALAPPDATA', 'CLAUDE_BOOTSTRAP_UPDATE_CHECK', 'XDG_CACHE_HOME')}
        env['XDG_CACHE_HOME'] = str(self.cache)
        env['HOME'] = str(self.tmp)
        env.update(extra)
        return env

    @contextlib.contextmanager
    def patched_env(self, **extra):
        env = self.env(**extra)
        with mock.patch.dict(os.environ, env, clear=True):
            yield

    def run(self, mode, stdin=None, args=(), env=None):
        payload = json.dumps(stdin) if isinstance(stdin, (dict, list)) else (stdin or '')
        return subprocess.run([sys.executable, '-X', 'utf8', str(self.hook), mode, *args], input=payload,
                              capture_output=True, text=True, cwd=self.root, env=env or self.env(), timeout=60)

    def context(self, source='startup', env=None):
        return self.run('context', {'source': source}, env=env).stdout

    def verify(self):
        return self.run('verify')

    def retrieve(self, paths=(), text='', role=''):
        args = ['--paths', *paths, '--text', text]
        if role:
            args += ['--role', role]
        result = self.run('retrieve', args=args)
        if result.returncode != 0:
            raise AssertionError('retrieve failed: ' + result.stdout + result.stderr)
        return json.loads(result.stdout)

    def load_module(self):
        """Import the fixture's helper in-process (ROOT resolves to this fixture)."""
        name = 'bootstrap_runtime_' + re.sub(r'\W', '_', str(self.tmp))
        spec = importlib.util.spec_from_file_location(name, self.hook)
        module = importlib.util.module_from_spec(spec)
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        return module

    def snapshot(self):
        return sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if '.git' not in p.parts)

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


