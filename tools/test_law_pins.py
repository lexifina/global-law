"""Tests for tools/law.py on a small tree built in a temporary directory. Run: python tools/test_law_pins.py"""

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


class MissingPins(unittest.TestCase):
    """A corpus whose history was rewritten after the tree was built: its documentation commit has a new id, and the
    tree still pins the old one, which the corpus no longer holds (lexifina/global-law#2)."""

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        root = Path(self.dir.name)
        corpus = root / CORPUS
        corpus.mkdir(parents=True)
        run(root, 'init', '-q')
        run(corpus, 'init', '-q')
        (corpus / 'art-1.md').write_text('Article 1, as enacted.\n')
        run(corpus, 'add', '.')
        enacted = commit(corpus, 'Law 1/2020\n\nIn-force: 2020-01-01')
        (corpus / 'art-1.md').write_text('Article 1, as amended.\n')
        run(corpus, 'add', '.')
        amended = commit(corpus, 'Law 2/2021\n\nIn-force: 2021-01-01', 'Law 2/2021')
        (corpus / 'README.md').write_text('About this corpus.\n')
        run(corpus, 'add', '.')
        documented = commit(corpus, 'Documentation\n\nKind: documentation', 'Lexifina')
        (root / 'manifest.json').write_text(
            json.dumps({'corpora': [{'path': CORPUS, 'in_force_trailer': 'In-force'}]})
        )
        run(root, 'add', 'manifest.json')
        self.pins = {}
        for sha, law_name, in_force, kind in (
            (enacted, 'Law 1/2020', '2020-01-01', 'law'),
            (amended, 'Law 2/2021', '2021-01-01', 'law'),
            (documented, 'Lexifina', '2022-01-01', 'documentation'),
        ):
            run(root, 'update-index', '--add', '--cacheinfo', f'160000,{sha},{CORPUS}')
            commit(
                root,
                f'{law_name}\n\nCorpus: {CORPUS}\nCorpus-commit: {sha}\nLaw: {law_name}\nIn-force: {in_force}\n'
                f'Kind: {kind}',
            )
            self.pins[in_force] = sha
        self.root, self.corpus = root, corpus
        # law.git's cwd defaults to ROOT as it was at import, so both are pointed here.
        self.saved = law.ROOT, dict(law.git.__kwdefaults__)
        law.ROOT, law.git.__kwdefaults__ = root, {'cwd': root, 'check': True}
        law._CACHE.clear()

    def tearDown(self) -> None:
        law.ROOT, law.git.__kwdefaults__ = self.saved
        law._CACHE.clear()
        self.dir.cleanup()

    def forget(self, sha: str) -> None:
        """Rewrite the corpus so `sha` is gone, as a history cleaning does."""
        run(self.corpus, 'reset', '-q', '--hard', f'{sha}~1')
        if sha == self.pins['2022-01-01']:
            (self.corpus / 'README.md').write_text('About this corpus, rewritten.\n')
            run(self.corpus, 'add', '.')
            commit(self.corpus, 'Documentation\n\nKind: documentation', 'Lexifina')
        run(self.corpus, 'reflog', 'expire', '--expire=now', '--all')
        run(self.corpus, 'gc', '-q', '--prune=now')
        law._CACHE.clear()
        self.assertNotEqual(
            subprocess.run(
                ['git', 'cat-file', '-e', sha], cwd=self.corpus, capture_output=True
            ).returncode,
            0,
        )

    def test_a_held_pin_reads_as_before(self) -> None:
        self.assertEqual(
            law.text_on('2022-06-01', f'{CORPUS}/art-1.md'), 'Article 1, as amended.\n'
        )
        self.assertEqual(
            law.text_on('2020-06-01', f'{CORPUS}/art-1.md'), 'Article 1, as enacted.\n'
        )

    def test_a_missing_documentation_pin_reads_through_the_last_held_one(self) -> None:
        self.forget(self.pins['2022-01-01'])
        self.assertEqual(
            law.text_on('2022-06-01', f'{CORPUS}/art-1.md'), 'Article 1, as amended.\n'
        )
        self.assertEqual(
            law.diff_between('2021-06-01', '2022-06-01', f'{CORPUS}/art-1.md'), ''
        )

    def test_a_missing_law_pin_stops_the_read(self) -> None:
        self.forget(self.pins['2021-01-01'])
        with self.assertRaises(SystemExit) as stop:
            law.text_on('2021-06-01', f'{CORPUS}/art-1.md')
        self.assertIn('Law 2/2021', str(stop.exception.code))


if __name__ == '__main__':
    unittest.main()
