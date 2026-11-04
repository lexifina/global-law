"""tools/verify.py on small trees built here, in a temporary folder: a shallow clone and its --depth 1 update,
`--since HEAD`, and a truncated checkpoint.

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

    def commit(self, pins: dict[str, str], gitmodules: dict[str, str] | None = None) -> str:
        """Set pins (path -> 40-hex commit) and write .gitmodules for gitmodules (default: every pin)."""
        self.pins.update(pins)
        entries = self.pins if gitmodules is None else gitmodules
        text = ''.join(f'[submodule "{p}"]\n\tpath = {p}\n\turl = https://example.org/{p.replace("/", "-")}\n'
                       for p in sorted(entries))
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
