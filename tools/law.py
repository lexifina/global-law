#!/usr/bin/env python3
"""Read the global law tree on any date. Standard library only.

Each corpus is read at the commit the tree pins, from its own history: every commit's In-force trailer says when its
text took force, so the text on a date is the version of each file with the latest in-force date on or before it,
whatever order the commits were made in. Nothing is checked out: the tools read the pinned commits straight from the
submodules. The first read of a corpus indexes its history once (kept in the tree's git folder, global-law-cache);
later reads load that index, and a pin that moves forward adds only its new commits.

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
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    _trees_alive()  # a swept tree store would fail every git command naming it as an alternate
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8')
    if check and done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


_CACHE: dict[tuple[str, str], object] = {}


def _head() -> str:
    """The tree's HEAD, asked of git at most once a second: every cache is keyed by it, so a long-running reader
    (the MCP server) still sees a new commit, without a git process for every lookup."""
    import time
    now = time.monotonic()
    seen = _CACHE.get(('head-at', ''))
    if not seen or now - seen[0] > 1.0:  # type: ignore[index]
        _CACHE[('head-at', '')] = (now, _head_from_files() or git('rev-parse', 'HEAD').strip())
    return _CACHE[('head-at', '')][1]  # type: ignore[index]


def _gitdirs(top: Path) -> tuple[Path, Path] | None:
    """A checkout's git folder and the folder it shares objects and refs with (the same unless it is a worktree),
    read from .git: a folder, or a file naming one (submodules and worktrees). None when there is neither."""
    try:
        dot = top / '.git'
        gitdir = dot if dot.is_dir() else (top / dot.read_text().split('gitdir:', 1)[1].strip()).resolve()
        common = (gitdir / (gitdir / 'commondir').read_text().strip()).resolve() if (gitdir / 'commondir').exists() else gitdir
        return gitdir, common
    except (OSError, IndexError):
        return None


def _head_from_files(top: Path = ROOT) -> str | None:
    """HEAD read from the git folder's files (HEAD, the branch's ref, packed-refs), which costs no process: starting
    git is the slowest part of a short read on some machines. None when the layout is not the plain one."""
    try:
        dirs = _gitdirs(top)
        if dirs is None:
            return None
        gitdir, common = dirs
        head = (gitdir / 'HEAD').read_text().strip()
        if re.fullmatch(r'[0-9a-f]{40}', head):
            return head
        if not head.startswith('ref: '):
            return None
        ref = head[5:].strip()
        for base in (gitdir, common):
            if (base / ref).is_file():
                sha = (base / ref).read_text().strip()
                return sha if re.fullmatch(r'[0-9a-f]{40}', sha) else None
        for line in (common / 'packed-refs').read_text().splitlines():
            if line.endswith(' ' + ref) and re.fullmatch(r'[0-9a-f]{40}', line[:40]):
                return line[:40]
    except (OSError, IndexError):
        return None
    return None


def _store() -> Path:
    """The tree's cache folder (global-law-cache in its git folder), found without a git process when it can be."""
    if ('store', '') not in _CACHE:
        dirs = _gitdirs(ROOT)
        _CACHE[('store', '')] = (dirs[1] / 'global-law-cache' if dirs else
                                 Path(git('rev-parse', '--path-format=absolute', '--git-path', 'global-law-cache').strip()))
    return _CACHE[('store', '')]  # type: ignore[return-value]


ROOT_FILES = ('manifest.json', 'data/moved-paths.tsv', 'data/future-pins.tsv', 'data/legacy-dates.tsv')


def _root() -> dict:
    """What every command reads from the tree's HEAD commit: manifest.json, data/moved-paths.tsv,
    data/future-pins.tsv and data/legacy-dates.tsv (None where missing), the submodule pins (`git ls-tree -r -d`) and .gitmodules' paths and
    urls. All of it depends on the commit alone, so it is kept on disk (global-law-cache/root-<commit>.json): after
    the first read of a commit, a command starts no git process for it, where it used to start five."""
    head = _head()
    key = ('root', head)
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    path = _store() / f'root-{head}.json'
    data = None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('v') != 1 or data.get('head') != head or not set(ROOT_FILES) <= set(data.get('files') or {}):
            data = None  # another version's cache, or one written before a file was added to ROOT_FILES
    except (OSError, ValueError):
        data = None
    if data is None:
        files = {}
        for name in ROOT_FILES:
            done = subprocess.run(['git', 'show', f'{head}:{name}'], cwd=ROOT, capture_output=True, encoding='utf-8')
            files[name] = done.stdout if done.returncode == 0 else None
        if files['manifest.json'] is None:
            raise RuntimeError(f'git show {head}:manifest.json: the tree has no manifest.json')
        data = {'v': 1, 'head': head, 'files': files, 'gitlinks': git('ls-tree', '-r', '-d', head),
                'modules': git('config', '--blob', f'{head}:.gitmodules', '--get-regexp', r'^submodule\..*\.(path|url)$',
                               check=False)}
        try:  # a cache: where it cannot be written, the next command reads the commit again
            import os
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
            tmp.write_text(json.dumps(data), encoding='utf-8')
            os.replace(tmp, path)
            for old in sorted(path.parent.glob('root-*.json'), key=lambda f: f.stat().st_mtime)[:-8]:
                old.unlink(missing_ok=True)  # only the last few commits' (pins move every few minutes)
        except OSError:
            pass
    _CACHE[key] = data
    return data


def manifest() -> dict:
    key = ('manifest', _head())
    if key not in _CACHE:
        _CACHE[key] = with_unlisted(json.loads(_root()['files']['manifest.json']))
    return _CACHE[key]  # type: ignore[return-value]


def with_unlisted(m: dict) -> dict:
    """manifest.json with every corpus the tree pins but does not list. Since 2 November 2026 the tree only adds
    submodules and moves pins, and manifest.json is no longer rewritten, so most corpora are in .gitmodules alone
    (603 of 710 on 3 November). Each is described by its own corpus.json, else data/repo.json and jurisdiction.json
    (what build.py repos ship), when it is checked out; else by its path. Defaults: In-force trailer, no citation rule."""
    listed = {c['path'] for c in m.get('corpora', [])}
    pins = [l.split(None, 3)[3] for l in _root()['gitlinks'].splitlines() if l.split(None, 3)[1] == 'commit']
    urls: dict[str, str] = {}
    paths: dict[str, str] = {}
    for line in _root()['modules'].splitlines():
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
        # The checked-out file: a corpus's own description, read without a git process per corpus.
        try:
            return json.loads((cwd / name).read_text(encoding='utf-8'))
        except (OSError, ValueError):
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
    commits now only date a corpus commit that carries no date of its own (legacy_dates). A law that only changed
    acts already ended (ended_rows) is left out, as history() leaves its versions out."""
    corpora = tuple(c['path'] for c in manifest()['corpora'])
    key = ('timeline', _head() + '|' + ','.join(corpora))
    recheck_missing_futures()
    if key not in _CACHE:
        events = [e for c in corpora for e in law_events(c)]
        events.sort(key=lambda e: e.in_force)  # stable: each corpus keeps its own order within a day
        _CACHE[key] = events
    return list(_CACHE[key])  # type: ignore[arg-type]


def tip(corpus: str) -> str | None:
    """The corpus commit the tree pins at HEAD."""
    key = ('tips', _head())
    if key not in _CACHE:
        out = _root()['gitlinks']
        _CACHE[key] = {path: sha for mode, kind, sha, path in (l.split(None, 3) for l in out.splitlines()) if kind == 'commit'}
    return _CACHE[key].get(corpus)  # type: ignore[union-attr]


def reachable_tip(corpus: str) -> str:
    """The commit the tree pins for a corpus, or the checkout's own HEAD if it has not fetched that commit yet."""
    key = ('reachable', f'{corpus}@{tip(corpus)}')
    if key not in _CACHE:
        sha = tip(corpus)
        ok = bool(sha) and _has_commit(corpus, corpus_dir(corpus), sha)
        _CACHE[key] = sha if ok else 'HEAD'
    return _CACHE[key]  # type: ignore[return-value]


def corpus_events(corpus: str) -> list[Event]:
    """The dated commits of one corpus, in its own history order, read at the commit the tree pins. Empty when the
    corpus is not checked out, or its checkout is unfinished (unreadable() names it). A commit is dated as history()
    dates it; one with no date of its own takes the date the tree's per-law history gave it (legacy_dates);
    documentation commits are kept with kind 'documentation'. Read from the corpus index (_index)."""
    cwd = ROOT / corpus
    if not (cwd / '.git').exists():
        return []
    if not _readable(corpus, cwd):
        return []  # an unfinished checkout: left out and named (unreadable()), so it does not stop every other corpus
    if not _full_history(corpus, cwd):
        return []  # left out and named (shallow()), so it does not stop every other corpus
    pin = tip(corpus)
    if pin and not _has_commit(corpus, cwd, pin):
        # The checkout is behind the tree (a pull without `git submodule update`, the usual state while pins move
        # every few minutes): left out of whole-tree reads and named (behind()); a read of this corpus alone stops.
        _CACHE[('behind', corpus)] = pin
        return []
    _CACHE.pop(('behind', corpus), None)
    ix = _index(corpus)
    key = ('corpus-events', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        _CACHE[key] = [Event(r[0], corpus, r[0], r[1], r[5], r[4], r[3]) for r in ix['rows'] if r[5]]
    return _CACHE[key]  # type: ignore[return-value]


def law_events(corpus: str) -> list[Event]:
    """corpus_events less the laws all of whose versions the act-end rule keeps out of force (ended_rows): history()
    gives none of their versions, so the timeline and `laws` do not say they took force. corpus_events itself keeps
    them, as finding them reads every file's versions, which a read of one provision does not need."""
    events = corpus_events(corpus)
    void = ended_rows(corpus) if events else frozenset()
    if not void:
        return events
    rows = _index(corpus)['rows']
    gone = {rows[n][0] for n in void}
    return [e for e in events if e.corpus_commit not in gone]


def corrections(corpus: str) -> list[dict]:
    """The corrections appended to a corpus (Kind: correction, with Corrects: <act> <from>..<to>), in history order.
    Each sets the files it names (one Files: trailer per corpus-relative path) to the corrected text for those dates,
    whether or not git shows a change for a file: a late-found version can equal the text the tip already has.
    Act-path: names the act, whose next ordinary commit ends an open range."""
    if not corpus_events(corpus):
        return []
    return [r[9] for r in _index(corpus)['rows'] if r[9]]


def act_next(corpus: str, paths: list[str], after: str) -> str | None:
    """The in-force date of the act's next ordinary commit (not a correction, not documentation) after `after`: the
    first commit by in-force date that touches any of `paths` (folders or files)."""
    paths = [p for p in paths if p]
    if not paths:
        return None
    ix = _index(corpus)
    key = ('act-next', f"{corpus}@{_at(ix)}:" + '\x1f'.join(paths))
    if key not in _CACHE:
        found = _act_days(corpus, ix)
        days: set = set()
        for p in paths:
            days.update(found.get(p, ()))
        _CACHE[key] = sorted(days)
    days = _CACHE[key]
    import bisect
    i = bisect.bisect_right(days, after)  # type: ignore[arg-type]
    return days[i] if i < len(days) else None  # type: ignore[index,arg-type]


def _act_days(corpus: str, ix: dict) -> dict[str, list[str]]:
    """Every file, and every folder above it -> the sorted in-force days of the ordinary commits that touch it, read
    from the index in one pass: act_next looks an act up here instead of walking every file for each act."""
    key = ('act-days', f"{corpus}@{ix['pin']}")
    if key not in _CACHE:
        rows = ix['rows']
        found: dict[str, set] = {}
        for rel, versions in ix['files'].items():
            days = {rows[o][5] for o, _, _ in versions if rows[o][5] and rows[o][4] not in ('correction', 'documentation')}
            if days:
                parts = rel.split('/')
                for n in range(1, len(parts) + 1):
                    found.setdefault('/'.join(parts[:n]), set()).update(days)
        _CACHE[key] = {p: sorted(d) for p, d in found.items()}
    return _CACHE[key]  # type: ignore[return-value]


def correction_end(corpus: str, fix: dict, rel: str) -> str:
    """The last day a correction applies: its own end, or for an open range the day before the act's next ordinary
    commit (the act is Act-path:, else the folders of its Files:, else the folder of the file read). Never past the
    end data/acts.json gives the file's act (correction_cap)."""
    cap = correction_cap(corpus, rel, fix['from']) or '9999-12-31'  # never past the file's act's end
    if fix.get('to'):
        return min(fix['to'], cap)
    folder = lambda f: f.rsplit('/', 1)[0] if '/' in f else f  # noqa: E731
    paths = [fix['act_path']] if fix.get('act_path') else sorted({folder(f) for f in fix['files']}) or [folder(rel)]
    nxt = act_next(corpus, paths, fix['from'])
    if not nxt:
        return cap
    import datetime as dt
    return min((dt.date.fromisoformat(nxt) - dt.timedelta(days=1)).isoformat(), cap)


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
    starting edition with no trailer of its own (the US 2017 edition). That history no longer grows, so the dates it
    gives commits with no date of their own are shipped in data/legacy-dates.tsv; the root is read only without it."""
    key = ('legacy', _head())
    if key not in _CACHE:
        found: dict[str, dict[str, tuple[str, str]]] = {}
        shipped = _root()['files']['data/legacy-dates.tsv']
        if shipped is not None:
            for line in shipped.splitlines():
                if line and not line.startswith('#'):
                    c, sha, day_, kind = line.split('\t')[:4]
                    found.setdefault(c, {})[sha] = (day_, kind)
        else:
            if _shallow(ROOT):  # these dates come from the tree's own history: a shallow root would drop them silently
                raise SystemExit('This clone of the tree is shallow (--depth), so the dates its history gives some corpus '
                                 'commits cannot be read. Run: git fetch --unshallow')
            raw = git('log', '--first-parent', '--reverse', '--format=%(trailers:only,unfold)%x1e')
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
    # A corpus that moved or withdrew files reads a past date under the files' current paths, which only a built tree
    # gives: its commit-order prefix still holds the old paths and the withdrawn acts.
    ix = _index(corpus)
    # A forked future branch read beside main (future_pins) is not a prefix of main's history: only a built tree
    # holds main's files and the branch's versions together.
    if ix.get('future') and not ix['future']['linear']:
        return False
    # An act data/acts.json records as ended keeps its files in the commit-order prefix: only a built tree ends them.
    # A file whose text is a repeal notice is in the prefix too: only a built tree leaves it out (file_index).
    return (not corrections(corpus) and not ix.get('moves') and not ix.get('withdrawn')
            and not any(e['day'] for e in act_ends(corpus).values()) and not notice_blobs(corpus))


def _unquote(path: str) -> str:
    """A path git printed in C quotes (non-ASCII, when core.quotepath is on) back to the name itself."""
    if not path.startswith('"'):
        return path
    return path[1:-1].encode('latin-1', 'backslashreplace').decode('unicode_escape').encode('latin-1').decode('utf-8')


def file_index(corpus: str) -> tuple[dict, list]:
    """Every version of every file of a corpus, from the corpus index: path -> [(in force, order, blob or None for a
    deletion, mode)] for ordinary commits, and the corrections laid over them as [(fix, order, {path: (blob, mode)})]."""
    ix = _index(corpus)
    key = ('file-index', f"{corpus}@{_at(ix)}")
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    rows = ix['rows']
    index: dict[str, list] = {}
    touched: dict[int, dict] = {}
    notices = notice_blobs(corpus)
    for path, versions in ix['files'].items():
        for order, blob, mode in versions:
            r = rows[order]
            if blob in notices:  # a repeal notice ends the file there, as a deletion does (history() reads it so too)
                blob = None
            if r[9]:
                touched.setdefault(order, {})[path] = (blob, mode)
            elif r[5] and r[4] != 'documentation':
                index.setdefault(path, []).append((r[5], order, blob, mode))
    if act_ends(corpus):
        for path, versions in index.items():
            got = _cut(corpus, path)
            if got:
                end, cut = got
                mode = versions[-1][3]
                # After the end, only a version after_end lets re-enact the file (history() applies the same rule).
                versions[:] = [v for v in versions if after_end(corpus, end, cut, v[0], v[1], v[2], path) is None]
                versions.append((cut[0], cut[1], None, mode))
    cwd = corpus_dir(corpus)
    overlays = []
    wanted = {order: [f for f in r[9]['files'] if f not in touched.get(order, {})] for order, r in enumerate(rows) if r[9]}
    at = _named_at(ix, cwd, wanted)
    for order, r in enumerate(rows):
        fix = r[9]
        if not fix:
            continue
        files = dict(touched.get(order, {}))
        files.update(at.get(order, {}))  # named but unchanged: their text at the correction commit is the tip's
        if fix['files']:
            files = {p: v for p, v in files.items() if p in fix['files']}
        overlays.append((fix, order, files))
    _CACHE[key] = (index, overlays)
    return index, overlays


def _named_at(ix: dict, cwd: Path, wanted: dict[int, list[str]]) -> dict[int, dict[str, tuple]]:
    """row -> {path: (blob, mode)} for the paths a correction names but does not change: each as `git ls-tree` lists
    it at that commit. One `git cat-file --batch-check` gives every blob; the mode is the file's own last version in
    the index when that version has the same blob. Anything else (a folder, a path moved or withdrawn, a version the
    index does not hold) is asked of `git ls-tree`, one commit at a time, as before."""
    rows = ix['rows']
    queries = [(order, f) for order, named in wanted.items() for f in named]
    out: dict[int, dict[str, tuple]] = {}
    if not queries:
        return out
    odd = set(ix.get('moves', {})) | set(ix.get('moves', {}).values()) | set(ix.get('withdrawn', {}))
    raw = subprocess.run(['git', 'cat-file', '--batch-check=%(objectname) %(objecttype)'], cwd=cwd, capture_output=True,
                         input=''.join(f'{rows[o][0]}:{f}\n' for o, f in queries).encode('utf-8'))
    answers = raw.stdout.decode('utf-8', 'replace').splitlines() if not raw.returncode else []
    slow: dict[int, list[str]] = {}
    for n, (order, f) in enumerate(queries):
        answer = answers[n] if len(answers) == len(queries) else ''
        if answer == f'{rows[order][0]}:{f} missing':
            continue  # not in the tree at that commit: ls-tree lists nothing
        sha, _, kind = answer.partition(' ')
        last = None
        if kind == 'blob' and len(sha) == 40 and f not in odd:
            last = next((v for v in reversed(ix['files'].get(f, [])) if v[0] < order), None)
        if last is not None and last[1] == sha:
            out.setdefault(order, {})[f] = (sha, last[2])
        else:
            slow.setdefault(order, []).append(f)
    for order, named in slow.items():
        for line in git('ls-tree', rows[order][0], '--', *named, cwd=cwd).splitlines():
            meta, path = line.split('\t', 1)
            mode, _, blob = meta.split()
            out.setdefault(order, {})[_unquote(path)] = (blob, mode)
    return out


_TREES: dict = {'dir': None, 'beat': 0.0}
TREE_STORE_IDLE = 86400  # a store whose owner is gone and whose heartbeat is older than this is swept
TREE_STORE_BEAT = 600  # seconds between heartbeats while the owner is in use


def _pid_alive(pid: int) -> bool:
    """Whether a process is running, without signalling it (os.kill(pid, 0) on Windows would end it)."""
    import os
    if pid <= 0:
        return False
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5  # access denied: it exists
        try:
            code = wintypes.DWORD()
            return bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259  # STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True


def _sweep_tree_stores() -> None:
    """Remove tree stores left by killed processes: one whose owner (its `owner` file) is no longer running and whose
    heartbeat is over a day old. A store whose owner still runs stays, however long it has been idle."""
    import tempfile
    import time
    for old in Path(tempfile.gettempdir()).glob('global-law-trees-*'):
        try:
            owner = old / 'owner'
            try:
                pid = int(owner.read_text(encoding='utf-8').split()[0])
                beat = owner.stat().st_mtime
            except (OSError, ValueError, IndexError):  # a store from before owner files, or one just being made
                pid, beat = 0, old.stat().st_mtime
            if pid and _pid_alive(pid):
                continue
            if time.time() - beat > TREE_STORE_IDLE:
                _rmtree(old)
        except OSError:
            pass


def _make_tree_store(d: Path) -> None:
    import os
    (d / 'objects').mkdir(parents=True, exist_ok=True)
    (d / 'owner').write_text(f'{os.getpid()}\n', encoding='utf-8')
    os.environ['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = str(d / 'objects')


def _tree_store() -> Path:
    """A private object directory for the trees this process builds. Every git command reads it as an alternate,
    so a built tree can be grepped and listed like a commit; nothing is written into the clone. The store names its
    owner (an `owner` file with the pid, touched as a heartbeat while in use), so another process's sweep leaves it
    alone however long this process sits idle; if it is removed anyway, it is made again and the trees rebuilt."""
    import time
    if _TREES['dir'] is None:
        import atexit
        import tempfile
        _sweep_tree_stores()
        d = Path(tempfile.mkdtemp(prefix='global-law-trees-'))
        _make_tree_store(d)
        atexit.register(_rmtree, d)
        _TREES['dir'], _TREES['beat'] = d, time.time()
        return d
    d = _TREES['dir']
    if not (d / 'objects').is_dir() or not (d / 'owner').is_file():
        _make_tree_store(d)  # swept by another process: the same place, so git's alternate path holds again
        for k in [k for k in _CACHE if k[0] == 'tree']:  # its trees went with it; built again when next asked
            _CACHE.pop(k)
        _restart_readers()
        _TREES['beat'] = time.time()
    elif time.time() - _TREES['beat'] > TREE_STORE_BEAT:
        try:
            import os
            os.utime(d / 'owner')
            os.utime(d)
        except OSError:
            pass
        _TREES['beat'] = time.time()
    return d


def _trees_alive() -> None:
    """Check the tree store (made again if swept) and keep its heartbeat, where a process has one."""
    if _TREES['dir'] is not None:
        _tree_store()


def _rmtree(d: Path) -> None:
    """Remove a folder git wrote into: its objects are read-only, which Windows will not delete as they are."""
    import os
    import shutil
    import stat

    def writable(func, path, _):
        try:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            func(path)
        except OSError:
            pass
    try:
        shutil.rmtree(d, onerror=writable)
    except OSError:
        pass


def corpus_tree(date: str, corpus: str) -> str | None:
    """The corpus as in force on `date`, as something git reads like a commit (grep, ls-tree, show, diff): each file
    at the version file_commit would pick, corrections included. A corpus in in-force order is its commit-order
    prefix; any other (older acts appended after the tip, corrections) is a tree built from file_index for the date."""
    if in_order(corpus):
        return corpus_on(date, corpus)
    key = ('tree', f'{corpus}@{_at(_index(corpus))}@{date}')
    _trees_alive()  # a swept store drops the cached trees, so the one asked for is built again below
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
    try:  # the tree object is written; its index is not needed again (1-15 MB a date on a large corpus)
        os.unlink(env['GIT_INDEX_FILE'])
    except OSError:
        pass
    _CACHE[key] = sha
    return sha


def moved_paths() -> dict[str, str]:
    """Corpus folders the tree has moved (old path -> new), from data/moved-paths.tsv: a path given in the old form
    still reads, from the corpus's new place."""
    key = ('moved', _head())
    if key not in _CACHE:
        found: dict[str, str] = {}
        shipped = _root()['files']['data/moved-paths.tsv']
        if shipped is not None:
            for line in shipped.splitlines():
                if line and not line.startswith('#'):
                    old, new = line.split('\t')[:2]
                    found[old] = new
        _CACHE[key] = found
    return _CACHE[key]  # type: ignore[return-value]


def moved(path: str) -> str:
    """A path with a moved corpus folder at its start given its new place; any other path as it is."""
    for old, new in moved_paths().items():
        if path == old or path.startswith(old + '/'):
            return new + path[len(old):]
    return path


def corpus_of(path: str) -> tuple[str, str]:
    path = moved(path)
    for corpus in sorted(manifest()['corpora'], key=lambda c: -len(c['path'])):
        prefix = corpus['path'] + '/'
        if path.startswith(prefix) and path[len(prefix):]:
            return corpus['path'], path[len(prefix):]
        if path == corpus['path'] or path == prefix:
            raise SystemExit(f"{corpus['path']} is a whole corpus, not one provision: give a file inside it, for example "
                             f"{corpus['path']}/<act>/<provision>.md (git -C {corpus['path']} ls-files lists them)")
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
        raise SystemExit(f'{corpus} is not checked out; run: {countries_cmd()} add {corpus}')
    if not _readable(corpus, path):
        raise SystemExit(_UNREADABLE.format(corpus=corpus))
    _require_full_history(corpus, path)
    return path


_UNREADABLE = ('{corpus} is checked out but has no commit yet (an unfinished or interrupted clone). '
               'Run: git submodule update --init -- {corpus}')


def _readable(corpus: str, cwd: Path) -> bool:
    """Whether a corpus checkout has a commit to read. A clone that was interrupted, or is still running, has a .git
    but no HEAD; reading every corpus (timeline, world, laws) would then stop on it, so it is left out and named."""
    key = ('readable', corpus)
    if not _CACHE.get(key):  # asked again until it is readable: a clone still running finishes later
        head = _head_from_files(cwd)  # a checked-out commit; else (an unborn branch, an odd layout) git decides
        _CACHE[key] = (_has_commit(corpus, cwd, head) if head else
                       subprocess.run(['git', 'rev-parse', '-q', '--verify', 'HEAD^{commit}'], cwd=cwd,
                                      capture_output=True).returncode == 0)
    return bool(_CACHE[key])


def unreadable() -> list[str]:
    """The corpora left out of a whole-tree read because their checkout has no commit yet."""
    return sorted(k[1] for k, ok in _CACHE.items() if k[0] == 'readable' and not ok)


_BEHIND = ('{corpus} is behind the tree: its checkout does not have the commit the tree pins ({pin}), so it is left '
           'out. Run: git submodule update --init -- {corpus}  (or for every corpus: git submodule update --init)')


def behind() -> dict[str, str]:
    """The corpora left out of a whole-tree read because their checkout lacks the commit the tree pins: corpus ->
    that commit."""
    return {k[1]: v for k, v in _CACHE.items() if k[0] == 'behind'}  # type: ignore[misc]


def _shallow(cwd: Path) -> bool:
    dirs = _gitdirs(cwd)
    if dirs is not None and (dirs[1] / 'objects').is_dir():  # git's own test: a non-empty shallow file
        f = dirs[1] / 'shallow'
        return f.is_file() and f.stat().st_size > 0
    done = subprocess.run(['git', 'rev-parse', '--is-shallow-repository'], cwd=cwd, capture_output=True, encoding='utf-8')
    return done.stdout.strip() == 'true'


def _full_history(corpus: str, cwd: Path) -> bool:
    """Whether a corpus's checkout holds its whole history: not shallow, or shallow at commits that have no parent
    (a --depth clone of a corpus with fewer commits than the depth holds it all)."""
    key = ('full-history', corpus)
    if key not in _CACHE:
        ok = not _shallow(cwd)
        if not ok:
            dirs = _gitdirs(cwd)
            f = (dirs[1] / 'shallow') if dirs else None
            cut = f.read_text().split() if f and f.is_file() else []
            # A boundary commit's own object still names its parents; one that names none is a root.
            ok = bool(cut) and all(not re.search(r'^parent ', git('cat-file', 'commit', c, cwd=cwd).split('\n\n', 1)[0],
                                                     re.M)
                                   for c in cut)
        _CACHE[key] = ok
    return _CACHE[key]  # type: ignore[return-value]


_SHALLOW = ('{corpus} is a shallow clone (--depth), so its history is cut and its dates cannot be read; it is left '
            'out. Run: git -C {corpus} fetch --unshallow')


def shallow() -> list[str]:
    """The corpora left out of a whole-tree read because their clone is shallow."""
    return sorted(k[1] for k, ok in _CACHE.items() if k[0] == 'full-history' and not ok)


def _require_full_history(corpus: str, cwd: Path) -> None:
    """Dates come from a corpus's whole history, so a shallow clone (--depth) would give wrong answers, not an error:
    a provision in force reads as never changed or as repealed. Stop with the command that fixes it instead."""
    if not _full_history(corpus, cwd):
        raise SystemExit(f'{corpus} is a shallow clone (--depth), so its history is cut and its dates cannot be read. '
                         f'Run: git -C {corpus} fetch --unshallow')


def _under(path: str, prefix: str) -> bool:
    """Whether a corpus path is the folder `prefix` or inside it, by whole path segments (niger is not nigeria)."""
    prefix = prefix.strip('/')
    return not prefix or path == prefix or path.startswith(prefix + '/')


def _countries() -> set[str]:
    key = ('countries', _head())
    if key not in _CACHE:
        _CACHE[key] = {c['path'].split('/')[0] for c in manifest()['corpora']} | {str(c.get('iso_path') or '').split('/')[0] for c in manifest()['corpora'] if c.get('iso_path')}
    return _CACHE[key]  # type: ignore[return-value]


# Other names in common use for a country -> its ISO 3166-1 code; each takes in every corpus of that country.
COUNTRY_ALIASES = {
    'uk': 'gb', 'great-britain': 'gb', 'britain': 'gb', 'usa': 'us', 'united-states-of-america': 'us',
    'uae': 'ae', 'turkiye': 'tr', 'czech-republic': 'cz', 'ivory-coast': 'ci', 'cape-verde': 'cv',
    'east-timor': 'tl', 'swaziland': 'sz', 'burma': 'mm', 'holy-see': 'va', 'vatican': 'va', 'macedonia': 'mk',
    'drc': 'cd', 'the-gambia': 'gm', 'the-netherlands': 'nl', 'russian-federation': 'ru', 'republic-of-korea': 'kr',
}


def _plain(name: str) -> str:
    """A name as the tree's folders write it: no accents, lower case, no apostrophes, words joined by hyphens
    ("Côte d'Ivoire" -> cote-divoire, "São Tomé and Príncipe" -> sao-tome-and-principe)."""
    name = ''.join(ch for ch in unicodedata.normalize('NFKD', name) if not unicodedata.combining(ch))
    name = re.sub(r"['’ʼ`]", '', name.strip().strip('/').lower())
    return re.sub(r'\s+', '-', name)


def _country_names() -> dict[str, str]:
    """Every name that names a whole country -> its folder: the folder ("spain"), its ISO 3166-1 code ("es", the
    first part of its corpora's codes ES, ES-MD) and its other names in COUNTRY_ALIASES ("uk")."""
    key = ('country-names', _head())
    if key not in _CACHE:
        out: dict[str, str] = {}
        for c in manifest()['corpora']:
            folder = c['path'].split('/')[0]
            out.setdefault(folder, folder)
            code = str(c.get('code') or '').split('-')[0].lower()
            if code:
                out.setdefault(code, folder)
        for alias, code in COUNTRY_ALIASES.items():
            if code in out:
                out.setdefault(alias, out[code])
        _CACHE[key] = out
    return _CACHE[key]  # type: ignore[return-value]


def matches(corpus: dict, name: str) -> bool:
    """Whether a name a user gives for a jurisdiction takes in a corpus (a manifest entry): its country by folder,
    name, ISO code or other common name ("germany", "United Kingdom", "es", "uk", "Côte d'Ivoire"), which takes in
    every corpus of that country; a level ("united-states/federal", "us/federal") or the corpus itself, or a folder
    inside it, which takes in the whole corpus; or the corpus's own code ("ES-MD"). A state, province or city by its
    own name ("bremen", "california") takes in its corpora too; the generic levels ("national", "federal") do not.
    Accents and case do not matter."""
    name = _plain(name)
    if not name:
        return False
    # A corpus's old path, from before it moved (data/moved-paths.tsv), names it too, with or without /acts.
    renamed = moved(name) if moved(name) != name else moved(name + '/acts').removesuffix('/acts')
    if renamed != name and matches(corpus, renamed):
        return True
    countries = _country_names()
    if countries.get(name) == corpus['path'].split('/')[0]:
        return True
    for path in (corpus['path'], corpus.get('iso_path') or ''):
        if path and (path == name or path.startswith(name + '/') or name.startswith(path + '/')):
            return True
    # A state, province, canton or city by its own folder name, at any level below the country
    # (brazil/bahia/salvador/acts is taken in by "bahia" and by "salvador").
    # A country's own name or code (niger, georgia) names that country, not another's state of the same name.
    if (name not in GENERIC_LEVELS and name not in _countries() and name not in countries
            and name in corpus['path'].split('/')[1:-1]):
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
    sha = file_commit(date, path)
    return read_version(path, sha) if sha else None


GIT_DIFF_ABOVE = 1_000_000  # line pairs above which git's histogram diff matches the lines instead of difflib


def _git_line_opcodes(a: list[str], b: list[str]) -> list[tuple[str, int, int, int, int]] | None:
    """git's histogram diff of two lists of lines, as difflib opcodes; None if git cannot be run here or its answer
    does not check out (_opcodes_fit)."""
    return _GitDiffs([(a, b)]).opcodes()[0]


def _file_bytes(lines: list[str]) -> bytes:
    """Lines as git reads them for a diff: one line of the file for each line, so that two lines are the same line to
    git exactly when they are the same string. A line's own '\\n' ends its line; backslash, NUL and CR inside a line
    are escaped (git takes a file with a NUL for binary). In a list whose lines keep their endings (words), a line
    with no final newline is marked, so 'x' and 'x\\n' differ, as they do to difflib."""
    keeps = bool(lines) and lines[0].endswith('\n')
    out = []
    for x in lines:
        ended = x.endswith('\n')
        body = (x[:-1] if ended else x).replace('\\', '\\\\').replace('\x00', '\\0').replace('\r', '\\r')
        out.append(body.replace('\n', '\\n') + ('\\$' if keeps and not ended else '') + '\n')
    return ''.join(out).encode('utf-8', 'surrogatepass')


def _opcodes_fit(ops, a: list[str], b: list[str]) -> bool:
    """The opcodes walk both lists end to end in order, and every 'equal' stretch is equal: applied to `a` they give
    back `b` exactly. O(len(a) + len(b))."""
    kinds = {(True, True): 'replace', (True, False): 'delete', (False, True): 'insert'}
    ia = ib = 0
    for op, a0, a1, b0, b1 in ops:
        if (a0, b0) != (ia, ib) or a1 < a0 or b1 < b0:
            return False
        if op == 'equal':
            if a1 - a0 != b1 - b0 or a[a0:a1] != b[b0:b1]:
                return False
        elif op != kinds.get((a1 > a0, b1 > b0)):
            return False
        ia, ib = a1, b1
    return (ia, ib) == (len(a), len(b))


def _hunks_to_opcodes(hunks: list[str], a: list[str], b: list[str]) -> list[tuple[str, int, int, int, int]]:
    ops: list[tuple[str, int, int, int, int]] = []
    ia = ib = 0
    for line in hunks:
        hunk = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not hunk:
            continue
        a0, an, b0, bn = int(hunk[1]), int(hunk[2] or 1), int(hunk[3]), int(hunk[4] or 1)
        a0, b0 = (a0 if an == 0 else a0 - 1), (b0 if bn == 0 else b0 - 1)
        if a0 > ia or b0 > ib:
            ops.append(('equal', ia, a0, ib, b0))
        ops.append(('replace' if an and bn else 'delete' if an else 'insert', a0, a0 + an, b0, b0 + bn))
        ia, ib = a0 + an, b0 + bn
    if ia < len(a) or ib < len(b):
        ops.append(('equal', ia, len(a), ib, len(b)))
    return ops


# settings and options that fix the output _GitDiffs reads, whatever the user's git config, attributes or
# environment say (prefixes, colour, external diff, textconv, binary detection, renames, quoting, relative paths)
_GIT_DIFF_SETTINGS = ('core.quotePath=false', 'core.autocrlf=false', 'core.safecrlf=false', 'core.bigFileThreshold=1g',
                      'diff.noprefix=false', 'diff.mnemonicPrefix=false', 'diff.relative=false', 'diff.renames=false',
                      'diff.suppressBlankEmpty=false', 'diff.indentHeuristic=true', 'diff.interHunkContext=0',
                      'color.ui=never', 'color.diff=never')
_GIT_DIFF_OPTIONS = ('--no-index', '--text', '--no-textconv', '--no-ext-diff', '--no-color', '--no-renames',
                     '--src-prefix=a/', '--dst-prefix=b/', '-U0', '--inter-hunk-context=0', '--indent-heuristic',
                     '--diff-algorithm=histogram')


def _hermetic_git(folder: Path) -> tuple[list[str], dict]:
    """The command prefix and environment for a git that reads no config but these settings: no system or global
    config, no attributes file, no GIT_* variable of the caller's, and no repository looked for above `folder`."""
    import os
    empty = folder / 'empty'
    empty.write_bytes(b'')
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_') or k.upper() == 'GIT_EXEC_PATH'}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_ATTR_NOSYSTEM='1', GIT_CONFIG_GLOBAL=str(empty),
               GIT_CEILING_DIRECTORIES=str(folder.parent), XDG_CONFIG_HOME=str(folder), LC_ALL='C')
    cmd = ['git', '-c', f'core.attributesFile={empty.as_posix()}']
    for setting in _GIT_DIFF_SETTINGS:
        cmd += ['-c', setting]
    return cmd, env


class _GitDiffs:
    """git's histogram diff of many (a, b) pairs of lists of lines from ONE git process, started at once and read
    when wanted, so git works while Python credits the versions before. The pairs are written as files of the same
    name in two folders and `git diff --no-index` compares the folders file by file, with the same diff it gives two
    single files. git runs with fixed settings (_hermetic_git) and each pair's answer is checked (_opcodes_fit): a
    pair whose answer is missing, unreadable or wrong comes back None, never as a wrong credit. `ran`: git ran and
    exited normally. `encoded` (id of a list -> its bytes) keeps a version that is the new side of one pair and the
    old side of the next from being encoded twice."""

    def __init__(self, pairs: list[tuple[list[str], list[str]]], encoded: dict | None = None):
        import tempfile
        self.pairs, self.proc, self.dir, self.ran = pairs, None, None, False
        if not pairs:
            return
        encoded = {} if encoded is None else encoded

        def data(lines: list[str]) -> bytes:
            if id(lines) not in encoded:
                encoded[id(lines)] = _file_bytes(lines)
            return encoded[id(lines)]
        try:
            self.dir = tempfile.TemporaryDirectory()
            d = Path(self.dir.name)
            (d / 'a').mkdir()
            (d / 'b').mkdir()
            for k, (a, b) in enumerate(pairs):
                (d / 'a' / f'{k:06d}').write_bytes(data(a))
                (d / 'b' / f'{k:06d}').write_bytes(data(b))
            cmd, env = _hermetic_git(d)
            self.out = open(d / 'out', 'wb')
            self.proc = subprocess.Popen([*cmd, 'diff', *_GIT_DIFF_OPTIONS, 'a', 'b'], cwd=d, env=env,
                                         stdout=self.out, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        except (OSError, AttributeError, UnicodeError):
            self.close()

    def close(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        if getattr(self, 'out', None) is not None:
            self.out.close()
        if self.dir is not None:
            self.dir.cleanup()
        self.dir = None

    def opcodes(self) -> list[list[tuple[str, int, int, int, int]] | None]:
        """Each pair's difflib opcodes; None for a pair whose answer does not check out, and for every pair if git
        could not be run here."""
        if self.proc is None:
            self.close()
            return [None] * len(self.pairs)
        code = self.proc.wait()
        self.out.close()
        raw = Path(self.dir.name, 'out').read_bytes()
        self.close()
        if code not in (0, 1):
            return [None] * len(self.pairs)
        self.ran = True
        hunks: dict[int, list[str]] = {}
        current: list[str] | None = None
        # split at '\n' only, as git does: splitlines would also split at the form feeds and other breaks in the text
        for line in raw.decode('utf-8', 'replace').split('\n'):
            if line.startswith('diff '):
                head = re.fullmatch(r'diff --git a/a/(\d{6}) b/b/(\d{6})', line)
                current = hunks.setdefault(int(head[1]), []) if head and head[1] == head[2] else None
            elif current is not None and line.startswith('@@ '):
                current.append(line)
        out = []
        for k, (a, b) in enumerate(self.pairs):
            ops = _hunks_to_opcodes(hunks.get(k, []), a, b)
            out.append(ops if _opcodes_fit(ops, a, b) else None)
        return out


def _line_opcodes(a: list[str], b: list[str]) -> list[tuple[str, int, int, int, int]]:
    """How the lines of one version of a file (a) became the next (b), as difflib opcodes: difflib for most files;
    git's histogram diff when both versions are long. difflib is quadratic in lines that repeat (the blank lines that
    are half of a long statute) and took most of a minute on one; git's histogram diff gives nearly the same answer
    in milliseconds (performance/experiments/line_matching.md). difflib again if git cannot be run here."""
    if len(a) * len(b) > GIT_DIFF_ABOVE:
        ops = _git_line_opcodes(a, b)
        if ops is not None:
            return ops
    return difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()


STEP_BATCH = 48  # long-file steps one git process diffs; the next batch's git runs while this one is credited


def _step_opcodes(versions: list[list[str]], check=None):
    """_line_opcodes for each step of a file's history ([] -> versions[0] -> versions[1] -> ...), in order, the same
    answer step by step; but the long-file steps go to git STEP_BATCH at a time, one process each batch rather than
    one each step, and the next batch is started before this one is used."""
    check = check or (lambda: None)
    steps = [(versions[i - 1] if i else [], versions[i]) for i in range(len(versions))]
    big = [i for i, (a, b) in enumerate(steps) if len(a) * len(b) > GIT_DIFF_ABOVE]
    batches = [big[i:i + STEP_BATCH] for i in range(0, len(big), STEP_BATCH)]
    encoded: dict = {}
    running = [_GitDiffs([steps[i] for i in batch], encoded) for batch in batches[:1]]
    by_git: dict[int, list | None] = {}
    try:
        for n, batch in enumerate(batches):
            check()
            if n + 1 < len(batches):
                running.append(_GitDiffs([steps[i] for i in batches[n + 1]], encoded))
            by_git_now = dict(zip(batch, running[n].opcodes()))
            # versions of earlier batches are not needed again
            for i in by_git:
                encoded.pop(id(versions[i]), None)
            by_git = by_git_now
            for i in range(batch[0] if n else 0, (batches[n + 1][0] if n + 1 < len(batches) else len(steps))):
                ops = by_git.get(i)
                if ops is None and i in by_git and running[n].ran:
                    ops = _git_line_opcodes(*steps[i])  # git ran but this step's answer did not check out: alone
                yield ops if ops is not None else difflib.SequenceMatcher(None, *steps[i], autojunk=False).get_opcodes()
        if not batches:
            for a, b in steps:
                yield difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    finally:
        for r in running:
            r.close()


def blame_rows(date: str, path: str) -> list[tuple[str, str, str]]:
    """(corpus commit, law, line) for every line of the file as it stood on `date`. Each line is credited to the
    version that first wrote it, following the versions in the order they took force up to `date` (the same choice
    as file_commit), not the order of the commits: a corpus can append an older act or a correction after newer
    ones, and git blame would then credit lines to laws not yet in force on that date."""
    seq = versions_in_force(date, path)
    fast = _git_blame_if_same(path, seq)
    if fast is not None:
        return fast
    lines: list[str] = []
    credit: list[str] = []
    texts = [(read_version(path, sha) or '').splitlines() for sha, _ in seq]
    for (sha, law), new, step in zip(seq, texts, _step_opcodes(texts)):
        nc: list[str] = []
        for op, a0, a1, b0, b1 in step:
            nc += credit[a0:a1] if op == 'equal' else [f'{sha}\x1f{law}'] * (b1 - b0)
        lines, credit = new, nc
    return [(c.split('\x1f', 1)[0], c.split('\x1f', 1)[1], line) for c, line in zip(credit, lines)]


def _git_blame_if_same(path: str, seq: list[tuple[str, str]]) -> list[tuple[str, str, str]] | None:
    """git blame's answer, when it is the same as replaying `seq`: when the versions in force, in the order they took
    force, are exactly the commits that touched the file, in commit order (no correction or older act appended out of
    order, no documentation commit in between, no gap). git blame is far faster on a long file with many versions.
    None when they differ, or when git's answer does not cover the text: then the replay is used."""
    if not seq or any(not sha for sha, _ in seq):
        return None
    shas = {sha for sha, _ in seq}
    if any(h.get('repeal_notice') for h in history(path) if h['commit'] in shas):
        return None  # a repeal notice ends the text there; git blame would carry lines across it
    corpus, rel = corpus_of(path)
    ix = _index(corpus)
    rows = ix['rows']
    order_of = {rows[o][0]: o for o, _, _ in ix['files'].get(rel, [])}
    last = order_of.get(seq[-1][0])
    if last is None:
        return None
    touching = [rows[o][0] for o, _, _ in ix['files'].get(rel, []) if o <= last]
    if touching != [sha for sha, _ in seq]:
        return None
    label = dict(seq)
    out, commit = [], ''
    try:
        porcelain = git('blame', '--line-porcelain', seq[-1][0], '--', rel, cwd=corpus_dir(corpus))
    except RuntimeError:
        return None
    for line in porcelain.splitlines():
        if re.match(r'^[0-9a-f]{40} ', line):
            commit = line[:40]
        elif line.startswith('\t'):
            if commit not in label:
                return None
            out.append((commit, label[commit], line[1:]))
    return out if [l for _, _, l in out] == (read_version(path, seq[-1][0]) or '').splitlines() else None


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


WORD_DIFF_LIMIT = 400_000  # old tokens × new tokens above which a changed block is compared line by line
_WORD = re.compile(r'\s+|\S+')


def _tokens(line: str) -> list[str]:
    """A line as `words` compares it: words and the spaces between them, each a token."""
    return _WORD.findall(line)


def _pair_old_line(old_block: list[list[str]], line: list[str]) -> int | None:
    """In a large rewrite, the old line most like a new one (difflib's quick_ratio of their tokens, at least 0.6),
    or None."""
    best, score = None, 0.0
    for j, old in enumerate(old_block):
        s = difflib.SequenceMatcher(None, old, line, autojunk=False).quick_ratio()
        if s > score:
            best, score = j, s
    return best if best is not None and score >= 0.6 else None


MOVE_CREDIT = True  # words: a line moved and amended in one step keeps the law that wrote its unchanged words
MOVE_MIN_WORDS, MOVE_SIMILAR, MOVE_PAIRS_LIMIT = 5, 0.75, 400_000


def _credit_moves(lines: list[str], authors: list[list[str]], new_lines: list[str], new_authors: list[list[str]],
                  ops: list, law: str, check) -> None:
    """Text moved and amended in the same version (a subsection rewritten and renumbered elsewhere): the line
    matching sees a deletion in one place and an insertion in another, so every word of the insertion went to the
    amending law. Here a new line credited almost wholly to `law` is compared with the lines removed anywhere in the
    same step; the most similar one (at least MOVE_SIMILAR alike, MOVE_MIN_WORDS words or more, each removed line
    used once) gives back the credit of the words they share. Words the step changed stay with `law`."""
    removed = [j for op, a0, a1, b0, b1 in ops if op in ('delete', 'replace') for j in range(a0, a1)
               if len(lines[j].split()) >= MOVE_MIN_WORDS]
    fresh = [i for op, a0, a1, b0, b1 in ops if op in ('insert', 'replace') for i in range(b0, b1)
             if len(new_lines[i].split()) >= MOVE_MIN_WORDS]
    if not removed or not fresh or len(removed) * len(fresh) > MOVE_PAIRS_LIMIT:
        return
    old_tokens = {j: _tokens(lines[j]) for j in removed}
    holding: dict[str, list[int]] = {}  # word -> the removed lines that hold it, to compare only likely pairs
    for j in removed:
        for w in set(lines[j].split()):
            holding.setdefault(w, []).append(j)
    candidates = []
    m = difflib.SequenceMatcher(None, autojunk=False)
    for i in fresh:
        toks = _tokens(new_lines[i])
        words = [k for k, t in enumerate(toks) if not t.isspace()]
        if not words or sum(new_authors[i][k] == law for k in words) < 0.8 * len(words):
            continue  # already matched in place: most of its words kept their law
        check()
        mine = set(new_lines[i].split())
        shared: dict[int, int] = {}
        for w in mine:
            for j in holding.get(w, ()):
                shared[j] = shared.get(j, 0) + 1
        # Two lines MOVE_SIMILAR alike share at least about that share of their distinct words.
        likely = [j for j, n in shared.items() if n >= 0.5 * MOVE_SIMILAR * max(len(mine), 1)]
        m.set_seq2(toks)
        for j in likely:
            m.set_seq1(old_tokens[j])
            if m.real_quick_ratio() < MOVE_SIMILAR or m.quick_ratio() < MOVE_SIMILAR:
                continue
            r = m.ratio()
            if r >= MOVE_SIMILAR:
                candidates.append((r, i, j, toks))
    taken_new, taken_old = set(), set()
    for r, i, j, toks in sorted(candidates, key=lambda c: (-c[0], c[1], c[2])):
        if i in taken_new or j in taken_old:
            continue
        taken_new.add(i)
        taken_old.add(j)
        new_authors[i] = _credit_words(old_tokens[j], authors[j], toks, law)


def words_on(date: str, path: str, check=None) -> list[tuple[str, str]]:
    """(law, run of text) for the file as it stood on `date`, credited word by word. git blame credits whole lines;
    here each version of the file is compared with the one before, word by word, and words that survive keep the law
    that first wrote them. The versions are taken in the order they took force up to `date` (versions_in_force), not
    in commit order. Text moved within the file usually keeps its author; text that is rewritten in place is
    credited to the law that rewrote it. Unchanged lines are matched first, so only changed stretches are compared
    word by word, which keeps long sections fast. `check`, if given, is called between steps and may raise to stop
    a pass that is taking too long (the MCP server's time limit)."""
    check = check or (lambda: None)
    lines: list[str] = []
    authors: list[list[str]] = []  # per line, one law per token
    seq = versions_in_force(date, path)
    texts = [(read_version(path, commit) or '').splitlines(keepends=True) for commit, _ in seq]
    for (commit, law), new_lines, ops in zip(seq, texts, _step_opcodes(texts, check)):
        check()
        new_authors: list[list[str]] = []
        for op, a0, a1, b0, b1 in ops:
            if op == 'equal':
                new_authors += authors[a0:a1]
                continue
            check()
            old_block = [_tokens(line) for line in lines[a0:a1]]
            block = [_tokens(line) for line in new_lines[b0:b1]]
            old_tokens = [t for line in old_block for t in line]
            if len(old_tokens) * sum(map(len, block)) <= WORD_DIFF_LIMIT:
                old_credit = [a for line_authors in authors[a0:a1] for a in line_authors]
                credit = _credit_words(old_tokens, old_credit, [t for line in block for t in line], law)
                at = 0
                for line in block:
                    new_authors.append(credit[at:at + len(line)])
                    at += len(line)
            else:
                # A large rewrite: pair each new line with the most similar old line and compare only those two,
                # which keeps a whole-section rewrite (17 U.S.C. §115 in 2018) to seconds rather than minutes.
                for line in block:
                    check()
                    best = _pair_old_line(old_block, line)
                    if best is not None:
                        new_authors.append(_credit_words(old_block[best], authors[a0 + best], line, law))
                    else:
                        new_authors.append([law] * len(line))
        if MOVE_CREDIT:
            _credit_moves(lines, authors, new_lines, new_authors, ops, law, check)
        lines, authors = new_lines, new_authors
    tokens = [t for line in lines for t in _tokens(line)]
    flat = [a for line_authors in authors for a in line_authors]
    runs: list[tuple[str, list[str]]] = []  # the pieces of each run, joined once at the end
    for law, token in zip(flat, tokens):
        if token.isspace() and runs:
            law = runs[-1][0]  # spaces never start a new run
        if runs and runs[-1][0] == law:
            runs[-1][1].append(token)
        else:
            runs.append((law, [token]))
    return [(law, ''.join(pieces)) for law, pieces in runs]


EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'  # git's empty tree: "nothing yet", before a record starts


def diff_between(date_a: str, date_b: str, path: str) -> str:
    corpus, rel = corpus_of(path)
    a, b = file_commit(date_a, path), file_commit(date_b, path)
    if a == b:
        return ''
    # A side with no text (an act ended by data/acts.json, whose files stay in git) reads as the empty tree, so the
    # text the end removed is shown, headed by why that side has none.
    gone = [d for d, c in ((date_a, a), (date_b, b)) if c and read_version(path, c) is None]
    a, b = (EMPTY_TREE if date_a in gone else a), (EMPTY_TREE if date_b in gone else b)
    if a == b:
        return ''
    out = git('diff', '--word-diff=plain', a or EMPTY_TREE, b or EMPTY_TREE, '--', rel, cwd=corpus_dir(corpus))
    return ''.join(f'{explain_missing(d, path)}\n' for d in gone) + out if out else out


def corpus_info(corpus: str) -> dict:
    return next(c for c in manifest()['corpora'] if c['path'] == corpus)


# What a corpus may model beyond its text (corpus.json `effects`, corpus standard): anything not listed, answers name.
EFFECTS = {'modifications': 'changes that alter how a provision applies without changing its words (Modifies:)',
           'commencement': 'commencement orders and conditions that decide when or to whom a change applies (Applies:)',
           'transitional': 'transitional and saving rules that keep older text applying to some cases'}


def effects_of(corpus: str) -> list[str]:
    """The effects a corpus models, from its manifest entry, else its checked-out corpus.json; [] when it says none."""
    info = corpus_info(corpus)
    got = info['effects'] if 'effects' in info else described(corpus).get('effects', [])
    return [str(e) for e in got] if isinstance(got, list) else []


def caveats(date: str, corpus: str, events: list[Event] | None = None) -> list[str]:
    """What a reader must know about a date in one corpus: before its record starts or after it ends, what kind of
    record it is (current text only, a list of acts without their text), and changes on main not yet in force.
    Reads only this corpus (`events`, if given, may hold others: only this corpus's are used)."""
    own = [e for e in (events if events is not None else corpus_events(corpus)) if e.corpus == corpus and e.kind != 'documentation']
    info = corpus_info(corpus)
    out = []
    if (ROOT / corpus / '.git').exists() and not _readable(corpus, ROOT / corpus):
        return [_UNREADABLE.format(corpus=corpus)]
    if own:
        first = min(own, key=lambda e: e.in_force)
        if date < first.in_force:
            out.append(f"{corpus}: the record starts on {first.in_force} ({first.law}); nothing earlier is in it.")
    # The record covers every day up to the later of its last change and the day it was checked against the source;
    # a corpus that does not say gives its latest dated change.
    covered = max(filter(None, (info.get('record_to'), info.get('checked_on'))), default=None)
    import datetime as dt
    today = dt.date.today().isoformat()
    if covered and date > covered:
        checked = f", checked on {info['checked_on']}" if info.get('checked_on') else ''
        out.append(f"{corpus}: the record runs to {info.get('record_to') or covered}{checked}. {info.get('record_note', '')}".rstrip())
    elif not covered and own:
        last = max((e.in_force for e in own if e.in_force <= today), default=None)
        if last and date > last:
            out.append(f"{corpus}: the latest change in this record took force on {last}; it does not say whether it "
                       "covers later changes.")
    if info.get('provisional'):
        out.append(f"{corpus}: provisional upload: {info['provisional']}.")
    if info.get('history') == 'as-enacted':
        out.append(f"{corpus}: each law is shown as first published; later amendments are not applied, so this is not "
                   "the text in force on a date.")
    if info.get('history') == 'replayed':
        checked = f" {info['verification']}" if info.get('verification') else ''
        out.append(f"{corpus}: earlier versions were rebuilt by applying each amending act, not read from an official text.{checked}")
    current_only = info.get('history') == 'current-only' or (own and all(e.kind == 'baseline' for e in own))
    if current_only and (not covered or date < covered):
        out.append(f"{corpus}: this record holds only the text as the publisher gave it on the day it was read; an "
                   "earlier date shows that text only from that day, not as the law was in force before.")
    if own and _metadata_only(corpus):
        out.append(f"{corpus}: this record lists acts (titles, numbers, dates) without their text, so what it shows "
                   "is a catalogue entry, not the law.")
    ahead = sum(1 for e in own if e.in_force > today)
    fut = _index(corpus).get('future') if own else None
    if ahead and fut:
        out.append(f"{corpus}: {ahead} change(s) in this record (main and its {fut['branch']} branch, recorded at "
                   f"{fut['sha'][:10]}) take force after today; they are shown only from their dates.")
    elif ahead:
        out.append(f"{corpus}: {ahead} change(s) in this record take force after today; they are shown only from their "
                   "dates, but the files at the corpus's HEAD already hold them.")
    note = future_note(corpus)
    if note:
        out.append(note)
    missing = [EFFECTS[e] for e in EFFECTS if e not in effects_of(corpus)]
    if own and missing and info.get('history') not in ('metadata-only',):
        out.append(f"{corpus}: this record changes the text on each change's in-force date only; it does not hold "
                   f"{', '.join(missing)}, so the text shown may not be the whole law that applied on {date}.")
    odd = _index(corpus)['unknown'] if own else set()
    if odd:
        out.append(f"{corpus}: commit kind(s) not recognised, read as laws: {', '.join(sorted(odd))}.")
    return out


# Kind words for a version that revises or amends an act already in force: China's Law（修订） (a full revision) and
# 修正 (an amendment). An act whose record starts at such a version was in force before it, so the record starts
# there, as at a publisher's starting text (#17: 50 Chinese acts, 标准化法 and 证券法 among them). Only these: other
# corpora write "amendment" for an amending law kept as its own act (Azerbaijan, 1,025 acts), which starts there.
_REVISION_WORDS = ('修订', '修正')


def record_floor(path: str) -> dict | None:
    """The version where a file's record starts without the provision starting there, or None: its first version
    when that is a starting text (baseline), or when it came with the first version of its act (the file's folder)
    and that version's Kind names a revision or an amendment (_REVISION_WORDS; the row then has `kind_written`)."""
    h = history(path)
    if not h:
        return None
    first = min(h, key=lambda x: x['in_force'])
    if first['kind'] == 'baseline':
        return first
    corpus, rel = corpus_of(path)
    ix = _index(corpus)
    raw = (ix['rows'][first['order']][6] or '') if isinstance(first.get('order'), int) else ''
    folder = rel.rpartition('/')[0]
    if first['kind'] != 'law' or not folder or not any(w in raw for w in _REVISION_WORDS):
        return None
    key = ('act-start', f"{corpus}@{_at(ix)}:{folder}")
    if key not in _CACHE:  # the first in-force day of any file of the act
        rows, pre = ix['rows'], folder + '/'
        _CACHE[key] = min((rows[o][5] for f, vs in ix['files'].items() if f.startswith(pre) for o, *_ in vs
                           if rows[o][5] and rows[o][4] != 'documentation'), default=None)
    return dict(first, kind_written=raw) if _CACHE[key] == first['in_force'] else None


def act_floor_note(date: str, path: str) -> str:
    """What data/acts.json says of a file's act on a date before its record starts: the act's own in_force (the day
    it first came into force) or, without one, its `adopted` day. '' when it gives neither."""
    corpus, rel = corpus_of(path)
    fact = act_fact(corpus, rel)
    since, adopted = (str(fact.get(k) or '')[:10] for k in ('in_force', 'adopted'))
    if ISO_DAY.fullmatch(since):
        if since <= date:
            return (f" Its act was in force from {since} (data/acts.json), so the provision may well have been in "
                    f"force on {date}, in words this record does not have.")
        return f" Its act came into force only on {since} (data/acts.json), so it was not yet in force on {date}."
    if ISO_DAY.fullmatch(adopted):
        if adopted <= date:
            return (f" Its act was adopted on {adopted} (data/acts.json); the record does not give the day it first "
                    f"came into force, so the provision may well have been in force on {date}, in words this record "
                    "does not have.")
        return f" Its act was adopted only on {adopted} (data/acts.json), so it was not yet in force on {date}."
    return ''


def explain_missing(date: str, path: str) -> str:
    """Why there is no text: a mistyped path, before the record, not yet in force, or repealed."""
    corpus, rel = corpus_of(path)
    files = _index(corpus)['files']
    if rel not in files:
        close = difflib.get_close_matches(rel, list(files), n=3, cutoff=0.6)
        hint = f" Did you mean {', '.join(f'{corpus}/{c}' for c in close)}?" if close else ''
        return f'{path} is not in this record at any date.{hint}'
    h = history(path)
    if not h:
        return f'{path} has no dated change in the record.'
    first = min(h, key=lambda x: x['in_force'])
    if date < first['in_force'] and first.get('repeal_notice'):
        return (f"{path} is not in the record on {date}: the record first has it on {first['in_force']} "
                f"({first['law']}), and then only as a repeal notice (\"{first['repeal_notice']}\"); it holds no text "
                "of the provision in force.")
    floor = record_floor(path) if date < first['in_force'] else None
    if floor:
        what = ('' if floor['kind'] == 'baseline' else
                f", a revision of an act already in force then (Kind: {floor['kind_written']})")
        return (f"{path} is not in the record on {date}: the record starts on {first['in_force']} ({first['law']})"
                f"{what}, which is where this record starts, not the day it came into force.{act_floor_note(date, path)}")
    if date < first['in_force']:
        return f"{path} was not yet in force on {date}. It first appears on {first['in_force']} ({first['law']})."
    gone = max((x for x in h if x['in_force'] <= date), key=lambda x: x['in_force'])
    back = min((x for x in h if x['in_force'] > date), key=lambda x: x['in_force'], default=None)
    latest_that_day = max((x for x in h if x['in_force'] == gone['in_force']), key=lambda x: x['order'])
    if latest_that_day.get('restates'):  # a correction says the version first published for that day was not in force
        until = f" It takes effect on {back['in_force']} ({back['law']})." if back else ''
        return (f"{path} was not in force on {date}. The record first gave it a version from {gone['in_force']}, but a "
                f"correction appended later (commit {latest_that_day['commit'][:10]}) replaces that version: the "
                f"provision was not in force from that day.{until}")
    again = f" It is in force again from {back['in_force']} ({back['law']})." if back else ''
    if latest_that_day.get('repeal_notice'):
        notice = latest_that_day['repeal_notice']
        if any(x.get('blob') for x in h if x['in_force'] < gone['in_force']):
            return (f"{path} was not in force on {date}: repealed on {gone['in_force']} by {latest_that_day['law']}, "
                    f"the record keeps its repeal notice: \"{notice}\".{again}")
        # Its first version is the notice (a current-only record such as Sweden's): the record does not hold the day
        # of the repeal, only the day of the version that holds the notice; the notice names the repealing law.
        return (f"{path} was not in force on {date}: repealed, the record keeps its repeal notice: \"{notice}\" (in "
                f"its version of {gone['in_force']}, {latest_that_day['law']}; the record holds no text of the "
                f"provision, nor the day of its repeal).{again}")
    if latest_that_day.get('ends'):
        return (f"{path} was not in force on {date}: its act ({latest_that_day['act']}) was {latest_that_day['ends']} "
                f"on {gone['in_force']}" + (f" by {latest_that_day['law']}" if latest_that_day['law'] and
                                             '(data/acts.json)' not in latest_that_day['law'] else '') +
                f", as the corpus's data/acts.json records; the record did not remove the file itself.{again}"
                + _not_reenacting(latest_that_day))
    return f"{path} was not in force on {date}: it was removed on {gone['in_force']} ({gone['law']}).{again}"


def _not_reenacting(end_row: dict) -> str:
    later = end_row.get('not_reenacting')
    return (f" Later version(s) are not read as re-enacting it (only a version whose law was enacted on or after that "
            f"day, is not the law that ended the act and is not a repeal note does): {'; '.join(later)}."
            if later else '')


def file_notes(date: str, path: str) -> list[str]:
    """What a reader must know about one file on a date, beyond its corpus's caveats: an act recorded as ended with no
    date, and a version in force whose date the record itself makes doubtful."""
    corpus, rel = corpus_of(path)
    out = []
    end = act_end(corpus, rel)
    if end and not end['day']:
        out.append(f"{path}: data/acts.json records its act ({end['act']}) as {end['how']}, but not from when; the "
                   "text shown may no longer be in force.")
    hist = history(path)
    sha = file_commit(date, path)
    row = next((h for h in reversed(hist) if h['commit'] == sha), None) if sha else None
    if row and row.get('date_doubtful'):
        out.append(f"{path}: the version shown is {row['date_doubtful']}.")
    ended = next((h for h in hist if h.get('ends') and h['in_force'] <= date), None)
    if row and not row.get('ends') and ended and (row['in_force'], row['order']) > (ended['in_force'], ended['order']):
        made = enacted_day(row.get('enacted'))
        out.append(f"{path}: data/acts.json records its act ({ended['act']}) as {ended['ends']} on {ended['in_force']}; "
                   f"the version shown, by {row['law']}" + (f" (enacted {made})" if made else '') + ", is read as "
                   "bringing it back into force, as its law was made after that day. It may only apply to cases "
                   "from before the end: read the law that made it.")
    # One act held only as captured text, in a corpus whose history is otherwise in force (the UK's 4,375 Acts as
    # current text among its full histories): the corpus caveats do not say so for it.
    info = corpus_info(corpus)
    texts = [h for h in hist if not h.get('ends')]
    if texts and all(h['kind'] == 'baseline' for h in texts) and info.get('history') not in ('current-only', 'as-enacted'):
        first = min(h['in_force'] for h in texts)
        out.append(f"{path}: this record holds only the text as the publisher gave it (from {first}), not the "
                   "versions before it or the laws that changed it; later changes appear only where the record "
                   "read the text again.")
    return out


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
ENACTED = ('Enacted', 'Made', 'Beschlossen', 'Adopted', 'Dated', 'Signed', 'Promulgated', 'Issued', 'Assented')
# Promulgated (Japan), Issued (Sweden), Assented (Australia): the act's own date under the name its source uses
PUBLISHED = ('Published', 'Proclaimed', 'Printed-in', 'Verkuendet', 'Verkündet')
ISO_DAY = re.compile(r'\d{4}-\d{2}-\d{2}')


def history(path: str) -> list[dict]:
    """Every dated change to a file, in the corpus's commit order, with its dates: the reader's "follow" list.

    A change is dated by the corpus's in-force trailer; failing that by its baseline or correction trailer (Malta's
    consolidated versions, Switzerland's first versions and corrections), which must hold an ISO date (Liechtenstein's
    `Consolidated:` is a URL, not a date); failing that, a printing that differs from the laws behind it (US
    "Printed text differs") is dated by its commit. Documentation commits are left out. Read at the pinned commit,
    from the corpus index."""
    corpus, rel = corpus_of(path)
    ix = _index(corpus)
    key = ('history', f"{corpus}@{_at(ix)}:{rel}")
    if key not in _CACHE:
        _CACHE[key] = _history(corpus, rel)
    return [dict(h) for h in _CACHE[key]]  # type: ignore[union-attr]


CORRECTS = re.compile(r'(\d{4}-\d{2}-\d{2})(?:\s*\.\.\s*(\d{4}-\d{2}-\d{2})?)?')


def _history(corpus: str, rel: str) -> list[dict]:
    ix = _index(corpus)
    rows = ix['rows']
    out = []
    for order, blob, mode in ix['files'].get(rel, []):
        r = rows[order]
        commit, author, when, subject, kind, in_force, raw_kind, enacted, published, fix = r
        if kind == 'documentation' or not in_force:
            continue
        row = {'commit': commit, 'law': author, 'in_force': in_force, 'kind': kind, 'enacted': enacted,
               'published': published, 'blob': blob, 'order': order}
        notice = notice_text(corpus, blob)
        if notice:  # a version that only says the provision is gone ends it, as a deletion would (row 33)
            row.update({'blob': None, 'repeal_notice': notice, 'notice_blob': blob})
        restated = ix.get('restates', {}).get(commit)
        if restated:  # a correction appended later: this version replaces the one first published for its day
            row['restates'] = restated[0]
            row['restated_because'] = 'its text was wrong' if restated[1] == 'Corrects' else 'it had to be restated'
        credit_fix = credited(corpus, rel, in_force, commit)
        if credit_fix:  # data/credits.csv: the words stand, the law credited changes
            row.update({'law': credit_fix[0], 'credit_corrected_from': credit_fix[2]})
            row['kind'] = 'uncredited' if credit_fix[1] else ('law' if kind == 'uncredited' else kind)
        if fix:
            row.update({'corrects': fix['corrects'], 'until': fix['to'], 'supersedes': fix['supersedes'],
                        'reason': fix['reason']})
        out.append(row)
    seen = {r['commit'] for r in out}
    for order, r in enumerate(rows):
        fix = r[9]
        if fix and rel in fix['files'] and r[0] not in seen:
            out.append({'commit': r[0], 'law': r[1], 'in_force': fix['from'], 'kind': 'correction', 'enacted': None,
                        'published': None, 'order': order, 'corrects': fix['corrects'], 'until': fix['to'],
                        'supersedes': fix['supersedes'], 'reason': fix['reason']})
    end = act_end(corpus, rel)
    if end and end['day'] and out:
        commit, order = _end_commit(corpus, end)
        # The act-end rule (after_end): a version dated after the end re-enacts the file only if its law was enacted
        # on or after the end, is not the law that ended the act, and is not a repeal note. A correction is cut at
        # the end too (correction_cap): one starting after it applies only once a later version re-enacted the file.
        kept, dropped = [], []
        for h in out:
            if h.get('corrects'):
                cap = correction_cap(corpus, rel, h['in_force'])
                if cap is not None and cap < h['in_force']:
                    dropped.append(dict(h, why='a correction for days after the end'))
                    continue
                if cap is not None and (h.get('until') or '9999-12-31') > cap:
                    h['until'] = cap
                kept.append(h)
                continue
            why = after_end(corpus, end, (end['day'], order + 0.5), h['in_force'], h['order'],
                            h.get('notice_blob') or h.get('blob', ''), rel)
            (dropped.append(dict(h, why=why)) if why else kept.append(h))
        out = kept
        out.append({'commit': commit, 'law': end['by'] or f"{end['how']} (data/acts.json)", 'in_force': end['day'],
                    'kind': 'law', 'enacted': None, 'published': None, 'blob': None, 'order': order + 0.5,
                    'ends': end['how'], 'act': end['act'],
                    'not_reenacting': [f"{h['in_force']} {h['law']} ({h['why']})" for h in dropped]})
    retro = ix.get('retroactive')
    capture = capture_day(corpus)
    earliest = str(corpus_info(corpus).get('earliest') or '1500-01-01')
    for h in out:
        if h.get('ends'):
            continue
        made = enacted_day(h.get('enacted'))
        if h['in_force'] < earliest:
            h['date_doubtful'] = (f"dated {h['in_force']}, before anything this record can hold "
                                  f"({earliest}): a mistyped date")
        elif retro is not None and made and h['commit'] not in retro and (_days(h['in_force'], made) or 0) > 366:
            # Days or months before the act is often real (retroactive effect: Swiss acts, US appropriations); more
            # than a year with no Retroactive: trailer is as often a date taken from the wrong field.
            h['date_doubtful'] = (f"dated {h['in_force']}, more than a year before its act was made ({made}); the "
                                  "record does not say it took effect retroactively, so the date may be wrong")
        elif capture and h['in_force'] == capture[0] and h['kind'] != 'baseline':
            h['date_doubtful'] = (f"{capture[1]} of {capture[2]} changes in this record are dated {capture[0]}: "
                                  "probably the day the text was read, not the day it took force")
    out.sort(key=lambda h: h['order'])
    return out


def enacted_day(enacted: str | None) -> str | None:
    """The ISO day a law was enacted (law.py's `enacted`: Enacted, Made, Signed, Adopted ...), or None when the record
    gives none or a placeholder (LEGI's 2999-01-01 for a text it holds no signing date for)."""
    made = enacted[:10] if enacted and ISO_DAY.fullmatch(enacted[:10]) else None
    return None if made and made > day('today') else made


def reenacts(end: dict, enacted: str | None) -> bool:
    """Whether a version dated after an act's end (act_end) brings its file back into force: only when the law that
    made it was enacted on or after the end. A delayed amendment enacted before the repeal, taking effect after it,
    amended an act that no longer exists; a version with no enactment date cannot be shown to re-enact, so the act
    stays ended (its history's end row names it in `not_reenacting`). after_end adds the other two conditions."""
    made = enacted_day(enacted)
    return bool(made) and made >= end['day']


def is_repeal_note(text: str | None) -> bool:
    """Whether a version's text is only a repeal or annulment note ("Norma derogada por ...", "(Derogada)", "Norma
    anulada por Sentencia ...", "[Repealed]", "16 § Har upphävts genom lag (2011:1252)."): repeal_notice, the one
    detector, with the built-in markers only, in its `lead` form. Spain's repealing laws write such a note into the repealed act's folder
    (no.md) or over a provision; after the act's end it is the end restated, not a re-enactment (after_end)."""
    return repeal_notice(text, lead=True) is not None


# A repeal notice kept as a provision's whole text (audit row 33: 4,610 tip files in Sweden, Georgia and Malta): the
# publisher keeps the number of a repealed provision and prints only that it is gone ("16 § Har upphävts genom lag
# (2011:1252).", "# მუხლი 26. (ამოღებულია)", "Repealed by Legal Notice 99 of 2026.", "§ 5 (weggefallen)"). The
# markers, per language: a line counts only when, once its number is set aside, it is a marker alone or a marker and
# the law that made the repeal ("by ...", "genom ...", "por ...", or a dash and a citation). A corpus can add its own
# (corpus.json `repeal_notice`: regexes for such a line) or turn the rule off (`"repeal_notice": false`).
NOTICE_MARKERS = (
    r'(?:har\s+)?(?:upph[äa]vts|upph[äa]vt|upph[äa]vd[ae]?|utg[åa]tt|upph[öo]rt\s+att\s+g[äa]lla)'  # sv
    r'|repealed|revoked|deleted|omitted|spent|lapsed|expired|annulled|rescinded'  # en
    r'|ამოღებულია|ძალადაკარგულია'  # ka
    r'|derogad[oa]s?|deogad[oa]s?|suprimid[oa]s?|anulad[oa]s?|revogad[oa]s?|abrogad[oa]s?'  # es, pt
    r'|abrogat[oaie]|abrogat[ăe]?|abrog[ée]e?s?|supprim[ée]e?s?|derogat[ăa]?'  # it, ro, fr
    r'|aufgehoben|weggefallen|gestrichen|vervallen|oph[æe]vet|opph[æe]vet'  # de, nl, da, no
    r'|zru[šs]en[oaýáé]?|vypu[šs]t[ěe]n[oaýáé]?|uchylon[yae]|skre[śs]lon[yae]'  # cs, sk, pl
    r'|brisan[oaie]?|prestao\s+da\s+va[žz]i|[čc]rtan[oaie]?|ukinut[oaie]?'  # hr, sr, bs, sl
    r'|(?:on\s+)?kumottu|kehtetu|izsl[ēe]gt[sa]|neteko\s+galios|hat[áa]lyon\s+k[íi]v[üu]l\s+helyezve|m[üu]lga'  # fi et lv lt hu tr
    r'|утратил[аио]?\s+силу|исключен[аоы]?|втратил[аио]?\s+чинн[іи]сть|виключен[аоі]?|καταργ[ήη]θηκε')  # ru uk el
# What may follow the marker: the law that made the repeal ("by Act XIX.2021.76", "genom lag (2011:1252)", "por la
# Ley 2/2011", "L:lla 123/2020", "- ... კანონი №5"), short, or a citation in brackets.
NOTICE_BY = (r'(?:by|under|genom|enligt|por|pela|pelo|per|par|durch|mit|door|ved|med|av|przez|z|zákonem|zakonem'
             r'|l:lla|lailla|asetuksella|con\s+efectos|[-–—]|(?=[(\[]))')
# Spain's act-level notes name what is gone before the marker: "Norma derogada, con efectos de ..., por ...".
NOTICE_SUBJECT = r'(?:(?:norma|disposici[oó]n|art[ií]culo)\s+(?:\w+\s+)?)?'
NOTICE_LINE = re.compile(r'[\[(*_\s]*' + NOTICE_SUBJECT + r'(?:' + NOTICE_MARKERS + r')[\])*_\s.,:;]*(?:' + NOTICE_BY + r'\W.{0,250}?)?'
                         r'[\s.\])*_;:]*', re.I | re.S)
# A provision's number, set aside before the marker: "16 §", "5 b §", "§ 5", "Art. 5", "Artículo 12.", "მუხლი 43 3 .",
# "107.", "(1)", "Article 5 bis -", "15 § 2 mom.", "Section 4:", "(XXXX) §§ 42 und 42a", "Anlage 2", "Art. 66 bis 69".
_NOTICE_NUM = r'(?:\d|(?-i:[IVXLCDM]))+[\w¹²³⁴⁵⁶⁷⁸⁹⁰~-]*'
NOTICE_NUMBER = re.compile(
    r'\s*(?:(?:\(XXXX\)\s*)?(?:art(?:icle|[ií]culo|igo|ikel|icolo|\.)?|section|sec\.|ss?\.?(?=\s*\d)|§+|[čc]l\.|'
    r'[čc]l[áa]nek|[čc]len|[čc]lan|paragraf|pyk[äa]l[äa]|madde|მუხლი|თავი|kap(?:itel)?\.?|chapter|regulation|reg\.|'
    r'rule|para(?:graph)?\.?|item|schedule|annex|anexo|anlage|anhang|'
    r'disposici[oó]n(?:\s+(?:adicional|transitoria|final|derogatoria))?)\s*'
    r'(?:' + _NOTICE_NUM + r'(?:\s*(?:bis|und|u\.|to|–|-)\s*' + _NOTICE_NUM + r')?'
    r'(?:\s+(?:bis|ter|quater|[a-z]|\d{1,2})\b)?|única|unica|primera|segunda)?'
    r'\s*[.:)–—-]?'
    r'|\d+[\w¹²³⁴⁵⁶⁷⁸⁹⁰]*(?:\s+[a-z])?\s*§(?:\s*\d+\s*mom\.)?'
    r'|\(?\d+[A-Za-z]{0,3}[¹²³⁴⁵⁶⁷⁸⁹⁰]*\)?\.?)\s*', re.I)
NOTICE_MAX_LINE = 320
NOTICE_RULE_WORDS = re.compile(r'\b(?:shall|may|must|ska|skall|får|deberá|podrá|muss|kann|soll|doit|peut|deve|pode)\b',
                               re.I)


# The start of a note after an act's end (repeal_notice's `lead`): "Norma derogada, con efectos de ...", "(Derogado)",
# "Repealed by ...", then anything on that line; later lines only an editor's remarks ("Téngase en cuenta ...").
NOTICE_LEAD = re.compile(r'[\[(*_\s]*' + NOTICE_SUBJECT + r'(?:' + NOTICE_MARKERS + r')(?:[\])*_\s]*(?:$|[,.:;)]|'
                         + NOTICE_BY + r'\W))', re.I)
NOTICE_REMARK = re.compile(r'(?:t[ée]ngase|no obstante|nota\b|v[ée]ase|see\b)', re.I)
# Notes whose first words alone mark them (any text may follow): Spain's act notes ("Norma derogada, excepto su art. 7
# ...", "(Derogado)") and "Repealed ...", "Revoked ...", "Annulled ..." (the act-end rule's notes since #8).
NOTICE_OPEN = re.compile(r'[\s\[(*_]*(?:(?:norma|disposici[oó]n|art[ií]culo)\s+(?:\w+\s+)?)?'
                         r'(?:derogad|deogad|anulad|suprimid)[oa]s?\b|[\s\[(*_]*(?:repealed|revoked|annulled)\b', re.I)


def notice_line(line: str, extra: tuple = ()) -> bool:
    """Whether one line of a provision says only that the provision is gone (NOTICE_LINE, or a corpus's own pattern),
    once its number (NOTICE_NUMBER) is set aside."""
    line = line.strip().lstrip('#').strip().strip('*_').strip()
    if not line or len(line) > NOTICE_MAX_LINE:
        return False
    bare = line.lstrip('[(').strip()  # "[s 67 repealed by ...]"
    for cand in (NOTICE_NUMBER.sub('', line, count=1), NOTICE_NUMBER.sub('', bare, count=1), line):
        if any(re.fullmatch(p, cand, re.I | re.S) for p in extra):
            return True
        # What follows the marker names a law; it does not lay down a rule ("shall", "may", "ska" ...).
        if NOTICE_LINE.fullmatch(cand) and len(cand.split()) <= 40 and not NOTICE_RULE_WORDS.search(cand):
            return True
    return False


def repeal_notice(text: str | None, extra: tuple = (), lead: bool = False) -> str | None:
    """The notice, when a version's whole text is only a repeal notice for its provision, else None. Lines listing
    the provision's amendment history ("- Amended by: ...", Georgia's "- საქართველოს ... კანონი №...") and editors'
    notes quoted below it (Spain's "> Se deroga por ...") are set aside; then every line of the body (its headings,
    when it has no other text) must be a notice line (notice_line). A text with any substance besides ("1) Aufgehoben
    2) Die Regierung ...", "Genom lagen upphävs lagen (1996:764)") is law.

    `lead` is for a version dated after its act's end (after_end), where the act is already ended and a note need
    only restate it: the body (headings aside, at most 1,500 characters) may also just start with a notice, with no
    number before it and editors' remarks after it ("Abrogé." then "NOTA : ..."), or start with a note whose first
    words alone mark it (NOTICE_OPEN: "Norma derogada, excepto su art. 7 ...", "(Derogado) ...", "Repealed by ...").
    "1. (Derogado) 2. La información ...", "Abrogat. Posesorul nu poate ..." and "Aufgehoben werden: a) ..." are
    law."""
    if not text or len(text) > NOTICE_MAX_BYTES:
        return None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lead:
        body = [l for l in lines if not l.startswith('#')]
        if body and len(' '.join(body)) <= 1500 and (NOTICE_OPEN.match(body[0]) or (
                NOTICE_LEAD.match(body[0]) and all(NOTICE_REMARK.match(l) for l in body[1:]))):
            return body[0]
    lines = [l for l in lines if not re.match(r'[-–]\s|>', l)]
    body = [l for l in lines if not l.startswith('#')] or lines
    if not body or len(body) > 4 or not all(notice_line(l, extra) for l in body):
        return None
    return ' '.join(l.lstrip('#').strip() for l in body)


NOTICE_RULE = 2  # raise when repeal_notice changes what it reads as a notice: the kept lists are then made again
NOTICE_MAX_BYTES = 6000


def notice_patterns(corpus: str) -> tuple | None:
    """The corpus's own notice patterns (corpus.json `repeal_notice`: a regex or a list of them, matched against a
    whole line once its number is set aside), or None when the corpus turns the rule off (`"repeal_notice": false`)."""
    ix = _index(corpus)
    key = ('notice-patterns', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        value = corpus_info(corpus).get('repeal_notice', _MISSING)
        if value is _MISSING:  # a corpus manifest.json lists is described there, not by its corpus.json
            try:
                value = json.loads(read_object(corpus, f"{ix['pin']}:corpus.json") or '{}').get('repeal_notice')
            except (ValueError, AttributeError):
                value = None
        if value is False:
            _CACHE[key] = None
        else:
            pats = [value] if isinstance(value, str) else value if isinstance(value, list) else []
            good = []
            for p in pats:
                try:
                    re.compile(p)
                    good.append(p)
                except (re.error, TypeError):
                    pass
            _CACHE[key] = tuple(good)
    return _CACHE[key]  # type: ignore[return-value]


def notice_text(corpus: str, blob: str | None) -> str | None:
    """The repeal notice a version's text is (repeal_notice, with the corpus's own patterns), else None."""
    if not blob:
        return None
    extra = notice_patterns(corpus)
    if extra is None:
        return None
    key = ('notice', f'{corpus}:{blob}')
    if key not in _CACHE:
        text = read_object(corpus, blob)
        _CACHE[key] = repeal_notice(text, extra) if text and len(text.encode('utf-8')) <= NOTICE_MAX_BYTES else None
    return _CACHE[key]  # type: ignore[return-value]


# Words at least one of which every notice holds (NOTICE_MARKERS): a corpus-wide pass greps blobs for these first.
NOTICE_STEMS = ('upphäv', 'upphav', 'upphört', 'upphort', 'utgått', 'utgatt', 'repealed', 'revoked', 'deleted',
                'omitted', 'spent', 'lapsed', 'expired', 'annulled', 'rescinded', 'ამოღებულია', 'ძალადაკარგულია',
                'derogad', 'deogad', 'suprimid', 'anulad', 'revogad', 'abrogad', 'abrogat', 'abrogă', 'abrog',
                'supprim', 'derogat', 'aufgehoben', 'weggefallen', 'gestrichen', 'vervallen', 'ophævet', 'ophaevet',
                'opphevet', 'opphævet', 'zrušen', 'zrusen', 'vypušt', 'vypust', 'uchylon', 'skreślon', 'skreslon',
                'brisan', 'prestao', 'črtan', 'crtan', 'ukinut', 'kumottu', 'kehtetu', 'izslēgt', 'izslegt',
                'neteko galios', 'hatályon', 'hatalyon', 'mülga', 'mulga', 'утратил', 'исключен', 'втратил',
                'виключен', 'καταργ', 'Καταργ')


def notice_blobs(corpus: str) -> frozenset:
    """Every blob of a corpus whose text is a repeal notice (notice_text), for the readers that take in a whole corpus
    at once (file_index, so every built tree; in_order). The list is kept on disk beside the corpus index with the
    commits it covers, so a pin that moves reads only the blobs its new commits add."""
    extra = notice_patterns(corpus)
    if extra is None:
        return frozenset()
    ix = _index(corpus)
    key = ('notice-blobs', f"{corpus}@{_at(ix)}")
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    import hashlib
    import os
    tag = hashlib.sha1(f"{NOTICE_RULE}|{json.dumps(extra)}".encode('utf-8')).hexdigest()[:12]
    path = _store() / f"{corpus.replace('/', '~')}.notices.{tag}.json"
    try:
        kept = json.loads(path.read_text(encoding='utf-8'))
        checked, found = set(kept['checked']), set(kept['notices'])
    except (OSError, ValueError, TypeError, KeyError):
        checked, found = set(), set()
    rows = ix['rows']
    todo = {o for o, r in enumerate(rows) if r[0] not in checked}
    if todo:
        blobs = sorted({b for versions in ix['files'].values() for o, b, _ in versions if b and o in todo})
        found |= _notice_scan(corpus, blobs, extra)
        checked |= {r[0] for r in rows}
        try:  # a cache: a tree that cannot be written to makes the list again next time, nothing more
            tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps({'checked': sorted(checked), 'notices': sorted(found)}), encoding='utf-8')
            os.replace(tmp, path)
        except OSError:
            pass
    _CACHE[key] = frozenset(found)
    return _CACHE[key]  # type: ignore[return-value]


def _notice_scan(corpus: str, blobs: list[str], extra: tuple) -> set[str]:
    """The blobs among `blobs` that are repeal notices. Only blobs of at most NOTICE_MAX_BYTES can be. Reading each
    costs minutes on a large corpus (git rebuilds it from its pack's deltas), so they are listed as one tree in the
    private tree store and one `git grep` names those holding a notice word (NOTICE_STEMS); only those are read. A
    corpus's own patterns can match any words, so with them every small blob is read."""
    import os
    cwd = corpus_dir(corpus)
    small = []
    for i in range(0, len(blobs), 50000):
        got = subprocess.run(['git', 'cat-file', '--buffer', '--batch-check=%(objectname) %(objectsize)'], cwd=cwd,
                             input=''.join(f'{b}\n' for b in blobs[i:i + 50000]).encode(), capture_output=True)
        for line in got.stdout.decode('ascii', 'replace').splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit() and int(parts[1]) <= NOTICE_MAX_BYTES:
                small.append(parts[0])
    if small and not extra:
        store = _tree_store()
        objects = git('rev-parse', '--path-format=absolute', '--git-path', 'objects', cwd=cwd).strip()
        env = {**os.environ, 'GIT_INDEX_FILE': str(store / f'notice-index-{os.getpid()}'),
               'GIT_OBJECT_DIRECTORY': str(store / 'objects'), 'GIT_ALTERNATE_OBJECT_DIRECTORIES': objects}
        listing = b''.join(f'100644 blob {b}\t{b[:2]}/{b}'.encode() + b'\0' for b in small)
        run = subprocess.run(['git', 'update-index', '--add', '-z', '--index-info'], cwd=cwd, env=env, input=listing,
                             capture_output=True)
        tree = subprocess.run(['git', 'write-tree'], cwd=cwd, env=env, capture_output=True, encoding='utf-8')
        try:
            os.unlink(env['GIT_INDEX_FILE'])
        except OSError:
            pass
        if not run.returncode and not tree.returncode:
            words = sorted({w for s in NOTICE_STEMS for w in (s, s.upper(), s.capitalize())})
            grep = subprocess.run(['git', 'grep', '-l', '-F', '-i', *[x for w in words for x in ('-e', w)],
                                   tree.stdout.strip(), '--'], cwd=cwd, capture_output=True)
            if grep.returncode in (0, 1):
                small = [line.rsplit('/', 1)[-1] for line in grep.stdout.decode('ascii', 'replace').splitlines()]
    hits = set()
    for i in range(0, len(small), 20000):
        got = subprocess.run(['git', 'cat-file', '--buffer', '--batch'], cwd=cwd, capture_output=True,
                             input=''.join(f'{b}\n' for b in small[i:i + 20000]).encode()).stdout
        at = 0
        while at < len(got):
            end = got.index(b'\n', at)
            head = got[at:end].split()
            at = end + 1
            if len(head) < 3 or head[1] != b'blob':
                continue
            size = int(head[2])
            text = got[at:at + size].decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
            at += size + 1
            if repeal_notice(text, extra):
                hits.add(head[0].decode('ascii'))
    return hits


def _names_law(by: str, law: str) -> bool:
    """Whether an act's ending law (acts.json `repealed_by` ...) names the law that made a version: an official id they
    share (BOE-A-2012-1033), or one name holding the other."""
    by, law = by.strip().lower(), law.strip().lower()
    if not by or not law:
        return False
    ids = re.compile(r'\b[a-z]{2,}-[a-z]-\d{4}-\d+\b')
    if set(ids.findall(by)) & set(ids.findall(law)):
        return True
    return (len(law) >= 6 and law in by) or (len(by) >= 6 and by in law)


def after_end(corpus: str, end: dict, cut: tuple, in_force: str, order: int, blob: str | None,
              rel: str | None = None) -> str | None:
    """The act-end rule, which history(), file_index (and so every tree), ended_rows (laws, timeline) and
    correction_cap share: for a version of a file whose act data/acts.json ends (act_end), why it does not take
    force, or None when it does. A version at or before the end (`cut`: the end day and the end commit's place that
    day) takes force as dated. One after it re-enacts the file only when all of these hold:
      - its law was enacted on or after the end day (reenacts): a delayed amendment made before the repeal, or a
        version with no enactment date, amended an act that no longer exists;
      - its law is not the law that ended the act (`repealed_by` ...): Spain's repealing laws restate the repeal in
        the repealed act's folder, sometimes after the day acts.json gives;
      - its text is not a repeal or annulment note (notice_text: "Norma derogada ...", "(Derogada)");
      - given the file (`rel`), it is not the text in force at the end with only quoted repeal notes added
        (adds_only_repeal_note: BOE's "> Se derogan las reglas ..." for a later partial repeal of an ended act).
    A real later amendment to an ended act (Ley 9/2015 amending the repealed corporate-tax law for past tax periods)
    still re-enacts its file, and file_notes says so. Text is read only for a version that passes the first two."""
    if (in_force, order) <= cut:
        return None
    row = _index(corpus)['rows'][order]
    made = enacted_day(row[7])
    if not reenacts(end, row[7]):
        return f'enacted {made}' if made else 'no enactment date'
    if _names_law(end['by'], row[1]):
        return f'enacted {made}; the law that ended the act'
    extra = notice_patterns(corpus)
    if blob and extra is not None and repeal_notice(_blob_text(corpus, blob), extra, lead=True):
        return f'enacted {made}; a repeal note, not a re-enactment'
    if blob and rel:
        before = _pre_end_blob(corpus, rel, cut)
        if before and before != blob and adds_only_repeal_note(_blob_text(corpus, before), _blob_text(corpus, blob)):
            return f'enacted {made}; the ended text with a repeal note added, not a re-enactment'
    return None


# One added line of a quoted change note that records a repeal or annulment: BOE's "> Se derogan las reglas ...",
# "> Queda derogado ...", "> Derogado ...", "> Se anula ...".
ADDED_REPEAL_NOTE = re.compile(r'^>\s*(?:se\s+(?:derogan?|anulan?)\b|quedan?\s+(?:derogad|anulad|sin\s+efecto)'
                               r'|(?:derogad|anulad)[oa]s?\b)', re.I)


def adds_only_repeal_note(before: str | None, after: str | None) -> bool:
    """Whether `after` is `before` with nothing changed but added quoted repeal-note lines (ADDED_REPEAL_NOTE) and
    blank lines: no line removed or rewritten, at least one note added. Conservative: any other difference is a change
    to the law."""
    if before is None or after is None:
        return False
    import difflib
    a, b = before.splitlines(), after.splitlines()
    added = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        if tag != 'insert' and any(line.strip() for line in a[i1:i2]):
            return False
        added += [line for line in b[j1:j2] if line.strip()]
    return bool(added) and all(ADDED_REPEAL_NOTE.match(line.strip()) for line in added)


def _pre_end_blob(corpus: str, rel: str, cut: tuple) -> str | None:
    """The blob of a file's last ordinary version at or before its act's end (`cut`), or None."""
    ix = _index(corpus)
    rows = ix['rows']
    best = None
    for o, blob, _ in ix['files'].get(rel, []):
        r = rows[o]
        if r[9] or not r[5] or r[4] == 'documentation' or (r[5], o) > cut:
            continue
        if best is None or (r[5], o) > best[0]:
            best = ((r[5], o), blob)
    return best[1] if best else None


def _blob_text(corpus: str, blob: str) -> str | None:
    key = ('blob-text', f'{corpus}:{blob}')
    if key not in _CACHE:
        _CACHE[key] = read_object(corpus, blob)
    return _CACHE[key]  # type: ignore[return-value]


def _cut(corpus: str, rel: str) -> tuple[dict, tuple] | None:
    """(end, cut) for a file whose act data/acts.json ends on a day (act_end), else None."""
    end = act_end(corpus, rel)
    if not end or not end['day']:
        return None
    return end, (end['day'], _end_commit(corpus, end)[1] + 0.5)


def reenacted_on(corpus: str, rel: str) -> str | None:
    """The first day after its act's end that a version brings a file back into force (after_end), else None."""
    got = _cut(corpus, rel)
    if not got:
        return None
    end, cut = got
    ix = _index(corpus)
    rows = ix['rows']
    days = [rows[o][5] for o, blob, _ in ix['files'].get(rel, [])
            if not rows[o][9] and rows[o][5] and rows[o][4] != 'documentation' and (rows[o][5], o) > cut
            and after_end(corpus, end, cut, rows[o][5], o, blob, rel) is None]
    return min(days, default=None)


def correction_cap(corpus: str, rel: str, start: str) -> str | None:
    """The last day a correction starting on `start` may apply to a file, given its act's end (data/acts.json): the day
    before the end, so a corrected range that runs past the end does not keep the file in force; for a correction
    starting after the end, None (no cap) once a later version re-enacted the file by then, else the day before
    `start` (it never applies). None when the act has no dated end."""
    got = _cut(corpus, rel)
    if not got:
        return None
    end = got[0]
    import datetime as dt
    if start >= end['day']:
        back = reenacted_on(corpus, rel)
        if back and back <= start:
            return None
        return (dt.date.fromisoformat(start) - dt.timedelta(days=1)).isoformat()
    return (dt.date.fromisoformat(end['day']) - dt.timedelta(days=1)).isoformat()


def ended_rows(corpus: str) -> frozenset:
    """Index rows of ordinary commits every file version of which after_end keeps out of force: a law that only
    changed acts data/acts.json had already ended (Spain's repealing decrees writing their note into the repealed
    act's folder after its end day). history() lists none of its versions, so law_events leaves it out too, and
    `laws` and the timeline do not say it took force."""
    ends = act_ends(corpus)
    if not any(e['day'] for e in ends.values()):
        return frozenset()
    ix = _index(corpus)
    key = ('ended-rows', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        rows = ix['rows']
        touched: dict[int, int] = {}
        dropped: dict[int, int] = {}
        folders = {f for f, e in ends.items() if e['day']}
        for rel, versions in ix['files'].items():
            parts = rel.split('/')
            got = _cut(corpus, rel) if any('/'.join(parts[:i]) in folders for i in range(1, len(parts))) else None
            for order, blob, _ in versions:
                r = rows[order]
                if r[9] or not r[5] or r[4] == 'documentation':
                    continue
                touched[order] = touched.get(order, 0) + 1
                if got and after_end(corpus, got[0], got[1], r[5], order, blob, rel):
                    dropped[order] = dropped.get(order, 0) + 1
        _CACHE[key] = frozenset(o for o, n in dropped.items() if n == touched[o])
    return _CACHE[key]  # type: ignore[return-value]


def _days(a: str, b: str) -> int | None:
    """Days from a to b (ISO dates), or None when either is not a real date (2021-02-30)."""
    import datetime as dt
    try:
        return (dt.date.fromisoformat(b[:10]) - dt.date.fromisoformat(a[:10])).days
    except ValueError:
        return None


def act_ends(corpus: str) -> dict[str, dict]:
    """Acts the corpus's data/acts.json (corpus standard, gitlaw_common) records as repealed, expired or annulled, at
    the pinned commit: act folder -> {'act', 'how' ('repealed', 'expired' or 'annulled'), 'day' (or None when not
    recorded), 'by' (`<how>_by`)}. A builder may record a whole-law repeal there without removing each file of the law
    (spain-law until November 2026: 1,991 norms), so the readers end every file of the act on that day themselves. An
    annulment (a court striking the act down: 16 Spanish decrees and orders) ends it like a repeal, from the day
    recorded."""
    ix = _index(corpus)
    key = ('act-ends', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        out: dict[str, dict] = {}
        facts: dict[str, dict] = {}
        try:
            acts = json.loads(read_object(corpus, f"{ix['pin']}:data/acts.json") or '{}').get('acts') or []
        except (ValueError, AttributeError):
            acts = []
        for a in acts if isinstance(acts, list) else []:
            folder = str(a.get('path') or a.get('slug') or '').strip('/') if isinstance(a, dict) else ''
            if not folder:
                continue
            facts[folder] = a
            _CACHE[('act-facts', f"{corpus}@{_at(ix)}")] = facts
            status = str(a.get('status') or '').lower()
            for how in ('repealed', 'expired', 'annulled'):
                d = a.get(how)
                if isinstance(d, str) and ISO_DAY.match(d) and status not in ('in force', 'not yet in force'):
                    out[folder] = {'act': folder, 'how': how, 'day': d[:10], 'by': str(a.get(f'{how}_by') or '')}
                    break
            else:
                if status in ('repealed', 'expired', 'annulled'):
                    out[folder] = {'act': folder, 'how': status, 'day': None, 'by': str(a.get(f'{status}_by') or '')}
        _CACHE[key] = out
    return _CACHE[key]  # type: ignore[return-value]


def act_fact(corpus: str, rel: str) -> dict:
    """data/acts.json's row for the act holding a file (its longest folder), or {}."""
    act_ends(corpus)
    facts = _CACHE.get(('act-facts', f"{corpus}@{_at(_index(corpus))}")) or {}
    parts = rel.split('/')
    for i in range(len(parts) - 1, 0, -1):
        f = facts.get('/'.join(parts[:i]))  # type: ignore[union-attr]
        if f:
            return f
    return {}


def act_end(corpus: str, rel: str) -> dict | None:
    """The end data/acts.json records for the act holding a file (its longest folder), or None."""
    ends = act_ends(corpus)
    if not ends:
        return None
    parts = rel.split('/')
    for i in range(len(parts) - 1, 0, -1):
        e = ends.get('/'.join(parts[:i]))
        if e:
            return e
    return None


def _end_commit(corpus: str, end: dict) -> tuple[str, int]:
    """The commit that ended an act, for the history row of its repeal: of the commits in force on that day, one that
    names the repealing law (its author or subject), else the latest; else the pinned commit, where data/acts.json
    says so. (commit, its row)."""
    ix = _index(corpus)
    key = ('end-commit', f"{corpus}@{_at(ix)}:{end['act']}")
    if key not in _CACHE:
        rows = ix['rows']
        that_day = [i for i, r in enumerate(rows) if r[5] == end['day'] and r[4] != 'documentation']
        by = end['by'].lower()
        named = [i for i in that_day if by and (by in rows[i][1].lower() or by in rows[i][3].lower()
                                                 or rows[i][1].lower() in by)]
        pick = (named or that_day or [None])[-1]
        _CACHE[key] = (rows[pick][0], pick) if pick is not None else (ix['pin'], len(rows))
    return _CACHE[key]  # type: ignore[return-value]


def capture_day(corpus: str) -> tuple[str, int, int] | None:
    """(day, commits that day, dated commits) when a third or more of a corpus's dated commits take force on one day
    and they are not marked as starting texts: a capture day written as an in-force date (check_corpus.py warns the
    builder; New Jersey 713 of 1,145 on 3 November 2026). None otherwise."""
    ix = _index(corpus)
    key = ('capture-day', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        days: dict[str, int] = {}
        starting: dict[str, int] = {}
        for r in ix['rows']:
            if r[5] and r[4] != 'documentation':
                days[r[5]] = days.get(r[5], 0) + 1
                if r[4] == 'baseline':
                    starting[r[5]] = starting.get(r[5], 0) + 1
        total = sum(days.values())
        found = None
        if total >= 20:
            d, n = max(days.items(), key=lambda kv: kv[1])
            if n / total >= 0.3 and starting.get(d, 0) < n / 2:
                found = (d, n, total)
        _CACHE[key] = found
    return _CACHE[key]  # type: ignore[return-value]


# Commit kinds. Corpora write many words in Kind:; the tools read them as one of: law (a law taking effect),
# baseline (a starting text: the text as a publisher gave it, no law named), correction, printing, court (a ruling),
# treaty, uncredited (a change no law is named for), documentation. A word not listed is read as a law and named in
# the caveats, never silently.
_LAW_KINDS = {'', 'law', 'decree', 'amendment', 'act', 'amending law', 'lov', 'lbk', 'laki', 'ustawa', 'zakon',
              'rozporządzenie', 'legal notice', 'ordinance', 'several', 'enacted', 'original', 'version', 'repeal'}
_START_KINDS = {'baseline', 'consolidated', 'current', 'current-only', 'current-text', 'publisher', 'consolidation',
                'first published version (publisher)', 'tekst jednolity (current text)'}
_UNCREDITED_KINDS = {'unexplained', 'change no law explains', 'republication', 'obwieszczenie'}
_COURT_KINDS = {'orzeczenie', 'nález'}  # rulings of the Polish and Slovak constitutional courts
# Words in the longer Kind values corpora write (Australia, Canada, Hong Kong, Poland, Portugal and others).
_START_WORDS = ('first version in the database', 'oldest version available', 'publisher-text', 'record starts here')
_UNCREDITED_WORDS = ('editorial', 'notes only', 'style only', 'no act named', 'no law named', 'no amending law',
                     'not identified', 'several candidate laws', 'credited to neither', 'no change to the',
                     'without a change', 'no change in the text', 'removed from the consolidation', 'layout',
                     'typesetting', 'reprint')
_CORRECTION_WORDS = ('retificação', 'rectificação', 'ispravak', 'sprostowanie')
_LAW_WORDS = ('law', 'act', 'decree', 'decreto', 'regulation', 'instrument', 'notice', 'order in council', 'lei',
              'zákon', 'zakon', 'закон', 'ustav', 'uredba', 'constitution', 'constituicao', 'конституция',
              'referendum', 'reform', 'amend', 'enact', 'lov', 'lag', 'laki', 'expiry', 'replacement', 'reverted',
              'declaração', 'uznesenie', 'several', 'two or more', '修', '决定', 'regulation (sor)')


MAINTAINER = 'Lexifina'  # the author of documentation commits, and of some corpora's versions (the UK, Romania's corrections)


def maintainer_credit(t: dict, subject: str) -> str:
    """The law a maintainer-written version stands for: its Law: trailer, else the act its subject names ("Sentencing
    Act 2020: Royal Assent, the text as enacted", "Correction: Legea nr. 85/2003 as in force on 2003-03-27")."""
    if t.get('Law'):
        return t['Law']
    name = re.sub(r'^Correction:\s*', '', subject.strip())
    name = re.split(r':\s| as (?:enacted|in force|published|made|amended)\b| the text\b', name, maxsplit=1)[0].strip()
    return name or MAINTAINER


def moves(corpus: str) -> dict[str, str]:
    """old path -> its path at the pin, for files a documentation commit moved unchanged (romania-law's layout move of
    November 2026: codul-civil/art-1112.md is lege/2009/287/art-1112.md). Their history is the new path's (_extend)."""
    ix = _index(corpus)
    key = ('moves', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        step, out = ix.get('moves', {}), {}
        for old, new in step.items():
            seen = {old}
            while new in step and new not in seen:  # moved again later
                seen.add(new)
                new = step[new]
            out[old] = new
        _CACHE[key] = out
    return _CACHE[key]  # type: ignore[return-value]


def withdrawn(corpus: str) -> dict[str, str]:
    """path -> the commit (not a law) that removed it and its versions from the record (_extend)."""
    return dict(_index(corpus).get('withdrawn', {}))


def credited(corpus: str, rel: str, in_force: str, commit: str = '') -> tuple[str, bool, str] | None:
    """A corrected credit for one provision's change of one day, made by `commit`: (the law's label, whether it is
    "no law", the label first credited), or None. romania-law corrects a wrongly credited change without restating
    it: a Kind: correction commit with no In-force adds rows to data/credits.csv (act,in_force,provision,law,was_law,
    was_commit; the last row for a key counts; labels in data/laws.csv). A row naming the commit it re-credits applies
    to that commit only; a row without one, to the day. The commit's author stays as published."""
    pin = _index(corpus)['pin']
    folder, _, unit = rel.rpartition('/')
    table = _credits_for(corpus, pin, folder)
    if not table:
        return None
    found = table.get((folder, in_force, unit.removesuffix('.md')), [])  # type: ignore[union-attr]
    mine = [e for c, e in found if c and commit and (c.startswith(commit) or commit.startswith(c))]
    return (mine or [e for c, e in found if not c] or [None])[-1]


def _credits_for(corpus: str, pin: str, folder: str) -> dict:
    """data/credits.csv's rows for one act folder, as credited() reads them. Only the lines that name the folder (or
    the act's name before the layout move) are parsed: a read of one provision parses a few rows, not every row of
    the table and of data/laws.csv (0.3 s on romania-law)."""
    import csv
    import io
    key = ('credits-raw', f'{corpus}@{pin}')
    if key not in _CACHE:
        text = read_object(corpus, f'{pin}:data/credits.csv') or ''
        header, _, body = text.partition('\n')
        raw = None
        if {'act', 'in_force', 'provision', 'law'} <= set(next(csv.reader([header]), [])):
            try:
                folders = json.loads(read_object(corpus, f'{pin}:data/paths.json') or '{}').get('paths', {})
            except ValueError:
                folders = {}
            raw = {'header': header, 'lines': body.splitlines(), 'folders': folders, 'labels': None,
                   'quoted': '"' in body or header.split(',')[0] != 'act'}  # else every row is parsed
        _CACHE[key] = raw
    raw = _CACHE[key]
    if raw is None:
        return {}
    fkey = ('credits', f'{corpus}@{pin}@{folder}')
    if fkey not in _CACHE:
        names = {folder} | {act for act, now in raw['folders'].items() if now == folder}
        lines = raw['lines'] if raw['quoted'] else [l for l in raw['lines'] if l.split(',', 1)[0] in names]
        table: dict[tuple[str, str, str], list] = {}
        if lines and raw['labels'] is None:
            laws = csv.DictReader(io.StringIO(read_object(corpus, f'{pin}:data/laws.csv') or ''))
            raw['labels'] = {r.get('key', ''): r.get('label', '') for r in laws}
        unexplained = 'no law named (a change the record leaves unexplained)'
        for r in csv.DictReader(io.StringIO('\n'.join([raw['header'], *lines]))):
            law_key, was = (r.get('law') or '').strip(), (r.get('was_law') or '').strip()
            labels = raw['labels']
            entry = (labels.get(law_key) or law_key or unexplained, not law_key, labels.get(was) or was or unexplained)
            for f in {r['act'], raw['folders'].get(r['act'], r['act'])}:  # the act's folder now and before the move
                if f == folder:
                    table.setdefault((f, r['in_force'], r['provision']), []).append(((r.get('was_commit') or '').strip(), entry))
        _CACHE[fkey] = table
    return _CACHE[fkey]  # type: ignore[return-value]


def countries_cmd() -> str:
    """tools/countries.py as the user runs it here: with the Python that started the MCP server (tools/mcp.sh sets
    GLOBAL_LAW_PYTHON), else python3, or python on Windows, where python3 is usually the Microsoft Store's placeholder."""
    import os
    return f"{os.environ.get('GLOBAL_LAW_PYTHON') or ('python' if sys.platform == 'win32' else 'python3')} tools/countries.py"


def kind_of(raw: str | None, author: str = '') -> tuple[str, str | None]:
    """(the tools' kind, the word itself when it is not one the tools know) for a commit's Kind: and author."""
    k = (raw or '').strip().lower()
    if author == 'Lexifina' or k == 'documentation':
        return 'documentation', None
    if k in ('correction', 'printing', 'treaty'):
        return k, None
    if k == 'court' or k.startswith('court ') or k in _COURT_KINDS:
        return 'court', None
    if k in _START_KINDS or k.startswith(('baseline', 'first published')) or any(w in k for w in _START_WORDS):
        return 'baseline', None
    if k in _UNCREDITED_KINDS or 'not credited' in k or any(w in k for w in _UNCREDITED_WORDS):
        return 'uncredited', None
    if any(w in k for w in _CORRECTION_WORDS):
        return 'correction', None
    if k in _LAW_KINDS or any(w in k for w in _LAW_WORDS):
        return 'law', None
    return 'law', k


CREDIT = {'printing': '{} (printing)', 'baseline': '{} (text as published; no law named)', 'correction': '{} (correction)',
          'court': '{} (court ruling, not a law)', 'treaty': '{} (treaty)', 'uncredited': '{} (no law named for this change)'}


def credit(author: str, kind: str) -> str:
    """How blame and words credit a version: a law by its name; anything else says what it is."""
    return CREDIT.get(kind, '{}').format(author)


INDEX_VERSION = 8  # raise when what the index keeps changes: old indexes are then rebuilt


def _index_version() -> str:
    """INDEX_VERSION and a fingerprint of the tables a commit's kind is read with: the index keeps each commit's kind,
    so an index built before a Kind word was added kept calling it unknown (Romania's "referendum" note, 3 November
    2026, long after the word was known). A change to the tables now rebuilds the index by itself."""
    import hashlib
    tables = repr([sorted(t) for t in (_LAW_KINDS, _START_KINDS, _UNCREDITED_KINDS, _COURT_KINDS)]
                  + [list(t) for t in (_START_WORDS, _UNCREDITED_WORDS, _CORRECTION_WORDS, _LAW_WORDS)] + [MAINTAINER])
    return f'{INDEX_VERSION}-{hashlib.sha256(tables.encode("utf-8")).hexdigest()[:12]}'


def _derive(info: dict, commit: str, author: str, when: str, subject: str, block: str) -> tuple[tuple, str | None]:
    """One commit as the index keeps it: (commit, author, date, subject, kind, in force or None, Kind as written,
    enacted, published, correction or None), and the Kind word when it is not one the tools know."""
    every = trailer_values(block)
    t = {k: v[0] for k, v in every.items()}
    raw = (t.get('Kind') or '').strip()
    kind, unknown = kind_of(raw, author)
    trailer = info.get('in_force_trailer') or 'In-force'
    # Lexifina writes documentation, and also versions of the law: the UK corpus's texts (9,201 of its 9,212 commits)
    # and romania-law's corrections. A maintainer's commit is documentation only when it has no in-force day; a dated
    # one is a version, credited to its Law: trailer or the act its subject names (and, for a restated version, the
    # law of the version it restates: _extend).
    if kind == 'documentation' and author == MAINTAINER and raw.lower() != 'documentation' and \
            (ISO_DAY.match(t.get(trailer) or '') or ISO_DAY.match(t.get('Text-as-of') or '')):
        kind, unknown = kind_of(raw, '')
        author = maintainer_credit(t, subject)
    if kind == 'documentation':
        return (commit, author, when, subject, kind, None, raw, None, None, None), None
    # The shared builder writes Kind: publisher both for an act's first text and for a change in a later text that no
    # law explains ("... (unexplained)", Words-changed: yes): the second is a change no law is named for.
    if raw.lower() == 'publisher' and ('(unexplained)' in subject or t.get('Words-changed', '').lower() == 'yes'):
        kind = 'uncredited'
    in_force = t.get(trailer)
    # A text read on a day, with no in-force day of its own: Text-as-of alone, or In-force set to that same day, or
    # In-force-basis saying the source gives no date. It is a starting text: before it the record does not reach.
    as_of = t.get('Text-as-of', '')[:10] if ISO_DAY.match(t.get('Text-as-of', '')) else None
    no_date = 'no date' in t.get('In-force-basis', '').lower()
    if as_of and (not in_force or in_force[:10] == as_of or no_date):
        in_force, kind = in_force or as_of, ('baseline' if kind == 'law' else kind)
    elif no_date and kind == 'law':
        kind = 'baseline'
    via = None
    for key, label in (('baseline_trailer', 'baseline'), ('correction_trailer', 'correction')):
        k = info.get(key)
        if k and not in_force and k in t and ISO_DAY.match(t[k]):
            in_force, via = t[k][:10], label
    if not in_force and 'Printed-in' in t:
        in_force, kind = when[:10], 'printing'
    fix = None
    # An overlay correction names the days it covers (Corrects: <act> <from>..<to>). One that names a commit
    # (Corrects: or Re-asserts: <commit>, as romania-law appends them: 1,092 by 3 November 2026) restates a version
    # with its own In-force day: an ordinary version, the later commit winning its day. Read as overlays they each
    # cost a path-limited git log, and a whole country on a past date timed out.
    span = CORRECTS.search(t.get('Corrects', '')) if raw.lower() == 'correction' else None
    if span:
        start = span.group(1)
        if ISO_DAY.match(start):
            fix = {'commit': commit, 'law': author, 'from': start, 'to': span.group(2) if span else None,
                   'files': every.get('Files', []), 'act_path': t.get('Act-path'), 'corrects': t['Corrects'],
                   'supersedes': t.get('Supersedes'), 'reason': t.get('Reason')}
            in_force = in_force or start  # a correction appended at the tip: dated by the first day it corrects
    if via == 'correction' or (info.get('correction_trailer') and info['correction_trailer'] in t):
        kind = 'correction'
    elif via == 'baseline' and kind == 'law':
        kind = 'baseline'
    in_force = in_force[:10] if in_force and ISO_DAY.match(in_force) else None
    enacted = next((t[k] for k in ENACTED if k in t), None)
    published = next((t[k] for k in PUBLISHED if k in t), None)
    return (commit, author, when, subject, kind, in_force, raw, enacted, published, fix), unknown


REDATES = re.compile(r'^Redates:\s*([0-9a-f]{7,40})\s+(\d{4}-\d{2}-\d{2}|no-date)\s*$', re.M)


def _redate(data: dict, rows: list, block: str) -> None:
    """A dated version's date, corrected by a later commit (corpus standard; an append-only corpus cannot change the
    commit itself). One `Redates: <commit> <YYYY-MM-DD>` trailer per version gives the day it took force;
    `Redates: <commit> no-date` says the source gives none, so the version is text as of its recorded day. With
    `Retroactive: yes; <provision>` the versions took force before their act was made, as that provision says."""
    retro = trailer_lines(block).get('Retroactive', '').strip().lower().startswith('yes')
    for target, day in REDATES.findall(block):
        at = data['pos'].get(target) if len(target) == 40 else \
            next((i for c, i in data['pos'].items() if c.startswith(target)), None)
        if at is None:
            continue
        r = rows[at]
        if day == 'no-date':
            if r[4] == 'law':
                rows[at] = r[:4] + ('baseline',) + r[5:]
        else:
            rows[at] = r[:5] + (day,) + r[6:]
            if r[9]:  # an overlay correction (Corrects: <act> <from>..<to>): its text applies from the corrected day
                rows[at] = rows[at][:9] + ({**r[9], 'from': day},)
        data.setdefault('redated', {})[r[0]] = (r[5], day)
        if retro:
            data.setdefault('retroactive', set()).add(r[0])


def _extend(corpus: str, cwd: Path, data: dict, revs: str, skip: frozenset = frozenset()) -> None:
    """Add the commits in `revs` to a corpus index, oldest first: one `git log --raw` for every commit and file.
    Commits in `skip` are left out (a forked future branch's copies of main's commits: _future_index)."""
    info = corpus_info(corpus)
    fmt = '--format=%x1d%H%x1f%an%x1f%aI%x1f%s%x1f%(trailers:only,unfold)%x1e'
    raw = git('log', '--reverse', '--raw', '--find-renames=100%', '--no-abbrev', fmt, revs, cwd=cwd)
    legacy = None
    rows, files = data['rows'], data['files']
    for chunk in raw.split('\x1d')[1:]:
        head, _, changes = chunk.partition('\x1e')
        commit, author, when, subject, block = head.split('\x1f', 4)
        if commit in skip:
            continue
        row, unknown = _derive(info, commit, author, when, subject, block)
        if unknown:
            data['unknown'].add(unknown)
        if trailer_lines(block).get('Retroactive', '').strip().lower().startswith('yes'):
            # "Retroactive: yes; <the provision that says so>" (corpus standard): in force before the act was made, and
            # the source says so: not a doubtful date.
            data.setdefault('retroactive', set()).add(commit)
        if author == MAINTAINER and row[4] != 'documentation':
            # A restated version (Corrects: or Re-asserts: <commit>) is credited to the law of the version it
            # restates, followed back through a correction of a correction.
            t = trailer_lines(block)
            target = (t.get('Corrects') or t.get('Re-asserts') or '').split()
            if target and re.fullmatch(r'[0-9a-f]{7,40}', target[0]) and not CORRECTS.search(target[0]):
                data['restates'][commit] = (target[0], 'Corrects' if t.get('Corrects') else 'Re-asserts')
                at = data['pos'].get(target[0]) if len(target[0]) == 40 else \
                    next((i for c, i in data['pos'].items() if c.startswith(target[0])), None)
                if at is not None and not t.get('Law'):
                    row = (row[0], rows[at][1]) + row[2:]
        if author == MAINTAINER and 'Redates:' in block:
            _redate(data, rows, block)
        data['pos'][commit] = len(rows)
        if row[5] is None and row[4] != 'documentation':
            legacy = legacy if legacy is not None else legacy_dates(corpus)
            if commit in legacy:
                day_, k = legacy[commit]
                kind = kind_of(k, author)[0]
                row = row[:4] + (row[4] if kind == 'law' else kind, day_) + row[6:]
        order = len(rows)
        rows.append(row)
        for line in changes.splitlines():
            if not line.startswith(':') or '\t' not in line:
                continue
            meta, *paths = line.split('\t')
            f = meta.split()
            if f[4].startswith('R') and len(paths) == 2:
                old, new = _unquote(paths[0]), _unquote(paths[1])
                if row[4] == 'documentation':
                    # A file moved unchanged by a documentation commit (a corpus renaming its folders) keeps its
                    # history: the new path takes the old one's versions, which are read by blob, not by path.
                    files[new] = files.get(new, []) + files.pop(old, [])
                    data['moves'][old] = new  # one step; moves() follows a file moved more than once
                    continue
                files.setdefault(old, []).append((order, None, f[1]))  # moved by a law: gone here, new there
                files.setdefault(new, []).append((order, f[3], f[1]))  # f[1]: the new side's mode (f[2] is a blob id)
                continue
            path = _unquote(paths[0])
            if row[4] == 'documentation' and f[4].startswith('D'):
                # Deleted by a commit that is not a law: withdrawn (romania-law's Withdraws:, an act that never
                # belonged). Its versions leave the record on every day; read by in-force day alone, the act stayed
                # in force on every past date. A later law may add the path again.
                files.pop(path, None)
                data['withdrawn'][path] = commit
                continue
            files.setdefault(path, []).append((order, None if f[4].startswith('D') else f[3], f[1]))


def _main_index(corpus: str) -> dict:
    """The corpus read once at the commit the tree pins: every commit (rows, in history order) and every version of
    every file (files: path -> [(row, blob or None for a deletion, mode)]). Kept on disk in the tree's git folder
    (global-law-cache), keyed by the pin: a pin that moved forward adds only the new commits, so after the first read
    a corpus costs one file load, not a walk of its history."""
    cwd = corpus_dir(corpus)
    sha = tip(corpus)
    if not sha:
        raise SystemExit(f'{corpus} is not pinned in this tree')
    key = ('index', f'{corpus}@{sha}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    if not _has_commit(corpus, cwd, sha):
        raise SystemExit(f'{corpus}: this checkout does not have the commit the tree pins ({sha[:10]}), so the law it '
                         f'holds cannot be read as of now. Run: git submodule update --init -- {corpus}')
    import os
    store = _store()
    name = corpus.replace('/', '~')
    # Named by version and pin: a file is never replaced in place (a reader holds its file open, row 22 of the audit
    # of 4 November 2026), and a new pin extends the newest index of an earlier pin.
    path = store / f'{name}.v{INDEX_VERSION}.{sha[:12]}.index'
    source = path
    if not path.is_file():
        older = [f for f in store.glob(f'{name}.v{INDEX_VERSION}.*index') if f.suffix == '.index'] if store.is_dir() else []
        source = max(older, key=lambda f: f.stat().st_mtime) if older else path
    data = None
    changed = False
    try:
        data = _load_index(source)
        if data.get('v') != _index_version():
            data = None
    except Exception:
        data = None
        try:  # an index kept in one piece (until 4 November 2026): read once, and kept in pieces from now on
            with open(path.with_suffix('.pickle'), 'rb') as f:
                data = _unpickle(f.read())
            changed = data.get('v') == _index_version() or None
            data = data if changed else None
        except Exception:
            data = None
    if data and source != path and data['pin'] == sha:  # the same pin under an earlier name: kept under this one
        held = data['files']
        data['files'] = dict(held.items())
        held.close()
        changed = True
    if data and data['pin'] != sha:
        held = data['files']
        data['files'] = dict(held.items())  # every file, to extend
        held.close()  # so that the index of the earlier pin can be removed below
        forward = subprocess.run(['git', 'merge-base', '--is-ancestor', data['pin'], sha], cwd=cwd,
                                 capture_output=True).returncode == 0
        if forward:
            _extend(corpus, cwd, data, f"{data['pin']}..{sha}")
            data['pin'], changed = sha, True
        else:
            data = None
    if data is None:
        # moves: old path -> new, one step each (moves()); withdrawn: path -> the commit that removed it; restates:
        # correction -> the commit it restates; pos: commit -> its row.
        data = {'v': _index_version(), 'pin': sha, 'rows': [], 'files': {}, 'unknown': set(), 'moves': {}, 'withdrawn': {},
                'restates': {}, 'pos': {}, 'retroactive': set()}
        _extend(corpus, cwd, data, sha)
        changed = True
    if changed:
        try:  # a cache: a tree that cannot be written to is read the slow way next time, nothing more
            store.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
            _save_index(tmp, data)
            os.replace(tmp, path)
        except OSError:
            try:
                tmp.unlink(missing_ok=True)  # a refused replace leaves no corpus-sized .tmp behind
            except (OSError, NameError):
                pass
        _prune_indexes(store, name, path)
    _forget_other_pins(corpus, sha)
    _CACHE[key] = data
    return data


def _prune_indexes(store: Path, name: str, keep: Path) -> None:
    """Remove a corpus's indexes this one replaces: earlier pins of this version, the names used before (one piece
    until 4 November 2026, then one per version), other versions unused for a week, and .tmp files over an hour old.
    A file another process still reads is refused on Windows and left for a later run; elsewhere it stays readable
    to the process that holds it open."""
    import time
    now = time.time()
    for f in store.glob(f'{name}.*'):
        if f == keep or not f.name.startswith(name + '.'):
            continue
        try:
            age = now - f.stat().st_mtime
            this_version = f.name.startswith(f'{name}.v{INDEX_VERSION}.')
            if (f.suffix == '.tmp' and age > 3600) or (f.suffix in ('.index', '.pickle') and (
                    this_version or not f.name.startswith(f'{name}.v') or age > 7 * 86400)):
                f.unlink()
        except OSError:
            pass


def _forget_other_pins(corpus: str, sha: str) -> None:
    """Drop what this process keeps for earlier pins of a corpus (a long-running reader, such as the MCP server, sees
    pins move several times an hour; each index of a large corpus holds hundreds of MB)."""
    mine = f'{corpus}@'
    for k in [k for k in _CACHE if len(k) == 2 and isinstance(k[1], str) and k[1].startswith(mine)
              and not k[1].startswith(mine + sha)]:
        v = _CACHE.pop(k)
        if k[0] == 'index' and isinstance(v, dict) and isinstance(v.get('files'), _Files):
            v['files'].close()


def _at(ix: dict) -> str:
    """What an index was read at, for the caches built from it: the pin, and the future pin when one is read with it."""
    return ix.get('at') or ix['pin']


def future_pins() -> dict[str, tuple[str, str, str]]:
    """{corpus: (future branch, future commit, main pin)} from the tree's data/future-pins.tsv (corpus, branch,
    future_sha, main_pin), written in the same root commit as the gitlinks (tools/future_pins.py), so a reading stays
    reproducible. A row names the main pin it was made for: it is read only while the tree still pins that commit."""
    key = ('future-pins', _head())
    if key not in _CACHE:
        out = {}
        for line in (_root()['files'].get('data/future-pins.tsv') or '').splitlines():
            parts = line.rstrip('\r').split('\t')
            if line.startswith('#') or len(parts) != 4:
                continue
            if all(re.fullmatch(r'[0-9a-f]{40}', x) for x in parts[2:]):
                out[parts[0]] = (parts[1], parts[2], parts[3])
        _CACHE[key] = out
    return _CACHE[key]  # type: ignore[return-value]


def future_note(corpus: str) -> str | None:
    """Why a corpus's future branch is not read, though the tree records it: the row was made for an earlier pin (the
    pin moved and data/future-pins.tsv was not written again with it), or the checkout lacks the commit. Then the
    reader shows main alone, and laws that took force since main's last law may be missing. None when it is read."""
    fp = future_pins().get(corpus)
    pin = tip(corpus)
    cwd = ROOT / corpus
    if not fp or not pin or not (cwd / '.git').exists() or not _readable(corpus, cwd):
        return None
    branch, fut, main_pin = fp
    if main_pin != pin:
        return (f"{corpus}: laws with a later in-force day are kept on its {branch} branch, but data/future-pins.tsv "
                f"records that branch for an earlier pin ({main_pin[:10]}, not {pin[:10]}), so it is not read: changes "
                "that took force after the last law on main may be missing until the file is written again.")
    if not _has_commit(corpus, cwd, fut):
        return (f"{corpus}: laws with a later in-force day are kept on its {branch} branch ({fut[:10]}), which this "
                "checkout does not have, so changes that took force after the last law on main may be missing. "
                f"Run: git -C {corpus} fetch origin {branch}  (if the branch has moved on since: git -C {corpus} "
                f"fetch origin refs/tags/global-law/future-pinned-{fut})")
    diverged = _future_check(corpus, corpus_dir(corpus), pin, fut)['diverged']
    if diverged:
        return (f"{corpus}: laws with a later in-force day are kept on its {branch} branch ({fut[:10]}), but "
                f"{len(diverged)} commit(s) there carry the author, date and message of a law on main and change "
                f"different text (first: {diverged[0][:10]}), so the branch is not read: main alone is shown, and "
                "changes that took force after the last law on main may be missing until the branch is rebuilt.")
    return None


def _tree_changes(cwd: Path, shas) -> dict[str, frozenset]:
    """Each commit's changes against its first parent, as (path, mode, blob id) after it (a zero id where it deletes
    the path), from one `git diff-tree --stdin`."""
    shas = list(dict.fromkeys(shas))
    if not shas:
        return {}
    done = subprocess.run(['git', 'diff-tree', '--stdin', '-r', '-m', '--first-parent', '--no-renames', '--root',
                           '--no-abbrev'], cwd=cwd, input=''.join(s + '\n' for s in shas), capture_output=True,
                          encoding='utf-8', errors='replace')
    if done.returncode:
        raise RuntimeError(f'git diff-tree --stdin: {done.stderr.strip()}')
    out: dict[str, set] = {s: set() for s in shas}
    sha = None
    for line in done.stdout.splitlines():
        if line.startswith(':'):
            meta, _, path = line.partition('\t')
            parts = meta.split()
            if sha is not None and len(parts) >= 5:
                out[sha].add((path, parts[1], parts[3]))
        elif line.strip():
            sha = line.split()[0]
            out.setdefault(sha, set())
    return {s: frozenset(v) for s, v in out.items()}


ZERO_SHA = '0' * 40


def _holds(cwd: Path, sha: str, change: frozenset) -> bool:
    """Whether a commit's tree has each path of `change` (another commit's _tree_changes) at that commit's blob, or
    lacks it where that commit deletes it: the commit carries the other's change, though it may change more, or have
    had the same text already. Trees only (git ls-tree), never blobs."""
    want = {path: blob for path, _, blob in change}
    have: dict[str, str] = {}
    paths = sorted(want)
    for i in range(0, len(paths), 200):  # keep the command line short
        out = subprocess.run(['git', '--literal-pathspecs', 'ls-tree', '-r', '-z', '--full-tree', sha, '--',
                              *paths[i:i + 200]], cwd=cwd, capture_output=True)
        if out.returncode:
            return False
        for entry in out.stdout.decode('utf-8', 'replace').split('\0'):
            meta, _, path = entry.partition('\t')
            if path:
                have[path] = meta.split()[2]
    return all(have.get(path, ZERO_SHA) == blob for path, blob in want.items())


def _replays(cwd: Path, pin: str, fut: str) -> tuple[frozenset, tuple]:
    """Commits of pin..fut that copy a main commit made after the fork: a forked future branch replays main's laws so
    that it reads whole on its own; read beside main they would be doubles. A copy has the main commit's author line,
    raw date and message, and leaves each path the main commit changes at the main commit's blob (the same change,
    or text the branch had already; a file more written or removed on the branch is left out with the copy).
    Returns (copies, diverged): diverged are the commits with a main commit's author, date and message whose tree
    holds other text at a path that commit changes (a "copy" which, read on, would undo main's change): the caller
    does not read such a branch."""
    fork = git('merge-base', pin, fut, cwd=cwd).strip()
    fmt = '--format=%x1d%H%x1f%an <%ae> %ad%x1f%B'

    def keyed(*revs: str) -> dict:
        out = {}
        for chunk in git('log', '--date=raw', fmt, *revs, cwd=cwd).split('\x1d')[1:]:
            sha, author, body = chunk.split('\x1f', 2)
            out[sha] = (author, body.strip())
        return out
    on_main: dict[tuple, list[str]] = {}
    for sha, k in (keyed(pin, f'^{fork}') if fork else {}).items():
        on_main.setdefault(k, []).append(sha)
    candidates = {sha: on_main[k] for sha, k in keyed(fut, f'^{pin}').items() if k in on_main}
    changed = _tree_changes(cwd, [*candidates, *(m for ms in candidates.values() for m in ms)])
    copies = frozenset(sha for sha, ms in candidates.items()
                       if any(changed.get(sha) == changed.get(m) for m in ms)  # the same change: no more to ask
                       or any(_holds(cwd, sha, changed.get(m, frozenset())) for m in ms))
    return copies, tuple(sha for sha in candidates if sha not in copies)


def _future_check(corpus: str, cwd: Path, pin: str, fut: str) -> dict:
    """Whether a recorded future commit descends from the pin (linear), and if not, which of its commits are copies
    of main's (skipped when read) and which only look like copies (diverged: the branch is not read). Once a process,
    and only once the checkout has the commit."""
    key = ('future-check', f'{corpus}@{pin}+{fut}')
    if key not in _CACHE:
        linear = subprocess.run(['git', 'merge-base', '--is-ancestor', pin, fut], cwd=cwd,
                                capture_output=True).returncode == 0
        skip, diverged = (frozenset(), ()) if linear else _replays(cwd, pin, fut)
        _CACHE[key] = {'linear': linear, 'skip': skip, 'diverged': diverged}
    return _CACHE[key]  # type: ignore[return-value]


_MISSING = object()


class _FilesOver:
    """An index's files with a future branch's versions laid over them, the main index left as it is: a path the
    branch touches is copied on first write, a path it removes is hidden. Read like the dict (or _Files) beneath."""

    def __init__(self, base):
        self._base, self._own, self._gone = base, {}, set()

    def get(self, rel, default=None):
        if rel in self._own:
            return self._own[rel]
        if rel in self._gone:
            return default
        return self._base.get(rel, default)

    def __getitem__(self, rel):
        v = self.get(rel, _MISSING)
        if v is _MISSING:
            raise KeyError(rel)
        return v

    def __contains__(self, rel) -> bool:
        return self.get(rel, _MISSING) is not _MISSING

    def setdefault(self, rel, default):
        if rel not in self._own:
            v = self.get(rel, _MISSING)
            self._own[rel] = list(v) if v is not _MISSING else default
            self._gone.discard(rel)
        return self._own[rel]

    def __setitem__(self, rel, value) -> None:
        self._own[rel] = value
        self._gone.discard(rel)

    def pop(self, rel, *default):
        v = self.get(rel, _MISSING)
        if v is _MISSING:
            if default:
                return default[0]
            raise KeyError(rel)
        self._own.pop(rel, None)
        self._gone.add(rel)
        return v

    def items(self):
        out, seen = [], set()
        for rel, v in self._base.items():
            seen.add(rel)
            if rel in self._own:
                out.append((rel, self._own[rel]))
            elif rel not in self._gone:
                out.append((rel, v))
        out += [(rel, v) for rel, v in self._own.items() if rel not in seen]
        return out

    def keys(self):
        return [k for k, _ in self.items()]

    def values(self):
        return [v for _, v in self.items()]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.items())


def _index(corpus: str) -> dict:
    """The corpus index (_main_index), and, where the tree records the corpus's future branch for this very pin
    (future_pins) and the checkout has the commit, the branch's own commits up to it (_future_index). Readers pick
    each file's version by its in-force day, so a version from the branch is read from its day on, never before."""
    data = _main_index(corpus)
    fp = future_pins().get(corpus)
    if not fp or fp[2] != data['pin']:
        return data  # none recorded, or recorded for an earlier pin (stale): main alone, and future_note says so
    branch, fut, _ = fp
    key = ('index', f"{corpus}@{data['pin']}+{fut}")
    missing = ('future-missing', f"{corpus}@{data['pin']}+{fut}")
    if missing in _CACHE and _has_commit(corpus, corpus_dir(corpus), fut):
        _future_arrived(corpus, data['pin'], fut)  # fetched since (as future_note asks): read it from now on
    if key not in _CACHE:
        mine = f"{corpus}@{data['pin']}+"  # what this process kept for an earlier future pin of the same main pin
        for k in [k for k in _CACHE if len(k) == 2 and isinstance(k[1], str) and k[1].startswith(mine)
                  and not k[1].startswith(mine + fut)]:
            _CACHE.pop(k)
        cwd = corpus_dir(corpus)
        if _has_commit(corpus, cwd, fut):
            _CACHE[key] = _future_index(corpus, cwd, data, branch, fut)
        else:
            # Main alone for now. A long-running reader (the MCP server) asks again on each read, one line to the
            # batch reader (_has_commit keeps only a yes), and reads the branch once the commit is fetched.
            _CACHE[missing] = True
            _CACHE[key] = data
    return _CACHE[key]  # type: ignore[return-value]


def _future_arrived(corpus: str, pin: str, fut: str) -> None:
    """A recorded future commit the checkout lacked is there now: drop what this process built from main alone (the
    caches keyed <corpus>@<pin> without the +<future>, but not main's own index, which the merged reading is built
    on, and every timeline), so the next read builds the merged reading."""
    at = f'{corpus}@{pin}'
    for k in [k for k in _CACHE if len(k) == 2 and isinstance(k[1], str)
              and (k[0] == 'timeline' or (k[1].startswith(at) and not k[1].startswith(at + '+')
                                          and k != ('index', at)))]:
        _CACHE.pop(k)
    _CACHE.pop(('index', f'{at}+{fut}'), None)
    _CACHE.pop(('future-missing', f'{at}+{fut}'), None)


def recheck_missing_futures() -> bool:
    """For readers of every corpus at once (timeline), which do not go through _index on a cache hit, and for the
    MCP server's own caches: whether any recorded future commit the checkout lacked when it was last read is there
    now (its main-only caches are then dropped). One line to each such corpus's batch reader."""
    arrived = False
    for k in [k for k in _CACHE if k[0] == 'future-missing']:
        at, fut = str(k[1]).rsplit('+', 1)
        corpus, pin = at.rsplit('@', 1)
        if _has_commit(corpus, corpus_dir(corpus), fut):
            _future_arrived(corpus, pin, fut)
            arrived = True
    return arrived


def _future_index(corpus: str, cwd: Path, data: dict, branch: str, fut: str) -> dict:
    """The main index with the commits pin..fut added, kept in memory only: the index on disk stays main's, keyed by
    the main pin, so moving either pin never leaves a branch's versions in it. A branch that forked from main before
    the pin (gitlaw_common's append_future.py forks at main's last law commit) has copies of main's later commits;
    those are left out (_replays). A branch with a commit that only looks like a copy (diverged) is not read at all:
    main alone, and future_note says why. Its cache keys start <corpus>@<pin>, so _forget_other_pins drops them with
    the pin, and nothing is written to disk for _prune_indexes to keep or remove."""
    pin = data['pin']
    check = _future_check(corpus, cwd, pin, fut)
    if check['diverged']:
        return data
    linear, skip = check['linear'], check['skip']
    over = dict(data)
    over['rows'] = list(data['rows'])
    over['files'] = _FilesOver(data['files'])
    for k in ('unknown', 'moves', 'withdrawn', 'restates', 'pos', 'retroactive', 'redated'):
        if k in data:
            over[k] = type(data[k])(data[k])
    before = len(over['rows'])
    _extend(corpus, cwd, over, f'{pin}..{fut}', skip=skip)
    over['at'] = f'{pin}+{fut}'
    over['future'] = {'branch': branch, 'sha': fut, 'linear': linear, 'commits': len(over['rows']) - before,
                      'replays_skipped': len(skip)}
    return over


INDEX_SHARDS = 64


def _shard(path: str) -> int:
    import zlib
    return zlib.crc32(path.encode('utf-8')) % INDEX_SHARDS


def _save_index(target: Path, data: dict) -> None:
    """The index as one file: its commits and tables in one piece, then every file's versions split in INDEX_SHARDS
    pieces by path, so that a read of one provision loads one piece (a 64th) and not every file of the corpus."""
    import pickle
    shards: list[tuple[dict, list]] = [({}, []) for _ in range(INDEX_SHARDS)]
    for n, (rel, versions) in enumerate(data['files'].items()):
        piece = shards[_shard(rel)]
        piece[0][rel] = versions
        piece[1].append(n)  # its place among all files, so that going through them all keeps the order
    blobs = [pickle.dumps(sh, protocol=pickle.HIGHEST_PROTOCOL) for sh in shards]
    head = {k: v for k, v in data.items() if k != 'files'}
    head['shards'] = [len(b) for b in blobs]
    head_blob = pickle.dumps(head, protocol=pickle.HIGHEST_PROTOCOL)
    with open(target, 'wb') as f:
        f.write(b'GLX2' + len(head_blob).to_bytes(8, 'little'))
        f.write(head_blob)
        for b in blobs:
            f.write(b)


def _load_index(path: Path) -> dict:
    import pickle
    with open(path, 'rb') as f:
        if f.read(4) != b'GLX2':
            raise ValueError('not an index')
        size = int.from_bytes(f.read(8), 'little')
        head = _unpickle(f.read(size))
    sizes = head.pop('shards')
    offsets, at = [], 12 + size
    for n in sizes:
        offsets.append((at, n))
        at += n
    head['files'] = _Files(path, offsets)
    return head


def _unpickle(raw: bytes):
    """pickle.loads with the garbage collector paused: loading builds millions of objects, which it would only walk
    (a fifth of the load)."""
    import gc
    import pickle
    gc.disable()
    try:
        return pickle.loads(raw)
    finally:
        gc.enable()


_OPEN_INDEXES: list = []


class _Files:
    """An index's files (path -> versions), read from disk a piece at a time: looking up one path loads the piece
    holding it; going through every path loads them all. Read-only."""

    def __init__(self, path: Path, offsets: list[tuple[int, int]]):
        self._path, self._offsets = path, offsets
        # Held open from load: another process may replace the file (a new pin, another law.py version), and the
        # pieces must come from the file this index was loaded from. On Windows the replace then fails and is skipped.
        self._f = open(path, 'rb')
        _OPEN_INDEXES.append(self._f)
        self._shards: dict[int, tuple[dict, list]] = {}
        self._ordered: list | None = None

    def close(self) -> None:
        if self._f in _OPEN_INDEXES:
            _OPEN_INDEXES.remove(self._f)
        self._f.close()

    def _piece(self, i: int) -> dict:
        if i not in self._shards:
            at, n = self._offsets[i]
            self._f.seek(at)
            raw = self._f.read(n)
            if len(raw) != n:
                raise OSError(f'{self._path}: index cut short')
            self._shards[i] = _unpickle(raw)
        return self._shards[i][0]

    def _all(self) -> list[tuple[str, list]]:
        """Every (path, versions), in the order they were indexed."""
        if self._ordered is None:
            if len(self._shards) < len(self._offsets):
                for i, (at, n) in enumerate(self._offsets):
                    if i not in self._shards:
                        self._f.seek(at)
                        self._shards[i] = _unpickle(self._f.read(n))
            placed: list = [None] * sum(len(self._shards[i][1]) for i in self._shards)
            for files, places in self._shards.values():
                for kv, at in zip(files.items(), places):
                    placed[at] = kv
            self._ordered = placed
        return self._ordered

    def get(self, rel, default=None):
        return self._piece(_shard(rel)).get(rel, default) if isinstance(rel, str) else default

    def __getitem__(self, rel):
        return self._piece(_shard(rel))[rel]

    def __contains__(self, rel) -> bool:
        return isinstance(rel, str) and rel in self._piece(_shard(rel))

    def items(self):
        return list(self._all())

    def keys(self):
        return [k for k, _ in self._all()]

    def values(self):
        return [v for _, v in self._all()]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._all())


_BATCH: dict = {}


def _batch_read(corpus: str, cwd: Path, spec: str) -> tuple[bytes | None, bytes | None]:
    """(type, content) of an object through the corpus's long-lived `git cat-file --batch`; (None, None) if missing."""
    _trees_alive()
    import os
    # The reader sees built trees only if it was started with the tree store as an alternate: one started before the
    # store existed (or under another store) is restarted with it.
    alt = str(_TREES['dir'] / 'objects') if _TREES['dir'] is not None else None
    p, started = _BATCH.get(corpus, (None, None))
    if p is not None and (p.poll() is not None or started != alt):
        _stop_reader(p)
        p = None
    if p is None:
        env = dict(os.environ)
        if alt is not None:
            env['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = alt
        p = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=cwd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
        _BATCH[corpus] = (p, alt)
        import atexit
        atexit.register(_stop_reader, p)
    p.stdin.write(spec.encode('utf-8') + b'\n')
    p.stdin.flush()
    head = p.stdout.readline().split()
    if len(head) < 3 or head[-1] in (b'missing', b'ambiguous'):
        return None, None
    data = p.stdout.read(int(head[2]))
    p.stdout.read(1)
    return head[1], data


def _has_commit(corpus: str, cwd: Path, sha: str) -> bool:
    """Whether a checkout has a commit, asked once a process, and of the batch reader the command uses anyway rather
    than a git process each time."""
    key = ('has-commit', f'{corpus}@{sha}')
    if not _CACHE.get(key):
        if hasattr(subprocess, 'Popen'):
            _CACHE[key] = _batch_read(corpus, cwd, f'{sha}^{{commit}}')[0] == b'commit'
        else:
            _CACHE[key] = subprocess.run(['git', 'cat-file', '-e', f'{sha}^{{commit}}'], cwd=cwd,
                                         capture_output=True).returncode == 0
    return bool(_CACHE[key])


def read_object(corpus: str, spec: str) -> str | None:
    """A file's text by blob id or <commit>:<path>, or None. One long-lived `git cat-file --batch` per corpus, so
    reading many files costs no process each; where processes can only be run one at a time, one `git cat-file`."""
    cwd = corpus_dir(corpus)
    if not hasattr(subprocess, 'Popen'):
        done = subprocess.run(['git', 'cat-file', 'blob', spec], cwd=cwd, capture_output=True)
        data = done.stdout if done.returncode == 0 else None
    else:
        kind, data = _batch_read(corpus, cwd, spec)
        if kind != b'blob':
            return None
    if data is None:
        return None
    # As `git show` read in text mode gave it: line ends as \n.
    return data.decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')


def _stop_reader(p) -> None:
    try:
        p.stdin.close()
        p.wait(5)
    except Exception:  # slow to exit (a busy machine) or gone already: stopped, without a traceback at exit
        try:
            p.kill()
        except Exception:
            pass


def _restart_readers() -> None:
    """Stop the batch readers; each starts again on its next read, with the tree store as it is now."""
    for p, _ in _BATCH.values():
        _stop_reader(p)
    _BATCH.clear()


def close_readers() -> None:
    """Stop the `git cat-file --batch` readers (they hold each corpus folder open while they run)."""
    _restart_readers()
    for f in _OPEN_INDEXES:  # and the index files they hold open
        f.close()
    _OPEN_INDEXES.clear()
    for k in [k for k in _CACHE if k[0] == 'index']:
        _CACHE.pop(k)


def read_version(path: str, commit: str) -> str | None:
    """The text a version of a file gives (None for a version that deletes it)."""
    if not commit:
        return None
    corpus, rel = corpus_of(path)
    row = next((h for h in reversed(history(path)) if h['commit'] == commit and 'blob' in h), None)
    if row is not None:
        return read_object(corpus, row['blob']) if row['blob'] else None
    return read_object(corpus, f'{commit}:{rel}')


def versions_in_force(date: str, path: str) -> list[tuple[str, str]]:
    """(commit, credit) for each version of a file that was in force at some time up to `date`, in the order they
    took force: the commit file_commit chooses on every day a version starts or a correction starts or ends.
    A day the file is not in force gives ('', '')."""
    import datetime as dt
    corpus, rel = corpus_of(path)
    hist = history(path)
    days = {h['in_force'] for h in hist if h['in_force'] <= date}
    mine = {h['commit'] for h in hist}
    for c in corrections(corpus):
        if not (rel in c['files'] or (not c['files'] and c['commit'] in mine)):
            continue
        if c['from'] <= date:
            days.add(c['from'])
        end = correction_end(corpus, c, rel)
        if end < date:
            days.add((dt.date.fromisoformat(end) + dt.timedelta(days=1)).isoformat())
    who = {h['commit']: credit(h['law'], h['kind']) for h in hist}
    who.update({c['commit']: credit(c['law'], 'correction') for c in corrections(corpus)})
    out: list[tuple[str, str]] = []
    for d in sorted(days):
        sha = file_commit(d, path) or ''
        for step in [*_same_day_steps(hist, d, sha), sha]:
            if not out or out[-1][0] != step:
                out.append((step, who.get(step, '') if step else ''))
    return out


def _same_day_steps(hist: list[dict], day: str, chosen: str) -> list[str]:
    """The versions of a file appended for `day` before the version file_commit chooses for it, when that version
    re-asserts an earlier one (Re-asserts: <commit>): a law in force the same day as another, whose version the
    first build left out, appended dated that day, then the day's last text restated (spain-law's same-day
    versions, global-law #12). The later commit wins the day, but the earlier law's words are its own, so blame and
    words step through them, in commit order. Only the versions appended after the restated commit count; left out
    are versions a later commit restates, deletions and correction overlays."""
    last = next((h for h in hist if h['commit'] == chosen and h['in_force'] == day and not h.get('corrects')), None)
    if last is None or not last.get('restates') or last.get('restated_because') != 'it had to be restated':
        return []
    restated = [h['restates'] for h in hist if h.get('restates')]
    after = next((h['order'] for h in hist if h['commit'].startswith(last['restates'])), None)
    if after is None:  # the restated commit never wrote this file: nothing here was left out of it
        return []
    return [h['commit'] for h in hist
            if h['in_force'] == day and after < h['order'] < last['order'] and h.get('blob') and not h.get('corrects')
            and not h.get('ends') and not any(h['commit'].startswith(r) or r.startswith(h['commit']) for r in restated)]


def _metadata_only(corpus: str) -> bool:
    """Whether a corpus says it holds a list of acts without their text (its README, at the pinned commit)."""
    key = ('metadata-only', corpus)
    if key not in _CACHE:
        text = read_object(corpus, f"{_index(corpus)['pin']}:README.md") or ''
        _CACHE[key] = bool(re.search(r'metadata only|no law text|catalogue only', text, re.I))
    return bool(_CACHE[key])


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
        by_corpus: dict[str, list[Event]] = {}
        for e in events:  # once, not once per corpus: the timeline holds every corpus's commits
            by_corpus.setdefault(e.corpus, []).append(e)
        for corpus in manifest()['corpora']:
            own = by_corpus.get(corpus['path'], [])
            last = [e for e in own if e.in_force <= args[0] and e.kind != 'documentation']
            state = (f'{last[-1].law}, in force {last[-1].in_force}' if last else 'not yet in the record') \
                if (ROOT / corpus['path'] / '.git').exists() else 'not checked out'
            if corpus['path'] in unreadable():
                state = 'checkout unfinished (no commit yet)'
            if corpus['path'] in behind():
                state = 'checkout behind the tree (git submodule update)'
            if corpus['path'] in shallow():
                state = 'shallow clone (git fetch --unshallow)'
            print(f"  {corpus['path']:<24} {state}")
        note(c for corpus in manifest()['corpora'] if corpus['path'] in by_corpus
             for c in caveats(args[0], corpus['path'], by_corpus[corpus['path']]) if 'runs to' in c)
        note(n for n in (future_note(corpus['path']) for corpus in manifest()['corpora']) if n)
        note(_UNREADABLE.format(corpus=c) for c in unreadable())
        note(_BEHIND.format(corpus=c, pin=p[:10]) for c, p in sorted(behind().items()))
        note(_SHALLOW.format(corpus=c) for c in shallow())
    elif command in ('show', 'blame', 'words'):
        corpus, _ = corpus_of(args[1])
        note(caveats(args[0], corpus) + file_notes(args[0], args[1]))
        text = text_on(args[0], args[1])
        if text is None:
            raise SystemExit(explain_missing(args[0], args[1]))
        if command == 'show':
            print(text, end='')
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
            if h.get('ends'):
                label = h['ends']
            if h.get('repeal_notice'):
                label = 'repealed'
            print(f"{label} {h['in_force']}  {h['law']}" + (f'  ({dates})' if dates else '')
                  + (f"  [repeal notice: {h['repeal_notice']}]" if h.get('repeal_notice') else '')
                  + (f"  [act {h['act']}, from data/acts.json]" if h.get('ends') else '')
                  + (f"  [not re-enacted by: {'; '.join(h['not_reenacting'])}]" if h.get('not_reenacting') else '')
                  + (f"  [date doubtful: {h['date_doubtful']}]" if h.get('date_doubtful') else ''))
    elif command == 'laws':
        if args[0] > args[1]:
            args[0], args[1] = args[1], args[0]
        name = args[2] if len(args) > 2 else ''
        # Only laws taking effect: starting texts (the text as a publisher gave it on the day it was read), corrections,
        # printings, court rulings, treaties and changes no law is named for are not laws taking effect that day.
        left_out: dict[str, int] = {}
        # Only the corpora the prefix takes in are read, not every corpus checked out.
        # A name takes in what countries.py and the MCP tools take in: a country, state, city, ISO code or old path.
        chosen = {c['path'] for c in manifest()['corpora'] if not name or matches(c, name)}
        if name and not chosen:
            import difflib
            folders = sorted({c['path'].split('/')[0] for c in manifest()['corpora']}
                             | {c['path'].split('/')[1] for c in manifest()['corpora'] if c['path'].count('/') >= 2}
                             - GENERIC_LEVELS)
            near = difflib.get_close_matches(name.strip().lower().replace(' ', '-'), folders, n=3)
            raise SystemExit(f'No body of law in this tree matches {name!r}.' + (f" Did you mean {', '.join(near)}?" if near
                             else '') + f' {countries_cmd()} lists them.')
        events = sorted((e for c in chosen for e in law_events(c)), key=lambda e: e.in_force) if name else timeline()
        for e in events:
            if args[0] <= e.in_force <= args[1] and e.corpus in chosen and e.kind != 'documentation':
                if e.kind == 'law':
                    print(f'{e.in_force}  {e.corpus:<24} {e.law}')
                else:
                    left_out[e.kind] = left_out.get(e.kind, 0) + 1
        for c in chosen:  # laws that only changed acts already ended: history() gives none of their versions
            rows = _index(c)['rows'] if corpus_events(c) else []
            for n in ended_rows(c) if rows else ():
                if args[0] <= rows[n][5] <= args[1] and rows[n][4] == 'law':
                    left_out['ended'] = left_out.get('ended', 0) + 1
        names = {'baseline': 'starting texts (text as published, no law named)', 'correction': 'corrections',
                 'ended': 'laws that changed only acts data/acts.json had already ended (none of their versions took '
                          'force)',
                 'printing': 'printings', 'court': 'court rulings', 'treaty': 'treaties',
                 'uncredited': 'changes no law is named for'}
        note(f'not listed, as they are not laws taking effect: {n} {names.get(k, k)}' for k, n in sorted(left_out.items()))
        note(n for n in (future_note(c) for c in sorted(chosen)) if n)
        note(_UNREADABLE.format(corpus=c) for c in unreadable() if c in chosen)
        note(_BEHIND.format(corpus=c, pin=p[:10]) for c, p in sorted(behind().items()) if c in chosen)
        note(_SHALLOW.format(corpus=c) for c in shallow() if c in chosen)
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
