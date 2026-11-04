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
        # A correction whose range runs past its act's end, and one that starts after it.
        a.commit('Gazette 2', {'cor/s2.md': 'cor two, corrected\n'}, In_force='2012-01-01', Kind='correction',
                 Corrects='cor 2012-01-01..2025-12-31', Files='cor/s2.md', Reason='misprint')
        a.commit('Gazette 3', {'cor/s1.md': 'cor one, corrected\n'}, In_force='2021-01-01', Kind='correction',
                 Corrects='cor 2021-01-01..2025-12-31', Files='cor/s1.md', Reason='misprint')
        acts = {'acts': [{'path': 'rep', 'status': 'repealed', 'repealed': '2015-01-01', 'repealed_by': 'Act 20 of 2016'},
                         {'path': 'ann', 'status': 'annulled', 'in_force': '2011-01-01', 'annulled': '2014-05-01'},
                         {'path': 'cor', 'status': 'repealed', 'repealed': '2020-01-01', 'repealed_by': 'Act 9 of 2019'},
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


if __name__ == '__main__':
    unittest.main()
