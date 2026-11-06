"""tools/describe.py's description of a corpus with no corpus.json, from the files its build publishes, read here from
a dictionary instead of GitHub.

  python -m unittest tests.test_describe -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE / 'tools'))
try:
    import describe
finally:
    del sys.path[0]

COMMITS = ('day,kind,law,acts,files,branch\n'
           '2015-03-10,start,,perda-2015-001-prasarana,39,main\n'
           '2016-12-05,start,,perda-2016-012-retribusi,5,main\n')
README = ('# Lamongan\n\n**Each Perda as enacted, not yet a history of amendments.** JDIH publishes each Perda as its '
          'signed copy; there is no consolidated text. ... its amendments are not applied to the Perda it amends, and '
          'a repeal is not applied.\n')


class HistoryDerivation(unittest.TestCase):
    """Audit row 79: the Indonesian builder writes each Perda as enacted as the publisher's starting text (Kind:
    publisher, commits.csv kind start, no law), which the rows alone read as current text only. A history the corpus
    declares in data/repo.json is kept as declared; undeclared, the README's as-enacted statement decides."""

    def describe_with(self, files: dict[str, str]) -> dict:
        saved = describe.fetch_text, describe.remote_heads
        describe.fetch_text = lambda repo, sha, name: files.get(name, '')
        describe.remote_heads = lambda repo: set()
        try:
            return describe.describe('indonesia/east-java/lamongan-regency/acts', 'a' * 40, 'lexifina/x')[0]
        finally:
            describe.fetch_text, describe.remote_heads = saved

    def test_declared_history_is_kept(self):
        repo = {'country': 'ID-JI-LAMONGAN', 'name': 'Lamongan', 'publisher': 'JDIH', 'history': 'as-enacted'}
        entry = self.describe_with({'data/repo.json': json.dumps(repo), 'data/commits.csv': COMMITS})
        self.assertEqual(entry['history'], 'as-enacted')
        self.assertNotIn('history', entry['derived'])
        self.assertIn('each act as enacted, later changes not applied', entry['coverage'])
        # Declared over what the rows alone would say, whatever the README says.
        repo['history'] = 'current-only'
        entry = self.describe_with({'data/repo.json': json.dumps(repo), 'data/commits.csv': COMMITS, 'README.md': README})
        self.assertEqual(entry['history'], 'current-only')

    def test_readme_as_enacted_over_publisher_rows(self):
        repo = {'country': 'ID-JI-LAMONGAN', 'name': 'Lamongan', 'publisher': 'JDIH'}
        entry = self.describe_with({'data/repo.json': json.dumps(repo), 'data/commits.csv': COMMITS, 'README.md': README})
        self.assertEqual(entry['history'], 'as-enacted')
        self.assertIn('history', entry['derived'])
        entry = self.describe_with({'data/repo.json': json.dumps(repo), 'data/commits.csv': COMMITS})
        self.assertEqual(entry['history'], 'current-only')  # nothing says otherwise
        # An act with several versions is in force, whatever the README says.
        several = COMMITS + '2018-01-01,law,Perda 2/2018,perda-2016-012-retribusi,5,main\n'
        entry = self.describe_with({'data/repo.json': json.dumps(repo), 'data/commits.csv': several, 'README.md': README})
        self.assertEqual(entry['history'], 'in-force')


if __name__ == '__main__':
    unittest.main()
