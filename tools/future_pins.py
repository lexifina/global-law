#!/usr/bin/env python3
"""Write data/future-pins.tsv: for each pinned corpus with a future branch, the branch tip that tools/law.py may read
beside the pinned main commit. Standard library only.

Many corpora keep laws whose in-force day is still to come on a branch of their own (future, zukunft, futuro, ...),
not on main. tools/law.py reads main at the pin, plus the commits pin..future_sha when this file has a row for the
corpus, so a law becomes readable on its in-force day without any corpus repo being changed or repinned.

  python tools/future_pins.py                                   every pinned corpus, pins from HEAD
  python tools/future_pins.py --today 2026-11-04 --report r.json
  python tools/future_pins.py --pins fresh-pins.tsv             pins from a tsv (path<TAB>sha) instead of the tree
  python tools/future_pins.py --only sweden/national/acts --out -
  python tools/future_pins.py --print-tags                      the tag pushes that would protect the recorded shas

It is meant to be run by the repoint loop, before it commits, so that the gitlinks and the future pins move together
in the same root commit and a reading stays reproducible.

For every pinned corpus it asks the remote for its branches (git ls-remote), and for each corpus with a future branch
fetches main and that branch without blobs into a bare clone kept in the tree's git folder
(global-law-cache/future-clones/<path with / as ~>.git), shared and reused across runs. Each is then classed:

  linear    the future tip descends from the pinned main commit
  forked    it does not, but every law commit of main after the fork, up to the pin, is held on the branch (same
            author line with its raw date, same message), and every main commit there that is not held on it only
            changes documentation: it deletes no file and touches no file the branch's own commits touch
  behind    neither: the branch has not caught up with the pin (or main moved or withdrew files the branch's own
            commits rely on); law.py then reads main alone
  unrelated, pin-missing, no-future-branch, ls-remote-failed, fetch-failed

Only linear and forked corpora get a row. future_own counts the branch's own commits (not replays of main), and due
those whose In-force trailer is on or before --today.

A recorded future sha must stay reachable, because full rebuilds rewrite future branches: protect it with a tag
refs/tags/global-law/future-pinned-<sha> on the corpus repo (--print-tags lists them). This script never pushes or
writes to any remote.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FUTURE_NAMES = ('future', 'zukunft', 'futuro', 'futur', 'fremtidig', 'mellon', 'mishiko', 'avenir', 'framtid',
                'toekomst', 'e-ardhme', 'badeshte')
LOCAL_BRANCH = 'future-branch'
HEADER = '# corpus\tbranch\tfuture_sha\tmain_pin'
RECORDED = ('linear', 'forked')


def run(args: list[str], cwd: Path | str | None = None, timeout: float | None = None) -> subprocess.CompletedProcess:
    """A git command that never prompts (the repoint loop runs it with no console); one that runs past `timeout`
    seconds counts as failed (exit 124)."""
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'}
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, b'', b'timed out')


def git(*args: str, cwd: Path | str = ROOT, check: bool = True) -> str:
    done = run(['git', *args], cwd)
    if check and done.returncode:
        raise RuntimeError(f"git {' '.join(args[:4])}: {done.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return done.stdout.decode('utf-8', 'replace')


def ok(*args: str, cwd: Path | str) -> bool:
    return run(['git', *args], cwd).returncode == 0


# ---- inputs -------------------------------------------------------------------------------------------------------

def read_pins(tree_ref: str, pins_tsv: str | None) -> dict[str, str]:
    if pins_tsv:
        pins = {}
        for line in Path(pins_tsv).read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.startswith('#'):
                path, sha = line.split('\t')[:2]
                pins[path.strip()] = sha.strip()
        return pins
    pins = {}
    for line in git('ls-tree', '-r', '-d', tree_ref).splitlines():
        meta, path = line.split('\t', 1)
        mode, kind, sha = meta.split()
        if mode == '160000' and kind == 'commit':
            pins[path] = sha
    return pins


def read_urls(tree_ref: str) -> dict[str, str]:
    """path -> url, from .gitmodules at the tree ref (falling back to the working file)."""
    paths, urls = {}, {}
    done = subprocess.run(['git', 'config', '--blob', f'{tree_ref}:.gitmodules', '--get-regexp',
                           r'^submodule\..*\.(path|url)$'], cwd=ROOT, capture_output=True)
    if done.returncode:
        done = subprocess.run(['git', 'config', '-f', '.gitmodules', '--get-regexp', r'^submodule\..*\.(path|url)$'],
                              cwd=ROOT, capture_output=True)
    for line in done.stdout.decode('utf-8', 'replace').splitlines():
        key, _, value = line.partition(' ')
        name, _, field = key[len('submodule.'):].rpartition('.')
        (paths if field == 'path' else urls)[name] = value.strip()
    return {paths.get(name, name): url for name, url in urls.items()}


def manifest_branches() -> dict[str, str]:
    try:
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    out = {}

    def walk(node):
        if isinstance(node, dict):
            if node.get('path') and node.get('future_branch'):
                out[node['path']] = node['future_branch']
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)
    return out


# ---- network ------------------------------------------------------------------------------------------------------

def ls_remote(url: str) -> list[str] | None:
    for _ in range(2):
        done = run(['git', 'ls-remote', '--heads', url], timeout=45)
        if done.returncode == 0:
            return [line.split('\trefs/heads/', 1)[1] for line in done.stdout.decode().splitlines() if '\t' in line]
    return None


def pick_branch(heads: list[str], preferred: str | None) -> str | None:
    if preferred and preferred in heads:
        return preferred
    for name in FUTURE_NAMES:
        if name in heads:
            return name
    return None


def fetch(repo: Path, url: str, branch: str, pin: str) -> str | None:
    """Fetch main and the branch blob-less into the bare clone; make sure the pin is there. Returns an error state."""
    if not (repo / 'HEAD').exists():
        repo.mkdir(parents=True, exist_ok=True)
        git('init', '--bare', '-q', str(repo), cwd=repo)
    refspecs = ['+refs/heads/main:refs/heads/main', f'+refs/heads/{branch}:refs/heads/{LOCAL_BRANCH}']
    done = None
    for _ in range(2):
        done = run(['git', 'fetch', '-q', '--filter=blob:none', '--no-tags', url, *refspecs], repo, timeout=300)
        if done.returncode == 0:
            break
    if done.returncode:
        return 'fetch-failed'
    if not ok('cat-file', '-e', pin + '^{commit}', cwd=repo):
        run(['git', 'fetch', '-q', '--filter=blob:none', '--no-tags', url, pin], repo, timeout=300)
        if not ok('cat-file', '-e', pin + '^{commit}', cwd=repo):
            return 'pin-missing'
    return None


# ---- classification -----------------------------------------------------------------------------------------------

def commits(repo: Path, *rng: str) -> dict[str, dict]:
    raw = git('log', '--first-parent', '--date=raw',
              '--format=%x1d%H%x1f%an <%ae> %ad%x1f%(trailers:key=Kind,valueonly,separator=)'
              '%x1f%(trailers:key=In-force,valueonly,separator=)%x1f%B', *rng, cwd=repo)
    out = {}
    for chunk in raw.split('\x1d')[1:]:
        sha, author, kind, in_force, body = chunk.split('\x1f', 4)
        out[sha] = {'key': (author, body.strip()), 'kind': kind.strip(), 'in_force': in_force.strip()[:10],
                    'law': not author.startswith('Lexifina <') or kind.strip() == 'correction'}
    return out


def changes(repo: Path, sha: str) -> list[tuple[str, str]]:
    """(status, path) of a commit against its first parent."""
    out = git('diff-tree', '-r', '-m', '--first-parent', '--no-renames', '--no-commit-id', '--name-status', '--root',
              sha, cwd=repo)
    rows = []
    for line in out.splitlines():
        status, _, path = line.partition('\t')
        if path:
            rows.append((status[:1], path))
    return rows


def classify(repo: Path, pin: str, fut: str, today: str) -> dict:
    linear = ok('merge-base', '--is-ancestor', pin, fut, cwd=repo)
    fork = git('merge-base', pin, fut, cwd=repo, check=False).strip()
    if not fork:
        return {'state': 'unrelated', 'reason': 'no merge base between the pin and the branch'}
    main_after = commits(repo, pin, f'^{fork}')
    main_law = {c['key'] for c in main_after.values() if c['law']}
    fut_rows = commits(repo, fut, f'^{pin}')
    held = {c['key'] for c in fut_rows.values()}
    main_keys = {c['key'] for c in main_after.values()}
    own = {s: c for s, c in fut_rows.items() if c['key'] not in main_keys}
    due = sum(1 for c in own.values() if re.fullmatch(r'\d{4}-\d{2}-\d{2}', c['in_force']) and c['in_force'] <= today)
    result = {'future_own': len(own), 'due': due}
    if linear:
        return {'state': 'linear', 'reason': '', **result}
    missing = main_law - held
    if missing:
        return {'state': 'behind', 'reason': f'{len(missing)} law commit(s) of main after the fork not on the branch',
                **result}
    own_paths: set[str] = set()
    for sha in own:
        own_paths.update(path for _, path in changes(repo, sha))
    bad = []
    for sha, c in main_after.items():
        if c['key'] in held:
            continue
        rows = changes(repo, sha)
        deleted = [p for s, p in rows if s == 'D']
        overlap = [p for _, p in rows if p in own_paths]
        if deleted or overlap:
            bad.append(f"{sha[:10]} ({len(deleted)} deleted, {len(overlap)} touched by the branch's own commits"
                       f"{': ' + ', '.join((deleted + overlap)[:3]) if deleted or overlap else ''})")
    if bad:
        return {'state': 'behind', 'reason': 'docs commit(s) of main not on the branch delete or overlap: '
                + '; '.join(bad[:5]) + (f' (+{len(bad) - 5} more)' if len(bad) > 5 else ''), **result}
    return {'state': 'forked', 'reason': '', **result}


def work(path: str, url: str, branch: str, pin: str, cache: Path, today: str) -> dict:
    repo = cache / (path.replace('/', '~') + '.git')
    row = {'corpus': path, 'url': url, 'branch': branch, 'pin': pin, 'fut': None}
    try:
        error = fetch(repo, url, branch, pin)
        fut = git('rev-parse', f'refs/heads/{LOCAL_BRANCH}', cwd=repo, check=False).strip() or None
        row['fut'] = fut
        if error:
            return {**row, 'state': error, 'reason': ''}
        return {**row, **classify(repo, pin, fut, today)}
    except Exception as exc:  # noqa: BLE001 - one corpus failing must not stop the run
        return {**row, 'state': 'error', 'reason': str(exc)[:300]}


# ---- main ---------------------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--cache', help='folder of bare clones (default: <git dir>/global-law-cache/future-clones)')
    ap.add_argument('--jobs', type=int, default=16)
    ap.add_argument('--today', default=dt.date.today().isoformat())
    ap.add_argument('--only', nargs='+', metavar='PATH', help='only these corpora (rows of others are dropped)')
    ap.add_argument('--out', default='data/future-pins.tsv', help="tsv to write, relative to the tree; '-' = stdout")
    ap.add_argument('--report', help='write every corpus checked, with its state, as JSON')
    ap.add_argument('--pins', help='tsv path<TAB>sha to use instead of the tree gitlinks')
    ap.add_argument('--tree-ref', default='HEAD', help='tree revision to read gitlinks and .gitmodules from')
    ap.add_argument('--print-tags', action='store_true',
                    help='print "<url> <future_sha> refs/tags/global-law/future-pinned-<future_sha>" per recorded row')
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding='utf-8')

    cache = Path(a.cache) if a.cache else \
        (ROOT / git('rev-parse', '--git-path', 'global-law-cache').strip()).resolve() / 'future-clones'
    cache.mkdir(parents=True, exist_ok=True)
    pins = read_pins(a.tree_ref, a.pins)
    urls = read_urls(a.tree_ref)
    preferred = manifest_branches()
    if a.only:
        pins = {p: s for p, s in pins.items() if p in set(a.only)}

    report: list[dict] = []
    todo = []
    with ThreadPoolExecutor(a.jobs) as pool:
        listed = dict(zip(pins, pool.map(lambda p: ls_remote(urls[p]) if p in urls else None, pins)))
    for path, pin in sorted(pins.items()):
        heads = listed[path]
        if path not in urls:
            report.append({'corpus': path, 'pin': pin, 'state': 'no-url', 'reason': 'not in .gitmodules'})
        elif heads is None:
            report.append({'corpus': path, 'url': urls[path], 'pin': pin, 'state': 'ls-remote-failed', 'reason': ''})
        elif (branch := pick_branch(heads, preferred.get(path))) is None:
            report.append({'corpus': path, 'url': urls[path], 'pin': pin, 'state': 'no-future-branch',
                           'reason': f"manifest names {preferred[path]!r}, not on the remote"
                           if path in preferred else ''})
        else:
            todo.append((path, urls[path], branch, pin))
    with ThreadPoolExecutor(a.jobs) as pool:
        report += list(pool.map(lambda t: work(*t, cache, a.today), todo))
    report.sort(key=lambda r: r['corpus'])

    rows = [r for r in report if r['state'] in RECORDED]
    tsv = HEADER + '\n' + ''.join(f"{r['corpus']}\t{r['branch']}\t{r['fut']}\t{r['pin']}\n" for r in rows)
    if a.out == '-':
        sys.stdout.write(tsv)
    else:
        out = ROOT / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(tsv.encode('utf-8'))
    if a.print_tags:
        for r in rows:
            print(f"{r['url']} {r['fut']} refs/tags/global-law/future-pinned-{r['fut']}")
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8',
                                  newline='\n')

    counts: dict[str, int] = {}
    for r in report:
        counts[r['state']] = counts.get(r['state'], 0) + 1
    notable = [r for r in report if r.get('due') or (r['state'] not in RECORDED and r['state'] != 'no-future-branch')]
    summary = {
        'today': a.today,
        'pinned': len(pins),
        'states': dict(sorted(counts.items())),
        'recorded': len(rows),
        'corpora_with_due': sum(1 for r in report if r.get('due')),
        'due_total': sum(r.get('due', 0) for r in report),
        'due_visible': sum(r.get('due', 0) for r in rows),
        'corpora': [{k: r.get(k) for k in ('corpus', 'branch', 'state', 'future_own', 'due', 'reason')}
                    for r in notable],
    }
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
