#!/usr/bin/env python3
"""Read the global law tree on any date. Standard library only.

Every root commit is one law taking effect somewhere, in the order the changes took force, and pins every corpus at
that moment. So one root commit is the state of all the law in the tree, and the tools below never check anything
out: they read the pinned corpus commits straight from the submodules.

  python tools/law.py world 2022-05-01                     what every corpus looked like that day
  python tools/law.py show 2022-05-01 united-states/federal/usc/title-11/1182.md
  python tools/law.py blame 2022-07-01 united-states/federal/usc/title-11/1182.md
  python tools/law.py words 2022-07-01 united-states/federal/usc/title-11/1182.md   which law wrote each word
  python tools/law.py diff 2022-05-01 2022-07-01 united-states/federal/usc/title-11/1182.md
  python tools/law.py today 2022-07-01 united-states/federal/usc/title-11/1182.md   is it worded the same today?
  python tools/law.py log united-states/federal/usc/title-11/1182.md   every law that changed a file, with its dates
  python tools/law.py laws 1990-01-01 1990-12-31 [germany]       laws that took force in a window, by jurisdiction

Run `git submodule update --init` once first. Dates are in-force dates read from each commit's In-force trailer,
so dates before 1970 work even though git cannot store them as commit dates.
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8')
    if check and done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


_CACHE: dict[tuple[str, str], object] = {}


def _head() -> str:
    return git('rev-parse', 'HEAD').strip()


def manifest() -> dict:
    key = ('manifest', _head())
    if key not in _CACHE:
        _CACHE[key] = with_unlisted(json.loads(git('show', 'HEAD:manifest.json')))
    return _CACHE[key]  # type: ignore[return-value]


def with_unlisted(m: dict) -> dict:
    """manifest.json with every corpus the tree pins but does not list. Since 2 November 2026 the tree only adds
    submodules and moves pins, and manifest.json is no longer rewritten, so most corpora are in .gitmodules alone
    (603 of 710 on 3 November). Each is described by its own corpus.json, else data/repo.json and jurisdiction.json
    (what build.py repos ship), when it is checked out; else by its path. Defaults: In-force trailer, no citation rule."""
    listed = {c['path'] for c in m.get('corpora', [])}
    pins = [l.split(None, 3)[3] for l in git('ls-tree', '-r', '-d', 'HEAD').splitlines() if l.split(None, 3)[1] == 'commit']
    urls: dict[str, str] = {}
    paths: dict[str, str] = {}
    for line in git('config', '--blob', 'HEAD:.gitmodules', '--get-regexp', r'^submodule\..*\.(path|url)$', check=False).splitlines():
        name, _, value = line.partition(' ')
        (paths if name.endswith('.path') else urls)[name.rsplit('.', 1)[0]] = value
    url_of = {p: urls.get(n, '') for n, p in paths.items()}
    extra = []
    for path in pins:
        if path in listed:
            continue
        folders = path.split('/')
        entry = {'path': path, 'name': ', '.join(f.replace('-', ' ').title() for f in folders[:2]), 'language': '',
                 'in_force_trailer': 'In-force', 'url': url_of.get(path, ''), 'unlisted': True}
        entry.update(described(path))
        extra.append(entry)
    return {**m, 'corpora': m.get('corpora', []) + extra}


def described(path: str) -> dict:
    """A checked-out corpus's own description: corpus.json, else data/repo.json and jurisdiction.json."""
    cwd = ROOT / path
    if not (cwd / '.git').exists():
        return {}

    def read(name: str) -> dict:
        done = subprocess.run(['git', 'show', f'HEAD:{name}'], cwd=cwd, capture_output=True, encoding='utf-8')
        try:
            return json.loads(done.stdout) if done.returncode == 0 else {}
        except ValueError:
            return {}

    cj = read('corpus.json')
    if cj:
        out = {k: v for k, v in cj.items() if k not in ('corpus', 'path')}
        if cj.get('corpus'):
            out['iso_path'] = cj['corpus']
        return out
    repo, juris = read('data/repo.json'), read('jurisdiction.json')
    out = {}
    if repo.get('name') or juris.get('name'):
        out['name'] = repo.get('name') or juris['name']
    if repo.get('country') or juris.get('code'):
        out['code'] = repo.get('country') or juris['code']
    if repo.get('publisher'):
        out['record_note'] = f"Publisher: {repo['publisher']}."
    return out


@dataclass
class Event:
    commit: str
    corpus: str
    corpus_commit: str
    law: str
    in_force: str
    kind: str
    subject: str


_TRAILER = re.compile(r'^([A-Z][A-Za-z0-9-]*): (.*)$')


def trailers_all(body: str) -> dict[str, list[str]]:
    """Every trailer of a commit message, with repeated keys kept in order (Malta lists each affected law on its own
    `Affecting:` line). As in `git interpret-trailers`, only the last paragraph counts, so a line in the body that
    happens to read "Word: text" is not taken for a trailer."""
    text = body.strip()
    # Nearly every commit ends in its trailers: try the last paragraph alone before splitting the whole message
    # (a timeline reads a hundred thousand messages).
    # (Lines of only spaces also end a paragraph; the blank lines this can leave in `last` are skipped.)
    last = _PARAGRAPH_BREAK.split(text.rsplit('\n\n', 1)[-1])[-1]
    found = _trailer_block(last)
    if found is not None:
        return found
    for para in reversed([p for p in _PARAGRAPH_BREAK.split(text) if p.strip()]):
        found = _trailer_block(para)
        if found is not None:
            return found
    return {}


_PARAGRAPH_BREAK = re.compile(r'\n\s*\n')


def _trailer_block(para: str) -> dict[str, list[str]] | None:
    """The trailers of one paragraph, or None when too few of its lines are trailers for it to be the trailer block."""
    lines = [l for l in para.splitlines() if l.strip()]
    found = [_TRAILER.match(l) for l in lines]
    if not lines or sum(1 for m in found if m) < max(1, len(lines) // 2):
        return None
    out: dict[str, list[str]] = {}
    for m in found:
        if m:
            out.setdefault(m.group(1), []).append(m.group(2).strip())
    return out


def trailers(body: str) -> dict[str, str]:
    """The first value of each trailer; trailers_all() keeps every value."""
    return {k: v[0] for k, v in trailers_all(body).items()}


def timeline() -> list[Event]:
    """Every dated commit of every corpus checked out, oldest in-force date first. Each corpus is read from its own
    history at the commit the tree pins at HEAD (corpus_events).

    Until 2 November 2026 the tree recorded one root commit per law taking effect, and this read those. Since then the
    tree only moves each corpus's pin forward (it grows by fast-forward alone, and corpus repositories may be rebuilt),
    so its root history ends there and an old root commit can pin a corpus commit that no longer exists. Those root
    commits now only date a corpus commit that carries no date of its own (legacy_dates)."""
    corpora = tuple(c['path'] for c in manifest()['corpora'])
    key = ('timeline', _head() + '|' + ','.join(corpora))
    if key not in _CACHE:
        events = [e for c in corpora for e in corpus_events(c)]
        events.sort(key=lambda e: e.in_force)  # stable: each corpus keeps its own order within a day
        _CACHE[key] = events
    return list(_CACHE[key])  # type: ignore[arg-type]


def tip(corpus: str) -> str | None:
    """The corpus commit the tree pins at HEAD."""
    key = ('tips', _head())
    if key not in _CACHE:
        out = git('ls-tree', '-r', '-d', 'HEAD')
        _CACHE[key] = {path: sha for mode, kind, sha, path in (l.split(None, 3) for l in out.splitlines()) if kind == 'commit'}
    return _CACHE[key].get(corpus)  # type: ignore[union-attr]


def reachable_tip(corpus: str) -> str:
    """The commit the tree pins for a corpus, or the checkout's own HEAD if it has not fetched that commit yet."""
    key = ('reachable', f'{corpus}@{tip(corpus)}')
    if key not in _CACHE:
        sha = tip(corpus)
        ok = bool(sha) and subprocess.run(['git', 'cat-file', '-e', f'{sha}^{{commit}}'], cwd=corpus_dir(corpus),
                                          capture_output=True).returncode == 0
        _CACHE[key] = sha if ok else 'HEAD'
    return _CACHE[key]  # type: ignore[return-value]


def corpus_events(corpus: str) -> list[Event]:
    """The dated commits of one corpus, in its own history order, read at the commit the tree pins (or the
    checkout's own HEAD, if the checkout has not fetched that commit yet). Empty when the corpus is not checked out.
    A commit is dated as history() dates it; one with no date of its own takes the date the tree's legacy root
    history gave it, if any; documentation commits are kept with kind 'documentation'."""
    cwd = ROOT / corpus
    if not (cwd / '.git').exists():
        return []
    sha = tip(corpus) or 'HEAD'
    key = ('corpus-events', f'{corpus}@{sha}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    info = corpus_info(corpus)
    trailer = info.get('in_force_trailer') or 'In-force'
    dated_by = [(info[k], kind) for k, kind in (('baseline_trailer', 'baseline'), ('correction_trailer', 'correction')) if info.get(k)]
    # Only the trailers, which git finds as interpret-trailers does: the whole messages are three times the bytes
    # (Czechia's 33,000 commits: 36 MB and 21 s, against 12 MB and 5 s).
    fmt = '--format=%H%x1f%an%x1f%aI%x1f%s%x1f%(trailers:only,unfold)%x1e'
    try:
        raw = git('log', '--reverse', fmt, sha, cwd=cwd)
    except RuntimeError:  # the checkout has not fetched the pinned commit yet: read what it has
        raw = git('log', '--reverse', fmt, 'HEAD', cwd=cwd)
    rows, undated, fixes = [], [], []
    for record in raw.split('\x1e'):
        if not record.strip():
            continue
        commit, author, when, subject, block = record.strip('\n').split('\x1f', 4)
        every = trailer_values(block)
        t = {k: v[0] for k, v in every.items()}
        kind = (t.get('Kind') or '').strip().lower()
        if kind == 'correction' and 'Corrects' in t:
            span = CORRECTS.search(t['Corrects'])
            start = span.group(1) if span else (t.get(trailer) or '')[:10]
            if ISO_DAY.match(start):
                fixes.append({'commit': commit, 'law': author, 'from': start, 'to': span.group(2) if span else None,
                              'files': every.get('Files', []), 'act_path': t.get('Act-path'), 'corrects': t['Corrects'],
                              'supersedes': t.get('Supersedes'), 'reason': t.get('Reason')})
        docs = kind == 'documentation' or author == 'Lexifina'
        in_force, what = (None, 'documentation') if docs else (t.get(trailer), 'law')
        for k, label in dated_by if not docs else ():
            if not in_force and k in t and ISO_DAY.match(t[k]):
                in_force, what = t[k][:10], label
        if not in_force and not docs and 'Printed-in' in t:
            in_force, what = when[:10], 'printing'
        if in_force and not docs:
            if kind == 'correction' or (info.get('correction_trailer') or '') in t:
                what = 'correction'
            elif kind in ('baseline', 'consolidated', 'current', 'current-only'):
                what = 'baseline'
        rows.append([commit, author, in_force[:10] if in_force and ISO_DAY.match(in_force) else None, what, subject])
        if rows[-1][2] is None and what != 'documentation':  # documentation is never law: no need to date it
            undated.append(len(rows) - 1)
    if undated:
        legacy = legacy_dates(corpus)
        for i in undated:
            if rows[i][0] in legacy:
                rows[i][2], kind = legacy[rows[i][0]]
                rows[i][3] = kind if rows[i][3] != 'documentation' else 'documentation'
    events = [Event(c, corpus, c, a, d, k, s) for c, a, d, k, s in rows if d]
    _CACHE[key] = events
    _CACHE[('corrections', key[1])] = fixes
    return events


def corrections(corpus: str) -> list[dict]:
    """The corrections appended to a corpus (Kind: correction, with Corrects: <act> <from>..<to>), in history order.
    Each sets the files it names (one Files: trailer per corpus-relative path) to the corrected text for those dates,
    whether or not git shows a change for a file: a late-found version can equal the text the tip already has.
    Act-path: names the act, whose next ordinary commit ends an open range."""
    corpus_events(corpus)
    return _CACHE.get(('corrections', f'{corpus}@{tip(corpus) or "HEAD"}'), [])  # type: ignore[return-value]


def act_next(corpus: str, paths: list[str], after: str) -> str | None:
    """The in-force date of the act's next ordinary commit (not a correction, not documentation) after `after`: the
    first commit by in-force date that touches any of `paths`."""
    key = ('act-next', f'{corpus}@{tip(corpus)}:' + '\x1f'.join(paths))
    if key not in _CACHE:
        cwd = corpus_dir(corpus)
        try:
            touched = set(git('log', '--format=%H', tip(corpus) or 'HEAD', '--', *paths, cwd=cwd).split())
        except RuntimeError:
            touched = set(git('log', '--format=%H', 'HEAD', '--', *paths, cwd=cwd).split())
        fixes = {c['commit'] for c in corrections(corpus)}
        _CACHE[key] = sorted(e.in_force for e in corpus_events(corpus)
                             if e.corpus_commit in touched and e.corpus_commit not in fixes and e.kind != 'documentation')
    return next((d for d in _CACHE[key] if d > after), None)  # type: ignore[union-attr]


def correction_end(corpus: str, fix: dict, rel: str) -> str:
    """The last day a correction applies: its own end, or for an open range the day before the act's next ordinary
    commit (the act is Act-path:, else the folders of its Files:, else the folder of the file read)."""
    if fix.get('to'):
        return fix['to']
    folder = lambda f: f.rsplit('/', 1)[0] if '/' in f else f  # noqa: E731
    paths = [fix['act_path']] if fix.get('act_path') else sorted({folder(f) for f in fix['files']}) or [folder(rel)]
    nxt = act_next(corpus, paths, fix['from'])
    if not nxt:
        return '9999-12-31'
    import datetime as dt
    return (dt.date.fromisoformat(nxt) - dt.timedelta(days=1)).isoformat()


def trailer_values(block: str) -> dict[str, list[str]]:
    """Every value of each trailer in a block git printed with %(trailers:only,unfold), repeated keys in order."""
    out: dict[str, list[str]] = {}
    for line in block.splitlines():
        m = _TRAILER.match(line)
        if m:
            out.setdefault(m.group(1), []).append(m.group(2).strip())
    return out


def trailer_lines(block: str) -> dict[str, str]:
    """The first value of each trailer in a block git printed with %(trailers:only,unfold)."""
    out: dict[str, str] = {}
    for line in block.splitlines():
        m = _TRAILER.match(line)
        if m:
            out.setdefault(m.group(1), m.group(2).strip())
    return out


def legacy_dates(corpus: str) -> dict[str, tuple[str, str]]:
    """corpus commit -> (in-force date, kind) from the tree's root commits made before 2 November 2026, which dated a
    starting edition with no trailer of its own (the US 2017 edition) and every documentation commit."""
    key = ('legacy', _head())
    if key not in _CACHE:
        raw = git('log', '--first-parent', '--reverse', '--format=%(trailers:only,unfold)%x1e')
        found: dict[str, dict[str, tuple[str, str]]] = {}
        for body in raw.split('\x1e'):
            if 'Corpus-commit:' not in body:
                continue
            t = trailer_lines(body)
            if 'Corpus' in t and 'Corpus-commit' in t and ISO_DAY.match(t.get('In-force', '')):
                kind = 'documentation' if t.get('Law', '') == 'Lexifina' else t.get('Kind', 'law')
                found.setdefault(t['Corpus'], {})[t['Corpus-commit']] = (t['In-force'][:10], kind)
        _CACHE[key] = found
    return _CACHE[key].get(corpus, {})  # type: ignore[union-attr]


@dataclass(frozen=True)
class Moment:
    """The tree as in force on a date, which root_on gives: each corpus at its last commit in force by then."""
    date: str

    def __str__(self) -> str:
        return self.date


def root_on(date: str, events: list[Event] | None = None) -> Moment | None:
    """The tree as in force on `date`, or None before every record. pinned() gives each corpus's commit in it."""
    events = events if events is not None else timeline()
    return Moment(date) if events and events[0].in_force <= date else None


def corpus_on(date: str, corpus: str) -> str | None:
    """The corpus commit in force on `date`: the last of its dated commits before the first one dated after `date`
    (a prefix, as the corpora record changes in the order they took force)."""
    found = None
    for event in corpus_events(corpus):
        if event.in_force > date:
            break
        found = event.corpus_commit
    return found


def in_order(corpus: str) -> bool:
    """Whether a corpus's history is in in-force order with no corrections: then the commit-order prefix (corpus_on)
    is exactly the corpus as in force on a date, and no tree has to be built."""
    last = ''
    for e in corpus_events(corpus):
        if e.kind == 'documentation':
            continue
        if e.in_force < last:
            return False
        last = e.in_force
    return not corrections(corpus)


def _unquote(path: str) -> str:
    """A path git printed in C quotes (non-ASCII, when core.quotepath is on) back to the name itself."""
    if not path.startswith('"'):
        return path
    return path[1:-1].encode('latin-1', 'backslashreplace').decode('unicode_escape').encode('latin-1').decode('utf-8')


def file_index(corpus: str) -> tuple[dict, list]:
    """Every version of every file of a corpus, from one `git log --raw` at the pinned tip: path -> [(in force, order,
    blob or None for a deletion, mode)] for ordinary commits, and the corrections laid over them as
    [(from, last day, order, {path: (blob, mode)})]."""
    key = ('file-index', f'{corpus}@{tip(corpus) or "HEAD"}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    cwd = corpus_dir(corpus)
    events = corpus_events(corpus)
    dates = {e.corpus_commit: (e.in_force, i) for i, e in enumerate(events) if e.kind != 'documentation'}
    fixes = {c['commit']: c for c in corrections(corpus)}
    try:
        raw = git('log', '--reverse', '--raw', '--no-renames', '--no-abbrev', '--format=@%H', tip(corpus) or 'HEAD', cwd=cwd)
    except RuntimeError:
        raw = git('log', '--reverse', '--raw', '--no-renames', '--no-abbrev', '--format=@%H', 'HEAD', cwd=cwd)
    index: dict[str, list] = {}
    touched: dict[str, dict] = {}
    commit = ''
    for line in raw.splitlines():
        if line.startswith('@'):
            commit = line[1:]
            continue
        if not line.startswith(':') or '\t' not in line:
            continue
        meta, path = line.split('\t', 1)
        _, mode, _, blob, status = meta.split()[:5]
        path = _unquote(path)
        if commit in fixes:
            touched.setdefault(commit, {})[path] = (None if status.startswith('D') else blob, mode)
        elif commit in dates:
            day, order = dates[commit]
            index.setdefault(path, []).append((day, order, None if status.startswith('D') else blob, mode))
    order_of = {e.corpus_commit: i for i, e in enumerate(events)}
    overlays = []
    for sha, fix in fixes.items():
        files = dict(touched.get(sha, {}))
        named = [f for f in fix['files'] if f not in files]
        if named:  # named but unchanged: their text at the correction commit is the tip's
            for line in git('ls-tree', sha, '--', *named, cwd=cwd).splitlines():
                meta, path = line.split('\t', 1)
                mode, _, blob = meta.split()
                files[_unquote(path)] = (blob, mode)
        if fix['files']:
            files = {p: v for p, v in files.items() if p in fix['files']}
        overlays.append((fix, order_of.get(sha, len(order_of)), files))
    _CACHE[key] = (index, overlays)
    return index, overlays


_TREES: dict = {'dir': None}


def _tree_store() -> Path:
    """A private object directory for the trees this process builds. Every git command reads it as an alternate,
    so a built tree can be grepped and listed like a commit; nothing is written into the clone."""
    if _TREES['dir'] is None:
        import atexit
        import os
        import shutil
        import tempfile
        d = Path(tempfile.mkdtemp(prefix='global-law-trees-'))
        (d / 'objects').mkdir()
        atexit.register(shutil.rmtree, d, True)
        os.environ['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = str(d / 'objects')
        _TREES['dir'] = d
    return _TREES['dir']


def corpus_tree(date: str, corpus: str) -> str | None:
    """The corpus as in force on `date`, as something git reads like a commit (grep, ls-tree, show, diff): each file
    at the version file_commit would pick, corrections included. A corpus in in-force order is its commit-order
    prefix; any other (older acts appended after the tip, corrections) is a tree built from file_index for the date."""
    if in_order(corpus):
        return corpus_on(date, corpus)
    key = ('tree', f'{corpus}@{tip(corpus) or "HEAD"}@{date}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    index, overlays = file_index(corpus)
    chosen: dict[str, tuple] = {}
    for path, versions in index.items():
        best = None
        for day, order, blob, mode in versions:
            if day <= date and (best is None or (day, order) >= (best[0], best[1])):
                best = (day, order, blob, mode)
        if best and best[2]:
            chosen[path] = (best[2], best[3])
    best_fix: dict[str, tuple] = {}
    for fix, order, files in overlays:
        if fix['from'] > date:
            continue
        for path, (blob, mode) in files.items():
            if date > correction_end(corpus, fix, path):
                continue
            prev = best_fix.get(path)
            if prev is None or (fix['from'], order) >= prev[0]:
                best_fix[path] = ((fix['from'], order), blob, mode)
    for path, (_, blob, mode) in best_fix.items():
        if blob:
            chosen[path] = (blob, mode)
        else:
            chosen.pop(path, None)
    if not chosen:
        _CACHE[key] = None
        return None
    store = _tree_store()
    cwd = corpus_dir(corpus)
    objects = git('rev-parse', '--path-format=absolute', '--git-path', 'objects', cwd=cwd).strip()
    import os
    env = {**os.environ, 'GIT_INDEX_FILE': str(store / f'index-{abs(hash(key))}'), 'GIT_OBJECT_DIRECTORY': str(store / 'objects'),
           'GIT_ALTERNATE_OBJECT_DIRECTORIES': objects}
    # Bytes, NUL-terminated: in text mode Windows writes \r\n, and git reads "act/a.md\r" and ignores it.
    listing = b''.join(f'{mode} blob {blob}\t{path}'.encode('utf-8') + b'\0' for path, (blob, mode) in sorted(chosen.items()))
    run = subprocess.run(['git', 'update-index', '--add', '-z', '--index-info'], cwd=cwd, env=env, input=listing,
                         capture_output=True)
    if run.returncode or b'Ignoring path' in run.stderr:  # git exits 0 when it drops a path it cannot read
        raise RuntimeError(f"git update-index: {run.stderr.decode('utf-8', 'replace').strip()[:300]}")
    tree = subprocess.run(['git', 'write-tree'], cwd=cwd, env=env, capture_output=True, encoding='utf-8')
    if tree.returncode:
        raise RuntimeError(f'git write-tree: {tree.stderr.strip()[:300]}')
    sha = tree.stdout.strip()
    _CACHE[key] = sha
    return sha


def corpus_of(path: str) -> tuple[str, str]:
    for corpus in sorted(manifest()['corpora'], key=lambda c: -len(c['path'])):
        prefix = corpus['path'] + '/'
        if path.startswith(prefix):
            return corpus['path'], path[len(prefix):]
    raise SystemExit(f'{path} is not inside a corpus; see manifest.json')


def pinned(root_commit, corpus: str) -> str | None:
    """A corpus's commit in the tree at a Moment (root_on), at 'HEAD', or at a commit of the tree."""
    if root_commit is None:
        return None
    if isinstance(root_commit, Moment):
        return corpus_tree(root_commit.date, corpus)
    line = git('ls-tree', root_commit, '--', corpus).split()
    return line[2] if len(line) >= 3 and line[1] == 'commit' else None


def corpus_dir(corpus: str) -> Path:
    path = ROOT / corpus
    if not (path / '.git').exists():
        raise SystemExit(f'{corpus} is not checked out; run: python3 tools/countries.py add {corpus}')
    return path


def matches(corpus: dict, name: str) -> bool:
    """Whether a name a user gives for a jurisdiction takes in a corpus (a manifest entry): its country folder
    ("germany", "united kingdom"), its ISO code ("de"), a level ("united-states/federal", "us/federal") or the corpus
    itself, or a folder inside it, which takes in the whole corpus. A state, province or city by its own name
    ("bremen", "california") takes in its corpora too; the generic levels ("national", "federal") do not."""
    name = re.sub(r'\s+', '-', name.strip().strip('/').lower())
    if not name:
        return False
    for path in (corpus['path'], corpus.get('iso_path') or ''):
        if path and (path == name or path.startswith(name + '/') or name.startswith(path + '/')):
            return True
    level = corpus['path'].split('/')[1:2]
    if level and level[0] == name and name not in GENERIC_LEVELS:
        return True
    return name == str(corpus.get('code') or '').lower()


GENERIC_LEVELS = {'national', 'federal', 'bund', 'uk', 'central', 'state', 'acts', 'statutes'}


def file_commit(date: str, path: str) -> str | None:
    """The commit whose version of a provision is in force on `date`. First the ordinary commit: of the dated commits
    that touch the file, the one with the greatest in-force date on or before `date`, a later commit winning a tie.
    The order of commits does not matter, because a corpus can append an older act after its tip. Then, file by
    file, the latest correction whose dates cover the day and that names this file (Files:), or touches it when it
    names none: its text replaces the ordinary one. A commit may delete the file: then nothing is in force."""
    corpus, rel = corpus_of(path)
    hist = history(path)
    base = None
    for h in hist:
        if h.get('corrects') or h['in_force'] > date:
            continue
        if base is None or h['in_force'] >= base['in_force']:
            base = h
    mine = {h['commit'] for h in hist}
    fix = None
    for c in corrections(corpus):
        if not (rel in c['files'] or (not c['files'] and c['commit'] in mine)):
            continue
        if c['from'] <= date <= correction_end(corpus, c, rel) and (fix is None or c['from'] >= fix['from']):
            fix = c
    chosen = fix or base
    return chosen['commit'] if chosen else None


def text_on(date: str, path: str) -> str | None:
    corpus, rel = corpus_of(path)
    sha = file_commit(date, path)
    if sha is None:
        return None
    done = subprocess.run(['git', 'show', f'{sha}:{rel}'], cwd=corpus_dir(corpus), capture_output=True, encoding='utf-8')
    return done.stdout if done.returncode == 0 else None


def blame_rows(date: str, path: str) -> list[tuple[str, str, str]]:
    """(corpus commit, law, line) for every line of the file as it stood on `date`."""
    corpus, rel = corpus_of(path)
    sha = file_commit(date, path)
    if sha is None:
        return []
    out, commit, law = [], '', ''
    for line in git('blame', '--line-porcelain', sha, '--', rel, cwd=corpus_dir(corpus)).splitlines():
        if re.match(r'^[0-9a-f]{40} ', line):
            commit = line[:40]
        elif line.startswith('author '):
            law = line[7:]
        elif line.startswith('\t'):
            out.append((commit, law, line[1:]))
    return out


def blame_on(date: str, path: str) -> list[tuple[str, str]]:
    """(law, line) for every line of the file as it stood on `date`."""
    return [(law, line) for _, law, line in blame_rows(date, path)]


def today_diff(date: str, path: str) -> tuple[str, str]:
    """Is the text on `date` worded the same today? Returns (answer, word diff from that date to today)."""
    import datetime as dt
    now = dt.date.today().isoformat()
    then, current = text_on(date, path), text_on(now, path)
    if then is None:
        return 'not in force on that date', ''
    if current is None:
        return 'no longer in force today', ''
    if then == current:
        return 'same wording as today', ''
    return 'worded differently today', diff_between(date, now, path)


def _credit_words(old: list[str], old_authors: list[str], new: list[str], law: str) -> list[str]:
    ops = difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()
    credited: list[str] = []
    for i, (op, a0, a1, b0, b1) in enumerate(ops):
        # A few common words ("means a") left between two rewritten stretches were rewritten too.
        island = (op == 'equal' and 0 < i < len(ops) - 1 and ops[i - 1][0] != 'equal' and ops[i + 1][0] != 'equal'
                  and sum(not t.isspace() for t in new[b0:b1]) < 3)
        credited += [law] * (b1 - b0) if op != 'equal' or island else old_authors[a0:a1]
    return credited


def words_on(date: str, path: str, check=None) -> list[tuple[str, str]]:
    """(law, run of text) for the file as it stood on `date`, credited word by word. git blame credits whole lines;
    here each version of the file is compared with the one before, word by word, and words that survive keep the law
    that first wrote them. Text moved within the file usually keeps its author; text that is rewritten in place is
    credited to the law that rewrote it. Unchanged lines are matched first, so only changed stretches are compared
    word by word, which keeps long sections fast. `check`, if given, is called between steps and may raise to stop
    a pass that is taking too long (the MCP server's time limit)."""
    check = check or (lambda: None)
    corpus, rel = corpus_of(path)
    sha = file_commit(date, path)
    if sha is None:
        return []
    cwd = corpus_dir(corpus)
    lines: list[str] = []
    authors: list[list[str]] = []  # per line, one law per token
    for record in git('log', '--reverse', '--format=%H%x1f%an', sha, '--', rel, cwd=cwd).splitlines():
        check()
        commit, law = record.split('\x1f', 1)
        shown = subprocess.run(['git', 'show', f'{commit}:{rel}'], cwd=cwd, capture_output=True, encoding='utf-8')
        new_lines = shown.stdout.splitlines(keepends=True) if shown.returncode == 0 else []
        new_authors: list[list[str]] = []
        for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, lines, new_lines, autojunk=False).get_opcodes():
            if op == 'equal':
                new_authors += authors[a0:a1]
                continue
            check()
            old_block = [re.findall(r'\s+|\S+', line) for line in lines[a0:a1]]
            block = [re.findall(r'\s+|\S+', line) for line in new_lines[b0:b1]]
            old_tokens = [t for line in old_block for t in line]
            if len(old_tokens) * sum(map(len, block)) <= 400_000:
                old_credit = [a for line_authors in authors[a0:a1] for a in line_authors]
                credit = _credit_words(old_tokens, old_credit, [t for line in block for t in line], law)
                for line in block:
                    new_authors.append(credit[:len(line)])
                    credit = credit[len(line):]
            else:
                # A large rewrite: pair each new line with the most similar old line and compare only those two,
                # which keeps a whole-section rewrite (17 U.S.C. §115 in 2018) to seconds rather than minutes.
                for line in block:
                    check()
                    best, score = None, 0.0
                    for j, old in enumerate(old_block):
                        s = difflib.SequenceMatcher(None, old, line, autojunk=False).quick_ratio()
                        if s > score:
                            best, score = j, s
                    if best is not None and score >= 0.6:
                        new_authors.append(_credit_words(old_block[best], authors[a0 + best], line, law))
                    else:
                        new_authors.append([law] * len(line))
        lines, authors = new_lines, new_authors
    tokens = [t for line in lines for t in re.findall(r'\s+|\S+', line)]
    flat = [a for line_authors in authors for a in line_authors]
    runs: list[tuple[str, str]] = []
    for law, token in zip(flat, tokens):
        if token.isspace() and runs:
            law = runs[-1][0]  # spaces never start a new run
        if runs and runs[-1][0] == law:
            runs[-1] = (law, runs[-1][1] + token)
        else:
            runs.append((law, token))
    return runs


EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'  # git's empty tree: "nothing yet", before a record starts


def diff_between(date_a: str, date_b: str, path: str) -> str:
    corpus, rel = corpus_of(path)
    a, b = file_commit(date_a, path), file_commit(date_b, path)
    if a == b:
        return ''
    return git('diff', '--word-diff=plain', a or EMPTY_TREE, b or EMPTY_TREE, '--', rel, cwd=corpus_dir(corpus))


def corpus_info(corpus: str) -> dict:
    return next(c for c in manifest()['corpora'] if c['path'] == corpus)


def caveats(date: str, corpus: str, events: list[Event] | None = None) -> list[str]:
    """What a reader must know about a date in one corpus: before its record starts, or after it ends."""
    own = [e for e in (events if events is not None else timeline()) if e.corpus == corpus and e.kind != 'documentation']
    info = corpus_info(corpus)
    out = []
    if own and date < own[0].in_force:
        out.append(f"{corpus}: the record starts on {own[0].in_force} ({own[0].law}); nothing earlier is in it.")
    # The record covers every day up to the later of its last change and the day it was checked against the source.
    covered = max(filter(None, (info.get('record_to'), info.get('checked_on'))), default=None)
    if covered and date > covered:
        checked = f", checked on {info['checked_on']}" if info.get('checked_on') else ''
        out.append(f"{corpus}: the record runs to {info.get('record_to') or covered}{checked}. {info.get('record_note', '')}".rstrip())
    if info.get('provisional'):
        out.append(f"{corpus}: provisional upload: {info['provisional']}.")
    if info.get('history') == 'as-enacted':
        out.append(f"{corpus}: each law is shown as first published; later amendments are not applied, so this is not "
                   "the text in force on a date.")
    if info.get('history') == 'replayed':
        checked = f" {info['verification']}" if info.get('verification') else ''
        out.append(f"{corpus}: earlier versions were rebuilt by applying each amending act, not read from an official text.{checked}")
    if info.get('history') == 'current-only' and (not covered or date < covered):
        out.append(f"{corpus}: this record holds only the current text; an earlier date shows each law as last updated, not as it was in force then.")
    return out


def explain_missing(date: str, path: str) -> str:
    """Why there is no text: a mistyped path, before the record, not yet in force, or repealed."""
    corpus, rel = corpus_of(path)
    cwd = corpus_dir(corpus)
    if not git('log', '-1', '--format=%H', 'HEAD', '--', rel, cwd=cwd).strip():
        names = git('ls-tree', '-r', '--name-only', 'HEAD', cwd=cwd).split()
        close = difflib.get_close_matches(rel, names, n=3, cutoff=0.6)
        hint = f" Did you mean {', '.join(f'{corpus}/{c}' for c in close)}?" if close else ''
        return f'{path} is not in this record at any date.{hint}'
    h = history(path)
    if not h:
        return f'{path} has no dated change in the record.'
    if date < h[0]['in_force'] and h[0]['kind'] == 'baseline':
        return (f"{path} is not in the record on {date}: the record starts on {h[0]['in_force']} ({h[0]['law']}), "
                f"which is where this record starts, not the day it came into force.")
    if date < h[0]['in_force']:
        return f"{path} was not yet in force on {date}. It first appears on {h[0]['in_force']} ({h[0]['law']})."
    gone = [x for x in h if x['in_force'] <= date][-1]
    back = next((x for x in h if x['in_force'] > date), None)
    again = f" It is in force again from {back['in_force']} ({back['law']})." if back else ''
    return f"{path} was not in force on {date}: it was removed on {gone['in_force']} ({gone['law']}).{again}"


USAGE = {'world': 1, 'show': 2, 'blame': 2, 'words': 2, 'today': 2, 'diff': 3, 'log': 1, 'laws': 2}


def day(value: str) -> str:
    """An ISO date, checked. "today" is allowed; times are dropped."""
    import datetime as dt
    if value == 'today':
        return dt.date.today().isoformat()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}(T.*)?', value):
        try:
            return dt.date.fromisoformat(value[:10]).isoformat()
        except ValueError:
            pass
    raise SystemExit(f'Not a date: {value!r}. Use YYYY-MM-DD, for example 2022-05-01.')


def norm(path: str) -> str:
    return path.replace('\\', '/').removeprefix('./').strip('/')


# The trailers corpora use for a law's other dates. The German keys are ASCII since its 2026-10-28 rebuild; the
# newer corpora use Adopted, Proclaimed and Published (corpus.json `dates.other_trailers`).
ENACTED = ('Enacted', 'Made', 'Beschlossen', 'Adopted', 'Dated')
PUBLISHED = ('Published', 'Proclaimed', 'Printed-in', 'Verkuendet', 'Verkündet')
ISO_DAY = re.compile(r'\d{4}-\d{2}-\d{2}')


def history(path: str) -> list[dict]:
    """Every dated change to a file, oldest first, with its dates: the reader's "follow" list.

    A change is dated by the corpus's in-force trailer; failing that by its baseline or correction trailer (Malta's
    consolidated versions, Switzerland's first versions and corrections), which must hold an ISO date (Liechtenstein's
    `Consolidated:` is a URL, not a date); failing that, a printing that differs from the laws behind it (US
    "Printed text differs") is dated by its commit. Documentation commits are left out."""
    corpus, rel = corpus_of(path)
    key = ('history', f'{corpus}@{tip(corpus)}:{rel}')
    if key not in _CACHE:
        _CACHE[key] = _history(corpus, rel)
    return [dict(h) for h in _CACHE[key]]  # type: ignore[union-attr]


CORRECTS = re.compile(r'(\d{4}-\d{2}-\d{2})(?:\s*\.\.\s*(\d{4}-\d{2}-\d{2})?)?')


def _history(corpus: str, rel: str) -> list[dict]:
    info = corpus_info(corpus)
    trailer = info['in_force_trailer']
    dated_by = [(info[k], kind) for k, kind in (('baseline_trailer', 'baseline'), ('correction_trailer', 'correction')) if info.get(k)]
    raw = git('log', '--reverse', '--format=%H%x1f%an%x1f%aI%x1f%B%x1e', '--', rel, cwd=corpus_dir(corpus))
    # The tree's own dating of each corpus commit: it dates a starting edition with no trailer of its own (the US
    # 2017 edition) as the baseline, so a file that starts there is not reported as starting with its first amendment.
    placed = {e.corpus_commit: e for e in corpus_events(corpus)}
    out = []
    for record in raw.split('\x1e'):
        if not record.strip():
            continue
        sha, author, date, body = record.strip('\n').split('\x1f', 3)
        t = trailers(body)
        if t.get('Kind', '').strip().lower() == 'documentation' or author == 'Lexifina':
            continue
        in_force, kind = t.get(trailer), 'law'
        for key, k in dated_by:
            if not in_force and key in t and ISO_DAY.match(t[key]):
                in_force, kind = t[key][:10], k
        if not in_force and 'Printed-in' in t:
            in_force, kind = date[:10], 'printing'
        corrects = CORRECTS.search(t.get('Corrects', ''))
        if not in_force and corrects:  # a correction appended at the tip: dated by the first day it corrects
            in_force, kind = corrects.group(1), 'correction'
        if not in_force and sha in placed and placed[sha].kind == 'baseline':
            in_force, kind = placed[sha].in_force, 'baseline'
        if not in_force:
            continue  # documentation and an undated starting edition
        # A publisher's correction is never a law, whatever In-force says (In-force only places it in the order).
        if t.get('Kind', '').strip().lower() == 'correction' or (info.get('correction_trailer') or '') in t:
            kind = 'correction'
        elif t.get('Kind', '').strip().lower() in ('baseline', 'consolidated', 'current', 'current-only'):
            kind = 'baseline'  # a starting text the corpus labels as such (Turkey: Kind: consolidated)
        row = {'commit': sha, 'law': author, 'in_force': in_force[:10], 'kind': kind,
               'enacted': next((t[k] for k in ENACTED if k in t), None),
               'published': next((t[k] for k in PUBLISHED if k in t), None)}
        if kind == 'correction' and 'Corrects' in t:
            # Corrects: <act> <from>..<to>, the end open when it runs to the present.
            row.update({'corrects': t['Corrects'], 'until': corrects.group(2) if corrects else None,
                        'supersedes': t.get('Supersedes'), 'reason': t.get('Reason')})
        out.append(row)
    seen = {r['commit'] for r in out}
    extra = [c for c in corrections(corpus) if rel in c['files'] and c['commit'] not in seen]
    if extra:
        out += [{'commit': c['commit'], 'law': c['law'], 'in_force': c['from'], 'kind': 'correction', 'enacted': None,
                 'published': None, 'corrects': c['corrects'], 'until': c['to'], 'supersedes': c['supersedes'],
                 'reason': c['reason']} for c in extra]
        order = {e.corpus_commit: i for i, e in enumerate(corpus_events(corpus))}
        out.sort(key=lambda r: order.get(r['commit'], len(order)))
    return out


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)
    sys.stdout.reconfigure(encoding='utf-8')  # law names and texts are not ASCII; Windows consoles default to cp1252
    sys.stderr.reconfigure(encoding='utf-8')
    command, args = argv[0], argv[1:]
    if command not in USAGE or len(args) < USAGE[command]:
        raise SystemExit(__doc__)
    # Dates are checked and paths accept ./ and Windows backslashes; caveats go to stderr so the text stays clean.
    if command in ('world', 'show', 'blame', 'words', 'today', 'laws'):
        args[0] = day(args[0])
    if command in ('diff', 'laws'):
        args[1] = day(args[1])
    if command in ('show', 'blame', 'words', 'today'):
        args[1] = norm(args[1])
    if command == 'diff':
        args[0], args[2] = day(args[0]), norm(args[2])
    if command == 'log':
        args[0] = norm(args[0])
    note = lambda lines: [print(f'Note: {line}', file=sys.stderr) for line in lines]  # noqa: E731
    if command == 'world':
        events = timeline()
        print(f'The law on {args[0]}' + ('' if root_on(args[0], events) else ' (nothing in force yet)') + ':')
        for corpus in manifest()['corpora']:
            last = [e for e in events if e.corpus == corpus['path'] and e.in_force <= args[0] and e.kind != 'documentation']
            state = (f'{last[-1].law}, in force {last[-1].in_force}' if last else 'not yet in the record') \
                if (ROOT / corpus['path'] / '.git').exists() else 'not checked out'
            print(f"  {corpus['path']:<24} {state}")
        note(c for corpus in manifest()['corpora'] for c in caveats(args[0], corpus['path'], events) if 'runs to' in c)
    elif command in ('show', 'blame', 'words'):
        corpus, _ = corpus_of(args[1])
        note(caveats(args[0], corpus))
        if text_on(args[0], args[1]) is None:
            raise SystemExit(explain_missing(args[0], args[1]))
        if command == 'show':
            print(text_on(args[0], args[1]), end='')
        elif command == 'blame':
            # git blame prints commit dates, which are 1970 for laws before 1970; print the in-force date instead.
            dates = {h['commit']: h['in_force'] for h in history(args[1])}
            for commit, law, line in blame_rows(args[0], args[1]):
                print(f"{dates.get(commit, 'start of record'):<15} {law[:52]:<52} | {line}")
        else:
            runs = words_on(args[0], args[1])
            keys: dict[str, int] = {}
            for law, _ in runs:
                keys.setdefault(law, len(keys) + 1)
            print(''.join(f'[{keys[law]}]{text}' for law, text in runs))
            print()
            for law, n in keys.items():
                print(f'[{n}] {law}')
    elif command == 'today':
        corpus, _ = corpus_of(args[1])
        note(caveats(args[0], corpus))
        answer, diff = today_diff(args[0], args[1])
        print(f'{args[1]} on {args[0]}: {answer}.')
        if diff:
            print(diff, end='')
    elif command == 'diff':
        corpus, _ = corpus_of(args[2])
        note(caveats(args[0], corpus) + caveats(args[1], corpus))
        print(diff_between(args[0], args[1], args[2]) or 'No change between those dates.')
    elif command == 'log':
        if not history(args[0]):
            raise SystemExit(explain_missing('9999-12-31', args[0]))
        for h in history(args[0]):
            dates = '; '.join(f'{k} {h[k]}' for k in ('enacted', 'published') if h[k])
            label = {'baseline': 'version of', 'correction': 'corrected', 'printing': 'printed'}.get(h.get('kind'), 'in force')
            print(f"{label} {h['in_force']}  {h['law']}" + (f'  ({dates})' if dates else ''))
    elif command == 'laws':
        if args[0] > args[1]:
            args[0], args[1] = args[1], args[0]
        prefix = args[2] if len(args) > 2 else ''
        for e in timeline():
            if args[0] <= e.in_force <= args[1] and e.corpus.startswith(prefix) and e.kind not in ('documentation', 'printing'):
                print(f'{e.in_force}  {e.corpus:<24} {e.law}')
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
