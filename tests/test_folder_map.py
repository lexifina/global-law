"""The folder map (mcp_server.folder_map_build) on a small corpus built here: every folder's commits as git log lists
them, the map extended when the pin moves, and folder_commits reading it.

  python -m unittest tests.test_folder_map -v
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAW = 'fixtureland/national/acts'
PROBE = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server as m\n'
         'law = m.law\n'
         'corpus = sys.argv[1]\n'
         'did = m.folder_map_build(corpus)\n'
         'again = m.folder_map_build(corpus)\n'
         'tip, cwd = law.reachable_tip(corpus), law.corpus_dir(corpus)\n'
         'out = {}\n'
         'for f in json.loads(sys.stdin.read()):\n'
         '    out[f] = {"map": m.folder_map_commits(corpus, f, tip), "git": law.git("log", "--format=%H", tip, "--", f, cwd=cwd).split(),\n'
         '              "asked": m.folder_commits(corpus, f)}\n'
         'print(json.dumps({"did": did, "again": again, "folders": out, "file": m._folder_map_file(corpus).name}))\n')
FOLDERS = ['act-a', 'act-a/part-1', 'act-b', 'act-b/schedule', 'act-c', 'gone', 'never']


class FolderMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        shutil.copy(ROOT / 'tools' / 'mcp_server.py', t.root / 'tools' / 'mcp_server.py')
        if (ROOT / 'tools' / 'usc_cite.py').exists():
            shutil.copy(ROOT / 'tools' / 'usc_cite.py', t.root / 'tools' / 'usc_cite.py')
        (t.root / 'manifest.json').write_text(json.dumps({'corpora': [
            {'path': LAW, 'name': 'Acts', 'language': 'en', 'in_force_trailer': 'In-force', 'code': 'FX'}]}), encoding='utf-8')
        c = cls.c = t.corpus(LAW)
        c.commit('Act A', {'act-a/part-1/1.md': 'One.\n', 'act-a/part-1/2.md': 'Two.\n', 'act-a/title.md': '# Act A\n'},
                 In_force='2001-01-01', Kind='law')
        c.commit('Act B', {'act-b/1.md': 'One.\n', 'act-b/schedule/1.md': 'A schedule.\n', 'gone/1.md': 'Soon gone.\n'},
                 In_force='2002-02-02', Kind='law')
        c.commit('Act A (Amendment)', {'act-a/part-1/2.md': 'Two, amended.\n'}, In_force='2003-03-03', Kind='law')
        run('rm', '-q', 'gone/1.md', cwd=c.path)
        c.commit('Repeal', {'act-b/1.md': 'One, after the repeal.\n'}, In_force='2004-04-04', Kind='law')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def probe(self) -> dict:
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', PROBE, LAW], cwd=self.t.root, input=json.dumps(FOLDERS),
                              capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def check(self, got: dict) -> None:
        for folder, row in got['folders'].items():
            if not row['git']:  # no such folder (yet): the map has no row, and git is asked (and lists nothing)
                self.assertIsNone(row['map'], folder)
                self.assertEqual(row['asked'], [], folder)
                continue
            self.assertEqual(row['map'], row['git'], folder)
            self.assertEqual(row['asked'], row['git'], folder)
        self.assertEqual(got['folders']['never']['git'], [])

    def test_1_built_and_as_git_lists(self):
        """Every folder's commits, newest first, as `git log -- <folder>` prints them: a folder two levels down, one
        whose only file a later commit removed (both commits), and none for a folder that never was."""
        got = self.probe()
        self.assertEqual(got['did'], 'built')
        self.assertEqual(got['again'], 'current')
        self.check(got)
        self.assertEqual(len(got['folders']['gone']['map']), 2)
        self.assertEqual(len(got['folders']['act-a']['map']), 2)

    def test_2_extended_when_the_pin_moves(self):
        """A new commit at the tip: the map is extended by it alone, and lists it first."""
        before = self.probe()['folders']['act-c']['map']
        self.assertIsNone(before)
        new = self.c.commit('Act C', {'act-c/1.md': 'One.\n', 'act-a/part-1/3.md': 'Three.\n'}, In_force='2005-05-05', Kind='law')
        self.t.pin()
        got = self.probe()
        self.assertEqual(got['did'], 'extended')
        self.check(got)
        self.assertEqual(got['folders']['act-c']['map'], [new])
        self.assertEqual(got['folders']['act-a/part-1']['map'][0], new)
        self.assertEqual(len(got['folders']['act-a/part-1']['map']), 3)

    def test_3_built_again_for_a_history_that_is_not_its_continuation(self):
        """A map whose tip the corpus no longer holds as an ancestor (a rebuilt corpus) is built again, whole."""
        import sqlite3
        store = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'global-law-cache'], cwd=self.t.root,
                               capture_output=True, encoding='utf-8').stdout.strip()
        name = self.probe()['file']
        db = sqlite3.connect(str(Path(store) / name))
        db.execute("update meta set value = ? where key = 'tip'", ('0' * 40,))
        db.commit()
        db.close()
        got = self.probe()
        self.assertEqual(got['did'], 'built')
        self.check(got)


if __name__ == '__main__':
    unittest.main()
