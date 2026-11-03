#!/usr/bin/env python3
"""Check this tree's history the way it now grows: only forward. Standard library and git only.

  python tools/verify.py                     the last 200 commits on the first-parent line
  python tools/verify.py --since <commit>    every commit after <commit>
  python tools/verify.py --fetch             also check every pin against its repository (commits only are
                                             fetched, into .git/global-law-verify; a first run takes a while)

For every commit in the range:
  - every corpus pinned (gitlink) has its .gitmodules entry, and every entry its gitlink: a checkout of that commit
    with `git submodule update --init` then works;
  - no repository is pinned at two paths.
With --fetch, also:
  - every pin set in the range, and every pin at HEAD, is a commit its repository still holds (on any branch or tag);
  - every pin that moved, moved forward: the new commit descends from the old one.
Exits 1 if anything fails, and names it. This replaces a rebuild: since 2 November 2026 the tree is not rebuilt but
grows by fast-forward, one commit at a time (REPRODUCE.md).
"""
from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8', errors='replace')
    if check and done.returncode:
        raise SystemExit(f"git {' '.join(args[:3])}: {done.stderr.strip()[:300]}")
    return done.stdout


def state(commit: str) -> tuple[dict[str, str], dict[str, str]]:
    """(path -> pinned commit, path -> repository URL) at a commit of the tree."""
    links = {l.split('\t', 1)[1]: l.split()[2] for l in git('ls-tree', '-r', commit).splitlines()
             if l.split()[1] == 'commit'}
    names, urls = {}, {}
    for line in git('config', '--blob', f'{commit}:.gitmodules', '--get-regexp', r'^submodule\..*\.(path|url)$',
                    check=False).splitlines():
        key, _, value = line.partition(' ')
        (names if key.endswith('.path') else urls)[key.rsplit('.', 1)[0]] = value
    return links, {p: urls.get(n, '') for n, p in names.items()}


def main(argv: list[str]) -> int:
    fetch = '--fetch' in argv
    since = argv[argv.index('--since') + 1] if '--since' in argv else None
    revs = f'{since}..HEAD' if since else 'HEAD'
    dated = git('log', '--first-parent', '--reverse', '--format=%H %cs', *([revs] if since else ['-200', revs])).splitlines()
    day = dict(l.split() for l in dated if l.strip())
    commits = [l.split()[0] for l in dated if l.strip()]
    problems: list[str] = []
    moves: list[tuple[str, str, str, str]] = []  # (tree commit, url, old pin, new pin)
    prev_links, prev_urls = state(f'{commits[0]}^') if commits and git('rev-parse', '-q', '--verify', f'{commits[0]}^',
                                                                       check=False).strip() else ({}, {})
    for c in commits:
        links, urls = state(c)
        missing = sorted(set(links) - set(urls))
        extra = sorted(set(urls) - set(links))
        if missing:
            problems.append(f'{c[:10]}: {len(missing)} gitlink(s) with no .gitmodules entry, e.g. {missing[:3]}')
        if extra:
            problems.append(f'{c[:10]}: {len(extra)} .gitmodules entr(y/ies) with no gitlink, e.g. {extra[:3]}')
        twice = [u for u, n in Counter(urls.values()).items() if n > 1 and u]
        if twice:
            problems.append(f'{c[:10]}: repository pinned at two paths: {twice[:3]}')
        for path, sha in links.items():
            old = prev_links.get(path)
            if old and old != sha:
                moves.append((c, urls.get(path) or prev_urls.get(path, ''), old, sha))
        prev_links, prev_urls = links, urls
    print(f'{len(commits)} commit(s) checked for gitlinks and .gitmodules; {len(moves)} pin move(s) in the range')
    if fetch:
        head_links, head_urls = state('HEAD')
        store = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'global-law-verify').strip())
        store.mkdir(parents=True, exist_ok=True)
        wanted: dict[str, set[str]] = {}
        for _, url, old, new in moves:
            wanted.setdefault(url, set()).update((old, new))
        for path, sha in head_links.items():
            wanted.setdefault(head_urls.get(path, ''), set()).add(sha)
        reach: dict[str, set[str]] = {}
        for url in sorted(u for u in wanted if u):
            repo = store / (url.rstrip('/').removesuffix('.git').rsplit('/', 1)[-1] + '.git')
            if (repo / 'HEAD').exists():
                git('fetch', '-q', '--filter=tree:0', '--force', 'origin', '+refs/heads/*:refs/heads/*',
                    '+refs/tags/*:refs/tags/*', cwd=repo, check=False)
            else:
                git('clone', '-q', '--bare', '--filter=tree:0', url, str(repo), cwd=store, check=False)
            env_free = {**os.environ, 'GIT_NO_LAZY_FETCH': '1'}  # only what the repository's refs reach
            done = subprocess.run(['git', 'rev-list', '--all'], cwd=repo, capture_output=True, encoding='utf-8', env=env_free)
            reach[url] = set(done.stdout.split())
        for path, sha in head_links.items():
            url = head_urls.get(path, '')
            if sha not in reach.get(url, set()):
                problems.append(f'HEAD: {path} pins {sha[:10]}, which {url} no longer holds')
        for c, url, old, new in moves:
            held = reach.get(url, set())
            if new not in held:
                problems.append(f'{c[:10]}: pins {new[:10]} in {url}, which no longer holds it')
            elif old in held and subprocess.run(['git', 'merge-base', '--is-ancestor', old, new],
                                                cwd=store / (url.rstrip('/').removesuffix('.git').rsplit('/', 1)[-1] + '.git'),
                                                capture_output=True).returncode:
                problems.append(f'{c[:10]}: moved {url} from {old[:10]} to {new[:10]}, not forward')
        print(f'{len(reach)} repositories fetched; {len(head_links)} pins at HEAD checked')
    # A summary by kind and by day, then the first of each kind: old damage and new breakage read apart.
    kinds = Counter()
    by_day = Counter()
    first: dict[str, list[str]] = {}
    for p in problems:
        kind = ('pin at HEAD not held' if p.startswith('HEAD:') else 'pin no longer held' if 'no longer holds' in p
                else 'pin moved backward' if 'not forward' in p else 'gitlink without .gitmodules entry'
                if 'with no .gitmodules entry' in p else '.gitmodules entry without gitlink' if 'with no gitlink' in p
                else 'repository pinned twice')
        kinds[kind] += 1
        short = p.split(':', 1)[0].strip()
        by_day[(kind, next((d for c, d in day.items() if c.startswith(short)), ''))] += 1
        first.setdefault(kind, []).append(p)
    for kind, n in kinds.most_common():
        days = ', '.join(f'{d or "?"}: {c}' for (k, d), c in sorted(by_day.items()) if k == kind)
        print(f'{kind}: {n} ({days})')
        for p in first[kind][:5]:
            print('  FAIL', p)
    print('ok' if not problems else f'{len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
