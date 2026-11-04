"""law.py on small corpora built here, in a temporary folder: no submodule needs to be checked out.

  python -m unittest tests.test_law_fixtures -v

Each case is a way a real corpus records its law: older acts appended after newer ones, corrections laid over past
dates, a publisher's starting text, court rulings and treaties, a list of acts without their text, laws not yet in
force on main, an unfinished or shallow checkout, a checkout at an older commit than the tree pins, and a pin that
moves forward (the index on disk grows by the new commits only).
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
        self.assertTrue((store / 'ff~national~acts.index').exists())


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


if __name__ == '__main__':
    unittest.main()
