#!/usr/bin/env python3
"""Check this tree's history the way it now grows: only forward. Standard library and git only.

  python tools/verify.py                     every commit since this clone's last clean check (its checkpoint), or the
                                             last 200 commits on the first-parent line if there is none
  python tools/verify.py --since <commit>    every commit after <commit>
  python tools/verify.py --full              every commit in the history (about 20 s for 340,000 commits)
  python tools/verify.py --remote            also check every pin against its repository's published main. Only
                                             commits are fetched, every repository into one store
                                             (.git/global-law-verify/store.git), --jobs at a time; a first run takes
                                             a few minutes, later runs fetch only what is new. --fetch is the old name.
  python tools/verify.py --remote --github-heads
                                             ask GitHub's API for every main first (8 queries; needs `gh`), and
                                             fetch only the repositories whose main moved since the store last did
  python tools/verify.py --no-checkpoint     neither read nor write the checkpoint

For every commit in the range (one `git log` over the range; each commit's change is read, not its whole tree):
  - every corpus pinned (gitlink) has its .gitmodules entry, and every entry its gitlink: a checkout of that commit
    with `git submodule update --init` then works;
  - no repository is pinned at two paths;
  - the checkpoint commit, if there is one, is still in this history: the tree itself was not rewritten.
With --remote, also:
  - every pin at HEAD, and every pin set in the range, is reachable from its repository's main branch as published
    now (before 4 November 2026 this asked only that some branch or tag held it);
  - every pin that moved, moved forward: the new commit descends from the old one;
  - no repository's main was rewritten since this store last fetched it, or since the checkpoint's check.
Exits 1 if anything fails, and names it. A clean run records its last commit (and, with --remote, each repository's
main) in .git/global-law-verify/verified.json, so the next run checks only what came after. The checkpoint is this
clone's own record, not something anyone else need trust: --full or --since checks again from any point. This
replaces a rebuild: since 2 November 2026 the tree is not rebuilt but grows by fast-forward (REPRODUCE.md).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GITLINK = '160000'
NO_LAZY = {**os.environ, 'GIT_NO_LAZY_FETCH': '1'}  # only what the store's refs reach; never ask the network


def git(*args: str, cwd: Path = ROOT, check: bool = True, env: dict | None = None) -> str:
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', env=env)
    if check and done.returncode:
        raise SystemExit(f"git {' '.join(args[:3])}: {done.stderr.strip()[:300]}")
    return done.stdout


def ok(*args: str, cwd: Path = ROOT, env: dict | None = None) -> bool:
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, env=env).returncode == 0


def prefetch(blobs: list[str | None]) -> None:
    """In a partial clone (--filter=blob:none), fetch the .gitmodules blobs a range needs in one request, not one
    lazy fetch each (823 commits since 2 November took 86 s that way)."""
    want = sorted({b for b in blobs if b and b.strip('0')})
    if not want or not git('config', '--get', 'remote.origin.promisor', check=False).strip():
        return
    have = subprocess.run(['git', 'cat-file', '--batch-check'], cwd=ROOT, input='\n'.join(want) + '\n',
                          capture_output=True, encoding='utf-8', env=NO_LAZY).stdout
    missing = [line.split()[0] for line in have.splitlines() if line.endswith(' missing')]
    if missing:
        subprocess.run(['git', '-c', 'fetch.negotiationAlgorithm=noop', 'fetch', '-q', '--no-tags',
                        '--no-write-fetch-head', '--recurse-submodules=no', '--filter=blob:none', '--stdin', 'origin'],
                       cwd=ROOT, input='\n'.join(missing) + '\n', capture_output=True, encoding='utf-8')


_modules: dict[str, dict[str, str]] = {}


def modules(blob: str | None) -> dict[str, str]:
    """path -> repository URL from one .gitmodules blob (cached: a few hundred distinct blobs in all the history)."""
    if not blob:
        return {}
    if blob not in _modules:
        names, urls = {}, {}
        for line in git('config', '--blob', blob, '--get-regexp', r'^submodule\..*\.(path|url)$', check=False).splitlines():
            key, _, value = line.partition(' ')
            (names if key.endswith('.path') else urls)[key.rsplit('.', 1)[0]] = value
        _modules[blob] = {p: urls.get(n, '') for n, p in names.items()}
    return _modules[blob]


def state(commit: str | None) -> tuple[dict[str, str], str | None]:
    """(path -> pinned commit, .gitmodules blob) at a commit of the tree."""
    if not commit:
        return {}, None
    links, blob = {}, None
    for line in git('ls-tree', '-r', commit).splitlines():
        meta, _, path = line.partition('\t')
        mode, kind, sha = meta.split()
        if kind == 'commit':
            links[path] = sha
        elif path == '.gitmodules':
            blob = sha
    return links, blob


def walk(start: str | None, end: str):
    """Yield (commit, day, links, urls, changed_paths, modules_changed) after each first-parent commit in start..end.
    One git process for the whole range: each commit's diff against its first parent, gitlinks and .gitmodules only."""
    links, blob = state(start)
    revs = f'{start}..{end}' if start else end
    proc = subprocess.Popen(['git', 'log', '--first-parent', '--diff-merges=first-parent', '--reverse', '--raw', '-r',
                             '--no-renames', '--no-abbrev', '--format=C %H %cs', revs], cwd=ROOT,
                            stdout=subprocess.PIPE, encoding='utf-8', errors='replace')
    # Kept: commit lines, gitlink changes and .gitmodules changes (about 700,000 lines for the whole history).
    lines = [l for l in proc.stdout if l.startswith('C ') or (l.startswith(':') and (GITLINK in l[:16] or
                                                                                   l.endswith('\t.gitmodules\n')))]
    if proc.wait():
        raise SystemExit(f'git log {revs} failed')
    prefetch([blob] + [l.split()[3] for l in lines if l.endswith('\t.gitmodules\n')])
    current = None

    def flush():
        c, day, changed, mod = current
        return c, day, links, modules(blob), changed, mod

    for line in lines:
        if line.startswith('C '):
            if current:
                yield flush()
            _, c, day = line.split()
            current = (c, day, [], False)
        elif line.startswith(':'):
            meta, _, path = line.rstrip('\n').partition('\t')
            old_mode, new_mode, old_sha, new_sha, status = meta[1:].split()
            if path == '.gitmodules':
                blob = None if status == 'D' else new_sha
                current = (*current[:3], True)
            if GITLINK in (old_mode, new_mode):
                current[2].append((path, links.get(path), new_sha if new_mode == GITLINK else None))
                if new_mode == GITLINK:
                    links[path] = new_sha
                else:
                    links.pop(path, None)
    if current:
        yield flush()


def structure(commit: str, links: dict[str, str], urls: dict[str, str]) -> list[str]:
    problems = []
    missing = sorted(set(links) - set(urls))
    extra = sorted(set(urls) - set(links))
    if missing:
        problems.append(f'{commit[:10]}: {len(missing)} gitlink(s) with no .gitmodules entry, e.g. {missing[:3]}')
    if extra:
        problems.append(f'{commit[:10]}: {len(extra)} .gitmodules entr(y/ies) with no gitlink, e.g. {extra[:3]}')
    twice = [u for u, n in Counter(urls.values()).items() if n > 1 and u]
    if twice:
        problems.append(f'{commit[:10]}: repository pinned at two paths: {twice[:3]}')
    return problems


def repo_name(url: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]', '_', url.rstrip('/').removesuffix('.git').rsplit('/', 1)[-1])


def github_heads(urls: list[str]) -> dict[str, str]:
    """url -> main's commit, for github.com URLs, 100 repositories per GraphQL query (cost 1 point each; 713
    repositories: 8 queries, about 14 s with 4 at a time). Needs the gh CLI signed in; {} for what it cannot answer,
    which is then fetched as usual."""
    hub = [u for u in urls if re.match(r'https://github\.com/[^/]+/[^/]+$', u.rstrip('/').removesuffix('.git'))]

    def one(chunk: list[str]) -> dict[str, str]:
        parts = []
        for j, u in enumerate(chunk):
            owner, name = u.rstrip('/').removesuffix('.git').split('/')[-2:]
            parts.append(f'r{j}:repository(owner:"{owner}",name:"{name}"){{ref(qualifiedName:"refs/heads/main")'
                         f'{{target{{oid}}}}}}')
        try:
            done = subprocess.run(['gh', 'api', 'graphql', '-f', 'query={' + ' '.join(parts) + '}'],
                                  capture_output=True, encoding='utf-8')
            data = json.loads(done.stdout or '{}').get('data') or {}
        except (OSError, ValueError):
            return {}
        return {u: (((data.get(f'r{j}') or {}).get('ref') or {}).get('target') or {}).get('oid')
                for j, u in enumerate(chunk)}

    with ThreadPoolExecutor(4) as ex:
        out: dict[str, str] = {}
        for part in ex.map(one, [hub[i:i + 100] for i in range(0, len(hub), 100)]):
            out.update({u: s for u, s in part.items() if s})
    return out


class Store:
    """One bare repository holding the commits (no trees, no files) of every corpus's main, one remote per corpus."""

    def __init__(self, path: Path, jobs: int, api: bool = False):
        self.path, self.jobs, self.api = path, jobs, api
        if not (path / 'HEAD').exists():
            path.mkdir(parents=True, exist_ok=True)
            git('init', '-q', '--bare', str(path), cwd=path)
            for k, v in (('core.repositoryformatversion', '1'), ('extensions.partialClone', 'origin'),
                         ('gc.auto', '0'), ('fetch.writeCommitGraph', 'false')):
                git('config', k, v, cwd=path)
        have = {}
        for line in git('config', '--get-regexp', r'^remote\..*\.url$', cwd=path, check=False).splitlines():
            key, _, url = line.partition(' ')
            have[url] = key[len('remote.'):-len('.url')]
        self.remotes = have

    def remote(self, url: str) -> str:
        return self.remotes[url]

    def add(self, urls: list[str]) -> None:
        new = [u for u in urls if u not in self.remotes]
        taken = set(self.remotes.values())
        with open(self.path / 'config', 'a', encoding='utf-8', newline='\n') as f:
            for u in new:
                name = repo_name(u)
                while name in taken:
                    name += '_'
                taken.add(name)
                self.remotes[u] = name
                f.write(f'[remote "{name}"]\n\turl = {u}\n\tfetch = +refs/heads/main:refs/remotes/{name}/main\n'
                        f'\ttagOpt = --no-tags\n\tpromisor = true\n\tpartialclonefilter = tree:0\n')

    def tips(self) -> dict[str, str]:
        by_name = {n: u for u, n in self.remotes.items()}
        out = {}
        for line in git('for-each-ref', '--format=%(objectname) %(refname)', 'refs/remotes', cwd=self.path).splitlines():
            sha, ref = line.split()
            name = ref.split('/')[2]
            if name in by_name and ref.endswith('/main'):
                out[by_name[name]] = sha
        return out

    def fetch(self, urls: list[str]) -> list[str]:
        """Fetch every url's main, --jobs at a time; the urls that could not be fetched, after one retry."""
        before = self.tips()

        def one(url: str) -> bool:
            # Each fetch offers the server only its own repository's history as common ground (a store of 700
            # unrelated histories would otherwise send thousands of useless "have" lines), and none on a first fetch.
            name = self.remote(url)
            tip = (['--negotiation-tip', f'refs/remotes/{name}/main'] if url in before
                   else ['-c', 'fetch.negotiationAlgorithm=noop'])
            cmd = ['git', *(tip if tip[0] == '-c' else []), 'fetch', '-q', '--no-tags', '--no-write-fetch-head',
                   *(tip if tip[0] != '-c' else []), name]
            for _ in range(2):  # one retry: a dropped connection is not a missing repository
                if subprocess.run(cmd, cwd=self.path, capture_output=True).returncode == 0:
                    return True
            return False

        if self.api:  # ask GitHub for every main at once, then fetch only the repositories whose main moved
            heads = github_heads(urls)
            todo = [u for u in urls if not heads.get(u) or heads[u] != before.get(u)]
        else:
            todo = urls
        self.fetched = len(todo)
        with ThreadPoolExecutor(self.jobs) as ex:
            done = {**{u: True for u in urls}, **dict(zip(todo, ex.map(one, todo)))}
        self.before = before
        return [u for u in urls if not done[u]]

    def commit_graph(self) -> None:
        git('commit-graph', 'write', '--reachable', '--split', cwd=self.path, check=False, env=NO_LAZY)

    def reach(self, url: str, shas: set[str], pairs: list[tuple[str, str]]) -> tuple[set[str], set[tuple[str, str]]]:
        """(the shas reachable from url's main, the (old, new) pairs where old is not an ancestor of new or equal)."""
        ref = f'refs/remotes/{self.remote(url)}/main'
        line = git('rev-list', '--first-parent', ref, cwd=self.path, check=False, env=NO_LAZY).split()
        index = {sha: i for i, sha in enumerate(line)}  # newest first
        held = {s for s in shas if s in index}
        rest = shas - held
        if rest:  # off the first-parent line: walk all of main
            every = set(git('rev-list', ref, cwd=self.path, check=False, env=NO_LAZY).split())
            held |= rest & every
        backward = set()
        for old, new in pairs:
            if old == new or old not in held or new not in held:  # a pin main does not reach is reported apart
                continue
            if old in index and new in index:
                if index[new] > index[old]:
                    backward.add((old, new))
            elif not ok('merge-base', '--is-ancestor', old, new, cwd=self.path, env=NO_LAZY):
                backward.add((old, new))
        return held, backward


def first_parent_base(n: int) -> str | None:
    """The commit before the last n on the first-parent line (None: the history is shorter)."""
    line = git('rev-list', '--first-parent', f'--max-count={n + 1}', 'HEAD').split()
    return line[n] if len(line) > n else None


def main(argv: list[str]) -> int:
    t0 = time.time()
    remote = '--remote' in argv or '--fetch' in argv
    jobs = int(argv[argv.index('--jobs') + 1]) if '--jobs' in argv else min(32, (os.cpu_count() or 4) * 2)
    use_checkpoint = '--no-checkpoint' not in argv
    store_dir = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'global-law-verify').strip())
    marker = store_dir / 'verified.json'
    checkpoint = json.loads(marker.read_text(encoding='utf-8')) if use_checkpoint and marker.exists() else {}
    head = git('rev-parse', 'HEAD').strip()
    problems: list[str] = []
    mark = checkpoint.get('remote' if remote else 'structure') or checkpoint.get('remote') or {}
    if mark and not ok('merge-base', '--is-ancestor', mark['commit'], 'HEAD', env=NO_LAZY):
        problems.append(f"{head[:10]}: the checkpoint commit {mark['commit'][:10]} ({mark.get('checked_at', '?')}) is "
                        f"not in this history: the tree was rewritten, or this clone is behind it")
        mark = {}
    if '--full' in argv:
        start, how = None, 'the whole history'
    elif '--since' in argv:
        start = git('rev-parse', argv[argv.index('--since') + 1]).strip()
        how = f'since {start[:10]}'
    elif mark:
        start, how = mark['commit'], f"since the checkpoint {mark['commit'][:10]} ({mark.get('checked_at', '?')})"
    else:
        start, how = first_parent_base(200), 'the last 200 commits'

    commits: list[str] = []
    day: dict[str, str] = {}
    moves: list[tuple[str, str, str, str]] = []  # (tree commit, url, old pin, new pin)
    set_in_range: list[tuple[str, str, str, str]] = []  # (tree commit, path, url, pin) for every pin set
    broken: list[str] = []  # the structural problems of the state as it stands, re-reported at each commit
    prev_urls: dict[str, str] = {}
    links: dict[str, str] = {}
    urls: dict[str, str] = {}
    first = True
    for c, d, links, urls, changed, mod in walk(start, 'HEAD'):
        commits.append(c)
        day[c] = d
        if first or mod or any(old is None or new is None for _, old, new in changed):
            broken = [p.split(': ', 1)[1] for p in structure(c, links, urls)]
            first = False
        problems.extend(f'{c[:10]}: {p}' for p in broken)
        for path, old, new in changed:
            if new is None:
                continue
            url = urls.get(path) or prev_urls.get(path, '')
            set_in_range.append((c, path, url, new))
            if old and old != new:
                moves.append((c, url, old, new))
        prev_urls = urls
    if not commits:
        links, blob = state('HEAD')
        urls = modules(blob)
    t_scan = time.time() - t0
    print(f'{len(commits)} commit(s) checked for gitlinks and .gitmodules ({how}); {len(moves)} pin move(s) in the '
          f'range [{t_scan:.1f} s]')

    tips_now: dict[str, str] = {}
    if remote:
        t1 = time.time()
        head_links, head_urls = links, urls
        store = Store(store_dir / 'store.git', jobs, api='--github-heads' in argv)
        wanted: dict[str, set[str]] = {}
        pairs: dict[str, list[tuple[str, str]]] = {}
        for _, path, url, sha in set_in_range:
            wanted.setdefault(url, set()).add(sha)
        for _, url, old, new in moves:
            wanted.setdefault(url, set()).update((old, new))
            pairs.setdefault(url, []).append((old, new))
        for path, sha in head_links.items():
            wanted.setdefault(head_urls.get(path, ''), set()).add(sha)
        known = (mark or {}).get('tips', {})
        urls_all = sorted(u for u in set(wanted) | set(known) if u)
        store.add(urls_all)
        failed = store.fetch(urls_all)
        t_fetch = time.time() - t1
        store.commit_graph()
        tips_now = store.tips()
        for url in failed:
            problems.append(f'{head[:10]}: could not fetch {url}: its pins are unchecked')
        # A main that moved must have moved forward: since the last fetch into this store, and since the checkpoint.
        for url in urls_all:
            for was, label in ((store.before.get(url), 'the last fetch'), (known.get(url), 'the checkpoint')):
                now = tips_now.get(url)
                if was and now and was != now and not ok('merge-base', '--is-ancestor', was, now, cwd=store.path,
                                                         env=NO_LAZY):
                    problems.append(f'{head[:10]}: {url} main was rewritten since {label}: {was[:10]} is not in '
                                    f'{now[:10]}')
        with ThreadPoolExecutor(jobs) as ex:
            work = {u: ex.submit(store.reach, u, wanted.get(u, set()), pairs.get(u, []))
                    for u in urls_all if u in tips_now}
            reach = {u: f.result() for u, f in work.items()}
        for path, sha in sorted(head_links.items()):
            url = head_urls.get(path, '')
            if url in failed:
                continue
            if sha not in reach.get(url, (set(), set()))[0]:
                problems.append(f'HEAD: {path} pins {sha[:10]}, which {url} main does not reach (no longer holds)')
        for c, path, url, sha in set_in_range:
            if url not in failed and sha not in reach.get(url, (set(), set()))[0]:
                problems.append(f'{c[:10]}: pins {sha[:10]} in {url}, which no longer holds it on main')
        for c, url, old, new in moves:
            held, backward = reach.get(url, (set(), set()))
            if url not in failed and old in held and new in held and (old, new) in backward:
                problems.append(f'{c[:10]}: moved {url} from {old[:10]} to {new[:10]}, not forward')
        print(f'{len(tips_now)} repositories in the store, {store.fetched - len(failed)} fetched [{t_fetch:.1f} s]; '
              f'{len(head_links)} pins at HEAD and {len(set_in_range)} pins set in the range checked against main '
              f'[{time.time() - t1:.1f} s]')
    # A summary by kind and by day, then the first of each kind: old damage and new breakage read apart.
    kinds = Counter()
    by_day = Counter()
    firsts: dict[str, list[str]] = {}
    day10 = {c[:10]: d for c, d in day.items()}  # problems name commits by 10 characters
    for p in problems:
        kind = ('pin at HEAD not held' if p.startswith('HEAD:') else 'pin no longer held' if 'no longer holds' in p
                else 'pin moved backward' if 'not forward' in p else 'gitlink without .gitmodules entry'
                if 'with no .gitmodules entry' in p else '.gitmodules entry without gitlink' if 'with no gitlink' in p
                else 'repository not fetched' if 'could not fetch' in p
                else 'corpus main rewritten' if 'main was rewritten' in p
                else 'tree history rewritten' if 'checkpoint commit' in p
                else 'repository pinned twice')
        kinds[kind] += 1
        short = p.split(':', 1)[0].strip()
        by_day[(kind, day10.get(short, ''))] += 1
        firsts.setdefault(kind, []).append(p)
    for kind, n in kinds.most_common():
        days = [f'{d or "?"}: {c}' for (k, d), c in sorted(by_day.items()) if k == kind]
        days = ', '.join(days if len(days) <= 12 else days[:6] + [f'... {len(days) - 12} more days ...'] + days[-6:])
        print(f'{kind}: {n} ({days})')
        for p in firsts[kind][:5]:
            print('  FAIL', p)
    if not problems and use_checkpoint:
        stamp = {'commit': head, 'tree': git('rev-parse', 'HEAD^{tree}').strip(),
                 'checked_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                 'from': start or 'root'}
        checkpoint['structure'] = stamp
        if remote:
            checkpoint['remote'] = {**stamp, 'tips': {u: tips_now[u] for u in sorted(tips_now)}}
        store_dir.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps(checkpoint, indent=1) + '\n', encoding='utf-8')
    print('ok' if not problems else f'{len(problems)} problem(s)', f'[{time.time() - t0:.1f} s]')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
