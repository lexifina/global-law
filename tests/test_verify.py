"""tools/verify.py on small trees built here, in a temporary folder: a shallow clone and its --depth 1 update,
`--since HEAD`, a truncated checkpoint, and --remote against a local corpus with a pin listed in
tools/verify-known.tsv.

  python -m unittest tests.test_verify -v
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
VERIFY = HERE / 'tools' / 'verify.py'
ENV = {**os.environ, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t',
       'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@t'}


def git(*args, cwd):
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8', env=ENV)
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr}")
    return done.stdout.strip()


class Tree:
    """A tree repository whose commits pin corpora (gitlinks) with their .gitmodules entries."""

    def __init__(self, path: Path):
        self.path = path
        path.mkdir(parents=True)
        git('init', '-q', '-b', 'main', cwd=path)
        self.pins: dict[str, str] = {}
        self.url = lambda p: f'https://example.org/{p.replace("/", "-")}'

    def commit(self, pins: dict[str, str], gitmodules: dict[str, str] | None = None) -> str:
        """Set pins (path -> 40-hex commit) and write .gitmodules for gitmodules (default: every pin)."""
        self.pins.update(pins)
        entries = self.pins if gitmodules is None else gitmodules
        text = ''.join(f'[submodule "{p}"]\n\tpath = {p}\n\turl = {self.url(p)}\n' for p in sorted(entries))
        (self.path / '.gitmodules').write_text(text, encoding='utf-8', newline='\n')
        git('add', '.gitmodules', cwd=self.path)
        for p, sha in pins.items():
            git('update-index', '--add', '--cacheinfo', f'160000,{sha},{p}', cwd=self.path)
        git('commit', '-q', '-m', f'pin {sorted(pins)}', cwd=self.path)
        return git('rev-parse', 'HEAD', cwd=self.path)


def verify(repo: Path, *args: str) -> tuple[int, str]:
    """Run this checkout's verify.py as if it lived in repo/tools (it reads the tree it sits in)."""
    tools = repo / 'tools'
    tools.mkdir(exist_ok=True)
    shutil.copy(VERIFY, tools / 'verify.py')
    done = subprocess.run([sys.executable, str(tools / 'verify.py'), *args], cwd=repo, capture_output=True,
                          encoding='utf-8', env=ENV)
    return done.returncode, done.stdout + done.stderr


def marker(repo: Path) -> Path:
    return repo / '.git' / 'global-law-verify' / 'verified.json'


class VerifyCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='verify-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.tree = Tree(self.tmp / 'origin')
        for i in range(5):
            self.tree.commit({f'a/{i}': f'{i + 1:040x}'})

    def clone(self, *args: str) -> Path:
        dest = self.tmp / 'clone'
        git('clone', '-q', *args, (self.tmp / 'origin').as_uri(), str(dest), cwd=self.tmp)
        return dest


class Shallow(VerifyCase):
    def test_depth_one_says_what_it_checked_and_never_marks_root(self):
        repo = self.clone('--depth', '1')
        code, out = verify(repo)
        self.assertEqual(code, 0, out)
        first = git('rev-parse', 'HEAD', cwd=repo)
        self.assertIn(f'shallow clone: checked 1 commit(s) from {first[:10]}', out)
        self.assertIn('git fetch --unshallow', out)
        stamp = json.loads(marker(repo).read_text(encoding='utf-8'))['structure']
        self.assertNotEqual(stamp['from'], 'root')
        self.assertTrue(stamp.get('shallow'))
        code, out = verify(repo, '--full')
        self.assertIn('shallow clone: checked 1 commit(s)', out)
        self.assertNotIn('the whole history)', out)

    def test_depth_one_update_is_not_a_rewrite(self):
        repo = self.clone('--depth', '1')
        self.assertEqual(verify(repo)[0], 0)
        old = git('rev-parse', 'HEAD', cwd=repo)
        self.tree.commit({'b/1': f'{99:040x}'})
        self.tree.commit({'b/2': f'{98:040x}'})
        git('fetch', '-q', '--depth', '1', 'origin', 'main', cwd=repo)
        git('checkout', '-q', 'FETCH_HEAD', cwd=repo)
        git('reflog', 'expire', '--expire=now', '--all', cwd=repo)
        git('gc', '-q', '--prune=now', cwd=repo)
        code, out = verify(repo)
        self.assertEqual(code, 0, out)
        self.assertNotIn('tree history rewritten', out)
        self.assertIn(f'checkpoint commit {old[:10]}', out)
        self.assertIn('cannot be checked here', out)
        self.assertIn('shallow clone: checked 1 commit(s)', out)
        stamp = json.loads(marker(repo).read_text(encoding='utf-8'))['structure']
        self.assertEqual(stamp['commit'], git('rev-parse', 'HEAD', cwd=repo))
        self.assertNotEqual(stamp['from'], 'root')
        code, out = verify(repo, '--full')
        self.assertEqual(code, 0, out)

    def test_full_clone_still_reports_a_rewrite(self):
        repo = self.clone()
        self.assertEqual(verify(repo)[0], 0)
        git('reset', '-q', '--hard', 'HEAD~2', cwd=repo)
        (repo / 'x').write_text('x', encoding='utf-8')
        git('add', 'x', cwd=repo)
        git('commit', '-q', '-m', 'other', cwd=repo)
        code, out = verify(repo)
        self.assertEqual(code, 1, out)
        self.assertIn('tree history rewritten', out)

    def test_full_clone_is_unchanged(self):
        repo = self.clone()
        code, out = verify(repo)
        self.assertEqual(code, 0, out)
        self.assertIn('5 commit(s) checked', out)
        self.assertNotIn('shallow', out)
        self.assertEqual(json.loads(marker(repo).read_text(encoding='utf-8'))['structure']['from'], 'root')


class Checkpoint(VerifyCase):
    def test_since_head_checks_nothing_and_writes_nothing(self):
        # HEAD pins a corpus with no .gitmodules entry: a real check fails it.
        self.tree.commit({'x/y/z': f'{7:040x}'}, gitmodules={p: '' for p in self.tree.pins if p != 'x/y/z'})
        repo = self.clone()
        code, out = verify(repo, '--since', 'HEAD')
        self.assertIn('0 commit(s) checked', out)
        self.assertIn('checkpoint is left as it was', out)
        self.assertFalse(marker(repo).exists())
        code, out = verify(repo)
        self.assertEqual(code, 1, out)
        self.assertIn('gitlink(s) with no .gitmodules entry', out)

    def test_since_head_does_not_advance_an_older_checkpoint(self):
        repo = self.clone()
        self.assertEqual(verify(repo)[0], 0)
        before = marker(repo).read_text(encoding='utf-8')
        self.tree.commit({'c/1': f'{55:040x}'})
        git('pull', '-q', '--ff-only', cwd=repo)
        verify(repo, '--since', 'HEAD')
        self.assertEqual(marker(repo).read_text(encoding='utf-8'), before)

    def test_since_head_at_the_checkpoint_may_rewrite_it(self):
        repo = self.clone()
        self.assertEqual(verify(repo)[0], 0)
        code, out = verify(repo, '--since', 'HEAD')
        self.assertEqual(code, 0, out)
        self.assertNotIn('left as it was', out)

    def test_since_inside_the_range_does_not_skip_the_gap(self):
        # Audit row 58: a clean run at A, then a commit pinning x/y/z with no .gitmodules entry, a commit adding the
        # entry, and one more. --since HEAD~1 reads only the last commit: it must not move the checkpoint past the
        # broken commit, so the next default run still reads from A and names it.
        repo = self.clone()
        self.assertEqual(verify(repo)[0], 0)
        before = marker(repo).read_text(encoding='utf-8')
        broken = self.tree.commit({'x/y/z': f'{7:040x}'}, gitmodules={p: '' for p in self.tree.pins if p != 'x/y/z'})
        self.tree.commit({})  # the entry added: .gitmodules lists every pin again
        self.tree.commit({'c/1': f'{55:040x}'})
        git('pull', '-q', '--ff-only', cwd=repo)
        code, out = verify(repo, '--since', 'HEAD~1')
        self.assertEqual(code, 0, out)
        self.assertIn('left as it was', out)
        self.assertEqual(marker(repo).read_text(encoding='utf-8'), before)
        code, out = verify(repo)
        self.assertEqual(code, 1, out)
        self.assertIn(f'{broken[:10]}: 1 gitlink(s) with no .gitmodules entry', out)

    def test_since_the_checkpoint_or_before_it_moves_it(self):
        repo = self.clone()
        self.assertEqual(verify(repo)[0], 0)
        at = json.loads(marker(repo).read_text(encoding='utf-8'))['structure']['commit']
        for since in (at, f'{at}~2'):
            self.tree.commit({f'c/{since[-2:]}': f'{56:040x}'})
            git('pull', '-q', '--ff-only', cwd=repo)
            code, out = verify(repo, '--since', since)
            self.assertEqual(code, 0, out)
            self.assertNotIn('left as it was', out)
            self.assertEqual(json.loads(marker(repo).read_text(encoding='utf-8'))['structure']['commit'],
                             git('rev-parse', 'HEAD', cwd=repo))
            at = git('rev-parse', 'HEAD', cwd=repo)

    def test_truncated_checkpoint_is_absent(self):
        repo = self.clone()
        self.assertEqual(verify(repo)[0], 0)
        text = marker(repo).read_text(encoding='utf-8')
        for bad in (text[:30], '[]', '{"structure": 3}', ''):
            marker(repo).write_text(bad, encoding='utf-8')
            code, out = verify(repo)
            self.assertEqual(code, 0, out)
            self.assertNotIn('Traceback', out)
            self.assertIn('could not be read', out)
            self.assertIn('5 commit(s) checked', out)
            json.loads(marker(repo).read_text(encoding='utf-8'))  # replaced by a clean run's checkpoint


if __name__ == '__main__':
    unittest.main()


class KnownUnheld(unittest.TestCase):
    """--remote fails a pin set in the range that its corpus's main does not hold, unless tools/verify-known.tsv
    lists that tree commit and corpus commit; a listing never covers another pair."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='verify-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        corpus = self.tmp / 'corpus'
        corpus.mkdir()
        git('init', '-q', '-b', 'main', cwd=corpus)
        sha = {}
        for name in ('c1', 'c2'):
            (corpus / 'f').write_text(name, encoding='utf-8')
            git('add', 'f', cwd=corpus)
            git('commit', '-q', '-m', name, cwd=corpus)
            sha[name] = git('rev-parse', 'HEAD', cwd=corpus)
        git('checkout', '-q', '-b', 'side', sha['c1'], cwd=corpus)
        (corpus / 'f').write_text('o1', encoding='utf-8')
        git('commit', '-q', '-am', 'o1', cwd=corpus)
        sha['o1'] = git('rev-parse', 'HEAD', cwd=corpus)
        git('checkout', '-q', 'main', cwd=corpus)
        self.sha = sha
        self.tree = Tree(self.tmp / 'tree')
        self.tree.url = lambda p: corpus.as_uri()
        self.tree.commit({'k/acts': sha['c1']})
        self.orphan_at = self.tree.commit({'k/acts': sha['o1']})  # o1 is on no main
        self.tree.commit({'k/acts': sha['c2']})

    def known(self, *rows: tuple[str, str, str]) -> None:
        tools = self.tree.path / 'tools'
        tools.mkdir(exist_ok=True)
        text = '# test\n' + ''.join(f'{c}\tk/acts\t{s}\t{why}\n' for c, s, why in rows)
        (tools / 'verify-known.tsv').write_text(text, encoding='utf-8', newline='\n')

    def run_remote(self) -> tuple[int, str]:
        return verify(self.tree.path, '--full', '--remote', '--no-checkpoint')

    def test_unlisted_pin_fails(self):
        code, out = self.run_remote()
        self.assertEqual(code, 1, out)
        self.assertIn(f'{self.orphan_at[:10]}: pins {self.sha["o1"][:10]}', out)
        self.assertIn('no longer holds it on main', out)

    def test_listed_pin_is_known_not_failed(self):
        self.known((self.orphan_at, self.sha['o1'], 'replaced the same day'))
        code, out = self.run_remote()
        self.assertEqual(code, 0, out)
        self.assertIn('known: 1 pin(s)', out)
        self.assertIn(f'known {self.orphan_at[:10]}: k/acts pins {self.sha["o1"][:10]}: replaced the same day', out)

    def test_a_listing_covers_only_its_own_pair(self):
        head = git('rev-parse', 'HEAD', cwd=self.tree.path)
        self.known((head, self.sha['o1'], 'wrong tree commit'), (self.orphan_at[:10], self.sha['o1'], 'short hash'))
        code, out = self.run_remote()
        self.assertEqual(code, 1, out)
        self.assertNotIn('known:', out)
