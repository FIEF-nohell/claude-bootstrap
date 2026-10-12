import json
import subprocess
import unittest
from unittest import mock

from helpers import Fixture, learning_text, plan_text, rule_text, today

SOURCES = ('startup', 'resume', 'clear', 'compact', 'fork')


class FixtureCase(unittest.TestCase):
    def make(self, **kw):
        fx = Fixture(**kw)
        self.addCleanup(fx.cleanup)
        return fx


class FakeResponse:
    def __init__(self, raw):
        self.raw = raw

    def read(self, n=-1):
        return self.raw if n is None or n < 0 else self.raw[:n]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    def __init__(self, raw=None, error=None):
        self.raw, self.error, self.requests = raw, error, []

    def open(self, request, timeout=None):
        self.requests.append((request.full_url, timeout))
        if self.error:
            raise self.error
        return FakeResponse(self.raw)


class ContextTests(FixtureCase):
    def test_sources(self):
        fx = self.make()
        fx.add_rule('universal-one')
        fx.add_rule('scoped-one', scope='src/**')
        fx.add_plan()
        with fx.patched_env():
            module = fx.load_module()
            config = module.update_config()
            config[2].parent.mkdir(parents=True)
            import time
            config[2].write_text(json.dumps({'checked-at': time.time(), 'version': fx.version + 1,
                                             'details-url': fx.manifest['update-source']['details-url']}))
        for source in SOURCES:
            with self.subTest(source=source):
                out = fx.context(source)
                self.assertIn('Active universal policy index', out)
                self.assertIn('universal-one [required] .docs/rules/universal-one.md', out)
                self.assertNotIn('scoped-one', out)
                self.assertIn('### Plan: .docs/plans/current.md', out)
                self.assertIn('next: - [ ] second task', out)
                self.assertIn('last log: - did first', out)
                if source == 'startup':
                    self.assertIn('Passive bootstrap notice', out)
                    self.assertIn(f'v{fx.version + 1} is available', out)
                    self.assertIn('Git health', out)
                else:
                    self.assertNotIn('Passive bootstrap notice', out)
                    self.assertNotIn('Git health', out)

    def test_unknown_or_missing_source_still_works(self):
        fx = self.make()
        fx.add_rule('universal-one')
        res = fx.run('context', {})
        self.assertIn('universal-one', res.stdout)

    def test_no_notice_without_cache(self):
        fx = self.make()
        self.assertNotIn('Passive bootstrap notice', fx.context('startup'))

    def test_oversize_fallback(self):
        fx = self.make()
        for i in range(150):
            fx.add_rule(f'rule-{i:03d}', ident='long-identifier-' + 'x' * 60 + f'-{i:03d}')
        out = fx.context('resume')
        self.assertIn('CONTEXT BUDGET EXCEEDED', out)
        self.assertLessEqual(len(out), 16000)
        self.assertNotIn('long-identifier', out)
        # verify flags it
        res = fx.verify()
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn('context:', res.stdout)

    def test_just_under_budget_not_fallback(self):
        fx = self.make()
        fx.add_rule('a-rule')
        self.assertNotIn('CONTEXT BUDGET EXCEEDED', fx.context('resume'))

    def test_legacy_rule_and_invalid_rule_are_reported(self):
        fx = self.make()
        fx.write('.docs/rules/legacy.md', '# no frontmatter\n')
        fx.write('.docs/rules/bad.md', rule_text('bad-one', scope='/abs'))
        out = fx.context('resume')
        self.assertIn('legacy/unmanaged rule', out)
        self.assertIn('invalid status/scope', out)


class GitHealthTests(FixtureCase):
    def test_not_a_repo(self):
        fx = self.make()
        self.assertIn('not a Git repository', fx.context('startup'))

    def test_clean_and_dirty(self):
        fx = self.make()
        fx.git_init()
        out = fx.context('startup')
        self.assertIn('branch: main', out)
        self.assertIn('worktree: clean', out)
        self.assertIn('upstream: none configured', out)
        self.assertIn('recent commits:', out)
        fx.write('scratch.txt', 'x')
        out = fx.context('startup')
        self.assertIn('worktree: dirty (1 changed entries)', out)

    def test_plan_git_evidence(self):
        fx = self.make()
        fx.git_init()
        base = fx.git('rev-parse', 'HEAD')
        fx.add_plan(base=base)
        fx.write('src/new.py', 'x')
        fx.git_commit('add new file')
        out = fx.context('resume')
        self.assertIn('git evidence: 1 of the latest post-base commits shown', out)
        self.assertIn('src/new.py', out)

    def test_plan_with_bad_base(self):
        fx = self.make()
        fx.git_init()
        fx.add_plan(base='abcdef1')
        self.assertIn('unable to compare plan base with HEAD', fx.context('resume'))

    def test_plan_base_digits_only_sha(self):
        # The plan template writes `base:` unquoted; a digits-only short sha parses as a YAML int.
        fx = self.make()
        fx.git_init()
        fx.add_plan(base='1234567')
        out = fx.context('resume')
        self.assertNotIn('plan has no usable base sha', out)

    def test_run_git_cannot_prompt_or_hang(self):
        fx = self.make()
        module = fx.load_module()
        self.assertEqual(module.GIT_ENV['GIT_TERMINAL_PROMPT'], '0')
        self.assertEqual(module.GIT_ENV['GCM_INTERACTIVE'], 'never')
        self.assertEqual(module.GIT_ENV['GIT_OPTIONAL_LOCKS'], '0')
        self.assertIn('BatchMode=yes', module.GIT_ENV['GIT_SSH_COMMAND'])
        with mock.patch.object(module.subprocess, 'run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, '', '')
            module.run_git('status')
            kwargs = run.call_args.kwargs
            self.assertIs(kwargs['stdin'], subprocess.DEVNULL)
            self.assertIs(kwargs['env'], module.GIT_ENV)
            self.assertIn('timeout', kwargs)

    def test_timeout_yields_124(self):
        fx = self.make()
        module = fx.load_module()
        with mock.patch.object(module.subprocess, 'run', side_effect=subprocess.TimeoutExpired('git', 2)):
            result = module.run_git('status')
        self.assertEqual(result.returncode, 124)
        self.assertEqual(result.stderr, 'timeout')
        with mock.patch.object(module.subprocess, 'run', side_effect=subprocess.TimeoutExpired('git', 2)):
            health = module.git_health() if (fx.root / '.git').exists() else None
        self.assertIsNone(health)

    def test_git_health_survives_timeouts(self):
        fx = self.make()
        fx.git_init()
        module = fx.load_module()
        with mock.patch.object(module.subprocess, 'run', side_effect=subprocess.TimeoutExpired('git', 2)):
            health = module.git_health()
        self.assertIn('git failed or timed out', health)
        self.assertIn('worktree: unknown', health)


class VerifyTests(FixtureCase):
    def test_clean_fixture(self):
        fx = self.make()
        fx.add_rule('universal-one')
        res = fx.verify()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(res.stdout.strip(), '')

    def test_marker_mismatch(self):
        fx = self.make()
        text = (fx.root / 'AGENTS.md').read_text()
        fx.write('AGENTS.md', text.replace(f'nohell v{fx.version}', f'nohell v{fx.version - 1}'))
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn(f'AGENTS.md: marker v{fx.version - 1} does not match manifest bootstrap-version {fx.version}',
                      res.stdout)

    def test_missing_or_duplicate_marker(self):
        fx = self.make()
        text = (fx.root / 'CLAUDE.md').read_text()
        fx.write('CLAUDE.md', text + f'\n> Bootstrapped by nohell v{fx.version}\n')
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('expected exactly one version marker, found 2', res.stdout)

    def test_always_loaded_size(self):
        fx = self.make()
        text = (fx.root / 'AGENTS.md').read_text()
        fx.write('AGENTS.md', text + '\n' + 'filler line\n' * 1500)
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('always-loaded size', res.stdout)

    def test_unregistered_agent(self):
        fx = self.make()
        fx.write('.claude/agents/ghost.md', '---\nname: ghost\ndescription: Haunts\n---\nBody\n')
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('ghost.md', res.stdout)
        self.assertIn('missing or stale AGENTS.md description registration', res.stdout)

    def test_registered_agent_missing_file(self):
        fx = self.make()
        (fx.root / '.claude/agents/reviewer.md').unlink()
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('registered agent missing: reviewer', res.stdout)

    def test_duplicate_active_rule_ids(self):
        fx = self.make()
        fx.add_rule('one', ident='same-id')
        fx.add_rule('two', ident='same-id')
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('duplicate active ID with .docs/rules/one.md', res.stdout)

    def test_missing_claude_pointer(self):
        fx = self.make()
        fx.write('CLAUDE.md', f'# Project\n\n> Bootstrapped by nohell v{fx.version}\n')
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('missing @AGENTS.md pointer import', res.stdout)

    def test_invalid_manifest_json_duplicate_keys(self):
        fx = self.make()
        fx.write('.claude/bootstrap-manifest.json', '{"schema-version": 1, "schema-version": 1}')
        res = fx.verify()
        self.assertEqual(res.returncode, 1)
        self.assertIn('duplicate key', res.stdout)


class RetrieveTests(FixtureCase):
    def ids(self, result, key='selected'):
        return [item['id'] for item in result[key]]

    def test_relevant_learning_selected(self):
        fx = self.make()
        fx.add_learning('auth-refresh', scope='src/**', tags=['auth', 'tokens'])
        res = fx.retrieve(['src/auth/login.ts'], 'fix auth token refresh')
        self.assertIn('auth-refresh', self.ids(res))
        item = res['selected'][0]
        self.assertEqual(item['kind'], 'learning')
        self.assertIn('scope', item['reason'])
        self.assertTrue(item['revision'])
        self.assertNotIn('no learning or decision matched; coverage is limited to active policy', res['coverage-notes'])

    def test_similar_out_of_scope_excluded(self):
        fx = self.make()
        fx.add_learning('billing-docs', scope='docs/**', tags=['billing'])
        res = fx.retrieve(['src/auth/login.ts'], 'fix auth token refresh')
        self.assertEqual(self.ids(res), [])
        self.assertIn('billing-docs', self.ids(res, 'rejected'))
        self.assertIn('out of scope', res['rejected'][0]['reason'])

    def test_missing_lesson_coverage_note(self):
        fx = self.make()
        fx.add_rule('src-rule', scope='src/**')
        res = fx.retrieve(['src/a.py'], 'anything')
        self.assertEqual(self.ids(res), ['src-rule'])
        self.assertIn('no learning or decision matched; coverage is limited to active policy', res['coverage-notes'])

    def test_no_paths_note(self):
        fx = self.make()
        res = fx.run('retrieve', args=['--text', 'x'])
        self.assertIn('no paths given', ' '.join(json.loads(res.stdout)['coverage-notes']))

    def test_invalidates_when_surfaced(self):
        fx = self.make()
        fx.add_learning('cache-quirk', scope='src/**', tags=['cache'],
                        invalidates_when=['cache layer is replaced'])
        res = fx.retrieve(['src/cache.py'], 'cache')
        self.assertEqual(res['selected'][0]['invalidates-when'], ['cache layer is replaced'])

    def test_duplicate_active_id_conflict(self):
        fx = self.make()
        fx.add_rule('one', ident='dup-id', scope='src/**')
        fx.add_rule('two', ident='dup-id', scope='src/**')
        res = fx.retrieve(['src/a.py'], '')
        self.assertTrue(any(c.startswith('duplicate active ID dup-id') for c in res['conflicts']), res['conflicts'])

    def test_conflicts_with_pair(self):
        fx = self.make()
        fx.add_rule('alpha', scope='src/**', extra='conflicts-with: [beta]\n')
        fx.add_rule('beta', scope='src/**', extra='conflicts-with: [alpha]\n')
        res = fx.retrieve(['src/a.py'], '')
        self.assertEqual(res['conflicts'], ['conflicting rules alpha <-> beta'])

    def test_conflicts_with_unselected_other_no_conflict(self):
        fx = self.make()
        fx.add_rule('alpha', scope='src/**', extra='conflicts-with: [beta]\n')
        fx.add_rule('beta', scope='docs/**')
        res = fx.retrieve(['src/a.py'], '')
        self.assertEqual(res['conflicts'], [])

    def test_superseded_rejected(self):
        fx = self.make()
        fx.add_rule('old', scope='src/**', status='superseded')
        fx.add_rule('cand', scope='src/**', status='candidate')
        fx.add_learning('old-lesson', scope='src/**', status='superseded', tags=['x'])
        res = fx.retrieve(['src/a.py'], 'old lesson')
        self.assertEqual(self.ids(res), [])
        reasons = {r['id']: r['reason'] for r in res['rejected']}
        self.assertEqual(reasons['old'], 'status superseded')
        self.assertEqual(reasons['old-lesson'], 'status superseded')
        self.assertEqual(reasons['cand'], 'status candidate')

    def test_ordering_rules_first_then_priority(self):
        fx = self.make()
        fx.add_learning('lesson', scope='src/**', tags=['x'])
        fx.add_rule('adv', scope='src/**', priority='advisory')
        fx.add_rule('req', scope='src/**', priority='required')
        res = fx.retrieve(['src/a.py'], '')
        self.assertEqual(self.ids(res), ['req', 'adv', 'lesson'])

    def test_universal_rule_always_selected(self):
        fx = self.make()
        fx.add_rule('everywhere', scope='**')
        self.assertEqual(self.ids(fx.retrieve(['anything/at/all.txt'], '')), ['everywhere'])

    def test_applies_to_role(self):
        fx = self.make()
        fx.add_learning('role-lesson', scope='docs/**', applies_to=['reviewer'])
        self.assertEqual(self.ids(fx.retrieve(['src/a.py'], '', role='reviewer')), ['role-lesson'])
        self.assertEqual(self.ids(fx.retrieve(['src/a.py'], '')), [])

    def test_overdue_review_flag(self):
        fx = self.make()
        fx.write('.docs/learnings/old.md', learning_text('stale-lesson', severity='high', tags=['x'])
                 .replace(f'last-reviewed: {today()}', 'last-reviewed: 2020-01-01'))
        res = fx.retrieve(['src/a.py'], '')
        self.assertTrue(res['selected'][0]['overdue-review'])

    def test_legacy_file_noted(self):
        fx = self.make()
        fx.write('.docs/learnings/legacy.md', '# old format\n')
        res = fx.retrieve(['src/a.py'], '')
        self.assertTrue(any('legacy or unmanaged' in n for n in res['coverage-notes']))

    def hits(self, fx, scope, path):
        fx.write('.docs/rules/probe.md', rule_text('probe', scope=scope))
        return 'probe' in self.ids(fx.retrieve([path], ''))

    def test_glob_scopes(self):
        fx = self.make()
        cases = [
            ('src/**', 'src/a/b/c.py', True),
            ('src/**', 'src/a.py', True),
            ('src/**', 'srcx/a.py', False),
            ('src/**', 'lib/src/a.py', False),
            ('*.md', 'README.md', True),
            ('*.md', 'docs/README.md', False),
            ('*.md', 'README.txt', False),
            ('a/?.py', 'a/b.py', True),
            ('a/?.py', 'a/bc.py', False),
            ('a/?.py', 'a/b/c.py', False),
            ('**/*.py', 'top.py', True),
            ('**/*.py', 'x/y/z.py', True),
            ('src/**', './src/a.py', True),
            ('*.md', './README.md', True),
            ('a/?.py', './a/b.py', True),
            ('.claude/**', '.claude/hooks/x.py', True),
            ('.claude/**', './.claude/hooks/x.py', True),
            ('.claude/**', 'claude/hooks/x.py', False),
            ('src/**', 'src\\win\\a.py', True),
            ('a.b', 'aXb', False),
        ]
        for scope, path, expected in cases:
            with self.subTest(scope=scope, path=path):
                self.assertEqual(self.hits(fx, scope, path), expected)

    def test_glob_regex_unit(self):
        fx = self.make()
        module = fx.load_module()
        self.assertTrue(module.scope_hits('**', []))
        self.assertFalse(module.scope_hits('src/**', []))
        for bad in ('/abs', '../up', 'a//b', './a', 'has space', '', None):
            self.assertFalse(module.scope_ok(bad), bad)
        for good in ('**', 'src/**', '*.md', 'a/?.py', '.claude/**'):
            self.assertTrue(module.scope_ok(good), good)


class UpdaterTests(FixtureCase):
    def refresh(self, fx, raw=None, error=None, source='startup', env=None):
        opener = FakeOpener(raw, error)
        module = fx.load_module()
        with fx.patched_env(**(env or {})):
            with mock.patch('urllib.request.build_opener', return_value=opener) as build:
                module.refresh({'source': source})
        return module, opener, build

    def body(self, fx, version, details=None, pad=0):
        data = {'version': version, 'details-url': details or fx.manifest['update-source']['details-url']}
        if pad:
            data['pad'] = 'x' * pad
        return json.dumps(data).encode()

    def cache_files(self, fx):
        return list(fx.cache.rglob('*.json'))

    def test_newer_creates_cache_and_startup_reports(self):
        fx = self.make()
        before = fx.snapshot()
        module, opener, _ = self.refresh(fx, self.body(fx, fx.version + 1))
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(opener.requests[0][0], fx.manifest['update-source']['metadata-url'])
        files = self.cache_files(fx)
        self.assertEqual(len(files), 1)
        self.assertEqual(json.loads(files[0].read_text())['version'], fx.version + 1)
        out = fx.context('startup')
        self.assertIn('### Passive bootstrap notice', out)
        self.assertIn(f'Bootstrap v{fx.version} is installed; v{fx.version + 1} is available.', out)
        self.assertNotIn('Passive bootstrap notice', fx.context('resume'))
        # cache lives outside the project and the project tree is untouched
        self.assertTrue(fx.cache in files[0].parents)
        self.assertNotIn(fx.root, files[0].parents)
        self.assertEqual(fx.snapshot(), before)

    def test_equal_and_older_no_notice(self):
        for version in (14, 3):
            with self.subTest(remote=version):
                fx = self.make()
                self.refresh(fx, self.body(fx, min(version, fx.version) if version < 14 else fx.version))
                self.assertEqual(len(self.cache_files(fx)), 1)
                self.assertNotIn('Passive bootstrap notice', fx.context('startup'))

    def test_malformed_response(self):
        for raw in (b'not json', b'{"version": "15"}', b'{"version": true}', b'[]', b'\xff\xfe', b'{"version": 1e9}'):
            with self.subTest(raw=raw):
                fx = self.make()
                self.refresh(fx, raw)
                self.assertNotIn('Passive bootstrap notice', fx.context('startup'))

    def test_wrong_details_url(self):
        fx = self.make()
        self.refresh(fx, self.body(fx, fx.version + 1, details='https://evil.example/x'))
        self.assertNotIn('Passive bootstrap notice', fx.context('startup'))

    def test_oversized_response(self):
        fx = self.make()
        raw = self.body(fx, fx.version + 1, pad=5000)
        self.assertGreater(len(raw), 4096)
        self.refresh(fx, raw)
        self.assertNotIn('Passive bootstrap notice', fx.context('startup'))

    def test_transport_error_no_notice_but_negative_cached(self):
        fx = self.make()
        _, opener, _ = self.refresh(fx, error=OSError('offline'))
        self.assertEqual(len(opener.requests), 1)
        self.assertNotIn('Passive bootstrap notice', fx.context('startup'))
        # negative result cached: a second refresh does not request again
        _, opener2, _ = self.refresh(fx, self.body(fx, fx.version + 1))
        self.assertEqual(opener2.requests, [])

    def test_opt_out_env(self):
        for value in ('0', 'false', 'off', 'OFF'):
            with self.subTest(value=value):
                fx = self.make()
                _, opener, build = self.refresh(fx, self.body(fx, fx.version + 1),
                                                env={'CLAUDE_BOOTSTRAP_UPDATE_CHECK': value})
                build.assert_not_called()
                self.assertEqual(opener.requests, [])
                self.assertEqual(self.cache_files(fx), [])

    def test_opt_out_manifest(self):
        fx = self.make()
        fx.manifest['update-source']['enabled'] = False
        fx.write_manifest()
        _, opener, build = self.refresh(fx, self.body(fx, fx.version + 1))
        build.assert_not_called()

    def test_untrusted_or_non_https_source(self):
        for mutate in (lambda s: s.update(trusted=False), lambda s: s.update({'metadata-url': 'http://x.example/a.json'}),
                       lambda s: s.update({'details-url': 'https://u:p@x.example/'})):
            fx = self.make()
            mutate(fx.manifest['update-source'])
            fx.write_manifest()
            _, _, build = self.refresh(fx, self.body(fx, fx.version + 1))
            build.assert_not_called()

    def test_non_startup_sources_make_no_request(self):
        for source in ('resume', 'clear', 'compact', 'fork', 'unknown'):
            with self.subTest(source=source):
                fx = self.make()
                _, opener, build = self.refresh(fx, self.body(fx, fx.version + 1), source=source)
                build.assert_not_called()
                self.assertEqual(self.cache_files(fx), [])

    def test_update_mode_cli_ignores_non_startup_stdin(self):
        fx = self.make()
        res = fx.run('update', {'source': 'resume'})
        self.assertEqual(res.returncode, 0)
        self.assertEqual(self.cache_files(fx), [])

    def test_cache_inside_project_disables_check(self):
        fx = self.make()
        module = fx.load_module()
        with fx.patched_env(XDG_CACHE_HOME=str(fx.root / '.cache')):
            self.assertIsNone(module.update_config())
        with fx.patched_env():
            config = module.update_config()
        self.assertIsNotNone(config)
        self.assertNotIn(fx.root, config[2].parents)

    def test_cache_ttl(self):
        fx = self.make()
        self.refresh(fx, self.body(fx, fx.version + 1))
        path = self.cache_files(fx)[0]
        data = json.loads(path.read_text())
        data['checked-at'] -= 86400 + 10
        path.write_text(json.dumps(data))
        self.assertNotIn('Passive bootstrap notice', fx.context('startup'))
        # expired cache triggers a new request
        _, opener, _ = self.refresh(fx, self.body(fx, fx.version + 2))
        self.assertEqual(len(opener.requests), 1)

    def test_no_redirect_handler(self):
        fx = self.make()
        module = fx.load_module()
        captured = {}

        def fake_build(*handlers):
            captured['handlers'] = handlers
            return FakeOpener(self.body(fx, fx.version + 1))
        with fx.patched_env(), mock.patch('urllib.request.build_opener', side_effect=fake_build):
            module.refresh({'source': 'startup'})
        handler = captured['handlers'][0]()
        self.assertIsNone(handler.redirect_request(None, None, 302, 'Found', {}, 'https://elsewhere.example/'))


if __name__ == '__main__':
    unittest.main()
