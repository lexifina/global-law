"""Tests for tools/law.py on a small tree built in a temporary directory. Run: python tools/test_law_shallow.py"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import law  # noqa: E402

CORPUS = 'atlantis/national/acts'


def run(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ['git', *args], cwd=cwd, check=True, capture_output=True, encoding='utf-8'
    ).stdout.strip()


def commit(cwd: Path, message: str, author: str = 'Law 1/2020') -> str:
    run(
        cwd,
        '-c',
        f'user.name={author}',
        '-c',
        'user.email=law@example.org',
        'commit',
        '-q',
        '--allow-empty',
        '-m',
        message,
    )
    return run(cwd, 'rev-parse', 'HEAD')


class ShallowClones(unittest.TestCase):
    """A shallow clone answers dated reads wrongly instead of failing (lexifina/global-law#3), so it stops the read."""

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        base = Path(self.dir.name)
        source = base / 'source'
        source.mkdir()
        run(source, 'init', '-q')
        pins = []
        for n, in_force in ((1, '2020-01-01'), (2, '2021-01-01')):
            (source / 'art-1.md').write_text(f'Article 1, version {n}.\n')
            run(source, 'add', '.')
            pins.append((commit(source, f'Law {n}\n\nIn-force: {in_force}', f'Law {n}'), in_force))
        root = base / 'tree'
        root.mkdir()
        run(root, 'init', '-q')
        (root / 'manifest.json').write_text(json.dumps({'corpora': [{'path': CORPUS, 'in_force_trailer': 'In-force'}]}))
        run(root, 'add', 'manifest.json')
        for n, (sha, in_force) in enumerate(pins, 1):
            run(root, 'update-index', '--add', '--cacheinfo', f'160000,{sha},{CORPUS}')
            commit(root, f'Law {n}\n\nCorpus: {CORPUS}\nCorpus-commit: {sha}\nLaw: Law {n}\nIn-force: {in_force}')
        self.base, self.source, self.root = base, source, root
        self.saved = law.ROOT, dict(law.git.__kwdefaults__)

    def use(self, root: Path, corpus_depth: int | None) -> None:
        """Point law.py at `root`, with the corpus cloned in full or to `corpus_depth` commits."""
        args = ['clone', '-q'] + (['--depth', str(corpus_depth)] if corpus_depth else []) + [f'file://{self.source}', CORPUS]
        run(root, *args)
        # law.git's cwd defaults to ROOT as it was at import, so both are pointed here.
        law.ROOT, law.git.__kwdefaults__ = root, {'cwd': root, 'check': True}
        law._CACHE.clear()

    def tearDown(self) -> None:
        law.ROOT, law.git.__kwdefaults__ = self.saved
        law._CACHE.clear()
        self.dir.cleanup()

    def test_full_clones_read_every_date(self) -> None:
        self.use(self.root, None)
        self.assertEqual(law.text_on('2020-06-01', f'{CORPUS}/art-1.md'), 'Article 1, version 1.\n')
        self.assertEqual(law.text_on('2021-06-01', f'{CORPUS}/art-1.md'), 'Article 1, version 2.\n')

    def test_a_shallow_corpus_stops_the_read(self) -> None:
        self.use(self.root, 1)
        with self.assertRaises(SystemExit) as stop:
            law.text_on('2020-06-01', f'{CORPUS}/art-1.md')
        self.assertIn('shallow', str(stop.exception.code))
        self.assertIn(f'git -C {CORPUS} fetch --unshallow', str(stop.exception.code))

    def test_a_shallow_tree_stops_the_read(self) -> None:
        tree = self.base / 'shallow-tree'
        run(self.base, 'clone', '-q', '--depth', '1', f'file://{self.root}', str(tree))
        self.use(tree, None)
        with self.assertRaises(SystemExit) as stop:
            law.text_on('2020-06-01', f'{CORPUS}/art-1.md')
        self.assertIn('the tree is a shallow clone', str(stop.exception.code))


if __name__ == '__main__':
    unittest.main()
