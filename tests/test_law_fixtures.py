"""law.py on small corpora built here, in a temporary folder: no submodule needs to be checked out.

  python -m unittest tests.test_law_fixtures -v

Each case is a way a real corpus records its law: older acts appended after newer ones, corrections laid over past
dates, a publisher's starting text, court rulings and treaties, a list of acts without their text, laws not yet in
force on main, an unfinished or shallow checkout, a checkout at an older commit than the tree pins, a pin that
moves forward (the index on disk grows by the new commits only), and laws kept on a future branch, read from their day
through data/future-pins.tsv.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
TODAY = dt.date.today().isoformat()


def run(*args, cwd, env=None, check=True):
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8',
                          env={**os.environ, 'GIT_CONFIG_NOSYSTEM': '1', **(env or {})})
    if check and done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr}")
    return done.stdout.strip()


class Corpus:
    """A corpus repository: each commit writes files (None deletes one) as a law, with trailers."""

    def __init__(self, path: Path):
        self.path = path
        path.mkdir(parents=True)
        run('init', '-q', '-b', 'main', cwd=path)
        run('config', 'core.autocrlf', 'false', cwd=path)
        self.n = 0

    def commit(self, author: str, files: dict, **trailers) -> str:
        for name, text in files.items():
            f = self.path / name
            if text is None:
                run('rm', '-q', name, cwd=self.path)
                continue
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(text.encode('utf-8'))
            run('add', name, cwd=self.path)
        self.n += 1
        body = ''.join(f"{k.replace('_', '-')}: {v}\n" for k, v in trailers.items() if not isinstance(v, list))
        body += ''.join(f"{k.replace('_', '-')}: {x}\n" for k, v in trailers.items() if isinstance(v, list) for x in v)
        stamp = f'2001-01-01T00:00:{self.n:02d}Z'
        env = {'GIT_AUTHOR_NAME': author, 'GIT_AUTHOR_EMAIL': 'law@example.org', 'GIT_AUTHOR_DATE': stamp,
               'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.org', 'GIT_COMMITTER_DATE': stamp}
        run('commit', '-q', '--allow-empty', '-m', f'{author}\n\n{body}', cwd=self.path, env=env)
        return run('rev-parse', 'HEAD', cwd=self.path)


class Tree:
    """A tree like global-law: tools/law.py, a manifest, and corpora pinned as submodules."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix='gl-fixture-'))
        run('init', '-q', '-b', 'main', cwd=self.root)
        run('config', 'core.autocrlf', 'false', cwd=self.root)
        (self.root / 'tools').mkdir()
        shutil.copy(HERE / 'tools' / 'law.py', self.root / 'tools' / 'law.py')
        shutil.copy(HERE / 'tools' / 'usc_cite.py', self.root / 'tools' / 'usc_cite.py')  # mcp_server.py imports it
        (self.root / 'manifest.json').write_text(json.dumps({'corpora': []}), encoding='utf-8')
        self.corpora: dict[str, Corpus] = {}

    def corpus(self, path: str) -> Corpus:
        c = self.corpora[path] = Corpus(self.root / path)
        return c

    def pin(self) -> None:
        """Point every corpus's submodule at its HEAD and commit the tree."""
        modules = ''.join(f'[submodule "{p}"]\n\tpath = {p}\n\turl = https://example.org/{p.replace("/", "-")}.git\n'
                          for p in sorted(self.corpora))
        (self.root / '.gitmodules').write_text(modules, encoding='utf-8')
        run('add', 'tools', 'manifest.json', '.gitmodules', cwd=self.root)
        for p, c in self.corpora.items():
            sha = run('rev-parse', 'HEAD', cwd=c.path, check=False)
            if sha and len(sha) == 40:
                run('update-index', '--add', '--cacheinfo', f'160000,{sha},{p}', cwd=self.root)
        run('-c', 'user.name=t', '-c', 'user.email=t@example.org', 'commit', '-q', '--allow-empty', '-m', 'pin',
            cwd=self.root)

    def law(self):
        spec = importlib.util.spec_from_file_location(f'law_{id(self)}', self.root / 'tools' / 'law.py')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod  # dataclasses look their module up by name
        spec.loader.exec_module(mod)
        return mod

    def cli(self, *args) -> tuple[str, str, int]:
        done = subprocess.run([sys.executable, '-X', 'utf8', str(self.root / 'tools' / 'law.py'), *args],
                              cwd=self.root, capture_output=True, encoding='utf-8')
        return done.stdout, done.stderr, done.returncode

    def close(self):
        def writable(func, path, _):  # git writes its objects read-only, which Windows will not delete
            os.chmod(path, 0o700)
            func(path)
        shutil.rmtree(self.root, onerror=writable)


class Fixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        # A: an older amendment appended after a newer one, then a repeal of one section.
        a = t.corpus('aa/national/acts')
        a.commit('Act 1 of 2010', {'act/s1.md': '# s1\nThe fee is 10.\nRule two.\n', 'act/s2.md': '# s2\nOld section.\n'},
                 In_force='2010-01-01', Kind='law')
        a.commit('Act 5 of 2020', {'act/s1.md': '# s1\nThe fee is 30.\nRule two.\n'}, In_force='2020-01-01', Kind='amendment')
        a.commit('Act 3 of 2015', {'act/s1.md': '# s1\nThe fee is 20.\nRule two.\n'}, In_force='2015-06-01', Kind='law')
        a.commit('Act 9 of 2022', {'act/s1.md': '# s1\nThe fee is 30.\nRule two.\n', 'act/s2.md': None},
                 In_force='2022-03-01', Kind='law')
        a.commit('Lexifina', {'README.md': '# AA\n'}, Kind='documentation')
        # B: a correction over 2005..2009, appended after the 2010 version.
        b = t.corpus('bb/national/acts')
        b.commit('Act 1 of 2000', {'act/x.md': 'line one\nline two a\n'}, In_force='2000-01-01')
        b.commit('Act 2 of 2010', {'act/x.md': 'line one\nline two b\nline three\n'}, In_force='2010-01-01')
        b.commit('Gazette', {'act/x.md': 'line one\nline two a, corrected\n'}, In_force='2005-01-01', Kind='correction',
                 Corrects='act 2005-01-01..2009-12-31', Files='act/x.md', Reason='misprint')
        b.commit('Act 2 of 2010', {'act/x.md': 'line one\nline two b\nline three\n'}, In_force='2010-01-01')
        # C: a publisher's starting text read on one day; D: other kinds; E: a list of acts; F: law not yet in force.
        c = t.corpus('cc/national/acts')
        c.commit('Publisher of CC', {'l1971/art-1.md': '# Art. 1\nText of 1971.\n'}, In_force='2026-10-30',
                 Kind='publisher')
        d = t.corpus('dd/national/acts')
        d.commit('Act 1 of 2001', {'act/a.md': 'Law text.\n'}, In_force='2001-01-01', Kind='law')
        d.commit('Court 7/2002', {'act/a.md': 'Law text, struck in part.\n'}, In_force='2002-01-01', Kind='court')
        d.commit('Treaty of 2003', {'treaty/t.md': 'Treaty text.\n'}, In_force='2003-01-01', Kind='treaty')
        d.commit('Reprint 2004', {'act/a.md': 'Law text, struck in part (reprint).\n'}, In_force='2004-01-01',
                 Kind='reprint (not credited)')
        d.commit('Odd 2005', {'act/b.md': 'Other law.\n'}, In_force='2005-01-01', Kind='wobble')
        d.commit('Publisher of DD', {'act/b.md': 'Other law, changed.\n'}, In_force='2006-01-01', Kind='publisher',
                 Words_changed='yes')
        c.commit('Publisher of CC', {'l1980/art-1.md': '# Art. 1\nText of 1980.\n'}, In_force='2026-10-31',
                 Text_as_of='2026-10-31', In_force_basis='source gives no date')
        e = t.corpus('ee/national/acts')
        e.commit('Lexifina', {'README.md': '# EE\n\n**Metadata only, no law text.**\n'}, Kind='documentation')
        e.commit('Register', {'acts/1.md': '# Law 1\nNumber: 1\n'}, In_force='2014-01-01')
        f = t.corpus('ff/national/acts')
        f.commit('Act 1 of 2020', {'act/a.md': 'Now.\n'}, In_force='2020-01-01')
        f.commit('Act 2 of 2099', {'act/a.md': 'Later.\n'}, In_force='2099-01-01')
        t.pin()
        cls.law = t.law()

    @classmethod
    def tearDownClass(cls):
        cls.law.close_readers()
        cls.t.close()

    def show(self, date, path):
        return self.law.text_on(date, path)

    def test_older_act_appended_after_newer_reads_by_date(self):
        p = 'aa/national/acts/act/s1.md'
        self.assertEqual(self.show('2009-12-31', p), None)
        self.assertIn('fee is 10', self.show('2012-01-01', p))
        self.assertIn('fee is 20', self.show('2016-01-01', p))
        self.assertIn('fee is 30', self.show('2021-01-01', p))
        self.assertIn('fee is 30', self.show('2023-01-01', p))

    def test_repeal_reads_as_removed(self):
        p = 'aa/national/acts/act/s2.md'
        self.assertIn('Old section', self.show('2021-01-01', p))
        self.assertIsNone(self.show('2023-01-01', p))
        self.assertIn('removed on 2022-03-01 (Act 9 of 2022)', self.law.explain_missing('2023-01-01', p))

    def test_blame_credits_in_force_order(self):
        rows = self.law.blame_on('2021-01-01', 'aa/national/acts/act/s1.md')
        self.assertEqual(dict((line, law) for law, line in rows)['The fee is 30.'], 'Act 5 of 2020')
        rows = self.law.blame_on('2016-01-01', 'aa/national/acts/act/s1.md')
        self.assertEqual(dict((line, law) for law, line in rows)['The fee is 20.'], 'Act 3 of 2015')

    def test_correction_applies_only_in_its_range(self):
        p = 'bb/national/acts/act/x.md'
        self.assertIn('two a\n', self.show('2003-01-01', p))
        self.assertIn('corrected', self.show('2007-01-01', p))
        self.assertIn('two b', self.show('2011-01-01', p))

    def test_blame_under_a_correction_names_no_later_law(self):
        rows = self.law.blame_on('2007-01-01', 'bb/national/acts/act/x.md')
        laws = {law for law, _ in rows}
        self.assertNotIn('Act 2 of 2010', laws)
        self.assertIn('Gazette (correction)', laws)
        words = {law for law, _ in self.law.words_on('2007-01-01', 'bb/national/acts/act/x.md')}
        self.assertNotIn('Act 2 of 2010', words)

    def test_publisher_text_is_where_the_record_starts(self):
        p = 'cc/national/acts/l1971/art-1.md'
        msg = self.law.explain_missing('2000-01-01', p)
        self.assertIn('the record starts on 2026-10-30', msg)
        self.assertNotIn('not yet in force', msg)
        out, err, _ = self.t.cli('laws', '2026-10-30', '2026-10-30')
        self.assertNotIn('cc/national/acts', out)
        self.assertIn('1 starting texts', err)
        # In-force written as the capture day, with Text-as-of and In-force-basis: still a starting text.
        msg = self.law.explain_missing('2000-01-01', 'cc/national/acts/l1980/art-1.md')
        self.assertIn('the record starts on 2026-10-31', msg)

    def test_kinds(self):
        kinds = {e.corpus_commit: e.kind for e in self.law.corpus_events('dd/national/acts')}
        self.assertEqual(sorted(kinds.values()), ['court', 'law', 'law', 'treaty', 'uncredited', 'uncredited'])
        out, err, _ = self.t.cli('laws', '2001-01-01', '2005-12-31', 'dd')
        self.assertIn('Act 1 of 2001', out)
        self.assertIn('Odd 2005', out)
        for left in ('Court 7/2002', 'Treaty of 2003', 'Reprint 2004'):
            self.assertNotIn(left, out)
        self.assertTrue(any('not recognised' in c and 'wobble' in c for c in self.law.caveats('2005-06-01', 'dd/national/acts')))
        rows = self.law.blame_on('2004-06-01', 'dd/national/acts/act/a.md')
        self.assertEqual(rows[0][0], 'Reprint 2004 (no law named for this change)')

    def test_metadata_only_and_current_only_caveats(self):
        cav = ' '.join(self.law.caveats(TODAY, 'ee/national/acts'))
        self.assertIn('without their text', cav)
        cav = ' '.join(self.law.caveats('2000-01-01', 'cc/national/acts'))
        self.assertIn('only the text as the publisher gave it', cav)

    def test_a_part_said_to_be_metadata_only_is_not_a_catalogue(self):
        # romania's README says "decisions about criminal matters are metadata only": that names a part of a record
        # with text, so its Civil Code articles must not be read as catalogue entries.
        key, real = ('metadata-only', 'aa/national/acts'), self.law.read_object
        for readme, expected in (('Decisions about criminal matters are metadata only.', False),
                                 ('**Metadata only, no law text.** A catalogue.', True)):
            self.law._CACHE.pop(key, None)
            self.law.read_object = lambda *a, text=readme: text
            try:
                self.assertEqual(self.law._metadata_only('aa/national/acts'), expected, readme)
            finally:
                self.law.read_object = real
                self.law._CACHE.pop(key, None)

    def test_law_not_yet_in_force_on_main(self):
        p = 'ff/national/acts/act/a.md'
        self.assertEqual(self.show(TODAY, p), 'Now.\n')
        self.assertTrue(any('take force after today' in c for c in self.law.caveats(TODAY, 'ff/national/acts')))

    def test_bare_corpus_path(self):
        out, err, code = self.t.cli('show', TODAY, 'aa/national/acts')
        self.assertNotEqual(code, 0)
        self.assertIn('a whole corpus, not one provision', err)
        self.assertNotIn('Traceback', err)

    def test_index_is_kept_on_disk_and_grows_with_the_pin(self):
        store = Path(subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'global-law-cache'],
                                    cwd=self.t.root, capture_output=True, encoding='utf-8').stdout.strip())
        self.law.corpus_events('ff/national/acts')
        self.assertTrue(list(store.glob('ff~national~acts.v*.*.index')))  # named by its version: two versions do not
        # rebuild each other's index


class LineMatching(unittest.TestCase):
    """How words and blame match one version's lines to the next (performance/experiments/line_matching.md)."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('law_lines', HERE / 'tools' / 'law.py')
        cls.law = importlib.util.module_from_spec(spec)
        sys.modules['law_lines'] = cls.law
        spec.loader.exec_module(cls.law)

    def covers(self, ops, a, b):
        """The opcodes walk both lists end to end, and every 'equal' stretch is equal."""
        ia = ib = 0
        for op, a0, a1, b0, b1 in ops:
            self.assertEqual((a0, b0), (ia, ib))
            if op == 'equal':
                self.assertEqual(a[a0:a1], b[b0:b1])
            ia, ib = a1, b1
        self.assertEqual((ia, ib), (len(a), len(b)))

    def statute(self, n, change):
        lines = []
        for i in range(n):
            lines += [f'## § {i}\n', '\n', f'(1) Text of section {i}, {"amended" if i in change else "as made"}.\n', '\n']
        return lines

    def test_small_comparison_is_difflib(self):
        import difflib
        a, b = self.statute(40, set()), self.statute(41, {3, 17})
        self.assertEqual(self.law._line_opcodes(a, b),
                         difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes())

    def test_large_comparison_is_git_and_matches_the_unchanged_lines(self):
        a = self.statute(700, set())
        b = self.statute(700, {5, 350, 690})
        del b[400:404]  # a section repealed
        b[100:100] = ['## § 100a\n', '\n', '(1) A new section.\n', '\n']  # one inserted
        self.assertGreater(len(a) * len(b), self.law.GIT_DIFF_ABOVE)
        ops = self.law._line_opcodes(a, b)
        self.covers(ops, a, b)
        changed_new = [i for op, _, _, b0, b1 in ops if op != 'equal' for i in range(b0, b1)]
        self.assertEqual(len([i for i in changed_new if b[i].strip()]), 3 + 2)  # 3 amended, the new heading and text

    def test_git_unavailable_falls_back_to_difflib(self):
        a, b = self.statute(700, set()), self.statute(700, {1})
        real = self.law._git_line_opcodes
        self.law._git_line_opcodes = lambda a, b: None
        try:
            self.covers(self.law._line_opcodes(a, b), a, b)
        finally:
            self.law._git_line_opcodes = real

    def test_a_wrong_git_answer_is_never_used(self):  # row 46
        a, b = self.statute(700, set()), self.statute(700, {1, 600})
        real = self.law._hunks_to_opcodes
        self.law._hunks_to_opcodes = lambda hunks, a, b: [('equal', 0, len(a), 0, len(b))]  # an answer read wrong
        try:
            self.assertIsNone(self.law._git_line_opcodes(a, b))
            for ops in self.law._step_opcodes([a, b]):
                pass
            self.covers(ops, a, b)
            self.assertEqual(len([1 for op, *_ in ops if op != 'equal']), 2)
        finally:
            self.law._hunks_to_opcodes = real


class HostileGitConfig(unittest.TestCase):
    """blame and words on a long file (git's batched line diffs) give the same answer whatever the user's git config
    says, and keep a NUL byte and a missing final newline (row 46)."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        base = ''.join(f'Article {i}. Text of article {i}.\n' if i % 2 else '\n' for i in range(1400))
        cls.texts = {
            'Act 1 of 2010': base + 'Final article',  # no final newline
            'Act 2 of 2012': base + 'Final article\nNew article by Act 2.\n',
            'Act 3 of 2015': (base + 'Final article\nNew article by Act 2.\n').replace(
                'Article 5. Text', 'Article 5. NEW\x00TEXT', 1),
        }
        cls.texts['Act 4 of 2020'] = cls.texts['Act 3 of 2015'].replace('Article 701. Text', 'Article 701. Amended', 1)
        a = t.corpus('hh/national/acts')
        # appended out of the order they took force, so blame replays the versions (no git blame)
        for name, day in [('Act 1 of 2010', '2010-01-01'), ('Act 4 of 2020', '2020-01-01'),
                          ('Act 2 of 2012', '2012-01-01'), ('Act 3 of 2015', '2015-01-01')]:
            a.commit(name, {'act/long.md': cls.texts[name]}, In_force=day)
        t.pin()
        cls.path = 'hh/national/acts/act/long.md'
        script = t.root / 'external-diff.sh'
        script.write_bytes(b'#!/bin/sh\nprintf "diff --git a/a/000000 b/b/000000\\n@@ -1 +1 @@\\n"\nexit 0\n')
        os.chmod(script, 0o755)
        cls.hostile = t.root / 'hostile.gitconfig'
        cls.hostile.write_text(
            '[diff]\n\tnoprefix = true\n\tmnemonicPrefix = true\n\trelative = true\n\trenames = copies\n'
            f'\texternal = {script.as_posix()}\n[color]\n\tdiff = always\n\tui = always\n'
            '[core]\n\tquotePath = true\n\tautocrlf = true\n', encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def answers(self, config: Path | None, batch: int | None = None):
        """(words, blame, git pairs that checked out, pairs that did not) with GIT_CONFIG_GLOBAL set to `config`."""
        saved = os.environ.get('GIT_CONFIG_GLOBAL')
        if config:
            os.environ['GIT_CONFIG_GLOBAL'] = str(config)
        law = self.t.law()
        if batch:
            law.STEP_BATCH = batch
        seen = [0, 0]
        real = law._GitDiffs.opcodes

        def counted(diffs):
            out = real(diffs)
            seen[0] += sum(x is not None for x in out)
            seen[1] += sum(x is None for x in out)
            return out
        law._GitDiffs.opcodes = counted
        try:
            return law.words_on('2021-01-01', self.path), law.blame_on('2021-01-01', self.path), seen
        finally:
            law.close_readers()
            if saved is None:
                os.environ.pop('GIT_CONFIG_GLOBAL', None)
            else:
                os.environ['GIT_CONFIG_GLOBAL'] = saved

    def test_the_config_is_hostile(self):
        f1, f2 = self.t.root / 'one.txt', self.t.root / 'two.txt'
        f1.write_text('a\n', encoding='utf-8')
        f2.write_text('b\n', encoding='utf-8')
        env = {**os.environ, 'GIT_CONFIG_GLOBAL': str(self.hostile)}
        diff = ['git', 'diff', '--no-index', str(f1), str(f2)]
        out = subprocess.run(diff, cwd=self.t.root, capture_output=True, env=env).stdout
        self.assertEqual(out, b'diff --git a/a/000000 b/b/000000\n@@ -1 +1 @@\n')  # the external diff ran
        out = subprocess.run([*diff, '--no-ext-diff'], cwd=self.t.root, capture_output=True, env=env).stdout
        self.assertIn(b'\x1b[', out)  # in colour
        self.assertNotIn(b' a/', out)  # with no prefixes

    def test_words_and_blame_are_right(self):
        words, blame, (good, bad) = self.answers(None)
        self.assertEqual((good, bad), (6, 0))  # the long steps (3 each) went to git, and each answer checked out
        text = self.texts['Act 4 of 2020']
        self.assertEqual(''.join(t for _, t in words), text)
        by = {}
        for who, run_ in words:
            for w in run_.split():
                by.setdefault(w, set()).add(who)
        self.assertEqual(by['NEW\x00TEXT'], {'Act 3 of 2015'})
        self.assertEqual(by['Amended'], {'Act 4 of 2020'})
        self.assertEqual(by['Act'], {'Act 2 of 2012'})
        self.assertEqual(by['Final'], {'Act 1 of 2010'})
        self.assertEqual([line for _, line in blame], text.splitlines())
        credit = {line: who for who, line in blame}
        self.assertEqual(credit['New article by Act 2.'], 'Act 2 of 2012')
        self.assertEqual(credit['Article 5. NEW\x00TEXT of article 5.'], 'Act 3 of 2015')
        self.assertEqual(credit['Article 701. Amended of article 701.'], 'Act 4 of 2020')
        self.assertEqual(credit['Article 703. Text of article 703.'], 'Act 1 of 2010')
        self.assertEqual(sum(who != 'Act 1 of 2010' for who, _ in blame), 3)  # blame lines keep no newline

    def test_a_hostile_git_config_changes_nothing(self):
        plain = self.answers(None)
        hostile = self.answers(self.hostile)
        self.assertEqual(hostile[2], [6, 0])
        self.assertEqual(hostile[:2], plain[:2])
        small_batches = self.answers(self.hostile, batch=2)
        self.assertEqual(small_batches[:2], plain[:2])


class StartupCost(unittest.TestCase):
    """What a short read costs before it reads any law (performance/experiments/startup.md): the index kept in
    pieces, the tree's HEAD files kept per commit, one git process a read, and the credits table read by act."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('law_startup', HERE / 'tools' / 'law.py')
        cls.law = importlib.util.module_from_spec(spec)
        sys.modules['law_startup'] = cls.law
        spec.loader.exec_module(cls.law)

    def test_index_in_pieces_gives_back_every_file_in_order(self):
        law = self.law
        files = {f'act{i % 7}/s{i}.md': [(i, f'{i:040x}', '100644')] for i in range(500)}
        data = {'v': 'x', 'pin': 'p', 'rows': [('c', 1)], 'files': dict(files)}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'c.index'
            law._save_index(path, data)
            back = law._load_index(path)
            self.assertEqual(back['rows'], data['rows'])
            self.assertEqual(back['files'].get('act3/s10.md'), files['act3/s10.md'])  # one piece, before the rest
            self.assertIsNone(back['files'].get('nope.md'))
            self.assertNotIn('nope.md', back['files'])
            self.assertEqual(list(back['files'].items()), list(files.items()))
            self.assertEqual(len(back['files']), 500)
            self.assertEqual(dict(back['files'].items()), files)
            back['files']._f.close()  # held open from load (an index replaced under a reader stays readable)

    def test_credits_read_by_act_equal_the_whole_table(self):
        law = self.law
        credits = ('act,in_force,provision,law,was_law,was_commit\n'
                   'old-name,2001-01-01,art-1,l1,,\nnew/1,2001-01-01,art-1,l2,l1,abc123\n'
                   'other,2001-01-01,art-1,l1,,\nnew/1,2002-02-02,art-2,,l1,\n')
        blobs = {'data/credits.csv': credits, 'data/laws.csv': 'key,label\nl1,Law One\nl2,Law Two\n',
                 'data/paths.json': json.dumps({'paths': {'old-name': 'new/1'}})}
        saved = law.read_object, law._index
        law.read_object = lambda corpus, spec: blobs.get(spec.split(':', 1)[1])
        law._index = lambda corpus: {'pin': 'p'}
        try:
            law._CACHE.clear()
            self.assertEqual(law.credited('c', 'new/1/art-1.md', '2001-01-01', 'abc123'), ('Law Two', False, 'Law One'))
            self.assertEqual(law.credited('c', 'new/1/art-1.md', '2001-01-01', 'fff'), ('Law One', False, 'no law named (a change the record leaves unexplained)'))
            self.assertEqual(law.credited('c', 'old-name/art-1.md', '2001-01-01'), law.credited('c', 'old-name/art-1.md', '2001-01-01'))
            self.assertEqual(law.credited('c', 'new/1/art-2.md', '2002-02-02')[:2], ('no law named (a change the record leaves unexplained)', True))
            self.assertIsNone(law.credited('c', 'other/art-9.md', '2001-01-01'))
        finally:
            law.read_object, law._index = saved
            law._CACHE.clear()

    def test_a_read_starts_one_git_process(self):
        t = Tree()
        try:
            a = t.corpus('aa/national/acts')
            a.commit('Act 1 of 2010', {'act/s1.md': 'one\n'}, In_force='2010-01-01', Kind='law')
            t.pin()
            out, err, code = t.cli('show', TODAY, 'aa/national/acts/act/s1.md')  # indexes, and keeps HEAD's files
            self.assertEqual(out, 'one\n', err)
            trace = t.root / 'trace.txt'
            done = subprocess.run([sys.executable, '-X', 'utf8', str(t.root / 'tools' / 'law.py'), 'show', TODAY,
                                   'aa/national/acts/act/s1.md'], cwd=t.root, capture_output=True, encoding='utf-8',
                                  env={**os.environ, 'GIT_TRACE2': str(trace)})
            self.assertEqual(done.stdout, 'one\n', done.stderr)
            started = [l for l in trace.read_text(encoding='utf-8').splitlines() if l.split()[2:3] == ['version']]
            self.assertEqual(len(started), 1, trace.read_text(encoding='utf-8'))
            a.commit('Act 2 of 2020', {'act/s1.md': 'two\n'}, In_force='2020-01-01', Kind='law')
            t.pin()  # a new HEAD: read again, not taken from the last commit's files
            out, err, code = t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
            self.assertEqual(out, 'two\n', err)
        finally:
            t.close()


class WholeLawRepealsAndDoubtfulDates(unittest.TestCase):
    """An act that data/acts.json records as repealed ends every file of it, though the files stay (global-law #8);
    dates the record itself makes doubtful are said so."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('aa/national/acts')
        a.commit('Act 1 of 2010', {'act/s1.md': 'one\n', 'act/s2.md': 'two\n', 'other/s1.md': 'other\n'},
                 In_force='2010-01-01', Kind='law', Enacted='2009-12-01')
        # Delayed amendments made before the repeal, taking effect after it (Spain's ET art. 48 bis, Ley 9/2009): one
        # enacted before the repeal, one with no enactment date. Neither brings its file back.
        a.commit('Act 6 of 2010', {'late/s1.md': 'late one\n', 'late/s2.md': 'late two\n'},
                 In_force='2010-01-01', Kind='law', Enacted='2009-12-01')
        a.commit('Act 8 of 2018', {'late/s1.md': 'late one, amended\n'}, In_force='2021-01-01', Kind='law',
                 Enacted='2018-03-01')
        a.commit('Act 7 of 2017', {'late/s2.md': 'late two, amended\n'}, In_force='2021-01-01', Kind='law')
        # And one enacted after the repeal: it re-enacts.
        a.commit('Act 13 of 2020', {'late/s3.md': 'late three\n'}, In_force='2021-03-01', Kind='law',
                 Enacted='2020-11-01')
        # The repeal as spain-law records it: a note in the act's folder, the provisions left as they were.
        a.commit('Act 9 of 2019', {'act/no.md': 'Repealed with effect from 2020-01-01.\n', 'other/s1.md': 'other 2\n'},
                 In_force='2020-01-01', Kind='law', Enacted='2019-06-01')
        a.commit('Act 12 of 2022', {'act/s1.md': 'one again\n'}, In_force='2022-01-01', Kind='law', Enacted='2021-11-01')
        a.commit('Act 3 of 2015', {'other/s2.md': 'typo\n'}, In_force='0015-03-01', Kind='law', Enacted='2015-02-01')
        a.commit('Act 4 of 2016', {'other/s3.md': 'late\n'}, In_force='2014-01-01', Kind='law', Enacted='2016-05-01')
        a.commit('Act 5 of 2016', {'other/s4.md': 'back\n'}, In_force='2016-01-01', Kind='law', Enacted='2016-05-01')
        # A paragraph moved to the end and amended by one law, unchanged rules between (sb/2007/378's case).
        rules = ''.join(f'Rule {n} stays exactly where it is, word for word.\n' for n in ('one', 'two', 'three'))
        old = 'The minister shall publish the yearly report of the agency in the gazette.\n' + rules
        new = (rules + 'A new rule about something else entirely added here.\n'
               'The minister shall publish the yearly report of the agency in the official gazette.\n')
        a.commit('Act 20 of 2001', {'move/s1.md': old}, In_force='2001-01-01', Kind='law', Enacted='2000-12-01')
        a.commit('Act 21 of 2005', {'move/s1.md': new}, In_force='2005-01-01', Kind='law', Enacted='2004-12-01')
        # An act held only as captured text (a baseline), its own commencement known from data/acts.json.
        a.commit('Publisher', {'cap/a.md': 'captured\n'}, Kind='baseline', Text_as_of='2018-05-01',
                 In_force_basis='source gives no date')
        b = t.corpus('bb/national/acts')  # a corpus that says it models every effect beyond the text
        b.commit('Act 1 of 2010', {'act/s1.md': 'bee\n'}, In_force='2010-01-01', Kind='law')
        b.commit('Lexifina', {'corpus.json': json.dumps({'effects': ['modifications', 'commencement', 'transitional']})},
                 Kind='documentation')
        run('checkout', '-q', 'main', cwd=b.path)
        acts = {'acts': [{'path': 'cap', 'status': 'as captured', 'in_force': '1990-01-01'},
                         {'path': 'act', 'status': 'repealed', 'repealed': '2020-01-01', 'repealed_by': 'Act 9 of 2019'},
                         {'path': 'late', 'status': 'repealed', 'repealed': '2020-01-01', 'repealed_by': 'Act 9 of 2019'},
                         {'path': 'other', 'status': 'in force'}]}
        a.commit('Lexifina', {'data/acts.json': json.dumps(acts)}, Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_a_repealed_act_ends_each_of_its_files(self):
        out, err, code = self.t.cli('show', '2019-12-31', 'aa/national/acts/act/s2.md')
        self.assertEqual(out, 'two\n', err)
        out, err, code = self.t.cli('show', '2020-01-01', 'aa/national/acts/act/s2.md')
        self.assertNotEqual(code, 0)
        self.assertIn('was repealed on 2020-01-01 by Act 9 of 2019', err)
        self.assertIn('data/acts.json', err)

    def test_the_repeal_is_in_the_log(self):
        out, err, code = self.t.cli('log', 'aa/national/acts/act/s2.md')
        self.assertIn('repealed 2020-01-01  Act 9 of 2019', out, err)

    def test_a_later_version_reenacts(self):
        out, err, code = self.t.cli('show', '2021-06-01', 'aa/national/acts/act/s1.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('in force again from 2022-01-01', err)
        out, err, code = self.t.cli('show', '2023-01-01', 'aa/national/acts/act/s1.md')
        self.assertEqual(out, 'one again\n', err)

    def test_a_delayed_amendment_made_before_the_repeal_stays_ended(self):
        out, err, code = self.t.cli('show', '2019-12-31', 'aa/national/acts/late/s1.md')
        self.assertEqual(out, 'late one\n', err)
        for date in ('2021-01-01', '2026-01-01'):
            out, err, code = self.t.cli('show', date, 'aa/national/acts/late/s1.md')
            self.assertNotEqual(code, 0, out)
            self.assertIn('was repealed on 2020-01-01', err)
            self.assertNotIn('in force again', err)
            self.assertIn('2021-01-01 Act 8 of 2018 (enacted 2018-03-01)', err)

    def test_a_delayed_amendment_with_no_enactment_date_stays_ended(self):
        out, err, code = self.t.cli('show', '2022-01-01', 'aa/national/acts/late/s2.md')
        self.assertNotEqual(code, 0, out)
        self.assertNotIn('in force again', err)
        self.assertIn('2021-01-01 Act 7 of 2017 (no enactment date)', err)

    def test_a_version_enacted_after_the_repeal_reenacts(self):
        out, err, code = self.t.cli('show', '2021-06-01', 'aa/national/acts/late/s3.md')
        self.assertEqual(out, 'late three\n', err)

    def test_show_log_and_world_agree_on_the_delayed_amendment(self):
        out, err, code = self.t.cli('log', 'aa/national/acts/late/s1.md')
        self.assertIn('repealed 2020-01-01  Act 9 of 2019', out, err)
        self.assertIn('not re-enacted by: 2021-01-01 Act 8 of 2018 (enacted 2018-03-01)', out)
        self.assertNotIn('in force 2021-01-01', out)
        law = self.t.law()
        try:
            self.assertIsNone(law.text_on('2022-01-01', 'aa/national/acts/late/s1.md'))
            index, _ = law.file_index('aa/national/acts')
            best = {p: max(v for v in vs if v[0] <= '2022-01-01') for p, vs in index.items() if p.startswith('late/')}
            self.assertEqual([p for p, v in sorted(best.items()) if v[2]], ['late/s3.md'])
            tree = law.corpus_tree('2022-01-01', 'aa/national/acts')
            names = law.git('ls-tree', '-r', '--name-only', tree, cwd=law.corpus_dir('aa/national/acts')).split()
        finally:
            law.close_readers()
        self.assertEqual([n for n in names if n.startswith('late/')], ['late/s3.md'])

    def test_other_acts_are_untouched(self):
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/other/s1.md')
        self.assertEqual(out, 'other 2\n', err)

    def test_blame_and_words_stop_at_the_repeal(self):
        for cmd in ('blame', 'words'):
            out, err, code = self.t.cli(cmd, '2020-06-01', 'aa/national/acts/act/s2.md')
            self.assertNotEqual(code, 0, out)
            self.assertIn('repealed on 2020-01-01', err)

    def test_the_world_on_a_date_leaves_the_repealed_files_out(self):
        law = self.t.law()
        files = law._index('aa/national/acts')['files']  # warm
        index, _ = law.file_index('aa/national/acts')
        best = {p: max((v for v in vs if v[0] <= '2021-01-01'), default=None) for p, vs in index.items()}
        law.close_readers()
        self.assertIsNone(best['act/s2.md'][2])
        self.assertIsNotNone(best['other/s1.md'][2])
        self.assertTrue(files)

    def test_search_and_world_trees_leave_the_repealed_act_out(self):
        law = self.t.law()
        self.assertFalse(law.in_order('aa/national/acts'))  # its commit-order prefix still holds the repealed files
        tree = law.corpus_tree('2021-01-01', 'aa/national/acts')
        names = law.git('ls-tree', '-r', '--name-only', tree, cwd=law.corpus_dir('aa/national/acts')).split()
        law.close_readers()
        self.assertNotIn('act/s2.md', names)
        self.assertIn('other/s1.md', names)

    def test_names_take_in_whole_path_segments_only(self):
        law = self.t.law()
        self.assertTrue(law._under('niger/national/acts', 'niger'))
        self.assertFalse(law._under('nigeria/national/acts', 'niger'))
        self.assertTrue(law._under('nigeria/niger/acts', 'nigeria/niger'))
        self.assertTrue(law._under('anything/at/all', ''))

    def test_moved_and_amended_text_keeps_its_law(self):
        law = self.t.law()
        runs = law.words_on('2010-01-01', 'aa/national/acts/move/s1.md')
        law.close_readers()
        by = {}
        for who, text in runs:
            for w in text.split():
                by.setdefault(w, set()).add(who)
        self.assertEqual(by['minister'], {'Act 20 of 2001'})  # moved: written in 2001
        self.assertEqual(by['yearly'], {'Act 20 of 2001'})
        self.assertEqual(by['official'], {'Act 21 of 2005'})  # the word the move added
        self.assertEqual(by['entirely'], {'Act 21 of 2005'})  # a new rule, not a move

    def test_effects_a_corpus_does_not_model_are_named(self):
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/other/s1.md')
        self.assertIn('does not hold changes that alter how a provision applies', err)
        self.assertIn('transitional and saving rules', err)
        out, err, code = self.t.cli('show', '2021-01-01', 'bb/national/acts/act/s1.md')
        self.assertEqual(out, 'bee\n', err)
        self.assertNotIn('does not hold', err)

    def test_an_act_held_only_as_captured_text_says_so(self):
        out, err, code = self.t.cli('show', '2000-01-01', 'aa/national/acts/cap/a.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('the record starts on 2018-05-01', err)
        self.assertIn('Its act was in force from 1990-01-01', err)  # A8: not "not yet in force"
        out, err, code = self.t.cli('show', '2020-01-01', 'aa/national/acts/cap/a.md')
        self.assertEqual(out, 'captured\n', err)
        self.assertIn('holds only the text as the publisher gave it (from 2018-05-01)', err)  # A9
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/other/s1.md')
        self.assertNotIn('holds only the text', err)

    def test_doubtful_dates_are_said(self):
        out, err, code = self.t.cli('log', 'aa/national/acts/other/s2.md')
        self.assertIn('date doubtful', out)
        self.assertIn('mistyped date', out)
        out, err, code = self.t.cli('log', 'aa/national/acts/other/s3.md')
        self.assertIn('more than a year before its act was made', out)
        out, err, code = self.t.cli('log', 'aa/national/acts/other/s4.md')  # months before: often real, not flagged
        self.assertNotIn('date doubtful', out)
        out, err, code = self.t.cli('show', '2015-01-01', 'aa/national/acts/other/s3.md')
        self.assertEqual(out, 'late\n')
        self.assertIn('more than a year before its act was made', err)


class RedatedVersions(unittest.TestCase):
    """An append-only corpus corrects a version's date with a later commit (Redates: <commit> <day> | no-date)."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('cc/national/acts')
        a.commit('Act 1 of 2010', {'s1.md': 'one\n', 's2.md': 'two\n', 's3.md': 'three\n'}, In_force='2010-01-01',
                 Kind='law', Enacted='2009-12-01')
        typo = a.commit('Act 2 of 2015', {'s1.md': 'one amended\n'}, In_force='0015-03-01', Kind='law',
                        Enacted='2015-02-01')
        retro = a.commit('Act 3 of 2016', {'s2.md': 'two amended\n'}, In_force='2014-01-01', Kind='law',
                         Enacted='2016-05-01')
        read = a.commit('Act 4 of 2017', {'s3.md': 'three as read\n'}, In_force='2017-06-01', Kind='law')
        a.commit('Lexifina', {}, Kind='documentation', Redates=[f'{typo} 2015-03-01', f'{read} no-date'],
                 Reason='the source gives 2015-03-01; the 2017 text is the day it was read')
        a.commit('Lexifina', {}, Kind='documentation', Redates=f'{retro} 2014-01-01',
                 Retroactive='yes; Act 3 of 2016, s. 9 (effect from 1 January 2014)')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_a_mistyped_date_is_corrected(self):
        out, err, code = self.t.cli('show', '2015-02-28', 'cc/national/acts/s1.md')
        self.assertEqual(out, 'one\n', err)
        out, err, code = self.t.cli('show', '2015-03-01', 'cc/national/acts/s1.md')
        self.assertEqual(out, 'one amended\n', err)
        out, err, code = self.t.cli('log', 'cc/national/acts/s1.md')
        self.assertIn('2015-03-01', out)
        self.assertNotIn('0015-03-01', out)
        self.assertNotIn('date doubtful', out)

    def test_a_retroactive_date_stands_unflagged(self):
        out, err, code = self.t.cli('show', '2014-06-01', 'cc/national/acts/s2.md')
        self.assertEqual(out, 'two amended\n', err)
        out, err, code = self.t.cli('log', 'cc/national/acts/s2.md')
        self.assertNotIn('date doubtful', out)

    def test_no_date_makes_a_version_text_as_read(self):
        out, err, code = self.t.cli('log', 'cc/national/acts/s3.md')
        self.assertIn('version of', out)


class SameDayVersions(unittest.TestCase):
    """Two laws in force the same day (#12): the first build kept only the last version, so the earlier law's
    version is appended, dated that day, and the last one re-asserted (Re-asserts: <commit>). The text in force
    stays; blame and words credit each law with its own words."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('sd/national/acts')
        a.commit('Act 1 of 2010', {'s1.md': 'alpha beta\n\nrate 10\n', 's2.md': 'two\n'}, In_force='2010-01-01')
        cls.last = a.commit('Act 9 of 2022', {'s1.md': 'alpha gamma delta\n\nrate 12\n'}, In_force='2023-01-01',
                            Enacted='2022-12-23')
        a.commit('Lexifina', {'s1.md': 'alpha gamma delta\n\nrate 10\n'}, In_force='2023-01-01',
                 Law='Act 8 of 2022', Enacted='2022-12-21')
        a.commit('Lexifina', {'s1.md': 'alpha gamma delta\n\nrate 12\n'}, In_force='2023-01-01',
                 Re_asserts=cls.last, Enacted='2022-12-23')
        # Romania's pattern stays as it was: a correction re-asserting a commit that never wrote the file, after
        # another version of that day.
        other = a.commit('Act 7 of 2022', {'s3.md': 'x\n'}, In_force='2023-01-01')
        a.commit('Act 6 of 2022', {'s2.md': 'two amended\n'}, In_force='2023-01-01')
        a.commit('Lexifina', {'s2.md': 'two amended\n'}, In_force='2023-01-01', Re_asserts=other, Kind='correction')
        t.pin()
        cls.law = t.law()

    @classmethod
    def tearDownClass(cls):
        cls.law.close_readers()
        cls.t.close()

    def test_text_in_force_is_unchanged(self):
        for day in ('2022-12-31', '2023-01-01', '2024-01-01'):
            out, err, code = self.t.cli('show', day, 'sd/national/acts/s1.md')
            self.assertEqual(out, 'alpha beta\n\nrate 10\n' if day < '2023' else 'alpha gamma delta\n\nrate 12\n', err)

    def test_each_law_is_credited_with_its_words(self):
        law = self.law
        rows = law.blame_on('2024-01-01', 'sd/national/acts/s1.md')
        self.assertEqual([who for who, _ in rows], ['Act 8 of 2022', 'Act 1 of 2010', 'Act 9 of 2022'])
        words = law.words_on('2024-01-01', 'sd/national/acts/s1.md')
        self.assertIn(('Act 8 of 2022', 'gamma delta\n\n'), [(w, t) for w, t in words])
        self.assertEqual([w for w, t in words if '12' in t], ['Act 9 of 2022'])

    def test_a_restated_commit_that_never_wrote_the_file_adds_no_step(self):
        law = self.law
        seq = law.versions_in_force('2024-01-01', 'sd/national/acts/s2.md')
        self.assertEqual(len(seq), 2)


class FifthOfNovemberFixes(unittest.TestCase):
    """Second audit (4 November 2026), rows 19-23: a redated overlay correction, laws by any name, built trees'
    index files, an index replaced under a reader, and a shallow corpus in a whole-tree read."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('rr/national/acts')
        a.commit('Act 1 of 2000', {'act/x.md': 'original\n'}, In_force='2000-01-01', Kind='law')
        a.commit('Act 2 of 2010', {'act/x.md': 'amended 2010\n'}, In_force='2010-01-01', Kind='law')
        fix = a.commit('Gazette', {'act/x.md': 'original, corrected\n'}, In_force='2005-01-01', Kind='correction',
                       Corrects='act 2005-01-01..2009-12-31', Files='act/x.md', Reason='misprint')
        a.commit('Act 2 of 2010', {'act/x.md': 'amended 2010\n'}, In_force='2010-01-01')
        a.commit('Lexifina', {}, Kind='documentation', Redates=f'{fix} 2007-01-01', Reason='applies from 2007')
        b = t.corpus('qq/upper/acts')  # a state of qq, named on its own
        b.commit('State Act 1 of 2020', {'s1.md': 'state\n'}, In_force='2020-06-01', Kind='law')
        s = t.corpus('tt/national/acts')  # cloned with --depth below: one commit, so the clone holds it all
        s.commit('Act 1 of 2021', {'s1.md': 'tee\n'}, In_force='2021-01-01', Kind='law')
        u = t.corpus('uu/national/acts')  # cloned with --depth 1 of 2: its history is cut
        u.commit('Act 1 of 2019', {'s1.md': 'you\n'}, In_force='2019-01-01', Kind='law')
        u.commit('Act 2 of 2022', {'s1.md': 'you two\n'}, In_force='2022-01-01', Kind='law')
        t.pin()
        for name in ('tt', 'uu'):
            src = t.root / f'{name}/national/acts'
            shutil.move(str(src), str(t.root / f'{name}-full'))
            run('clone', '-q', '--depth', '1', (t.root / f'{name}-full').as_uri(), str(src), cwd=t.root)

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_a_redated_overlay_correction_moves_its_text(self):  # row 19
        for day, text in (('2006-01-01', 'original\n'), ('2008-01-01', 'original, corrected\n')):
            out, err, code = self.t.cli('show', day, 'rr/national/acts/act/x.md')
            self.assertEqual(out, text, (day, err))

    def test_laws_takes_a_state_by_its_own_name_and_refuses_an_unknown_one(self):  # row 20
        out, err, code = self.t.cli('laws', '2020-01-01', '2020-12-31', 'upper')
        self.assertIn('State Act 1 of 2020', out, err)
        out, err, code = self.t.cli('laws', '2020-01-01', '2020-12-31', 'qqq')
        self.assertNotEqual(code, 0)
        self.assertIn('No body of law in this tree matches', err)

    def test_a_built_tree_leaves_no_index_file(self):  # row 21
        law = self.t.law()
        law.corpus_tree('2006-01-01', 'rr/national/acts')
        store = law._tree_store()
        left = list(store.glob('index-*'))
        law.close_readers()
        self.assertEqual(left, [])

    def test_a_reader_survives_its_index_being_replaced(self):  # row 22
        law = self.t.law()
        ix = law._index('rr/national/acts')
        path = next(Path(ix['files']._path).parent.glob('rr~national~acts.v*.*.index'))
        try:  # another process writes a different index in its place (refused on Windows while it is open)
            path.with_name('other.tmp').write_bytes(b'GLX2' + (5).to_bytes(8, 'little') + b'xxxxx')
            os.replace(path.with_name('other.tmp'), path)
        except OSError:
            path.with_name('other.tmp').unlink(missing_ok=True)
        try:
            self.assertEqual([v[0] for v in ix['files']['act/x.md']][:1], [0])
        finally:
            law.close_readers()
            path.unlink(missing_ok=True)

    def test_old_indexes_and_tmp_files_are_removed(self):  # row 29
        law = self.t.law()
        with tempfile.TemporaryDirectory() as d:
            store, name = Path(d), 'xx~national~acts'
            keep = store / f'{name}.v{law.INDEX_VERSION}.bbbbbbbbbbbb.index'
            gone = [store / f'{name}.v{law.INDEX_VERSION}.aaaaaaaaaaaa.index', store / f'{name}.v{law.INDEX_VERSION}.index',
                    store / f'{name}.index', store / f'{name}.pickle', store / f'{name}.v1.cccc.index.77.tmp']
            stays = [store / f'{name}.v99.dddd.index', store / 'xx~national~acts~other.v1.eeee.index']
            for f in [keep] + gone + stays:
                f.write_bytes(b'x')
            os.utime(gone[-1], (0, 0))  # an old .tmp
            law._prune_indexes(store, name, keep)
            self.assertEqual(sorted(f.name for f in store.iterdir()), sorted(f.name for f in [keep] + stays))

    def test_a_reader_keeps_only_the_current_pin(self):  # row 27
        law = self.t.law()
        law._CACHE[('index', 'rr/national/acts@old')] = {'files': {}}
        law._CACHE[('file-index', 'rr/national/acts@old')] = ({}, [])
        law._CACHE[('index', 'rr/national/acts~x@old')] = {}  # another corpus, a longer name
        law._forget_other_pins('rr/national/acts', 'new')
        self.assertNotIn(('index', 'rr/national/acts@old'), law._CACHE)
        self.assertNotIn(('file-index', 'rr/national/acts@old'), law._CACHE)
        self.assertIn(('index', 'rr/national/acts~x@old'), law._CACHE)

    def test_tree_folders_are_removed_though_git_made_them_read_only(self):  # row 28
        law = self.t.law()
        d = Path(tempfile.mkdtemp(prefix='gl-rmtree-'))
        (d / 'objects' / 'ab').mkdir(parents=True)
        f = d / 'objects' / 'ab' / 'cdef'
        f.write_bytes(b'x')
        os.chmod(f, 0o444)
        law._rmtree(d)
        self.assertFalse(d.exists())

    def test_a_shallow_corpus_is_left_out_of_world_not_fatal(self):  # row 23
        out, err, code = self.t.cli('world', '2023-01-01')
        self.assertEqual(code, 0, err)
        self.assertIn('uu/national/acts is a shallow clone', err)
        self.assertIn('Act 1 of 2021', out)  # tt: shallow but holding its root, so complete
        out, err, code = self.t.cli('show', '2023-01-01', 'uu/national/acts/s1.md')
        self.assertNotEqual(code, 0)
        self.assertIn('fetch --unshallow', err)


class FutureBranches(unittest.TestCase):
    """Laws with a later in-force day kept on a future branch, read beside main once their day comes, as the tree's
    data/future-pins.tsv records them (corpus, branch, future_sha, main_pin): a branch that descends from the pin, one
    that forked before it (main went on with documentation and a law the branch copied), a row made for an earlier
    pin, and a recorded commit the checkout does not have."""

    BEFORE, ON = '2020-05-31', '2020-06-01'

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        cls.rows = {}
        # Linear: the branch goes on from the pinned main commit.
        a = t.corpus('li/national/acts')
        a.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\nRule two.\n', 'act/s2.md': 'Other.\n'},
                 In_force='2010-01-01', Kind='law')
        pin = a.commit('Lexifina', {'README.md': '# LI\n'}, Kind='documentation')
        run('checkout', '-q', '-b', 'future', cwd=a.path)
        a.commit('Act 2 of 2020', {'act/s1.md': 'The fee is 20.\nRule two.\n'}, In_force=cls.ON, Kind='law')
        fut = a.commit('Act 3 of 2099', {'act/s1.md': 'The fee is 99.\nRule two.\n'}, In_force='2099-01-01', Kind='law')
        run('checkout', '-q', 'main', cwd=a.path)
        cls.rows['li/national/acts'] = ('future', fut, pin)
        # Forked: the branch left main at its last law; main went on with a law the branch copies (same author line
        # and message) and with documentation the branch does not have.
        f = t.corpus('fk/national/acts')
        f.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\nRule two.\n'}, In_force='2010-01-01', Kind='law')
        run('checkout', '-q', '-b', 'zukunft', cwd=f.path)
        run('checkout', '-q', 'main', cwd=f.path)
        later = f.commit('Act 4 of 2015', {'act/s4.md': 'Section four.\n'}, In_force='2015-01-01', Kind='law')
        pin = f.commit('Lexifina', {'README.md': '# FK\n'}, Kind='documentation')
        run('checkout', '-q', 'zukunft', cwd=f.path)
        run('cherry-pick', later, cwd=f.path,
            env={'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.org'})
        f.commit('Act 2 of 2020', {'act/s1.md': 'The fee is 20.\nRule two.\n'}, In_force=cls.ON, Kind='law')
        fut = f.commit('Act 3 of 2099', {'act/s1.md': 'The fee is 99.\nRule two.\n'}, In_force='2099-01-01', Kind='law')
        run('checkout', '-q', 'main', cwd=f.path)
        cls.rows['fk/national/acts'] = ('zukunft', fut, pin)
        # Stale: the row names the main pin before the last one (the pin moved, the file was not written again).
        s = t.corpus('st/national/acts')
        old = s.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\n'}, In_force='2010-01-01', Kind='law')
        run('checkout', '-q', '-b', 'future', cwd=s.path)
        fut = s.commit('Act 2 of 2020', {'act/s1.md': 'The fee is 20.\n'}, In_force=cls.ON, Kind='law')
        run('checkout', '-q', 'main', cwd=s.path)
        s.commit('Lexifina', {'README.md': '# ST\n'}, Kind='documentation')
        cls.rows['st/national/acts'] = ('future', fut, old)
        # Missing: the checkout has never fetched the recorded future commit.
        m = t.corpus('mi/national/acts')
        pin = m.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\n'}, In_force='2010-01-01', Kind='law')
        cls.rows['mi/national/acts'] = ('future', 'f' * 40, pin)
        # Behind (audit row 60): the row was written while the branch went on from the pin; then main moved on with a
        # law the branch lacks (Act 5 of 2015, at a file one of the branch's own laws also changes).
        b = t.corpus('bh/national/acts')
        old = b.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\nRule two.\n', 'act/s2.md': 'Other.\n'},
                       In_force='2010-01-01', Kind='law')
        run('checkout', '-q', '-b', 'zukunft', cwd=b.path)
        b.commit('Act 2 of 2020', {'act/s1.md': 'The fee is 20.\nRule two.\n'}, In_force=cls.ON, Kind='law')
        fut = b.commit('Act 6 of 2020', {'act/s2.md': 'Other, as the branch has it.\n'}, In_force=cls.ON, Kind='law')
        run('checkout', '-q', 'main', cwd=b.path)
        b.commit('Act 5 of 2015', {'act/s2.md': 'Other, amended.\n'}, In_force='2015-01-01', Kind='law')
        cls.rows['bh/national/acts'] = ('zukunft', fut, old)
        cls.write_rows()
        t.pin()

    @classmethod
    def write_rows(cls):
        data = cls.t.root / 'data'
        data.mkdir(exist_ok=True)
        (data / 'future-pins.tsv').write_bytes(
            ('# corpus\tbranch\tfuture_sha\tmain_pin\n'
             + ''.join(f'{c}\t{b}\t{f}\t{p}\n' for c, (b, f, p) in sorted(cls.rows.items()))).encode('utf-8'))
        run('add', 'data', cwd=cls.t.root)

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def check_reads(self, corpus):
        p = f'{corpus}/act/s1.md'
        out, err, code = self.t.cli('show', self.BEFORE, p)
        self.assertEqual(out, 'The fee is 10.\nRule two.\n', err)
        out, err, code = self.t.cli('show', self.ON, p)
        self.assertEqual(out, 'The fee is 20.\nRule two.\n', err)
        out, err, code = self.t.cli('show', TODAY, p)
        self.assertEqual(out, 'The fee is 20.\nRule two.\n', err)  # the 2099 law only from its day
        self.assertIn('take force after today', err)
        out, err, code = self.t.cli('blame', self.BEFORE, p)
        self.assertIn('Act 1 of 2010', out, err)
        self.assertNotIn('Act 2 of 2020', out)
        out, err, code = self.t.cli('blame', self.ON, p)
        line = next(l for l in out.splitlines() if 'fee is 20' in l)
        self.assertIn('Act 2 of 2020', line)
        self.assertIn(self.ON, line)
        self.assertIn('Act 1 of 2010', next(l for l in out.splitlines() if 'Rule two' in l))
        out, err, code = self.t.cli('diff', self.BEFORE, self.ON, p)
        self.assertIn('[-10.-]{+20.+}', out, err)
        out, err, code = self.t.cli('diff', '2010-01-01', self.BEFORE, p)
        self.assertIn('No change between those dates', out, err)
        out, err, code = self.t.cli('log', p)
        self.assertIn(f'in force {self.ON}  Act 2 of 2020', out, err)
        self.assertIn('in force 2099-01-01  Act 3 of 2099', out)
        out, err, code = self.t.cli('world', self.BEFORE)
        self.assertEqual(code, 0, err)
        self.assertRegex(out, rf'{corpus}\s+Act (1 of 2010|4 of 2015), in force 20(10|15)-01-01')
        out, err, code = self.t.cli('world', self.ON)
        self.assertRegex(out, rf'{corpus}\s+Act 2 of 2020, in force {self.ON}')
        out, err, code = self.t.cli('laws', '2020-01-01', '2020-12-31', corpus)
        self.assertIn(f'{self.ON}  {corpus}', out, err)
        self.assertIn('Act 2 of 2020', out)

    def test_a_linear_future_branch_is_read_from_its_day(self):
        self.check_reads('li/national/acts')
        law = self.t.law()
        ix = law._index('li/national/acts')
        self.assertTrue(ix['future']['linear'])
        self.assertTrue(law.in_order('li/national/acts'))
        law.close_readers()

    def test_a_forked_future_branch_is_read_beside_main(self):
        self.check_reads('fk/national/acts')
        out, err, code = self.t.cli('log', 'fk/national/acts/act/s4.md')
        self.assertEqual(out.count('Act 4 of 2015'), 1, out)  # the branch's copy of a main law is not a second one
        out, err, code = self.t.cli('show', self.ON, 'fk/national/acts/act/s4.md')
        self.assertEqual(out, 'Section four.\n', err)
        law = self.t.law()
        ix = law._index('fk/national/acts')
        self.assertFalse(ix['future']['linear'])
        self.assertEqual(ix['future']['replays_skipped'], 1)
        self.assertFalse(law.in_order('fk/national/acts'))
        tree = law.corpus_tree(self.ON, 'fk/national/acts')  # main's documentation and the branch's law together
        names = law.git('ls-tree', '-r', '--name-only', tree, cwd=law.corpus_dir('fk/national/acts')).split()
        law.close_readers()
        self.assertIn('act/s4.md', names)

    def test_a_row_for_an_earlier_pin_falls_back_to_main(self):
        p = 'st/national/acts/act/s1.md'
        out, err, code = self.t.cli('show', self.ON, p)
        self.assertEqual(out, 'The fee is 10.\n', err)  # main alone, never main and an old branch together
        self.assertIn('records that branch for an earlier pin', err)
        out, err, code = self.t.cli('log', p)
        self.assertNotIn('Act 2 of 2020', out)
        out, err, code = self.t.cli('world', self.ON)
        self.assertRegex(out, r'st/national/acts\s+Act 1 of 2010')
        self.assertIn('st/national/acts: laws with a later in-force day are kept on its future branch', err)

    def test_a_future_commit_the_checkout_lacks_falls_back_with_the_fetch(self):
        out, err, code = self.t.cli('show', self.ON, 'mi/national/acts/act/s1.md')
        self.assertEqual(out, 'The fee is 10.\n', err)
        self.assertIn('which this checkout does not have', err)
        self.assertIn('Run: git -C mi/national/acts fetch origin future', err)

    def run_future_pins(self) -> tuple[dict, dict]:
        """tools/future_pins.py over this tree as the repoint loop runs it (--pins, --tree-ref HEAD), the corpus
        repositories read from their folders: ({corpus: (branch, future_sha, main_pin)}, summary)."""
        import contextlib
        import io
        sys.path.insert(0, str(HERE / 'tools'))
        import future_pins as fp
        t = self.t
        local = {f'https://example.org/{p.replace("/", "-")}.git': str(c.path) for p, c in t.corpora.items()}
        work = Path(tempfile.mkdtemp(prefix='gl-fp-'))
        (work / 'pins.tsv').write_text(''.join(f"{p}\t{run('rev-parse', 'HEAD', cwd=c.path)}\n"
                                               for p, c in t.corpora.items()), encoding='utf-8')
        saved = fp.ROOT, fp.ls_remote, fp.fetch
        ls_remote, fetch = fp.ls_remote, fp.fetch
        fp.ROOT = t.root
        fp.ls_remote = lambda url: ls_remote(local[url])
        fp.fetch = lambda repo, url, branch, pin: fetch(repo, local[url], branch, pin)
        out = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        try:
            with contextlib.redirect_stdout(out):
                fp.main(['--pins', str(work / 'pins.tsv'), '--tree-ref', 'HEAD', '--cache', str(work / 'cache'),
                         '--out', str(work / 'future-pins.tsv'), '--today', TODAY, '--jobs', '2'])
            out.flush()
            summary = json.loads(out.buffer.getvalue().decode('utf-8'))
            rows = {}
            for line in (work / 'future-pins.tsv').read_text(encoding='utf-8').splitlines():
                if not line.startswith('#'):
                    c, branch, fut, pin = line.split('\t')
                    rows[c] = (branch, fut, pin)
            return rows, summary
        finally:
            fp.ROOT, fp.ls_remote, fp.fetch = saved
            shutil.rmtree(work, ignore_errors=True)

    def test_pin_move_behind_branch_keeps_due_law_or_notes_it(self):
        """Audit row 60: main's pin moved past the fork and the branch, behind main now, holds laws already in force.
        Its row is never dropped: while it names the old pin, law.py names those laws as not read; written again for
        the new pin (as behind), law.py reads the branch's law made on main's text and names the other."""
        corpus, b = 'bh/national/acts', self.t.corpora['bh/national/acts']
        s1, s2 = f'{corpus}/act/s1.md', f'{corpus}/act/s2.md'
        # The row still names the old pin: main alone, and a note that names both laws in force on the branch.
        out, err, code = self.t.cli('show', TODAY, s1)
        self.assertEqual(out, 'The fee is 10.\nRule two.\n', err)
        self.assertIn('2 change(s) in force by', err)
        self.assertIn(f'{self.ON} Act 2 of 2020', err)
        self.assertIn(f'{self.ON} Act 6 of 2020', err)
        # The repoint loop's future_pins.py run: the branch is behind, and its row is kept, now for the new pin.
        rows, summary = self.run_future_pins()
        pin = run('rev-parse', 'HEAD', cwd=b.path)
        self.assertEqual(rows.get(corpus), ('zukunft', self.rows[corpus][1], pin), summary)
        got = next(c for c in summary['corpora'] if c['corpus'] == corpus)
        self.assertEqual((got['state'], got['due'], got['due_unread']), ('behind', 2, 1), got)
        # A row that fails to class now (here: the branch is not on the remote) is kept as it was, and said so.
        self.assertEqual(rows.get('mi/national/acts'), self.rows['mi/national/acts'], summary)
        self.assertIn('mi/national/acts', summary['kept'])
        self.assertEqual(set(rows), set(self.rows))  # no row dropped
        before = self.rows[corpus]
        try:
            self.rows[corpus] = rows[corpus]
            self.write_rows()
            self.t.pin()
            out, err, code = self.t.cli('show', TODAY, s1)
            self.assertEqual(out, 'The fee is 20.\nRule two.\n', err)  # made on main's text: read
            out, err, code = self.t.cli('show', TODAY, s2)
            self.assertEqual(out, 'Other, amended.\n', err)  # made on text main has changed since: main's, and said
            self.assertIn('is behind main', err)
            self.assertIn(f'1 change(s) in force by {TODAY} are on that branch and not read: {self.ON} Act 6 of 2020',
                          err)
            self.assertNotIn('Act 2 of 2020 (', err)
            out, err, code = self.t.cli('log', s2)
            self.assertIn('Act 5 of 2015', out, err)
            self.assertNotIn('Act 6 of 2020', out)
        finally:
            self.rows[corpus] = before
            self.write_rows()
            self.t.pin()

    def test_the_index_on_disk_stays_mains_and_a_pin_move_rebuilds(self):
        self.t.cli('show', self.ON, 'li/national/acts/act/s1.md')
        law = self.t.law()
        main = law._main_index('li/national/acts')
        self.assertNotIn('Act 2 of 2020', [r[1] for r in main['rows']])
        self.assertNotIn('future', main)
        law.close_readers()
        # The pin moves on; the row still names the old pin: main alone (with its new law), then the branch again
        # once the row is written for the new pin.
        a = self.t.corpora['li/national/acts']
        branch, fut, _ = self.rows['li/national/acts']
        try:
            new = a.commit('Act 5 of 2021', {'act/s2.md': 'Other, amended.\n'}, In_force='2021-01-01', Kind='law')
            self.t.pin()
            out, err, code = self.t.cli('show', TODAY, 'li/national/acts/act/s1.md')
            self.assertEqual(out, 'The fee is 10.\nRule two.\n', err)
            self.assertIn('earlier pin', err)
            out, err, code = self.t.cli('show', TODAY, 'li/national/acts/act/s2.md')
            self.assertEqual(out, 'Other, amended.\n', err)
            run('checkout', '-q', 'future', cwd=a.path)  # the builder copies main's new law onto the branch
            run('cherry-pick', new, cwd=a.path, env={'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.org'})
            run('checkout', '-q', 'main', cwd=a.path)
            self.rows['li/national/acts'] = (branch, run('rev-parse', 'future', cwd=a.path), new)
            self.write_rows()
            self.t.pin()
            out, err, code = self.t.cli('show', TODAY, 'li/national/acts/act/s1.md')
            self.assertEqual(out, 'The fee is 20.\nRule two.\n', err)
            out, err, code = self.t.cli('show', TODAY, 'li/national/acts/act/s2.md')
            self.assertEqual(out, 'Other, amended.\n', err)
            law = self.t.law()
            self.assertFalse(law._index('li/national/acts')['future']['linear'])  # forked from the new pin now
            self.assertNotIn('Act 2 of 2020', [r[1] for r in law._main_index('li/national/acts')['rows']])
            law.close_readers()
        finally:  # back as setUpClass left it, for the other tests
            run('reset', '-q', '--hard', 'HEAD~1', cwd=a.path)
            run('branch', '-q', '-f', 'future', fut, cwd=a.path)
            self.rows['li/national/acts'] = (branch, fut, run('rev-parse', 'HEAD', cwd=a.path))
            self.write_rows()
            self.t.pin()


class RenamedByALaw(unittest.TestCase):
    """A file a law moves to a new path keeps a valid mode in the index, so a tree built for a date holds it."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('mv/national/acts')
        a.commit('Act 1 of 2000', {'act/art-205.md': 'the text of the article\n'}, In_force='2000-01-01', Kind='law')
        a.commit('Act 2 of 2010', {'act/art-205.md': None, 'act/art-105a.md': 'the text of the article\n'},
                 In_force='2010-01-01', Kind='law')
        a.commit('Act 3 of 2005', {'other.md': 'older, appended later\n'}, In_force='2005-01-01', Kind='law')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_a_tree_after_the_move_holds_the_moved_file(self):
        law = self.t.law()
        self.assertFalse(law.in_order('mv/national/acts'))  # out of order: the tree is built, not a prefix
        tree = law.corpus_tree('2011-01-01', 'mv/national/acts')
        names = law.git('ls-tree', '-r', tree, cwd=law.corpus_dir('mv/national/acts'))
        law.close_readers()
        self.assertIn('100644 blob', names)
        self.assertIn('act/art-105a.md', names)
        self.assertNotIn('act/art-205.md', names)


class Checkouts(unittest.TestCase):
    """Checkouts that are not what the tree pins."""

    def setUp(self):
        t = self.t = Tree()
        a = t.corpus('aa/national/acts')
        a.commit('Act 1 of 2010', {'act/s1.md': 'one\n'}, In_force='2010-01-01')
        a.commit('Act 2 of 2020', {'act/s1.md': 'two\n'}, In_force='2020-01-01')
        t.pin()

    def tearDown(self):
        self.t.close()

    def test_unfinished_checkout_is_named_not_fatal(self):
        broken = self.t.root / 'bb' / 'national' / 'acts'
        broken.mkdir(parents=True)
        run('init', '-q', cwd=broken)
        out, err, code = self.t.cli('world', TODAY)
        self.assertEqual(code, 0, err)
        self.assertIn('two', self.t.cli('show', TODAY, 'aa/national/acts/act/s1.md')[0])

    def test_checkout_behind_its_pin_reads_the_pin(self):
        run('checkout', '-q', 'HEAD~1', cwd=self.t.corpora['aa/national/acts'].path)
        out, err, code = self.t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
        self.assertEqual(out, 'two\n', err)

    def test_pin_not_fetched_stops_with_the_fix(self):
        a = self.t.corpora['aa/national/acts']
        a.commit('Act 3 of 2021', {'act/s1.md': 'three\n'}, In_force='2021-01-01')
        self.t.pin()
        run('reset', '-q', '--hard', 'HEAD~1', cwd=a.path)
        run('reflog', 'expire', '--expire=now', '--all', cwd=a.path)
        run('gc', '-q', '--prune=now', cwd=a.path)
        out, err, code = self.t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
        self.assertNotEqual(code, 0)
        self.assertIn('git submodule update --init -- aa/national/acts', err)

    def test_old_path_of_a_moved_corpus_still_reads(self):
        data = self.t.root / 'data'
        data.mkdir(exist_ok=True)
        (data / 'moved-paths.tsv').write_text('# old\tnew\tmoved on\nxx/old-city/acts\taa/national/acts\t2026-11-03\n',
                                             encoding='utf-8')
        run('add', 'data', cwd=self.t.root)
        self.t.pin()
        out, err, code = self.t.cli('show', TODAY, 'xx/old-city/acts/act/s1.md')
        self.assertEqual(out, 'two\n', err)
        law = self.t.law()  # a name that is the old path, with or without /acts, takes in the moved corpus
        corpus = {'path': 'aa/national/acts'}
        self.assertTrue(law.matches(corpus, 'xx/old-city/acts'))
        self.assertTrue(law.matches(corpus, 'xx/old-city'))
        out, err, code = self.t.cli('laws', '2000-01-01', '2030-01-01', 'xx/old-city/acts')
        self.assertIn('Act 2 of 2020', out, err)

    def test_folder_renamed_by_documentation_keeps_its_history(self):
        a = self.t.corpora['aa/national/acts']
        run('mv', 'act', 'act-1-2010', cwd=a.path)
        a.commit('Lexifina', {}, Kind='layout')
        self.t.pin()
        out, err, code = self.t.cli('show', '2015-01-01', 'aa/national/acts/act-1-2010/s1.md')
        self.assertEqual(out, 'one\n', err)
        out, err, code = self.t.cli('show', TODAY, 'aa/national/acts/act-1-2010/s1.md')
        self.assertEqual(out, 'two\n', err)

    def test_checkout_behind_its_pin_is_left_out_of_whole_tree_reads(self):
        a = self.t.corpora['aa/national/acts']
        a.commit('Act 3 of 2021', {'act/s1.md': 'three\n'}, In_force='2021-01-01')
        b = self.t.corpus('bb/national/acts')  # a corpus that is current, beside the one behind
        b.commit('Act 1 of 2015', {'act/x.md': 'x\n'}, In_force='2015-01-01')
        self.t.pin()
        run('reset', '-q', '--hard', 'HEAD~1', cwd=a.path)  # as after a pull without `git submodule update`
        run('reflog', 'expire', '--expire=now', '--all', cwd=a.path)
        run('gc', '-q', '--prune=now', cwd=a.path)
        out, err, code = self.t.cli('world', TODAY)
        self.assertEqual(code, 0, err)
        self.assertIn('Act 1 of 2015', out)
        self.assertIn('behind the tree', out + err)
        out, err, code = self.t.cli('laws', '2000-01-01', '2030-01-01')
        self.assertEqual(code, 0, err)
        self.assertIn('Act 1 of 2015', out)

    def test_pin_moving_forward_extends_the_index(self):
        self.t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
        a = self.t.corpora['aa/national/acts']
        a.commit('Act 3 of 2021', {'act/s1.md': 'three\n'}, In_force='2021-01-01')
        self.t.pin()
        out, err, code = self.t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
        self.assertEqual(out, 'three\n', err)
        out, err, code = self.t.cli('show', '2020-06-01', 'aa/national/acts/act/s1.md')
        self.assertEqual(out, 'two\n', err)

    def test_shallow_corpus_still_stops(self):
        a = self.t.corpora['aa/national/acts']
        shallow = self.t.root / 'shallow-src'
        run('clone', '-q', '--depth', '1', f'file://{a.path.as_posix()}', str(shallow), cwd=self.t.root)
        shutil.rmtree(a.path, onerror=lambda f, p, _: (os.chmod(p, 0o700), f(p)))
        shutil.move(str(shallow), str(a.path))
        out, err, code = self.t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
        self.assertNotEqual(code, 0)
        self.assertIn('shallow clone', err)

    def test_laws_names_corpora_not_checked_out(self):
        (self.t.root / 'manifest.json').write_text(json.dumps({'corpora': [
            {'path': 'aa/national/acts', 'name': 'Aa'}, {'path': 'nn/national/acts', 'name': 'Nn'}]}), encoding='utf-8')
        self.t.pin()
        out, err, code = self.t.cli('laws', '1900-01-01', '2026-12-31', 'nn')
        self.assertNotEqual(code, 0, out)
        self.assertEqual(out, '')
        self.assertIn('nn/national/acts is not checked out', err)
        self.assertIn('countries.py add nn/national/acts', err)
        out, err, code = self.t.cli('laws', '1900-01-01', '2026-12-31', 'aa')
        self.assertEqual(code, 0, err)
        self.assertNotIn('not checked out', err)


class FutureCommitFetchedLater(unittest.TestCase):
    """Audit row 37: a long-running reader (the MCP server) that started while the checkout lacked the recorded
    future commit reads the branch once the commit is fetched, as future_note asks, without a restart."""

    def test_a_running_reader_reads_the_branch_once_it_is_fetched(self):
        t = Tree()
        up = Path(tempfile.mkdtemp(prefix='gl-up-'))
        law = None
        try:
            a = t.corpus('li/national/acts')
            a.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\n'}, In_force='2010-01-01', Kind='law')
            pin = a.commit('Lexifina', {'README.md': '# LI\n'}, Kind='documentation')
            run('clone', '-q', str(a.path), str(up / 'r'), cwd=up)
            u = Corpus.__new__(Corpus)
            u.path, u.n = up / 'r', 10
            run('checkout', '-q', '-b', 'future', cwd=u.path)
            fut = u.commit('Act 2 of 2020', {'act/s1.md': 'The fee is 20.\n'}, In_force='2020-06-01', Kind='law')
            (t.root / 'data').mkdir()
            (t.root / 'data' / 'future-pins.tsv').write_bytes(
                f'# corpus\tbranch\tfuture_sha\tmain_pin\nli/national/acts\tfuture\t{fut}\t{pin}\n'.encode())
            run('add', 'data', cwd=t.root)
            t.pin()
            law = t.law()
            p = 'li/national/acts/act/s1.md'
            self.assertIn('which this checkout does not have', law.future_note('li/national/acts'))
            self.assertEqual(law.text_on('2021-01-01', p), 'The fee is 10.\n')
            self.assertNotIn('Act 2 of 2020', [e.law for e in law.timeline()])
            self.assertEqual([h['in_force'] for h in law.history(p)], ['2010-01-01'])
            run('fetch', '-q', str(u.path), 'future', cwd=a.path)
            self.assertIsNone(law.future_note('li/national/acts'))
            self.assertIn('Act 2 of 2020', [e.law for e in law.timeline()])  # a whole-tree read first
            self.assertEqual(law.text_on('2021-01-01', p), 'The fee is 20.\n')
            self.assertEqual(law.text_on('2019-01-01', p), 'The fee is 10.\n')
            self.assertEqual([h['in_force'] for h in law.history(p)], ['2010-01-01', '2020-06-01'])
            self.assertTrue(law._index('li/national/acts')['future']['linear'])
        finally:
            if law:
                law.close_readers()
            t.close()
            shutil.rmtree(up, onerror=lambda f, p, _: (os.chmod(p, 0o700), f(p)))


class FutureCopiesWithOtherText(unittest.TestCase):
    """Audit row 42: a forked future branch whose "copy" of a main law has the law's author line, date and message
    but other text. Read beside main it would undo main's amendment; future_pins.py classes it diverged (no row) and
    law.py, given a row for it anyway, reads main alone and says why. A true copy (cherry-pick), and one that also
    writes a file more, are still forked."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(HERE / 'tools'))
        import future_pins
        cls.fp = future_pins
        t = cls.t = Tree()
        rows = {}
        for corpus, copy in (('fk/national/acts', 'other text'), ('ok/national/acts', 'cherry-pick'),
                             ('mo/national/acts', 'and more')):
            f = t.corpus(corpus)
            f.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\nRule two.\n'}, In_force='2010-01-01', Kind='law')
            run('checkout', '-q', '-b', 'zukunft', cwd=f.path)
            run('checkout', '-q', 'main', cwd=f.path)
            later = f.commit('Act 4 of 2015', {'act/s1.md': 'The fee is 10.\nRule two, as amended in 2015.\n'},
                             In_force='2015-01-01', Kind='law')
            pin = f.commit('Lexifina', {'README.md': '# FK\n'}, Kind='documentation')
            run('checkout', '-q', 'zukunft', cwd=f.path)
            env = {'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.org'}
            text = 'The fee is 20.\nRule two, as amended in 2015.\n'
            if copy == 'cherry-pick':
                run('cherry-pick', later, cwd=f.path, env=env)
            elif copy == 'and more':  # main's change, and a file more (as Belgium's copies write a README): a copy
                (f.path / 'act' / 's1.md').write_bytes(b'The fee is 10.\nRule two, as amended in 2015.\n')
                (f.path / 'act' / 'README.md').write_bytes(b'# Act\n')
                run('add', 'act', cwd=f.path)
                run('commit', '-q', '-C', later, cwd=f.path, env=env)
            else:  # same author, author date and message (git commit -C), without the amendment
                (f.path / 'act' / 'note.md').write_text('replayed\n')
                run('add', 'act/note.md', cwd=f.path)
                run('commit', '-q', '-C', later, cwd=f.path, env=env)
                text = 'The fee is 20.\nRule two.\n'
            fut = f.commit('Act 2 of 2020', {'act/s1.md': text}, In_force='2020-06-01', Kind='law')
            run('checkout', '-q', 'main', cwd=f.path)
            rows[corpus] = (fut, pin)
        cls.rows = rows
        (t.root / 'data').mkdir()
        (t.root / 'data' / 'future-pins.tsv').write_bytes(
            ('# corpus\tbranch\tfuture_sha\tmain_pin\n'
             + ''.join(f'{c}\tzukunft\t{f}\t{p}\n' for c, (f, p) in sorted(rows.items()))).encode())
        run('add', 'data', cwd=t.root)
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_future_pins_classes_a_copy_with_other_text_diverged(self):
        fut, pin = self.rows['fk/national/acts']
        got = self.fp.classify(self.t.corpora['fk/national/acts'].path, pin, fut, '2026-11-04')
        self.assertEqual(got['state'], 'diverged', got)
        self.assertNotIn('diverged', self.fp.RECORDED)
        for corpus in ('ok/national/acts', 'mo/national/acts'):
            fut, pin = self.rows[corpus]
            got = self.fp.classify(self.t.corpora[corpus].path, pin, fut, '2026-11-04')
            self.assertEqual(got['state'], 'forked', (corpus, got))

    def test_law_reads_main_alone_beside_a_diverged_branch(self):
        p = 'fk/national/acts/act/s1.md'
        for day in ('2016-01-01', '2020-06-01'):
            out, err, code = self.t.cli('show', day, p)
            self.assertEqual(out, 'The fee is 10.\nRule two, as amended in 2015.\n', (day, err))
        self.assertIn('change different text', err)
        self.assertIn('so the branch is not read', err)
        out, err, code = self.t.cli('log', p)
        self.assertNotIn('Act 2 of 2020', out)
        self.assertEqual(out.count('Act 4 of 2015'), 1, out)

    def test_a_true_copy_is_still_skipped_and_the_branch_read(self):
        for corpus in ('ok/national/acts', 'mo/national/acts'):
            p = f'{corpus}/act/s1.md'
            out, err, code = self.t.cli('show', '2020-06-01', p)
            self.assertEqual(out, 'The fee is 20.\nRule two, as amended in 2015.\n', (corpus, err))
            out, err, code = self.t.cli('log', p)
            self.assertEqual(out.count('Act 4 of 2015'), 1, out)
            self.assertNotIn('change different text', err)


class FutureCopySupersedes(unittest.TestCase):
    """A future branch built before main published one of its laws (Czechia's): the branch holds its own earlier
    version of the law, and main the law with the same author line and message (written with CRLF line ends) but
    newer text. append_future.py's replay then adds a true copy of main's commit on top of the branch. future_pins.py
    reads the CRLF message as its LF twin, as law.py does, and both take the earlier version as superseded by the
    copy: the branch is forked and read, main's text stands for that law, and the branch's own later law reads from
    its day."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(HERE / 'tools'))
        import future_pins
        cls.fp = future_pins
        t = cls.t = Tree()
        f = t.corpus('cz/national/acts')
        f.commit('Act 1 of 2010', {'act/s1.md': 'The fee is 10.\nRule two.\n'}, In_force='2010-01-01', Kind='law')
        run('checkout', '-q', '-b', 'future', cwd=f.path)
        run('checkout', '-q', 'main', cwd=f.path)
        stamp = '2001-01-01T00:00:30Z'
        author = {'GIT_AUTHOR_NAME': 'Act 4 of 2015', 'GIT_AUTHOR_EMAIL': 'law@example.org', 'GIT_AUTHOR_DATE': stamp,
                  'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.org', 'GIT_COMMITTER_DATE': stamp}
        msg = 'Act 4 of 2015\n\nIn-force: 2015-01-01\nKind: law\n'
        (f.path / 'act' / 's1.md').write_bytes(b'The fee is 10.\nRule two, as amended in 2015.\n')
        run('add', 'act', cwd=f.path)
        msgf = Path(tempfile.mkdtemp()) / 'msg-crlf.txt'
        msgf.write_bytes(msg.replace('\n', '\r\n').encode())
        run('commit', '-q', '--cleanup=verbatim', '-F', str(msgf), cwd=f.path, env=author)
        later = run('rev-parse', 'HEAD', cwd=f.path)
        pin = f.commit('Lexifina', {'README.md': '# CZ\n'}, Kind='documentation')
        run('checkout', '-q', 'future', cwd=f.path)
        # the branch's own earlier version of the same law: same author line and message (LF), older text
        (f.path / 'act' / 's1.md').write_bytes(b'The fee is 10.\nRule two, as amended  in 2015.\n')
        run('add', 'act', cwd=f.path)
        run('commit', '-q', '-m', msg, cwd=f.path, env=author)
        cls.stale = run('rev-parse', 'HEAD', cwd=f.path)
        # append_future.py's replay of main's commit: its message bytes and its text
        (f.path / 'act' / 's1.md').write_bytes(b'The fee is 10.\nRule two, as amended in 2015.\n')
        run('add', 'act', cwd=f.path)
        run('commit', '-q', '-C', later, cwd=f.path, env={'GIT_COMMITTER_NAME': 'test',
                                                          'GIT_COMMITTER_EMAIL': 't@example.org'})
        fut = f.commit('Act 2 of 2020', {'act/s1.md': 'The fee is 20.\nRule two, as amended in 2015.\n'},
                       In_force='2020-06-01', Kind='law')
        run('checkout', '-q', 'main', cwd=f.path)
        cls.row = (fut, pin)
        # Audit row 59: the branch's own build of a repeal (another message, one file) that main then published as
        # a repeal of two, the same day; the builder's replay copies main's commit (deleting the other file).
        y = t.corpus('cy/national/acts')
        y.commit('Act 1 of 2010', {'act/a.md': 'Act a.\n', 'act/b.md': 'Act b.\n'}, In_force='2010-01-01', Kind='law')
        run('checkout', '-q', '-b', 'future', cwd=y.path)
        run('checkout', '-q', 'main', cwd=y.path)
        repeal = y.commit('Repeal of 2 acts', {'act/a.md': None, 'act/b.md': None}, In_force='2026-11-01', Kind='law')
        ypin = y.commit('Lexifina', {'README.md': '# CY\n'}, Kind='documentation')
        run('checkout', '-q', 'future', cwd=y.path)
        y.commit('Repeal of 1 act', {'act/a.md': None}, In_force='2026-11-01', Kind='law')
        run('cherry-pick', repeal, cwd=y.path, env={'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.org'})
        yfut = y.commit('Act 3 of 2026', {'act/c.md': 'Act c.\n'}, In_force='2026-11-02', Kind='law')
        run('checkout', '-q', 'main', cwd=y.path)
        cls.yrow = (yfut, ypin)
        (t.root / 'data').mkdir()
        (t.root / 'data' / 'future-pins.tsv').write_bytes(
            (f'# corpus\tbranch\tfuture_sha\tmain_pin\ncz/national/acts\tfuture\t{fut}\t{pin}\n'
             f'cy/national/acts\tfuture\t{yfut}\t{ypin}\n').encode())
        run('add', 'data', cwd=t.root)
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_future_pins_classes_it_forked(self):
        fut, pin = self.row
        got = self.fp.classify(self.t.corpora['cz/national/acts'].path, pin, fut, '2026-11-04')
        self.assertEqual(got['state'], 'forked', got)
        self.assertEqual(got['future_own'], 1, got)  # Act 2 of 2020 only

    def test_law_reads_mains_text_then_the_branch_law(self):
        p = 'cz/national/acts/act/s1.md'
        out, err, code = self.t.cli('show', '2016-01-01', p)
        self.assertEqual(out, 'The fee is 10.\nRule two, as amended in 2015.\n', err)
        self.assertNotIn('change different text', err)
        out, err, code = self.t.cli('show', '2020-06-01', p)
        self.assertEqual(out, 'The fee is 20.\nRule two, as amended in 2015.\n', err)
        out, err, code = self.t.cli('log', p)
        self.assertEqual(out.count('Act 4 of 2015'), 1, out)
        law = self.t.law()
        ix = law._index('cz/national/acts')
        self.assertEqual(ix['future']['replays_skipped'], 2)  # the copy and the version it supersedes
        law.close_readers()

    def test_an_own_commit_main_already_holds_is_not_read_twice(self):
        """Audit row 59 (Czechia): the branch's own earlier build of a repeal that main has since published under
        another message, the same day, is taken as main's law: one removal row, one law listed, and future_pins.py
        does not count it as the branch's own."""
        fut, pin = self.yrow
        got = self.fp.classify(self.t.corpora['cy/national/acts'].path, pin, fut, '2026-11-04')
        self.assertEqual(got['state'], 'forked', got)
        self.assertEqual(got['future_own'], 1, got)  # Act 3 of 2026 only
        out, err, code = self.t.cli('log', 'cy/national/acts/act/a.md')
        self.assertEqual(sum('2026-11-01' in line for line in out.splitlines()), 1, (out, err))  # one removal row
        self.assertNotIn('Repeal of 1 act', out)
        out, err, code = self.t.cli('laws', '2026-11-01', '2026-11-01', 'cy/national/acts')
        listed = [line for line in out.splitlines() if 'cy/national/acts' in line]
        self.assertEqual(len(listed), 1, (out, err))
        self.assertIn('Repeal of 2 acts', listed[0])
        out, err, code = self.t.cli('show', '2026-11-02', 'cy/national/acts/act/c.md')
        self.assertEqual(out, 'Act c.\n', err)  # the branch's own law is still read
        self.assertNotIn('not read', err)


class CountryNamesAndCodes(unittest.TestCase):
    """Audit row 47: a country's ISO code, its other common names ("uk") and its name with accents or in any case
    take in every corpus of the country, as its folder does; a country's name still never takes in another
    country's state of that name, and subdivision codes (ES-MD) still take in their own corpus only."""

    CORPORA = [('spain/national/acts', 'ES', 'es/national/acts'), ('spain/madrid/acts', 'ES-MD', 'es-md/acts'),
               ('united-kingdom/uk/legislation', 'GB', 'gb/uk/legislation'),
               ('cote-divoire/national/acts', 'CI', 'ci/national/acts'),
               ('georgia/national/acts', 'GE', 'ge/national/acts'),
               ('united-states/federal/usc', 'US', 'us/federal/usc'),
               ('united-states/georgia/acts', 'US-GA', 'united-states/georgia/acts')]

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        shutil.copy(HERE / 'tools' / 'countries.py', t.root / 'tools' / 'countries.py')
        for i, (path, code, iso) in enumerate(cls.CORPORA):
            t.corpus(path).commit(f'Act {i + 1} of 2020', {'act/s1.md': f'{path}\n'}, In_force=f'2020-01-0{i + 1}',
                                  Kind='law')
        (t.root / 'manifest.json').write_text(json.dumps({'corpora': [
            {'path': p, 'code': c, 'iso_path': i, 'name': p} for p, c, i in cls.CORPORA]}), encoding='utf-8')
        run('add', 'tools/countries.py', cwd=t.root)
        t.pin()
        cls.law = t.law()

    @classmethod
    def tearDownClass(cls):
        cls.law.close_readers()
        cls.t.close()

    def taken(self, name):
        return sorted(c['path'] for c in self.law.manifest()['corpora'] if self.law.matches(c, name))

    def test_names_and_codes(self):
        spain = ['spain/madrid/acts', 'spain/national/acts']
        us = ['united-states/federal/usc', 'united-states/georgia/acts']
        for name, want in (('es', spain), ('ES', spain), ('Spain', spain), ('spain', spain),
                           ('ES-MD', ['spain/madrid/acts']), ('es-md', ['spain/madrid/acts']),
                           ('madrid', ['spain/madrid/acts']),
                           ('uk', ['united-kingdom/uk/legislation']), ('UK', ['united-kingdom/uk/legislation']),
                           ('gb', ['united-kingdom/uk/legislation']),
                           ('United Kingdom', ['united-kingdom/uk/legislation']),
                           ("Côte d'Ivoire", ['cote-divoire/national/acts']),
                           ('CÔTE-DIVOIRE', ['cote-divoire/national/acts']),
                           ('ivory coast', ['cote-divoire/national/acts']),
                           ('us', us), ('usa', us), ('united states', us),
                           ('us/federal', ['united-states/federal/usc']),
                           ('georgia', ['georgia/national/acts']), ('Georgia', ['georgia/national/acts']),
                           ('ge', ['georgia/national/acts']), ('US-GA', ['united-states/georgia/acts']),
                           ('national', []), ('ga', [])):
            self.assertEqual(self.taken(name), want, name)

    def test_laws_by_code(self):
        out, err, code = self.t.cli('laws', '2020-01-01', '2020-12-31', 'es')
        self.assertIn('spain/madrid/acts', out, err)
        self.assertIn('spain/national/acts', out)
        out, err, code = self.t.cli('laws', '2020-01-01', '2020-12-31', 'UK')
        self.assertIn('united-kingdom/uk/legislation', out, err)

    def test_countries_only_takes_the_same_corpora(self):
        script = str(self.t.root / 'tools' / 'countries.py')
        try:
            for name, want in (('es', 'spain/national/acts, spain/madrid/acts'),
                               ('uk', 'united-kingdom/uk/legislation')):
                done = subprocess.run([sys.executable, '-X', 'utf8', script, 'only', name], cwd=self.t.root,
                                      capture_output=True, encoding='utf-8')
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertIn('The MCP server now serves only: ' + want, done.stdout)
        finally:
            run('config', '--unset', 'global-law.jurisdictions', cwd=self.t.root, check=False)


class ActEndRule(unittest.TestCase):
    """One act-end rule for every reader (audit rows 30, 43, 44, 45, 48): an act data/acts.json ends (repealed,
    expired or annulled) stays ended unless a later version's law was enacted on or after the end, is not the law that
    ended it, and is not a repeal note; corrections stop at the end; diff, laws and the timeline agree with history()."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('aa/national/acts')
        a.commit('Act 1 of 2010', {'rep/s1.md': '# s1\none\n', 'rep/s2.md': '# s2\ntwo\n', 'rep/s3.md': '# s3\nthree\n',
                                   'other/x.md': 'other\n'},
                 In_force='2010-01-01', Kind='law', Enacted='2009-12-01')
        a.commit('Order 2 of 2011', {'ann/s1.md': 'struck\n', 'cor/s1.md': 'cor one\n', 'cor/s2.md': 'cor two\n'},
                 In_force='2011-01-01', Kind='law', Enacted='2010-12-01')
        a.commit('Act 9 of 2014', {'other/x.md': 'other 2\n'}, In_force='2015-01-01', Kind='law', Enacted='2014-06-01')
        # The repealing law, made after the day acts.json gives (Spain's RD 199/2012 for RD 392/2011): its note in the
        # repealed act's folder, and its rewording of one provision, do not bring the act back.
        a.commit('Act 20 of 2016', {'rep/no.md': 'Norma derogada por Act 20 of 2016.\n',
                                    'rep/s1.md': '# s1\none, as ended\n'},
                 In_force='2016-02-01', Kind='law', Enacted='2016-01-10')
        # A later law's "(Derogado)" over a provision, and a real later amendment, both made after the end.
        a.commit('Act 30 of 2017', {'rep/s2.md': '## Section 2\n\n(Derogado)\n'}, In_force='2017-03-01', Kind='law',
                 Enacted='2017-02-01')
        a.commit('Act 40 of 2018', {'rep/s3.md': '# s3\nthree, amended for past years\n'}, In_force='2018-03-01',
                 Kind='law', Enacted='2018-02-01')
        # A provision of the ended act whose only later version is its old text with BOE's quoted partial-repeal note
        # added (Decreto 28-11-1933 art. 3 and RD 161/1997): the note restates an end, it does not re-enact.
        a.commit('Act 3 of 2012', {'rep/s4.md': '# s4\nfour\n\n> Se modifica por Act 3 of 2012.\n'},
                 In_force='2012-06-01', Kind='law', Enacted='2012-05-01')
        a.commit('Act 50 of 2019', {'rep/s4.md': '# s4\nfour\n\n> Se derogan las reglas de este artículo, según establece '
                                                 'Act 50 of 2019.\n\n> Se modifica por Act 3 of 2012.\n'},
                 In_force='2019-03-01', Kind='law', Enacted='2019-02-01')
        # A correction whose range runs past its act's end, and one that starts after it.
        a.commit('Gazette 2', {'cor/s2.md': 'cor two, corrected\n'}, In_force='2012-01-01', Kind='correction',
                 Corrects='cor 2012-01-01..2025-12-31', Files='cor/s2.md', Reason='misprint')
        a.commit('Gazette 3', {'cor/s1.md': 'cor one, corrected\n'}, In_force='2021-01-01', Kind='correction',
                 Corrects='cor 2021-01-01..2025-12-31', Files='cor/s1.md', Reason='misprint')
        # Spain's repeals (spain-law c0980c9, audit row 64): a dated correction from the end day that deletes the
        # repealed act's files, beside the same end in data/acts.json.
        a.commit('Act 7 of 2012', {'gone/s1.md': 'gone one\n', 'gone/s2.md': 'gone two\n'}, In_force='2012-03-01',
                 Kind='law', Enacted='2012-02-01')
        a.commit('Lexifina', {'gone/s1.md': None}, In_force='2020-06-01', Kind='correction',
                 Corrects='gone 2020-06-01..2026-10-28', Files='gone/s1.md', Act_path='gone',
                 Reason='remove the repealed normative files')
        acts = {'acts': [{'path': 'rep', 'status': 'repealed', 'repealed': '2015-01-01', 'repealed_by': 'Act 20 of 2016'},
                         {'path': 'ann', 'status': 'annulled', 'in_force': '2011-01-01', 'annulled': '2014-05-01'},
                         {'path': 'cor', 'status': 'repealed', 'repealed': '2020-01-01', 'repealed_by': 'Act 9 of 2019'},
                         {'path': 'gone', 'status': 'repealed', 'repealed': '2020-06-01', 'repealed_by': 'Act 60 of 2019'},
                         {'path': 'other', 'status': 'in force'}]}
        a.commit('Lexifina', {'data/acts.json': json.dumps(acts)}, Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def tree_names(self, date):
        law = self.t.law()
        try:
            tree = law.corpus_tree(date, 'aa/national/acts')
            return law.git('ls-tree', '-r', '--name-only', tree, cwd=law.corpus_dir('aa/national/acts')).split()
        finally:
            law.close_readers()

    # Row 43: a repeal note, "(Derogado)" text or the repealing law's own version is not a re-enactment.
    def test_the_repealing_laws_own_versions_do_not_reenact(self):
        for f in ('no.md', 's1.md'):
            out, err, code = self.t.cli('show', '2026-01-01', f'aa/national/acts/rep/{f}')
            self.assertNotEqual(code, 0, out)
            self.assertNotIn('in force again', err)
        self.assertIn('was repealed on 2015-01-01 by Act 20 of 2016', err)
        self.assertIn('2016-02-01 Act 20 of 2016 (enacted 2016-01-10; the law that ended the act)', err)

    def test_a_derogado_note_does_not_reenact(self):
        out, err, code = self.t.cli('show', '2026-01-01', 'aa/national/acts/rep/s2.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('2017-03-01 Act 30 of 2017 (enacted 2017-02-01; a repeal note, not a re-enactment)', err)
        out, err, code = self.t.cli('log', 'aa/national/acts/rep/s2.md')
        self.assertNotIn('in force 2017-03-01', out)
        self.assertIn('a repeal note', out)

    def test_a_real_later_amendment_reenacts_and_says_so(self):
        out, err, code = self.t.cli('show', '2026-01-01', 'aa/national/acts/rep/s3.md')
        self.assertEqual(out, '# s3\nthree, amended for past years\n', err)
        self.assertIn('is read as bringing it back into force', err)
        self.assertEqual([n for n in self.tree_names('2026-01-01') if n.startswith('rep/')], ['rep/s3.md'])

    def test_a_repeal_note_added_to_the_ended_text_does_not_reenact(self):
        out, err, code = self.t.cli('show', '2026-01-01', 'aa/national/acts/rep/s4.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('2019-03-01 Act 50 of 2019 (enacted 2019-02-01; the ended text with a repeal note added, not a '
                      're-enactment)', err)
        out, err, code = self.t.cli('show', '2014-12-31', 'aa/national/acts/rep/s4.md')
        self.assertEqual(out, '# s4\nfour\n\n> Se modifica por Act 3 of 2012.\n', err)
        law = self.t.law()
        before = '# s4\nfour\n\n> Se modifica por Act 3 of 2012.\n'
        self.assertTrue(law.adds_only_repeal_note(before, '# s4\nfour\n\n> Queda derogado el párrafo segundo.\n\n'
                                                          '> Se modifica por Act 3 of 2012.\n'))
        for after in (before,  # nothing added
                      '# s4\nfour, amended\n\n> Se derogan las reglas ...\n\n> Se modifica por Act 3 of 2012.\n',
                      '# s4\nfour\n\n> Se modifica por Act 60 of 2020.\n\n> Se modifica por Act 3 of 2012.\n',
                      '# s4\nfour\nSe derogan las reglas ...\n\n> Se modifica por Act 3 of 2012.\n',  # not a quoted note
                      '# s4\n\n> Se derogan las reglas ...\n\n> Se modifica por Act 3 of 2012.\n'):  # text removed
            self.assertFalse(law.adds_only_repeal_note(before, after), after)

    def test_repeal_notes_are_recognised(self):
        law = self.t.law()
        for text in ('Norma derogada por la disposición derogatoria única del Real Decreto 199/2012.\n',
                     'Norma deogada, con efectos de 11 de agosto de 2021.\n',
                     '## Disposición transitoria décima.\n\n(Derogada)\n',
                     'Norma anulada por Sentencia del TS de 17 de diciembre de 2024.\n', '[Repealed]\n'):
            self.assertTrue(law.is_repeal_note(text), text)
        for text in ('## Artículo 3\n\nLa norma derogada seguirá aplicándose a los periodos anteriores.\n', 'one\n', '',
                     '## Artículo 15. Reglas de valoración.\n\n1. Los elementos patrimoniales se valorarán ...\n'):
            self.assertFalse(law.is_repeal_note(text), text)

    # Row 30: an annulled act ends like a repeal, from the annulment day, and says it was annulled.
    def test_an_annulled_act_ends_on_its_annulment_day(self):
        out, err, code = self.t.cli('show', '2014-04-30', 'aa/national/acts/ann/s1.md')
        self.assertEqual(out, 'struck\n', err)
        out, err, code = self.t.cli('show', '2014-05-01', 'aa/national/acts/ann/s1.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('its act (ann) was annulled on 2014-05-01', err)
        self.assertIn('data/acts.json', err)
        out, err, code = self.t.cli('log', 'aa/national/acts/ann/s1.md')
        self.assertIn('annulled 2014-05-01  annulled (data/acts.json)', out, err)
        self.assertNotIn('ann/s1.md', self.tree_names('2020-01-01'))

    # Row 45: diff across an end shows the text removed and names the end.
    def test_diff_across_an_end_shows_the_text_removed(self):
        out, err, code = self.t.cli('diff', '2014-04-30', '2014-05-01', 'aa/national/acts/ann/s1.md')
        self.assertNotIn('No change', out)
        self.assertIn('was annulled on 2014-05-01', out)
        self.assertIn('[-struck-]', out)
        out, err, code = self.t.cli('diff', '2014-12-31', '2026-01-01', 'aa/national/acts/rep/s3.md')
        self.assertIn('three, amended for past years', out)
        out, err, code = self.t.cli('diff', '2015-06-01', '2026-01-01', 'aa/national/acts/rep/s1.md')
        self.assertIn('No change between those dates.', out)  # ended on both days

    # Row 48: a law whose every version the act-end rule drops is not listed as taking force.
    def test_laws_and_the_timeline_agree_with_history(self):
        out, err, code = self.t.cli('laws', '2016-01-01', '2017-12-31', 'aa')
        self.assertNotIn('Act 20 of 2016', out, err)
        self.assertNotIn('Act 30 of 2017', out, err)
        self.assertIn('2 laws that changed only acts data/acts.json had already ended', err)
        out, err, code = self.t.cli('laws', '2018-01-01', '2018-12-31')
        self.assertIn('Act 40 of 2018', out, err)
        law = self.t.law()
        try:
            self.assertNotIn('Act 20 of 2016', [e.law for e in law.timeline()])
            self.assertIn('Act 30 of 2017', [e.law for e in law.corpus_events('aa/national/acts')])  # raw history
            self.assertNotIn('Act 30 of 2017', [e.law for e in law.law_events('aa/national/acts')])
        finally:
            law.close_readers()

    # Row 44: a correction running past its act's end stops at the end; one starting after it never applies.
    def test_a_correction_stops_at_its_acts_end(self):
        out, err, code = self.t.cli('show', '2019-06-01', 'aa/national/acts/cor/s2.md')
        self.assertEqual(out, 'cor two, corrected\n', err)
        for date in ('2020-01-01', '2023-01-01'):
            out, err, code = self.t.cli('show', date, 'aa/national/acts/cor/s2.md')
            self.assertNotEqual(code, 0, out)
            self.assertIn('was repealed on 2020-01-01', err)
        out, err, code = self.t.cli('show', '2023-01-01', 'aa/national/acts/cor/s1.md')
        self.assertNotEqual(code, 0, out)
        self.assertNotIn('cor/s2.md', self.tree_names('2023-01-01'))
        self.assertNotIn('cor/s1.md', self.tree_names('2023-01-01'))
        self.assertIn('cor/s2.md', self.tree_names('2019-06-01'))
        law = self.t.law()
        try:
            h = law.history('aa/national/acts/cor/s2.md')
            self.assertEqual([x['until'] for x in h if x.get('corrects')], ['2019-12-31'])
            end = next(x for x in law.history('aa/national/acts/cor/s1.md') if x.get('ends'))
            self.assertIn('2021-01-01 Gazette 3 (a correction for days after the end)', end['not_reenacting'])
            self.assertEqual(law.versions_in_force('2023-01-01', 'aa/national/acts/cor/s2.md')[-1][1], 'Act 9 of 2019')
        finally:
            law.close_readers()

    # Row 64: a correction from the end day that deletes the file is the record carrying out the end, not a later
    # version that fails to re-enact it.
    def test_a_repeal_correction_is_the_end_not_a_candidate(self):
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/gone/s1.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('was repealed on 2020-06-01 by Act 60 of 2019', err)
        self.assertIn('the record removes the file from that day', err)
        self.assertNotIn('did not remove the file itself', err)
        self.assertNotIn('not read as re-enacting', err)
        out, err, code = self.t.cli('log', 'aa/national/acts/gone/s1.md')
        self.assertIn('repealed 2020-06-01  Act 60 of 2019  [act gone, from data/acts.json; the record removes the file '
                      'from that day]', out, err)
        self.assertNotIn('not re-enacted by', out)
        # The file the correction leaves alone is ended by data/acts.json alone, and says so.
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/gone/s2.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('the record did not remove the file itself', err)
        out, err, code = self.t.cli('show', '2019-12-31', 'aa/national/acts/gone/s1.md')
        self.assertEqual(out, 'gone one\n', err)
        self.assertNotIn('gone/s1.md', self.tree_names('2021-01-01'))


class BuiltTreeStore(unittest.TestCase):
    """Fundamentals audit rows 49-50: a built tree read by the batch reader of the process that built it, and a tree
    store that another process's sweep leaves alone while its owner runs (and that is made again if removed)."""

    C = 'ts/national/acts'

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus(cls.C)  # older acts appended after a newer one: not in in-force order
        # The trees for 2015-07-01 and 2017-01-01 are no commit's tree, so only a built tree holds them.
        a.commit('Act 1 of 2010', {'act/s1.md': 'fee 10\n', 'act/s2.md': 'two a\n', 'act/s3.md': 'three x\n'},
                 In_force='2010-01-01', Kind='law')
        a.commit('Act 5 of 2020', {'act/s1.md': 'fee 30\n'}, In_force='2020-01-01', Kind='law')
        a.commit('Act 3 of 2015', {'act/s2.md': 'two b\n'}, In_force='2015-06-01', Kind='law')
        a.commit('Act 4 of 2016', {'act/s3.md': 'three y\n'}, In_force='2016-06-01', Kind='law')
        a.commit('Lexifina', {'README.md': '# TS\n'}, Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def setUp(self):  # each test's law module makes its own store; none sees another's through the environment
        self.saved = os.environ.pop('GIT_ALTERNATE_OBJECT_DIRECTORIES', None)
        self.mods = []

    def tearDown(self):
        for law in self.mods:
            law.close_readers()
            if law._TREES['dir'] is not None:
                law._rmtree(law._TREES['dir'])
        os.environ.pop('GIT_ALTERNATE_OBJECT_DIRECTORIES', None)
        if self.saved is not None:
            os.environ['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = self.saved

    def law(self):
        law = self.t.law()
        self.mods.append(law)
        return law

    def test_the_batch_reader_reads_a_tree_built_after_it_started(self):  # row 49
        law = self.law()
        self.assertIsNotNone(law.read_object(self.C, f"{law._index(self.C)['pin']}:README.md"))  # the reader first
        self.assertFalse(law.in_order(self.C))
        tree = law.corpus_tree('2015-07-01', self.C)
        self.assertEqual(law.read_object(self.C, f'{tree}:act/s2.md'), 'two b\n')
        self.assertEqual(law.read_object(self.C, f'{tree}:act/s1.md'), 'fee 10\n')
        self.assertEqual(law.text_on('2015-07-01', f'{self.C}/act/s2.md'), 'two b\n')

    def test_the_batch_reader_reads_a_tree_under_another_alternate(self):  # row 49: another store in the environment
        law = self.law()
        elsewhere = self.t.root / 'elsewhere' / 'objects'
        elsewhere.mkdir(parents=True)
        os.environ['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = str(elsewhere)
        self.assertIsNotNone(law.read_object(self.C, f"{law._index(self.C)['pin']}:README.md"))
        tree = law.corpus_tree('2017-01-01', self.C)
        os.environ['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = str(elsewhere)  # set again, as another law module would
        self.assertEqual(law.read_object(self.C, f'{tree}:act/s3.md'), 'three y\n')

    def test_a_sweep_leaves_a_running_owners_idle_store(self):  # row 50
        law = self.law()
        tree = law.corpus_tree('2017-01-01', self.C)
        d = law._TREES['dir']
        old = dt.datetime.now().timestamp() - 3 * 86400  # idle for three days, as an MCP server can be
        for p in (d, d / 'owner'):
            os.utime(p, (old, old))
        self.law()._tree_store()  # another law.py starting its own store sweeps old ones
        self.assertTrue((d / 'objects').is_dir())
        law.close_readers()
        self.assertEqual(law.read_object(self.C, f'{tree}:act/s3.md'), 'three y\n')

    def test_a_sweep_removes_a_dead_owners_old_store(self):  # row 50
        law = self.law()
        dead = int(subprocess.run([sys.executable, '-c', 'import os; print(os.getpid())'], capture_output=True,
                                  encoding='utf-8').stdout)
        self.assertFalse(law._pid_alive(dead))
        self.assertTrue(law._pid_alive(os.getpid()))
        stale, fresh, legacy = (Path(tempfile.mkdtemp(prefix='global-law-trees-')) for _ in range(3))
        for d in (stale, fresh):
            (d / 'owner').write_text(f'{dead}\n', encoding='utf-8')
        old = dt.datetime.now().timestamp() - 3 * 86400
        for p in (stale, stale / 'owner', legacy):  # legacy: a store from before owner files, judged by its age
            os.utime(p, (old, old))
        try:
            law._sweep_tree_stores()
            self.assertFalse(stale.exists())
            self.assertFalse(legacy.exists())
            self.assertTrue(fresh.exists())  # its owner is gone, but its heartbeat is recent
        finally:
            for d in (stale, fresh, legacy):
                law._rmtree(d)

    def test_a_removed_store_is_made_again_and_its_trees_rebuilt(self):  # row 50
        law = self.law()
        tree = law.corpus_tree('2015-07-01', self.C)
        self.assertEqual(law.read_object(self.C, f'{tree}:act/s2.md'), 'two b\n')
        d = law._TREES['dir']
        law.close_readers()  # (a running reader may still hold the tree it parsed)
        law._rmtree(d)  # a sweep from an older law.py, which looked only at the folder's age
        self.assertFalse(d.exists())
        self.assertEqual(law.corpus_tree('2015-07-01', self.C), tree)
        self.assertEqual(law.read_object(self.C, f'{tree}:act/s2.md'), 'two b\n')
        grep = subprocess.run(['git', 'grep', '-c', 'two', tree, '--', '*.md'], cwd=self.t.root / self.C,
                              capture_output=True, encoding='utf-8')
        self.assertEqual((grep.returncode, grep.stderr), (0, ''))


class RecordFloors(unittest.TestCase):
    """Issue #17: where an act's record starts at a revision of it (China's Law（修订）) or at a publisher's text, the
    record starts there, not the act; data/acts.json's in_force or adopted dates the act itself."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        g = t.corpus('gg/national/acts')
        # rev: the record starts at the 2017 revision of an act adopted in 1988; the 2020 修正 adds art-003.
        g.commit('标准化法（2017年修订）', {'rev/art-001.md': '# 第一条\n修订后。\n', 'rev/art-002.md': '# 第二条\n二。\n'},
                 In_force='2018-01-01', Kind='Law（修订）')
        g.commit('关于修改《标准化法》的决定（2020年）', {'rev/art-003.md': '# 第三条\n新增。\n',
                                                     'rev/art-001.md': '# 第一条\n修正后。\n'},
                 In_force='2020-01-01', Kind='Law（修正）')
        # new: an act as adopted; base: a publisher's text of an act in force since 1994; amd: an amending law kept as
        # its own act (Azerbaijan), whose Kind says "amendment": it starts there.
        g.commit('劳动合同法（2007年）', {'new/art-001.md': '# 第一条\n原文。\n'}, In_force='2008-01-01', Kind='Law')
        g.commit('Publisher', {'base/art-001.md': '# 第一条\n2018年文本。\n'}, In_force='2018-10-26',
                 Kind='oldest version available')
        g.commit('Law 375 of 2021', {'amd/art-1.md': 'Amends Law 21300.\n'}, In_force='2021-11-26', Kind='amendment')
        g.commit('Lexifina', {'data/acts.json': json.dumps({'acts': [
            {'path': 'rev', 'status': 'in force', 'adopted': '1988-12-29'},
            {'path': 'new', 'status': 'in force', 'in_force': '2008-01-01', 'adopted': '2007-06-29'},
            {'path': 'base', 'status': 'in force', 'in_force': '1994-07-01', 'adopted': '1993-12-29'}]})},
            Kind='documentation')
        t.pin()
        cls.law = t.law()

    @classmethod
    def tearDownClass(cls):
        cls.law.close_readers()
        cls.t.close()

    def test_revision_is_where_the_record_starts(self):
        p = 'gg/national/acts/rev/art-001.md'
        msg = self.law.explain_missing('2015-01-01', p)
        self.assertIn('the record starts on 2018-01-01', msg)
        self.assertIn('a revision of an act already in force then (Kind: Law（修订）)', msg)
        self.assertIn('Its act was adopted on 1988-12-29 (data/acts.json)', msg)
        self.assertNotIn('not yet in force', msg)
        self.assertEqual(self.law.record_floor(p)['in_force'], '2018-01-01')
        # Before the act was adopted at all, it was not in force.
        self.assertIn('adopted only on 1988-12-29 (data/acts.json), so it was not yet in force on 1980-01-01',
                      self.law.explain_missing('1980-01-01', p))
        # From the floor on, the text is the record's, as before.
        self.assertEqual(self.law.text_on('2018-01-01', p), '# 第一条\n修订后。\n')
        self.assertEqual(self.law.text_on('2021-01-01', p), '# 第一条\n修正后。\n')

    def test_article_added_by_a_later_amendment_is_not_yet_in_force(self):
        p = 'gg/national/acts/rev/art-003.md'
        self.assertIsNone(self.law.record_floor(p))
        self.assertIn('was not yet in force on 2019-01-01', self.law.explain_missing('2019-01-01', p))

    def test_act_as_adopted_and_amending_law_start_with_the_law(self):
        self.assertIsNone(self.law.record_floor('gg/national/acts/new/art-001.md'))
        self.assertIn('was not yet in force on 2007-01-01',
                      self.law.explain_missing('2007-01-01', 'gg/national/acts/new/art-001.md'))
        self.assertIsNone(self.law.record_floor('gg/national/acts/amd/art-1.md'))
        self.assertIn('was not yet in force on 2020-01-01',
                      self.law.explain_missing('2020-01-01', 'gg/national/acts/amd/art-1.md'))

    def test_publisher_text_names_the_acts_own_dates(self):
        p = 'gg/national/acts/base/art-001.md'
        msg = self.law.explain_missing('2015-01-01', p)
        self.assertIn('the record starts on 2018-10-26', msg)
        self.assertIn('Its act was in force from 1994-07-01 (data/acts.json)', msg)
        self.assertIn('came into force only on 1994-07-01 (data/acts.json), so it was not yet in force on 1990-01-01',
                      self.law.explain_missing('1990-01-01', p))


class RepealNotices(unittest.TestCase):
    """A version whose whole text is a repeal notice ("16 § Har upphävts genom lag (2011:1252).", "# მუხლი 26.
    (ამოღებულია)", "Repealed by Legal Notice 99 of 2026.") ends the provision on that version's day, as a deletion
    does (audit row 33); a provision that only mentions a repeal is law; a corpus can add patterns or turn it off."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('se/national/acts')
        a.commit('Lag (2000:1)', {'l/16.md': '16 § Avgiften är 10 kronor.\n', 'l/17.md': '17 § Gäller alla.\n',
                                  'l/18.md': '18 § Lagen (1990:5) upphävs.\n',
                                  'l/19.md': '19 § Myndigheten tar ut avgift.\n',
                                  'l/20.md': '20 § Har upphävts genom lag (1995:3).\n'},
                 In_force='2000-01-01', Kind='law', Enacted='1999-12-01')
        a.commit('Lag (2011:1252)', {'l/16.md': '16 § Har upphävts genom lag (2011:1252).\n',
                                     'l/19.md': '19 § Har upphävts genom förordning (2011:9).\n\n'
                                                'Myndigheten får disponera avgiftsinkomsterna.\n'},
                 In_force='2012-01-01', Kind='law', Enacted='2011-11-01')
        a.commit('Lag (2020:7)', {'l/17.md': '### Rubrik\n\n17 § har upphävts genom lag (2020:7).\n'},
                 In_force='2020-07-01', Kind='law', Enacted='2020-02-01')
        a.commit('Lag (2024:3)', {'l/17.md': '17 § Gäller åter alla.\n'}, In_force='2024-01-01', Kind='law',
                 Enacted='2023-12-01')
        g = t.corpus('ge/national/acts')
        g.commit('კანონი №1', {'a/26.md': '# მუხლი 26. დროებითი წესი\n1. ტექსტი.\n'}, In_force='2010-11-03')
        g.commit('კანონი №5', {'a/26.md': '# მუხლი 26. (ამოღებულია)\n- საქართველოს 2011 წლის 17 ოქტომბრის კანონი №5 - '
                                         'ვებგვერდი, 25.10.2011წ.\n'}, In_force='2011-10-25')
        m = t.corpus('mt/national/acts')
        m.commit('Act I of 1935', {'cap/107.md': '# 107. Cellars used for habitation.\nNo cellar shall be used.\n',
                                   'cap/108.md': '# 108. Cellars.\nThe Minister may make rules.\n'},
                 In_force='1935-01-01')
        m.commit('Legal Notice 99 of 2026', {'cap/107.md': '# 107. Cellars used for habitation.\nRepealed by Legal '
                                                         'Notice 99 of 2026.\n- Amended by: XXIX.1935.6.\n'},
                 In_force='2026-03-01')
        o = t.corpus('oo/national/acts')  # a corpus with its own notice wording
        o.commit('Lexifina', {'corpus.json': json.dumps({'repeal_notice': [r'Entf(ä|ae)llt\.?']})},
                 Kind='documentation')
        o.commit('Gesetz 1', {'g/1.md': '# § 1\nText.\n', 'g/2.md': '# § 2\nText zwei.\n'}, In_force='2001-01-01')
        o.commit('Gesetz 2', {'g/1.md': '# § 1\nEntfällt.\n', 'g/2.md': '# § 2\n(aufgehoben)\n'}, In_force='2005-01-01')
        f = t.corpus('ff/national/acts')  # a corpus that turns the rule off
        f.commit('Lexifina', {'corpus.json': json.dumps({'repeal_notice': False})}, Kind='documentation')
        f.commit('Act 1', {'s/1.md': '# 1\nText.\n'}, In_force='2001-01-01')
        f.commit('Act 2', {'s/1.md': '# 1\n[Repealed]\n'}, In_force='2005-01-01')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def names(self, corpus, date):
        law = self.t.law()
        try:
            tree = law.corpus_tree(date, corpus)  # None: nothing in force
            return law.git('ls-tree', '-r', '--name-only', tree, cwd=law.corpus_dir(corpus)).split() if tree else []
        finally:
            law.close_readers()

    def test_notices_in_each_language_are_recognised(self):
        law = self.t.law()
        notices = ['16 § Har upphävts genom lag (2011:1252).', '5 b § Har upphävts genom förordning (2020:762).',
                   '### Inhämtande av uppgifter\n\n11 § Har upphävts genom förordning (2024:104).',
                   '15 § 2 mom. har upphävts genom lag (1993:36).', '3 § Har utgått genom lag (2005:456).',
                   '# მუხლი 43 3 . (ამოღებულია)\n- საქართველოს 2013 წლის 24 ივლისის კანონი №844 - ვებგვერდი, 16.08.2013წ.',
                   '# მუხლი 57¹. (ამოღებულია)', '# მუხლი 11. (ძალადაკარგულია )',
                   '# 72. Adultery.\nRepealed by: XXI.1993.37.',
                   '# 35. Register.\n(Repealed by Act X of 2010 - see L.N. 512 of 2010).\n- Substituted by: XXIII. 1997.16.',
                   '# 13. Eligible offices.\n(Deleted by Legal Notice 462 of 2014)',
                   '## Artículo 72.\n\n(Suprimido)\n\n> Se suprime por el art. 1 de la Ley 30/1981. Ref. BOE-A-1981-16216.',
                   '## Artículos 16 a 21.\n\n(Derogados).', '# Articolul 13\nAbrogat.', '# § 416a (weggefallen)',
                   '# (XXXX) §§ 311a und 311b (weggefallen)', '# Anlage 2 (weggefallen)', '# Art. 86\nAufgehoben',
                   '# Art. 37 bis 39\nAufgehoben', '§ 17 a. (Ophævet)', '# Article 54\nAbrogé.',
                   '# 67 Repeal\n[s 67 repealed by the Law Revision Commission under powers authorised by Act 10 of 2019]',
                   '# § 53. Elektrooniline hääletamine\n[Kehtetu]',
                   '# Статья 2.\nУТРАТИЛ СИЛУ (в соответствии с Законом КР от 18 января 2022 года №4)']
        for text in notices:
            self.assertTrue(law.repeal_notice(text + '\n'), text)
        law_texts = ['18 § Lagen (1990:5) upphävs.', '2. Genom lagen upphävs lagen (1996:764) om företagsrekonstruktion.',
                     '19 § Har upphävts genom förordning (2011:9).\n\nMyndigheten får disponera avgiftsinkomsterna.',
                     '# Art. 18 Entschädigungen\n1) Aufgehoben\n2) Die Regierung setzt die Entschädigung fest.',
                     '# 27 Repeal\nThe Antiquities Act 1935 is hereby repealed.',
                     '# 221 Repeal\nThe following Acts are repealed:\n(a) Port Authority Act 2015;',
                     '# მუხლი 1. ძალადაკარგულად გამოცხადდეს "საქართველოს სახელმწიფო ჰიმნის შესახებ" ორგანული კანონი.',
                     '## Artículo 33.\n\n(Sin contenido)', '## Disposición derogatoria única. Derogación normativa.',
                     'Quedan derogadas cuantas disposiciones de igual o inferior rango se opongan a lo establecido.',
                     '# 15. Prime Minister may extend.\nDeleted by XVI.2019.16 and the Minister shall make rules.',
                     '# 54. Exemption.\nRepealed by Act XIX.2024.50.\nPART X\nCo-ordination with other Authorities',
                     '28 § /Upphör att gälla U:2028-07-02/ Regeringen får meddela föreskrifter.', '# § 5', '']
        for text in law_texts:
            self.assertIsNone(law.repeal_notice(text + '\n'), text)
        self.assertTrue(law.repeal_notice('Norma derogada, con efectos de 1 de julio de 2020, por la disposición '
                                          'derogatoria única.1.a) del Real Decreto 550/2020. Ref. BOE-A-2020-6745#dd.\n'))
        # One detector: after an act's end (is_repeal_note, after_end) a note need only start as one.
        for text in ('Norma derogada, excepto su art. 7, según establece su disposición derogatoria única.\n\nDisposición'
                     ' transitoria quinta.\n', 'Repealed with effect from 2020-01-01.\n', '# Article 3\nAbrogé.\nNOTA : voir.\n',
                     '16 § Har upphävts genom lag (2011:1252).\n'):
            self.assertTrue(law.is_repeal_note(text), text)
        for text in ('## Artículo 5.\n\n1. (Derogado)\n\n2. La información se publicará.\n',
                     '# Art. 3\nAufgehoben werden:\n- a) die §§ 1 bis 3\n', '# Articolul 4\nAbrogat.\nPosesorul nu poate refuza.\n'):
            self.assertFalse(law.is_repeal_note(text), text)
        law.close_readers()

    def test_show_says_the_provision_was_repealed_and_by_which_law(self):
        out, err, code = self.t.cli('show', '2011-12-31', 'se/national/acts/l/16.md')
        self.assertEqual(out, '16 § Avgiften är 10 kronor.\n', err)
        out, err, code = self.t.cli('show', '2012-01-01', 'se/national/acts/l/16.md')
        self.assertEqual(out, '')
        self.assertNotEqual(code, 0)
        self.assertIn('repealed on 2012-01-01 by Lag (2011:1252), the record keeps its repeal notice: '
                      '"16 § Har upphävts genom lag (2011:1252)."', err)
        for path, day, law in (('ge/national/acts/a/26.md', '2011-10-25', 'კანონი №5'),
                               ('mt/national/acts/cap/107.md', '2026-03-01', 'Legal Notice 99 of 2026')):
            out, err, code = self.t.cli('show', '2026-10-01', path)
            self.assertNotEqual(code, 0, out)
            self.assertIn(f'repealed on {day} by {law}, the record keeps its repeal notice', err)
        # A record whose first version is the notice (current-only) does not hold the day of the repeal.
        out, err, code = self.t.cli('show', '2001-01-01', 'se/national/acts/l/20.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('repealed, the record keeps its repeal notice: "20 § Har upphävts '
                      'genom lag (1995:3)."', err)
        out, err, code = self.t.cli('show', '1999-01-01', 'se/national/acts/l/20.md')
        self.assertIn('only as a repeal notice', err)

    def test_log_labels_the_row_repealed(self):
        out, err, code = self.t.cli('log', 'ge/national/acts/a/26.md')
        self.assertIn('in force 2010-11-03  კანონი №1', out, err)
        self.assertIn('repealed 2011-10-25  კანონი №5', out)
        self.assertIn('[repeal notice: მუხლი 26. (ამოღებულია)]', out)

    def test_world_and_search_trees_leave_the_notice_out(self):
        law = self.t.law()
        try:
            self.assertFalse(law.in_order('se/national/acts'))  # its commit-order prefix still holds the notices
            self.assertTrue(law.in_order('ff/national/acts'))
        finally:
            law.close_readers()
        names = self.names('se/national/acts', '2021-01-01')
        self.assertNotIn('l/16.md', names)
        self.assertNotIn('l/17.md', names)
        for f in ('l/18.md', 'l/19.md'):
            self.assertIn(f, names)
        self.assertIn('l/16.md', self.names('se/national/acts', '2011-06-01'))
        self.assertIn('l/17.md', self.names('se/national/acts', '2025-01-01'))  # in force again
        self.assertNotIn('a/26.md', self.names('ge/national/acts', '2026-01-01'))
        self.assertEqual(self.names('mt/national/acts', '2026-06-01'), ['cap/108.md'])

    def test_diff_shows_the_text_removed(self):
        out, err, code = self.t.cli('diff', '2011-06-01', '2012-06-01', 'se/national/acts/l/16.md')
        self.assertIn('[-16 § Avgiften är 10 kronor.-]', out)
        self.assertIn('repealed on 2012-01-01 by Lag (2011:1252)', out)
        self.assertNotIn('{+', out)

    def test_blame_and_words_stop_at_the_notice(self):
        for cmd in ('blame', 'words', 'show'):
            out, err, code = self.t.cli(cmd, '2021-01-01', 'se/national/acts/l/17.md')
            self.assertNotEqual(code, 0, out)
            self.assertIn('repealed on 2020-07-01 by Lag (2020:7)', err)
        out, err, code = self.t.cli('blame', '2025-01-01', 'se/national/acts/l/17.md')
        self.assertIn('Lag (2024:3)', out, err)
        self.assertNotIn('Lag (2000:1)', out)
        out, err, code = self.t.cli('show', '2025-01-01', 'se/national/acts/l/17.md')
        self.assertEqual(out, '17 § Gäller åter alla.\n', err)

    def test_provisions_that_only_mention_a_repeal_are_unchanged(self):
        for path, text in (('se/national/acts/l/18.md', '18 § Lagen (1990:5) upphävs.\n'),
                           ('se/national/acts/l/19.md', '19 § Har upphävts genom förordning (2011:9).\n\n'
                                                        'Myndigheten får disponera avgiftsinkomsterna.\n'),
                           ('mt/national/acts/cap/108.md', '# 108. Cellars.\nThe Minister may make rules.\n')):
            out, err, code = self.t.cli('show', '2026-10-01', path)
            self.assertEqual((out, code), (text, 0), err)
            out, err, code = self.t.cli('log', path)
            self.assertNotIn('repealed', out)

    def test_a_corpus_adds_its_own_wording_or_turns_the_rule_off(self):
        out, err, code = self.t.cli('show', '2006-01-01', 'oo/national/acts/g/1.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('repealed on 2005-01-01 by Gesetz 2', err)
        out, err, code = self.t.cli('show', '2006-01-01', 'oo/national/acts/g/2.md')  # the built-in markers still apply
        self.assertNotEqual(code, 0, out)
        out, err, code = self.t.cli('show', '2006-01-01', 'ff/national/acts/s/1.md')
        self.assertEqual(out, '# 1\n[Repealed]\n', err)

    def test_the_notice_list_is_kept_on_disk(self):
        law = self.t.law()
        try:
            got = law.notice_blobs('se/national/acts')
            self.assertEqual(len(got), 3)  # l/16.md, l/17.md and l/20.md's notices; l/19.md is law
            kept = list(law._store().glob('se~national~acts.notices.*.json'))
            self.assertEqual(len(kept), 1)
            self.assertEqual(set(json.loads(kept[0].read_text(encoding='utf-8'))['notices']), set(got))
            self.assertEqual(law.notice_blobs('ff/national/acts'), frozenset())
        finally:
            law.close_readers()


class ReaderQuirks(unittest.TestCase):
    """Five reader quirks (4 November 2026): the log in in-force order, a corrected credit's own enacted day,
    Trinidad's versions dated by the consolidation that first shows them, Liechtenstein's Kind: start, and
    `Redates: <commit> enacted <day>` correcting a law's Adopted/Enacted day."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        # 1. Log order: a version found late, two laws in force the same day appended after a later one (spain-law's
        # same-day versions, LIRPF art. 93), and an act ended by data/acts.json.
        a = t.corpus('lo/national/acts')
        a.commit('Act 1 of 2010', {'act/s1.md': 'one\n', 'old/s1.md': 'old\n'}, In_force='2010-01-01', Kind='law')
        cls.nine = a.commit('Act 9 of 2022', {'act/s1.md': 'one, 9\n'}, In_force='2023-01-01', Enacted='2022-12-23')
        a.commit('Act 10 of 2024', {'act/s1.md': 'one, 10\n'}, In_force='2024-12-22', Enacted='2024-12-20')
        a.commit('Act 3 of 2015', {'act/s1.md': 'one, 3\n', 'old/s1.md': 'old, 3\n'}, In_force='2015-06-01')
        a.commit('Lexifina', {'act/s1.md': 'one, 8\n'}, In_force='2023-01-01', Law='Act 8 of 2022',
                 Enacted='2022-12-21')
        a.commit('Lexifina', {'act/s1.md': 'one, 9\n'}, In_force='2023-01-01', Re_asserts=cls.nine, Enacted='2022-12-23')
        a.commit('Lexifina', {'data/acts.json': json.dumps({'acts': [
            {'path': 'old', 'status': 'repealed', 'repealed': '2020-01-01', 'repealed_by': 'Act 19 of 2019'}]})},
            Kind='documentation')
        a.commit('Act 2 of 2012', {'old/s1.md': 'old, 2\n'}, In_force='2012-01-01', Enacted='2011-12-01')
        # 2. Credits corrected by data/credits.csv; the commit's own Enacted is the first-credited law's.
        c = t.corpus('cr/national/acts')
        c.commit('L1 of 1998', {'a/s0.md': 'zero\n'}, In_force='1998-06-01', Enacted='1998-05-17', Published='1998-05-18')
        cls.wrong = c.commit('L14 of 2000', {'a/s1.md': 'one\n', 'a/s2.md': 'two\n', 'a/s3.md': 'three\n',
                                            'a/s4.md': 'four\n'},
                             In_force='1999-01-01', Enacted='2000-12-29', Published='2000-12-30')
        credits = ('act,in_force,provision,law,was_law,was_commit\n'
                   f'a,1999-01-01,s1,k46,k14,{cls.wrong}\n'  # laws.csv gives its dates
                   f'a,1999-01-01,s2,BOE-A-1998-29216 (Ley 46/1998),k14,{cls.wrong}\n'  # normas.tsv does
                   f'a,1999-01-01,s3,L1 of 1998,k14,{cls.wrong}\n'  # its own commit does
                   f'a,1999-01-01,s4,Unknown Law,k14,{cls.wrong}\n')  # nothing does
        c.commit('Lexifina', {'data/credits.csv': credits,
                              'data/laws.csv': 'key,label,enacted,published\nk46,Law 46 of 1998,1998-12-17,1998-12-18\n'
                                               'k14,L14 of 2000,2000-12-29,2000-12-30\n',
                              'normas.tsv': 'id\trango\tpath\tfecha_disposicion\tfecha_publicacion\ttitulo\n'
                                            'BOE-A-1998-29216\tLey\ta\t1998-12-17\t1998-12-18\tLey 46/1998\n'},
                 Kind='documentation')
        # 3. Trinidad: a subsidiary-legislation folder whose first version is an amending Act first shown in a
        # Revised Edition; a section added to an existing chapter the same way; and a control without that basis.
        shown = ('1980 Revised Edition as at December 1990; the label gives the month only, so it is dated the '
                 "month's last day, 31 December 1990; a change first shown here took effect on or before it")
        tt = t.corpus('tt/national/acts')
        tt.commit('Law Revision Commission', {'chapters/88-09/s-1.md': 'Section 1 (1950).\n'}, In_force='1950-12-31',
                  Kind='consolidation', In_force_basis='1950 Revised Edition as at December 1950')
        tt.commit('Act No. 38 of 1961', {'chapters/88-09/s-1.md': 'Section 1 (1990).\n',
                                         'chapters/88-09/s-1A.md': 'Section 1A.\n',
                                         'chapters/88-09/sl-01/title.md': 'Regulations.\n'},
                  In_force='1990-12-31', Kind='amendment', In_force_basis=shown)
        tt.commit('Act No. 5 of 1990', {'chapters/90-01/sl-01/title.md': 'New regulations.\n'},
                  In_force='1990-12-31', Kind='amendment', In_force_basis='commencement order')
        # 4. Liechtenstein's Kind: start, the oldest version available of an act.
        li = t.corpus('li/national/acts')
        li.commit('LGBl. 2023 Nr. 252', {'lr-1/art-001.md': 'Art. 1\n'}, In_force='2023-07-01', Kind='start',
                  Published='2023-06-20 (LGBl. 2023 Nr. 252)')
        # 5. An Adopted day taken from another part of the act, corrected by Redates: <commit> enacted <day>.
        sw = t.corpus('sw/bund/acts')
        cls.part = sw.commit('AS 2025 422', {'0.232/r14.md': 'Regel 14\n'}, In_force='2023-04-01',
                             Adopted='2024-07-17', Published='2025-06-25 (AS 2025 422)')
        cls.other = sw.commit('AS 2025 423', {'0.232/r15.md': 'Regel 15\n'}, In_force='2023-04-01',
                              Adopted='2024-07-17')
        sw.commit('Lexifina', {}, Kind='documentation',
                  Redates=[f'{cls.part} enacted 2016-10-11', f'{cls.other[:10]} enacted no-date'])
        t.pin()
        cls.law = t.law()

    @classmethod
    def tearDownClass(cls):
        cls.law.close_readers()
        cls.t.close()

    @staticmethod
    def dated(out: str) -> list[tuple[str, str]]:
        """(in-force day, law) of each log line: '<label> <day>  <law>  ...'."""
        return [(line.split('  ')[0].split()[-1], line.split('  ')[1]) for line in out.splitlines() if line.strip()]

    def test_log_is_in_in_force_order(self):
        out, err, code = self.t.cli('log', 'lo/national/acts/act/s1.md')
        self.assertEqual(self.dated(out), [('2010-01-01', 'Act 1 of 2010'), ('2015-06-01', 'Act 3 of 2015'),
                                           ('2023-01-01', 'Act 9 of 2022'), ('2023-01-01', 'Act 8 of 2022'),
                                           ('2023-01-01', 'Act 9 of 2022'), ('2024-12-22', 'Act 10 of 2024')], err)
        # history() itself stays in commit order (blame, words and the MCP tools read it so).
        self.assertEqual([h['in_force'] for h in self.law.history('lo/national/acts/act/s1.md')],
                         ['2010-01-01', '2023-01-01', '2024-12-22', '2015-06-01', '2023-01-01', '2023-01-01'])
        self.assertEqual(self.law.text_on('2023-06-01', 'lo/national/acts/act/s1.md'), 'one, 9\n')

    def test_log_keeps_the_act_end_after_the_versions_before_it(self):
        out, err, code = self.t.cli('log', 'lo/national/acts/old/s1.md')
        self.assertEqual(self.dated(out), [('2010-01-01', 'Act 1 of 2010'), ('2012-01-01', 'Act 2 of 2012'),
                                           ('2015-06-01', 'Act 3 of 2015'), ('2020-01-01', 'Act 19 of 2019')], err)
        self.assertTrue(out.splitlines()[-1].startswith('repealed 2020-01-01'), out)

    def test_a_corrected_credit_shows_its_own_laws_dates(self):
        expected = {'s1': ('Law 46 of 1998', '1998-12-17', '1998-12-18'),
                    's2': ('BOE-A-1998-29216 (Ley 46/1998)', '1998-12-17', '1998-12-18'),
                    's3': ('L1 of 1998', '1998-05-17', '1998-05-18'),
                    's4': ('Unknown Law', None, None)}
        for unit, (label, enacted, published) in expected.items():
            row = self.law.history(f'cr/national/acts/a/{unit}.md')[0]
            self.assertEqual((row['law'], row['enacted'], row['published']), (label, enacted, published), unit)
            self.assertNotIn('date_doubtful', row, unit)
            out, err, code = self.t.cli('log', f'cr/national/acts/a/{unit}.md')
            self.assertNotIn('2000-12-29', out)
            self.assertNotIn('date doubtful', out)

    def test_a_version_first_shown_in_a_consolidation_is_a_record_floor(self):
        p = 'tt/national/acts/chapters/88-09/sl-01/title.md'
        floor = self.law.record_floor(p)
        self.assertEqual((floor['in_force'], floor['law']), ('1990-12-31', 'Act No. 38 of 1961'))
        self.assertIn('first shown here took effect on or before it', floor['in_force_basis'])
        msg = self.law.explain_missing('1985-01-01', p)
        self.assertIn('the record starts on 1990-12-31', msg)
        self.assertIn('so in force on or before that day', msg)
        self.assertNotIn('not yet in force', msg)
        self.assertEqual(self.law.text_on('1991-01-01', p), 'Regulations.\n')
        # The MCP server gives law.py a subprocess with run() only: the basis is read the same.
        import types
        saved = self.law.subprocess
        self.law.subprocess = types.SimpleNamespace(run=subprocess.run)
        try:
            self.assertEqual(self.law._in_force_basis('tt/national/acts', floor['commit']), floor['in_force_basis'])
        finally:
            self.law.subprocess = saved
        # A section added to a chapter already in the record, and a folder without that basis: as before.
        self.assertIsNone(self.law.record_floor('tt/national/acts/chapters/88-09/s-1A.md'))
        self.assertIsNone(self.law.record_floor('tt/national/acts/chapters/90-01/sl-01/title.md'))
        self.assertIn('was not yet in force on 1985-01-01',
                      self.law.explain_missing('1985-01-01', 'tt/national/acts/chapters/90-01/sl-01/title.md'))

    def test_kind_start_is_a_starting_text(self):
        self.assertEqual(self.law.kind_of('start'), ('baseline', None))
        out, err, code = self.t.cli('log', 'li/national/acts/lr-1/art-001.md')
        self.assertTrue(out.startswith('version of 2023-07-01'), out)
        out, err, code = self.t.cli('show', '2023-01-01', 'li/national/acts/lr-1/art-001.md')
        self.assertNotIn('not recognised', err)
        self.assertIn('the record starts on 2023-07-01', err)

    def test_redates_enacted_corrects_the_day_a_law_was_made(self):
        row = self.law.history('sw/bund/acts/0.232/r14.md')[0]
        self.assertEqual((row['in_force'], row['enacted']), ('2023-04-01', '2016-10-11'))
        self.assertNotIn('date_doubtful', row)
        out, err, code = self.t.cli('log', 'sw/bund/acts/0.232/r14.md')
        self.assertIn('(enacted 2016-10-11; published 2025-06-25 (AS 2025 422))', out, err)
        self.assertNotIn('2024-07-17', out)
        self.assertNotIn('date doubtful', out)
        row = self.law.history('sw/bund/acts/0.232/r15.md')[0]
        self.assertEqual((row['in_force'], row['enacted']), ('2023-04-01', None))
        ix = self.law._index('sw/bund/acts')
        self.assertEqual(ix['redated_enacted'][self.part], ('2024-07-17', '2016-10-11'))
        self.assertNotIn(self.part, ix.get('redated', {}))  # its in-force day stands

    def test_check_corpus_reads_redates_enacted_as_readers_do(self):
        sys.path.insert(0, str(HERE / 'tools'))
        try:
            import check_corpus
        finally:
            sys.path.pop(0)
        d = Path(tempfile.mkdtemp(prefix='gl-check-'))
        try:
            c = Corpus(d / 'repo')
            (c.path / 'REPRODUCE.md').write_text('x', encoding='utf-8')
            (c.path / 'corpus.json').write_text(json.dumps({
                'corpus': 'sw/bund/acts', 'name': 'SW', 'language': 'de', 'history_from': '2000-01-01',
                'record_to': '2026-11-01', 'in_force_trailer': 'In-force',
                'citation': {'file': '(a)/(b)', 'cites': 'x{n}'}}), encoding='utf-8')
            run('add', '-A', cwd=c.path)
            part = c.commit('AS 2025 422', {'r14.md': 'Regel 14\n'}, In_force='2023-04-01', Adopted='2024-07-17')
            fatal, warn = check_corpus.problems(c.path, '2026-11-03')
            self.assertTrue(any('in force before the act itself was made' in w for w in warn), warn)
            fix = c.commit('Lexifina', {}, Kind='documentation', Redates=f'{part} enacted 2016-10-11')
            fatal, warn = check_corpus.problems(c.path, '2026-11-03')
            self.assertEqual(fatal, [])
            self.assertFalse(any('in force before the act itself was made' in w for w in warn), warn)
            self.assertFalse(any('Redates' in w for w in warn), warn)
            self.assertEqual(check_corpus.reader_redates(c.path)['enacted'], [(fix, part, '2016-10-11')])
            c.commit('Lexifina', {}, Kind='documentation', Redates=[f'{part} adopted 2016-10-11',
                                                                   f'{part} enacted 2016-13-45'])
            fatal, warn = check_corpus.problems(c.path, '2026-11-03')
            self.assertTrue(any("is not 'Redates: <commit> [enacted]" in w for w in warn), warn)
            self.assertTrue(any('no day of the calendar' in w and '2016-13-45' in w for w in warn), warn)
        finally:
            def writable(func, path, _):
                os.chmod(path, 0o700)
                func(path)
            shutil.rmtree(d, onerror=writable)


class PartialRepeals(unittest.TestCase):
    """Audit row 53: an act data/acts.json ends whose repeal scope the corpus marks unresolved
    (lifecycle_scope_unresolved: spain-law's BOE "Norma derogada ... excepto ..." notes) is not ended file by file: the
    text stays readable, with a note that quotes the publisher's wording; where the row lists the provisions the repeal
    covers (lifecycle_repealed_provisions), only those end."""

    NOTICE = ('Norma derogada, con efectos de 1 de enero de 2020, por la disposición derogatoria única del Act 5 of '
              '2019, excepto el art. 2, que seguirá aplicándose hasta el 1 de enero de 2022.\n')

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('aa/national/acts')
        a.commit('Act 1 of 2010', {'part/a1.md': 'part one\n', 'part/a2.md': 'part two\n',
                                   'unres/a1.md': 'unres one\n', 'unres/a2.md': 'unres two\n',
                                   'bare/a1.md': 'bare one\n', 'whole/a1.md': 'whole one\n'},
                 In_force='2010-01-01', Kind='law', Enacted='2009-12-01')
        a.commit('Act 5 of 2019', {'unres/no.md': cls.NOTICE}, In_force='2020-01-01', Kind='law', Enacted='2019-12-01')
        acts = {'acts': [
            {'path': 'part', 'status': 'repealed', 'repealed': '2020-01-01',
             'repealed_by': 'Act 5 of 2019, excepto el art. 2', 'lifecycle_scope_unresolved': True,
             'lifecycle_repealed_provisions': ['a1.md']},
            # BOE gives the end of the saved part as the act's day (RD 384/2015): the general repeal was earlier.
            {'path': 'unres', 'status': 'repealed', 'repealed': '2022-01-01', 'repealed_by': None,
             'lifecycle_scope_unresolved': True, 'lifecycle_notice': 'no.md'},
            {'path': 'bare', 'status': 'repealed', 'repealed': '2020-01-01', 'lifecycle_scope_unresolved': True},
            {'path': 'whole', 'status': 'repealed', 'repealed': '2020-01-01', 'repealed_by': 'Act 5 of 2019',
             'lifecycle_scope_unresolved': False}]}
        a.commit('Lexifina', {'data/acts.json': json.dumps(acts)}, Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_a_repeal_that_saves_provisions(self):
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/part/a2.md')
        self.assertEqual((out, code), ('part two\n', 0), err)
        self.assertIn('lists the provisions that repeal covers', err)
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/part/a1.md')
        self.assertNotEqual(code, 0, out)
        self.assertIn('was repealed on 2020-01-01', err)

    def test_an_unresolved_scope_is_noted_not_applied(self):
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/unres/a1.md')
        self.assertEqual((out, code), ('unres one\n', 0), err)
        self.assertIn('saves some provisions', err)
        self.assertIn('excepto el art. 2', err)  # the publisher's own wording
        self.assertIn('2020-01-01', err)  # from the day the notice gives, before the act's recorded day
        out, err, code = self.t.cli('show', '2023-01-01', 'aa/national/acts/unres/a2.md')
        self.assertEqual((out, code), ('unres two\n', 0), err)
        self.assertIn('saves some provisions', err)
        out, err, code = self.t.cli('show', '2015-01-01', 'aa/national/acts/unres/a1.md')
        self.assertNotIn('saves some provisions', err)
        out, err, code = self.t.cli('log', 'aa/national/acts/unres/a1.md')
        self.assertNotIn('repealed 2022-01-01', out)
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/bare/a1.md')
        self.assertEqual((out, code), ('bare one\n', 0), err)
        self.assertIn('may not cover every provision', err)
        out, err, code = self.t.cli('show', '2021-01-01', 'aa/national/acts/whole/a1.md')  # resolved: ended as before
        self.assertNotEqual(code, 0, out)
        law = self.t.law()
        try:
            names = law.git('ls-tree', '-r', '--name-only', law.corpus_tree('2023-01-01', 'aa/national/acts'),
                            cwd=law.corpus_dir('aa/national/acts')).split()
        finally:
            law.close_readers()
        self.assertIn('unres/a1.md', names)
        self.assertIn('part/a2.md', names)
        self.assertNotIn('part/a1.md', names)
        self.assertNotIn('whole/a1.md', names)


class DeletionLabels(unittest.TestCase):
    """Audit row 57: a version that removes a provision is its end, not a law in force: log says "ended"; France's
    "Fin de vigueur" commits (a version ending with no successor, no law named) are ends, not laws, in laws and world."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('aa/national/acts')
        a.commit('Act 1', {'act1/s1.md': 'one\n', 'act1/s2.md': 'two\n', 'act1/s3.md': 'three\n'},
                 In_force='2010-01-01')
        a.commit('Act 2', {'act1/s1.md': None, 'act1/s3.md': 'three, amended\n'}, In_force='2020-01-01')
        a.commit('Fin de vigueur', {'act1/s2.md': None}, In_force='2020-01-01')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_log_labels_an_end_ended(self):
        out, err, code = self.t.cli('log', 'aa/national/acts/act1/s1.md')
        self.assertIn('ended 2020-01-01  Act 2', out, err)
        self.assertNotIn('in force 2020-01-01', out)
        out, err, code = self.t.cli('log', 'aa/national/acts/act1/s2.md')
        self.assertIn('ended 2020-01-01  Fin de vigueur', out, err)
        self.assertNotIn('in force 2020-01-01', out)
        out, err, code = self.t.cli('log', 'aa/national/acts/act1/s3.md')
        self.assertIn('in force 2020-01-01  Act 2', out, err)

    def test_an_end_of_validity_is_not_a_law(self):
        out, err, code = self.t.cli('laws', '2020-01-01', '2020-01-01', 'aa')
        self.assertIn('Act 2', out, err)
        self.assertNotIn('Fin de vigueur', out)
        self.assertIn('1 ends of validity', err)
        out, err, code = self.t.cli('world', '2021-01-01')
        self.assertIn('Act 2, in force 2020-01-01', out, err)
        self.assertEqual(self.t.law().kind_of('end of validity')[0], 'end')


class PublisherCredit(unittest.TestCase):
    """Audit row 62: a dated commit with no Kind (or a Kind word for a law) by the name the same corpus uses for its
    starting or unexplained texts is the publisher's change, not a law: "no law named", and not in laws. Kind: reverted
    (Monaco's "texte antérieur rétabli par Legimonaco (aucune loi)") is not a law either."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('aa/national/acts')
        a.commit('Publisher X', {'act/s1.md': 'one\n'}, In_force='2000-01-01', Kind='baseline')
        a.commit('Act 5 of 2010', {'act/s1.md': 'two\n'}, In_force='2010-01-01')
        a.commit('Publisher X', {'act/s1.md': 'three\n'}, In_force='2015-01-01')
        a.commit('Restorer', {'act/s1.md': 'two\n'}, In_force='2016-01-01', Kind='reverted')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_publisher_author_is_not_a_law(self):
        out, err, code = self.t.cli('log', 'aa/national/acts/act/s1.md')
        self.assertIn('in force 2015-01-01  Publisher X (no law named for this change)', out, err)
        self.assertIn('in force 2016-01-01  Restorer (no law named for this change)', out, err)
        self.assertIn('in force 2010-01-01  Act 5 of 2010', out)
        out, err, code = self.t.cli('laws', '2000-01-01', '2020-01-01', 'aa')
        self.assertEqual([line.split()[-4:] for line in out.splitlines()], [['Act', '5', 'of', '2010']], out)
        self.assertIn('2 changes no law is named for', err)
        out, err, code = self.t.cli('words', '2015-06-01', 'aa/national/acts/act/s1.md')
        self.assertIn('Publisher X (no law named for this change)', out, err)


class RestoredAfterWithdrawal(unittest.TestCase):
    """spain-law 645ca52 (documentation) recorded every file as deleted by mistake, and 57854db (documentation) put
    them all back: a file a documentation commit withdraws and a later one restores keeps its versions."""

    def test_a_restored_file_keeps_its_history(self):
        t = Tree()
        try:
            a = t.corpus('aa/national/acts')
            a.commit('Act 1 of 2010', {'act/s1.md': 'one\n', 'act/s2.md': 'gone\n'}, In_force='2010-01-01')
            a.commit('Act 2 of 2020', {'act/s1.md': 'two\n'}, In_force='2020-01-01')
            a.commit('Lexifina', {'act/s1.md': None, 'act/s2.md': None}, Kind='documentation')
            a.commit('Lexifina', {'act/s1.md': 'two\n'}, Kind='documentation')
            t.pin()
            out, err, code = t.cli('show', '2015-01-01', 'aa/national/acts/act/s1.md')
            self.assertEqual(out, 'one\n', err)
            out, err, code = t.cli('show', TODAY, 'aa/national/acts/act/s1.md')
            self.assertEqual(out, 'two\n', err)
            out, err, code = t.cli('show', '2015-01-01', 'aa/national/acts/act/s2.md')  # still withdrawn
            self.assertNotEqual(code, 0, out)
        finally:
            t.close()

class KindWords(unittest.TestCase):
    """Audit row 77: Australia's Register writes Kind: Unattributed for a compilation no one instrument made (authored
    by the Register itself), AsMade for an instrument as made, Disallow for a disallowance. Unattributed is not a law,
    and the Register is not a law either."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus('au/federal/instruments')
        a.commit('Federal Register of Legislation', {'reg/s1.md': 'one\n'}, In_force='2002-01-01', Kind='AsMade')
        a.commit('Amending Regulation 2003', {'reg/s1.md': 'two\n'}, In_force='2003-01-01', Kind='Amend')
        a.commit('Federal Register of Legislation', {'reg/s1.md': 'three\n'}, In_force='2004-01-01', Kind='Unattributed',
                 Attribution='not attributable to one instrument (no reason recorded)')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_register_kinds_are_known(self):
        law = self.t.law()
        try:
            self.assertEqual(law.kind_of('Unattributed'), ('uncredited', None))
            self.assertEqual(law.kind_of('not attributable to one instrument'), ('uncredited', None))
            self.assertEqual(law.kind_of('AsMade'), ('law', None))
            self.assertEqual(law.kind_of('Disallow'), ('law', None))
        finally:
            law.close_readers()

    def test_laws_lists_no_publisher(self):
        out, err, code = self.t.cli('laws', '2000-01-01', '2026-12-31', 'au')
        self.assertEqual(code, 0, err)
        self.assertNotIn('Federal Register of Legislation', out)
        self.assertIn('Amending Regulation 2003', out)
        self.assertIn('2 changes no law is named for', err)
        out, err, code = self.t.cli('show', '2005-01-01', 'au/federal/instruments/reg/s1.md')
        self.assertNotIn('not recognised', err)


class AsEnactedDeclared(unittest.TestCase):
    """Audit row 79: the Indonesian builder credits each Perda as enacted to the publisher (Kind: publisher, dated by
    the Perda's own day). A corpus that declares history as-enacted (data/repo.json, or corpus.json) is read so: the
    as-enacted note, not "the text as the publisher gave it on the day it was read"."""

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        for path, history in (('id/lamongan/acts', 'as-enacted'), ('id/other/acts', None)):
            a = t.corpus(path)
            repo = {'country': 'ID-XX', 'name': path, 'publisher': 'JDIH X'}
            if history:
                repo['history'] = history
            a.commit('Lexifina', {'data/repo.json': json.dumps(repo)}, Kind='documentation')
            a.commit('JDIH X', {'perda-2016-012/pasal-001.md': 'Pasal 1\n'}, In_force='2016-12-05', Kind='publisher')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_declared_as_enacted_is_not_read_as_current_text(self):
        law = self.t.law()
        try:
            self.assertEqual(law.corpus_info('id/lamongan/acts').get('history'), 'as-enacted')
            notes = ' '.join(law.caveats('2017-01-01', 'id/lamongan/acts'))
            self.assertIn('each law is shown as first published; later amendments are not applied', notes)
            self.assertNotIn('on the day it was read', notes)
            # Undeclared, the same commits still read as current text only.
            self.assertIn('on the day it was read', ' '.join(law.caveats('2017-01-01', 'id/other/acts')))
        finally:
            law.close_readers()


class NamedFilesScale(unittest.TestCase):
    """Audit row 54: a correction whose Files: names a whole code (Texas: 54,826 paths in 7 corrections) is read with
    one recursive ls-tree, not one <commit>:<path> lookup per named path, and builds the same tree."""

    N = 20000
    C = 'us/texas/acts'

    @classmethod
    def setUpClass(cls):
        t = cls.t = Tree()
        a = t.corpus(cls.C)
        code = a.path / 'code'
        code.mkdir()
        for i in range(cls.N):
            (code / f'f{i:05d}.md').write_bytes(f'section {i}\n'.encode('utf-8'))
        run('add', '-A', cwd=a.path)
        a.commit('Act 1 of 2010', {}, In_force='2010-01-01', Kind='law')
        a.commit('Act 2 of 2015', {'code/f00001.md': 'section 1, amended\n'}, In_force='2015-01-01', Kind='law')
        # The correction changes one file and names every file of the code (a message too long for a command line).
        (code / 'f00000.md').write_bytes(b'section 0, corrected\n')
        run('add', '-A', cwd=a.path)
        names = ''.join(f'Files: code/f{i:05d}.md\n' for i in range(cls.N))
        msg = a.path.parent / 'msg.txt'
        msg.write_text('Publisher\n\nKind: correction\nIn-force: 2012-01-01\nCorrects: code 2012-01-01..2014-12-31\n'
                       + names, encoding='utf-8')
        env = {'GIT_AUTHOR_NAME': 'Publisher', 'GIT_AUTHOR_EMAIL': 'p@example.org', 'GIT_COMMITTER_NAME': 't',
               'GIT_COMMITTER_EMAIL': 't@example.org'}
        run('commit', '-q', '-F', str(msg), cwd=a.path, env=env)
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_one_ls_tree_per_correction_and_the_same_tree(self):
        import subprocess as sp
        fast, slow = self.t.law(), self.t.law()
        slow.NAMED_TREE_MIN = 10 ** 9  # the per-path lookup, as before
        # What _named_at asks git, for the paths the correction names but does not change.
        calls = {'ls-tree -r': 0, 'ls-tree': 0, 'cat-file paths': 0}
        git, run_, named_at = fast.git, sp.run, fast._named_at
        active = []

        def counted_git(*args, **kw):
            if active and args[:1] == ('ls-tree',):
                calls['ls-tree -r' if args[1:2] == ('-r',) else 'ls-tree'] += 1
            return git(*args, **kw)

        def counted_run(cmd, *args, **kw):
            if active and isinstance(cmd, list) and 'cat-file' in cmd and kw.get('input'):
                calls['cat-file paths'] += kw['input'].count(b'\n')
            return run_(cmd, *args, **kw)

        def counted_named_at(*args, **kw):
            active.append(1)
            try:
                return named_at(*args, **kw)
            finally:
                active.pop()

        try:
            fast.git, sp.run, fast._named_at = counted_git, counted_run, counted_named_at
            try:
                fast.file_index(self.C)
            finally:
                fast.git, sp.run, fast._named_at = git, run_, named_at
            self.assertEqual(calls, {'ls-tree -r': 1, 'ls-tree': 0, 'cat-file paths': 0})
            for date in ('2011-01-01', '2013-01-01', '2016-01-01'):
                self.assertEqual(fast.corpus_tree(date, self.C), slow.corpus_tree(date, self.C), date)
            out, err, code = self.t.cli('show', '2013-01-01', f'{self.C}/code/f00000.md')
            self.assertEqual(out, 'section 0, corrected\n', err)
        finally:
            fast.close_readers()
            slow.close_readers()


if __name__ == '__main__':
    unittest.main()
