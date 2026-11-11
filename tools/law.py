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
  python tools/law.py caselaw-index     after an update: index the case law checked out (read once per pin)

Run `git submodule update --init` once first. Dates are in-force dates read from each commit's In-force trailer,
so dates before 1970 work even though git cannot store them as commit dates.
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import subprocess as _subprocess  # the module itself: a reader (the MCP server) replaces `subprocess` with run() only
import sys
import threading
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
        head = _head_from_files() or git('rev-parse', 'HEAD').strip()
        if seen and seen[1] != head:  # type: ignore[index]
            _forget_other_heads(head, seen[1])  # type: ignore[index]
        _CACHE[('head-at', '')] = seen = (now, head)
    return seen[1]  # type: ignore[index]


# What is kept per HEAD of the tree: keyed by the commit alone, by "<commit>|...", or by "<corpus>@<commit>".
_HEAD_KEYS = frozenset(('root', 'manifest', 'tips', 'legacy', 'moved', 'countries', 'country-names', 'future-pins'))
_HEAD_LED_KEYS = frozenset(('timeline', 'cl-vouched', 'caselaw-index-quick'))


def _forget_other_heads(head: str, before: str) -> None:
    """HEAD moved: drop what this process keeps for earlier commits of the tree (a long-running reader sees pins move
    several times an hour, and each kept a manifest, the pins and a timeline of every corpus for good). The commit
    HEAD moved from is kept one move longer: a call that has just stored something under it reads it back."""
    for k in list(_CACHE):
        if len(k) != 2 or not isinstance(k[1], str):
            continue
        kind, at = k
        if kind in _HEAD_KEYS:
            gone = at not in (head, before)
        elif kind in _HEAD_LED_KEYS:
            gone = not at.startswith((head + '|', before + '|'))
        elif kind == 'corpus-timeline':
            gone = not at.endswith(('@' + head, '@' + before))
        else:
            continue
        if gone:
            _CACHE.pop(k, None)


def _gitdirs(top: Path) -> tuple[Path, Path] | None:
    """A checkout's git folder and the folder it shares objects and refs with (the same unless it is a worktree),
    read from .git: a folder, or a file naming one (submodules and worktrees). None when there is neither. Kept for
    the process once found (where a checkout keeps its git folder does not move under a running reader): asked of
    every case-law corpus on every call, Path.resolve's file system calls cost 0.8 ms a corpus on Windows."""
    import os
    key = ('gitdirs', str(top))
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    try:
        dot = top / '.git'
        gitdir = dot if dot.is_dir() else Path(os.path.normpath(top / dot.read_text().split('gitdir:', 1)[1].strip()))
        common = Path(os.path.normpath(gitdir / (gitdir / 'commondir').read_text().strip())) if (gitdir / 'commondir').exists() else gitdir
    except (OSError, IndexError):
        return None
    _CACHE[key] = (gitdir, common)
    return gitdir, common


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


# Every corpus in the tree, whatever a reader serves: the MCP server replaces manifest() with the corpora it serves, and
# names (_countries, _country_names) mean the same however few that is ("georgia" is the country, served or not).
_whole_manifest = manifest


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
    if repo.get('history'):  # declared (corpus standard), as tools/describe.py takes it: never guessed over
        out['history'] = repo['history']
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


class _Events(list):
    """A list of events that is kept and never changed once made (a corpus's events at one reading of its index, a
    timeline): what is worked out from it is kept on it (`memo`), so it lasts exactly as long as the list does and a
    new pin or index starts afresh. Entries are set whole and never changed, so threads may share them."""
    __slots__ = ('memo',)

    def __init__(self, items=()):
        super().__init__(items)
        self.memo: dict = {}


def _kept(events, name, make):
    """make() for a list of events, worked out once when the list is a kept one (_Events)."""
    memo = getattr(events, 'memo', None)
    if memo is None:
        return make()
    got = memo.get(name)
    if got is None:
        got = memo[name] = make()
    return got


def by_corpus(events: list[Event]) -> dict[str, list[Event]]:
    """corpus -> its events in `events`, in their order there, documentation left out: grouped once for a kept list
    (a timeline of every corpus), so a reader of one corpus does not go through the events of all of them."""
    def group():
        out: dict[str, list[Event]] = {}
        for e in events:
            if e.kind != 'documentation':
                got = out.get(e.corpus)
                if got is None:
                    got = out[e.corpus] = _Events()
                got.append(e)
        return out
    return _kept(events, 'by-corpus', group)


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


def timeline(caselaw: bool = False) -> list[Event]:
    """Every dated commit of every corpus checked out, oldest in-force date first. Bodies of case law (is_caselaw) are
    left out unless `caselaw` is true: a commit per decision (about a million in Switzerland alone) would make every
    answer about law read them; a read of one case-law corpus takes its own events (corpus_timeline, corpus_events). Each corpus is read from its own
    history at the commit the tree pins at HEAD (corpus_events).

    Until 2 November 2026 the tree recorded one root commit per law taking effect, and this read those. Since then the
    tree only moves each corpus's pin forward (it grows by fast-forward alone, and corpus repositories may be rebuilt),
    so its root history ends there and an old root commit can pin a corpus commit that no longer exists. Those root
    commits now only date a corpus commit that carries no date of its own (legacy_dates). A law that only changed
    acts already ended (ended_rows) is left out, as history() leaves its versions out."""
    corpora = tuple(c['path'] for c in manifest()['corpora'] if caselaw or not is_caselaw(c))
    key = ('timeline', _head() + '|' + ','.join(corpora))
    recheck_missing_futures()
    events = _CACHE.get(key)  # read once: another thread may drop it (a future commit arrived, HEAD moved)
    if events is None:
        events = [e for c in corpora for e in law_events(c)]
        events.sort(key=lambda e: e.in_force)  # stable: each corpus keeps its own order within a day
        _CACHE[key] = events
    return list(events)  # type: ignore[arg-type]


def corpus_timeline(corpus: str) -> list[Event]:
    """One corpus's dated commits in in-force order: timeline() restricted to it, read without every other corpus
    (and so the way to read a body of case law, which timeline() leaves out)."""
    key = ('corpus-timeline', f'{corpus}@{_head()}')
    events = _CACHE.get(key)
    if events is None:
        events = _CACHE[key] = sorted(law_events(corpus), key=lambda e: e.in_force)
    return list(events)  # type: ignore[arg-type]


def latest_decision(corpus: str, date: str) -> tuple[str, str, str] | None:
    """(name, day, commit) of the last decision given on or before `date` in a body of case law, or None. Its decisions are
    committed in the order given, each dated noon of its day (Europe/Zurich), so one `git log -n --before` finds it
    without reading the corpus's history; days before 1970, which git dates 1970-01-01, are read from its index."""
    cwd = ROOT / corpus
    if not (cwd / '.git').exists() or not _readable(corpus, cwd):
        return None
    days = _decision_days(corpus, cwd)
    if days is not None:  # not committed in the order given: the latest day on or before the date, from every decision's
        import bisect
        i = bisect.bisect_right(days, (date, '￿'))
        return (days[i - 1][1], days[i - 1][0], days[i - 1][2]) if i else None
    if date < '1970-01-02':
        last = [e for e in corpus_events(corpus) if e.in_force <= date and e.kind not in ('documentation', 'end', 'correction')]
        return max(((e.law, e.in_force, e.corpus_commit) for e in last), key=lambda f: f[1], default=None)
    # git reads no date after 2099 ("--before=9999-12-31" read as 2012-12-28 gave every case-law corpus that last
    # decision in list_jurisdictions): a later date needs no --before, and no commit is made after it.
    cutoff = f'{date}T23:59:59+01:00'
    later = date < '2100'
    found = _late_decisions(corpus, cwd, cutoff, date) if later else []
    out = git('log', '-n', '8', *([f'--before={cutoff}'] if later else []), *NOT_CORRECTION,
              '--format=%an%x1f%(trailers:key=In-force,valueonly,separator=%x2C)%x1f%H',
              reachable_tip(corpus), cwd=cwd, check=False)
    for line in out.splitlines():
        name, day, sha = (line.split('\x1f') + ['', ''])[:3]
        if name != MAINTAINER and ISO_DAY.match(day.strip()) and day.strip()[:10] <= date:
            found.append((name, day.strip()[:10], sha.strip()))
            break
    return max(found, key=lambda f: f[1]) if found else None  # on a tie, the one committed later


# A correction is appended after the decisions, dated its decision's day: it is not a decision given, and the 5514
# Bundesarbeitsgericht corrections on top of that corpus would name whichever was fixed last (or be walked on every call).
NOT_CORRECTION = ('--invert-grep', '--grep=^Kind: correction$')


def _decision_days(corpus: str, cwd: Path) -> list[tuple[str, str, str]] | None:
    """None when a body of case law is committed in the order its decisions were given (each decision's In-force day
    on or after the one before it), as latest_decision's `git log -n` assumes. Otherwise every day a decision was given,
    sorted, as (day, name, commit) of the last decision committed for that day: a backfill (US decisions of 2014-2019
    from CourtListener appended after CAP's of 2019) puts older decisions after newer, and the last commit would be
    named the latest decision. Read from the decisions' trailers once per pin and kept in global-law-cache; a pin that
    moved forward reads only the commits added since."""
    pin = reachable_tip(corpus)
    key = ('decision-days', f'{corpus}@{pin}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    import os
    store, name = _store(), corpus.replace('/', '~')
    path = store / f'decision-days-{name}-{pin[:12]}.json'
    data = None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('pin') != pin:
            data = None
    except (OSError, ValueError):
        data = None
    if data is None:
        base = None
        for old in sorted(store.glob(f'decision-days-{name}-*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:3]:
            try:
                prev = json.loads(old.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                continue
            if prev.get('pin') and subprocess.run(['git', 'merge-base', '--is-ancestor', prev['pin'], pin], cwd=cwd,
                                                  capture_output=True).returncode == 0:
                base = prev
                break
        span = f"{base['pin']}..{pin}" if base else pin
        out = git('log', '--reverse', *NOT_CORRECTION, '--format=%H%x1f%an%x1f%(trailers:key=In-force,valueonly,separator=%x2C)',
                  span, cwd=cwd, check=False)
        last, ordered = (base['last'], base['in_order']) if base else ('', True)
        days = {d: (n, s) for d, n, s in base['days']} if base and base.get('days') is not None else None
        new = []
        for line in out.splitlines():
            sha, author, day = (line.split('\x1f') + ['', ''])[:3]
            day = day.strip()[:10]
            if author == MAINTAINER or not ISO_DAY.fullmatch(day):
                continue
            new.append((day, author, sha))
            if day < last:
                ordered = False
            last = max(last, day)
        if not ordered and days is None:  # out of order from now on: every decision's day, read once from the start
            days = {}
            for line in git('log', '--reverse', *NOT_CORRECTION, '--format=%H%x1f%an%x1f%(trailers:key=In-force,valueonly,separator=%x2C)',
                            pin, cwd=cwd, check=False).splitlines():
                sha, author, day = (line.split('\x1f') + ['', ''])[:3]
                day = day.strip()[:10]
                if author != MAINTAINER and ISO_DAY.fullmatch(day):
                    days[day] = (author, sha)
        elif days is not None:
            for day, author, sha in new:
                days[day] = (author, sha)
        data = {'pin': pin, 'in_order': ordered, 'last': last,
                'days': None if ordered else sorted([d, n, s] for d, (n, s) in days.items())}
        try:
            store.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            os.replace(tmp, path)
        except OSError:
            pass
    result = None if data['in_order'] else [tuple(r) for r in data['days']]
    _CACHE[key] = result
    return result


def _late_decisions(corpus: str, cwd: Path, cutoff: str, date: str) -> list[tuple[str, str, str]]:
    """The latest decision given on or before `date` but committed after it. A nightly run appends each new decision
    dated the day decided (author date) and committed the day it ran (committer date), and `git log --before` reads the
    committer date: the Dutch decisions of 2026-04-24 to 11-05, appended on 11-06, were missing from world on any day
    before 11-06. Only commits made after the cutoff are read, newest first, down to the first decision committed on
    its own day (author and committer dates equal: the build, which `--before` reads), where the walk stops."""
    fmt = '--format=%ct%x1f%at%x1f%an%x1f%(trailers:key=In-force,valueonly,separator=%x2C)%x1f%H'
    found: list[tuple[str, str, str]] = []
    skip, n = 0, 500  # in growing pages, as git is run to completion (the MCP server's time limits): no stream to cut
    while True:
        lines = git('log', f'--since={cutoff}', f'--skip={skip}', '-n', str(n), *NOT_CORRECTION, fmt, reachable_tip(corpus), cwd=cwd,
                    check=False).splitlines()
        for line in lines:
            ct, at, name, day, sha = (line.split('\x1f') + [''] * 4)[:5]
            if name == MAINTAINER:
                continue
            if ct == at:
                return found
            day = day.strip()[:10]
            if ISO_DAY.match(day) and day <= date and (not found or day > found[0][1]):
                found = [(name, day, sha.strip())]
        if len(lines) < n:
            return found
        skip, n = skip + n, n * 2


# --- the case-law index: what the tools read of every case-law corpus, kept once per set of pins --------------------
#
# Reading each case-law corpus on every call (a git log for its latest decision, a cat-file for its judgment overlay,
# a file list for its count, a docket file per corpus) made the cost of a call grow with the number of corpora: about
# 70 more US courts would have put six features of the speed gate over 2 s (US case-law sizing, 2026-11-07). Instead,
# each corpus is read once per pin into small files in global-law-cache (cl-v1-<corpus>-<pin>.*), a pin that moved
# forward reading only its new commits, and the corpora served are joined into one index per set of pins
# (cl-set-v1-<hash>.*). A call then reads one summary, one sorted file of decision days, one sorted file of judgment
# overlays and one Bloom filter of docket keys, whatever the number of corpora. `law.py caselaw-index` builds it after
# an update (the MCP server also builds it in the background when it starts); until it is built, calls read each
# corpus as before.

CASELAW_INDEX_V = 2  # 2: overlay files with their line counts, and summaries of the long ones
SUM_ROWS = 2000  # overlay rows in one file above which the index keeps its summary (rows by day, the latest SUM_TAIL rows)
SUM_TAIL = 300
_DECIDED_ROW = re.compile(rb'"decided":\s*"(\d{4}-\d{2}-\d{2})"')
_CL_NOT_FILE = re.compile(r'(^|/)(README|LICENSE|REPRODUCE|KORREKTUREN|CHANGELOG|RESEARCH)[^/]*$|(^|/)(tools|tests|data|build|\.github)/'
                          r'|^[A-Z][A-Z0-9_-]*\.md$')  # as the MCP server's NOT_LAW and ROOT_DOC: a corpus's own docs
_CL_JUDGMENTS = re.compile(r'^judgments/(.+?)(?:\.(?:19[5-9]\d|20[0-4]\d|2050))?\.jsonl$')  # split by year as INDEX_YEARS
_CL_INDEX_FILE = re.compile(r'^decision-index(?:-(?:19[5-9]\d|20[0-4]\d|2050))?\.tsv$')
_CL_LOG = '--format=%H%x1f%an%x1f%(trailers:key=In-force,valueonly,separator=%x2C)'
BLOOM_BITS_PER_KEY, BLOOM_HASHES = 10, 7  # about 1% false positives: one corpus in a hundred is read for nothing


def decision_key(text: str) -> str:
    """A docket or BGE reference as a key: letters and digits only, upper case, without BGE/ATF/DTF ("4A_123/2024" and
    the file 4A_123-2024.md, "ATF 142 II 307" and the file 142-II-307.md give the same key)."""
    text = re.sub(r'^(?:BGE|ATF|DTF)(?=[\s_-]|\d)', '', text.strip(), flags=re.I)
    return re.sub(r'[^0-9A-Za-z]', '', text).upper()


def _cl_name(corpus: str) -> str:
    return corpus.replace('/', '~')


def _write_atomic(path: Path, data: bytes) -> None:
    import os
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f'{path.name}.{os.getpid()}.part')
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _git_bytes(args: list[str], cwd: Path, data: bytes | None = None) -> bytes:
    done = subprocess.run(['git', *args], cwd=cwd, input=data, capture_output=True)
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args[:4])}: {done.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return done.stdout


def _cat_batch(cwd: Path, specs: list[str], env: dict | None = None) -> list[tuple[bytes, bytes | None]]:
    """(type, content) for each spec (<blob or commit>, or <commit>:<path>), by one `git cat-file --batch`; (b'missing',
    None) for one not there. A partial clone is never asked to fetch what is missing (GIT_NO_LAZY_FETCH)."""
    import os
    if not specs:
        return []
    run_env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1', **(env or {})}
    done = subprocess.run(['git', 'cat-file', '--batch'], cwd=cwd, input=('\n'.join(specs) + '\n').encode('utf-8'),
                          capture_output=True, env=run_env)
    out, data, i = [], done.stdout or b'', 0
    while i < len(data) and len(out) < len(specs):
        nl = data.find(b'\n', i)
        if nl < 0:
            break
        head = data[i:nl].split()
        i = nl + 1
        if len(head) == 3 and head[2].isdigit():
            size = int(head[2])
            out.append((head[1], data[i:i + size]))
            i += size + 1
        else:
            out.append((b'missing', None))
    return out + [(b'missing', None)] * (len(specs) - len(out))


def _bloom_positions(key: bytes, m: int, k: int) -> list[int]:
    import hashlib
    h = hashlib.blake2b(key, digest_size=16).digest()
    a, b = int.from_bytes(h[:8], 'little'), int.from_bytes(h[8:], 'little') | 1
    return [(a + i * b) % m for i in range(k)]


def _bloom_build(keys, n: int, base: bytes | None = None) -> bytes:
    """A Bloom filter of docket keys: b'GLB1', the bit count (8 bytes), the hash count (1 byte), the bits. `base`, a
    filter of an earlier pin, is copied and added to while it has room (keys only grow: the repos are append-only)."""
    if base is not None:
        m, k = int.from_bytes(base[4:12], 'little'), base[12]
        bits = bytearray(base[13:])
    else:
        m = max(1024, (BLOOM_BITS_PER_KEY * max(n, 1) + 7) // 8 * 8)
        k = BLOOM_HASHES
        bits = bytearray(m // 8)
    for key in keys:
        for p in _bloom_positions(key, m, k):
            bits[p >> 3] |= 1 << (p & 7)
    return b'GLB1' + m.to_bytes(8, 'little') + bytes([k]) + bytes(bits)


def _decision_lines_full(corpus: str, pin: str, cwd: Path, tree: list[tuple[str, str]]) -> list[bytes]:
    """Every '<key>\\t<corpus>/<file>\\n' of a corpus at a pin, as the docket lookups read it: a decision's file is named
    from its docket (decisions/<court>/<year>/<docket>.md, --<hash> after it where two share a name), and a corpus whose
    files are named by another id lists its other references in decision-index.tsv (or one file a year)."""
    lines = set()
    index_blobs = []
    same = _same_decision(cwd, next((b for p, b in tree if p == 'decision-relations.tsv'), None))
    for path, blob in tree:
        if path.startswith('decisions/') and path.endswith('.md'):
            name = path.rsplit('/', 1)[-1]
            lines.add(f'{decision_key(name[:-3].split("--", 1)[0])}\t{corpus}/{same.get(path, path)}\n'.encode('utf-8'))
        elif _CL_INDEX_FILE.match(path):
            index_blobs.append(blob)
    for _, text in _cat_batch(cwd, index_blobs):
        lines.update(_index_tsv_lines(corpus, (text or b'').decode('utf-8', 'replace').splitlines(), same))
    return sorted(lines)


def _same_decision(cwd: Path, blob: str | None) -> dict[str, str]:
    """A case-law corpus's decision-relations.tsv (path, relation, target, note): each file that is the same decision as
    another ('same-decision-as') -> the file kept. The docket file names the kept file for both, so a citation of either
    finds one decision; a file moved to another corpus ('moved-to') is gone from the tree with its index rows."""
    if not blob:
        return {}
    data = (_cat_batch(cwd, [blob])[0][1] or b'').decode('utf-8', 'replace')
    out = {}
    for line in data.splitlines()[1:]:
        a = line.split('\t')
        if len(a) >= 3 and a[1].strip() == 'same-decision-as' and a[0] and a[2].strip():
            out[a[0]] = a[2].strip()
    return out


def _index_tsv_lines(corpus: str, rows, same: dict[str, str] | None = None) -> set[bytes]:
    out = set()
    for line in rows:
        ref, _, path = line.partition('\t')
        if ref and path.strip() and not ref.startswith('#') and ref.strip().lower() != 'reference':  # the header line
            path = (same or {}).get(path.strip(), path.strip())
            out.add(f'{decision_key(ref)}\t{corpus}/{path}\n'.encode('utf-8'))
    return out


def _sorted_merge(old: Path, new: list[bytes]) -> bytes:
    import heapq
    with open(old, 'rb') as fh:
        merged = heapq.merge(fh, sorted(new))
        out, last = [], None
        for line in merged:
            if line != last:
                out.append(line)
                last = line
    return b''.join(out)


def _cl_files(corpus: str, pin: str) -> dict[str, Path]:
    store, stem = _store(), f'cl-v{CASELAW_INDEX_V}-{_cl_name(corpus)}-{pin[:12]}'
    return {'json': store / f'{stem}.json', 'days': store / f'{stem}.days.tsv', 'overlay': store / f'{stem}.overlay.tsv',
            'sums': store / f'{stem}.sums.tsv', 'decisions': store / f'decisions-{pin}.tsv', 'bloom': store / f'decisions-{pin}.bloom'}


def _overlay_stats(cwd: Path, blobs: list[str]) -> tuple[dict[str, int], dict[str, str]]:
    """(lines of each overlay blob, and for a long one, its summary as JSON: rows, rows by day decided, and its latest
    SUM_TAIL rows as written), read SUM_BATCH blobs to a git process. An article cited in hundreds of thousands of
    decisions (art. 1.022 of the Brazilian CPC: 614,000 rows) is then counted and its latest decisions read from the
    summary, not from its files on each call."""
    import heapq
    lines: dict[str, int] = {}
    sums: dict[str, str] = {}
    todo = sorted(set(blobs))
    for i in range(0, len(todo), 200):
        part = todo[i:i + 200]
        for blob, (kind, data) in zip(part, _cat_batch(cwd, part)):
            if data is None:
                continue
            n = data.count(b'\n') + (0 if data.endswith(b'\n') or not data else 1)
            lines[blob] = n
            if n < SUM_ROWS:
                continue
            hist: dict[str, int] = {}
            tail: list = []
            rows = 0
            for line in data.splitlines():
                m = _DECIDED_ROW.search(line)
                if not m:
                    continue
                d = m.group(1).decode('ascii')
                rows += 1
                hist[d] = hist.get(d, 0) + 1
                if len(tail) < SUM_TAIL:
                    heapq.heappush(tail, (d, line))
                elif (d, line) > tail[0]:  # the latest by day, ties by the row itself (as judgments_counted picks)
                    heapq.heapreplace(tail, (d, line))
            sums[blob] = json.dumps({'rows': rows, 'hist': sorted(hist.items()),
                                     'tail': [l.decode('utf-8', 'replace') for _, l in sorted(tail)]}, ensure_ascii=False)
    return lines, sums


def _write_overlay(f: dict[str, Path], rows: list[tuple[str, str, str]], lines: dict[str, int], sums: dict[str, str]) -> None:
    """The corpus's overlay files, '<law key>\\t<blob>\\t<path>\\t<lines>' sorted, and the summaries of the long ones,
    '<blob>\\t<summary>' sorted by blob."""
    _write_atomic(f['overlay'], ''.join(sorted(f'{k}\t{b}\t{p}\t{lines.get(b, 0)}\n' for k, b, p in rows)).encode('utf-8'))
    used = {b for _, b, _ in rows}
    _write_atomic(f['sums'], ''.join(f'{b}\t{sums[b]}\n' for b in sorted(sums) if b in used).encode('utf-8'))


def _cl_base(corpus: str, pin: str, cwd: Path) -> dict | None:
    """The record of an earlier pin of this corpus that `pin` descends from, to read only the commits added since."""
    for old in sorted(_store().glob(f'cl-v{CASELAW_INDEX_V}-{_cl_name(corpus)}-*.json'), key=lambda p: p.stat().st_mtime,
                      reverse=True)[:4]:
        try:
            rec = json.loads(old.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        f = _cl_files(corpus, rec.get('pin', ''))
        if (rec.get('pin') and rec['pin'] != pin and all(f[k].exists() for k in ('days', 'overlay', 'sums', 'decisions'))
                and subprocess.run(['git', 'merge-base', '--is-ancestor', rec['pin'], pin], cwd=cwd,
                                   capture_output=True).returncode == 0):
            return rec
    return None


def _days_rows(cwd: Path, span: str) -> list[tuple[str, str, str]]:
    """(day, commit, name) of each decision committed in a span, oldest first: corrections and the maintainer's
    documentation commits left out, as latest_decision leaves them out."""
    out = []
    raw = _git_bytes(['log', '--reverse', *NOT_CORRECTION, _CL_LOG, span], cwd).decode('utf-8', 'replace')
    for line in raw.splitlines():
        sha, author, day = (line.split('\x1f') + ['', ''])[:3]
        day = day.strip()[:10]
        if author != MAINTAINER and ISO_DAY.fullmatch(day):
            out.append((day, sha.strip(), author.replace('\t', ' ')))
    return out


def _cl_redates(cwd: Path, span: str) -> dict[str, str]:
    """The maintainer's `Redates: <commit> <YYYY-MM-DD>` trailers in a span of a case-law corpus (a decision its source
    misdated: CAP's few wrong New York and Kentucky days): commit -> its day."""
    raw = _git_bytes(['log', f'--author={MAINTAINER}', '--grep=^Redates:', '--format=%B%x1e', span], cwd).decode('utf-8', 'replace')
    return {m.group(1): m.group(3) for m in REDATES.finditer(raw) if ISO_DAY.fullmatch(m.group(3))}


def _apply_redates(days: dict[str, tuple[str, str]], redates: dict[str, str]) -> None:
    """Each redated decision moved to its day in the days file (day -> the last decision committed that day)."""
    if not redates:
        return
    for d, (sha, n) in list(days.items()):
        new = next((day for c, day in redates.items() if sha.startswith(c)), None)
        if new and new != d:
            del days[d]
            days.setdefault(new, (sha, n))


def caselaw_record(corpus: str, pin: str, cwd: Path) -> dict:
    """One case-law corpus at one pin, read once and kept: its decision files (count and an example), its decisions by
    day (the last committed for each day, as latest_decision names it), its judgment overlay files (judgments/<law
    path>[.<year>].jsonl and their blobs), and its docket file with a Bloom filter of its keys. From the record of an
    earlier pin when there is one (git diff and git log of the commits since), else from one ls-tree and one git log."""
    f = _cl_files(corpus, pin)
    try:
        rec = json.loads(f['json'].read_text(encoding='utf-8'))
        if rec.get('pin') == pin and all(f[k].exists() for k in ('days', 'overlay', 'sums', 'decisions', 'bloom')):
            return rec
    except (OSError, ValueError):
        pass
    base = _cl_base(corpus, pin, cwd)
    if base is not None:
        rec = _cl_update(corpus, pin, cwd, base, f)
    else:
        rec = _cl_build(corpus, pin, cwd, f)
    _write_atomic(f['json'], json.dumps(rec, ensure_ascii=False).encode('utf-8'))
    # Keep the last few pins of each corpus (the base of the next update is among them); an older pin's files go.
    for old in sorted(_store().glob(f'cl-v{CASELAW_INDEX_V}-{_cl_name(corpus)}-*.json'), key=lambda p: p.stat().st_mtime)[:-3]:
        try:
            gone = json.loads(old.read_text(encoding='utf-8')).get('pin', '')
        except (OSError, ValueError):
            gone = ''
        if gone and gone != pin:
            for p in _cl_files(corpus, gone).values():
                p.unlink(missing_ok=True)
        old.unlink(missing_ok=True)
    return rec


def _write_days(path: Path, days: dict[str, tuple[str, str]]) -> None:
    _write_atomic(path, ''.join(f'{d}\t{s}\t{n}\n' for d, (s, n) in sorted(days.items())).encode('utf-8'))


def _cl_build(corpus: str, pin: str, cwd: Path, f: dict[str, Path]) -> dict:
    raw = _git_bytes(['-c', 'core.quotePath=false', 'ls-tree', '-r', pin], cwd).decode('utf-8', 'replace')
    tree, files, example, overlay = [], 0, '', []
    for line in raw.splitlines():
        meta, _, path = line.partition('\t')
        parts = meta.split()
        if len(parts) != 3 or parts[1] != 'blob':
            continue
        tree.append((path, parts[2]))
        m = _CL_JUDGMENTS.match(path)
        if m:
            overlay.append((m.group(1), parts[2], path))
        elif path.endswith('.md') and not _CL_NOT_FILE.search(path):
            files += 1
            if not example or (path.startswith('decisions/') and not example.startswith('decisions/')):
                example = path
    days: dict[str, tuple[str, str]] = {}
    for d, s, n in _days_rows(cwd, pin):
        days[d] = (s, n)
    _apply_redates(days, _cl_redates(cwd, pin))
    _write_days(f['days'], days)
    _write_overlay(f, overlay, *_overlay_stats(cwd, [b for _, b, _ in overlay]))
    if not f['decisions'].exists():
        lines = _decision_lines_full(corpus, pin, cwd, tree)
        _write_atomic(f['decisions'], b''.join(lines))
    _write_bloom(f)
    return {'v': CASELAW_INDEX_V, 'corpus': corpus, 'pin': pin, 'files': files, 'example': example, 'days': len(days)}


def _write_bloom(f: dict[str, Path], base: Path | None = None, new: list[bytes] | None = None) -> None:
    if base is not None and base.exists() and new is not None:
        data = base.read_bytes()
        m = int.from_bytes(data[4:12], 'little')
        keys = {l.split(b'\t', 1)[0] for l in new}
        with open(f['decisions'], 'rb') as fh:
            n_now = sum(1 for _ in fh)
        if n_now * BLOOM_BITS_PER_KEY <= m * 1.5:  # still room: add the new keys to the earlier filter
            _write_atomic(f['bloom'], _bloom_build(keys, len(keys), data))
            return
    keys = set()
    with open(f['decisions'], 'rb') as fh:
        for line in fh:
            keys.add(line.split(b'\t', 1)[0])
    _write_atomic(f['bloom'], _bloom_build(keys, len(keys)))


def _cl_update(corpus: str, pin: str, cwd: Path, base: dict, f: dict[str, Path]) -> dict:
    b = _cl_files(corpus, base['pin'])
    raw = _git_bytes(['-c', 'core.quotePath=false', 'diff', '--raw', '--no-renames', '--no-abbrev', '-z', base['pin'], pin], cwd)
    parts = raw.split(b'\0')
    files, example = base['files'], base['example']
    overlay = {}
    lines: dict[str, int] = {}
    for line in b['overlay'].read_text(encoding='utf-8').splitlines():
        key, blob, path, n = line.split('\t')
        overlay[path] = (key, blob)
        lines[blob] = int(n)
    sums = dict(l.split('\t', 1) for l in b['sums'].read_text(encoding='utf-8').splitlines() if '\t' in l)
    new_lines: list[bytes] = []
    rebuild = False
    i = 0
    while i + 1 < len(parts):
        meta, path = parts[i].decode('utf-8', 'replace'), parts[i + 1].decode('utf-8', 'replace')
        i += 2
        fields = meta.lstrip(':').split()
        if len(fields) < 5:
            continue
        old_blob, new_blob, status = fields[2], fields[3], fields[4][:1]
        m = _CL_JUDGMENTS.match(path)
        if m:
            if status == 'D':
                overlay.pop(path, None)
            else:
                overlay[path] = (m.group(1), new_blob)
            continue
        if path.endswith('.md') and not _CL_NOT_FILE.search(path):
            files += {'A': 1, 'D': -1}.get(status, 0)
            if status == 'D' and path == example:
                example = ''
        if path == 'decision-relations.tsv':  # duplicates named or changed: the docket file is read again
            rebuild = True
        if path.startswith('decisions/') and path.endswith('.md'):
            if status == 'D':
                rebuild = True
            elif status == 'A':
                name = path.rsplit('/', 1)[-1]
                new_lines.append(f'{decision_key(name[:-3].split("--", 1)[0])}\t{corpus}/{path}\n'.encode('utf-8'))
        elif _CL_INDEX_FILE.match(path):
            if status == 'A':
                text = (_cat_batch(cwd, [new_blob])[0][1] or b'').decode('utf-8', 'replace')
                new_lines += sorted(_index_tsv_lines(corpus, text.splitlines()))
            elif status == 'M':
                diff = _git_bytes(['diff', '--no-color', '-U0', old_blob, new_blob], cwd).decode('utf-8', 'replace')
                body = [l for l in diff.splitlines() if l[:1] in '+-' and not l.startswith(('+++', '---'))]
                if any(l.startswith('-') for l in body):
                    rebuild = True
                new_lines += sorted(_index_tsv_lines(corpus, [l[1:] for l in body if l.startswith('+')]))
            else:
                rebuild = True
    if not example:
        rec = _cl_build(corpus, pin, cwd, f)  # the example was deleted: read the tree once more
        return rec
    days: dict[str, tuple[str, str]] = {}
    for line in b['days'].read_text(encoding='utf-8').splitlines():
        d, s, n = (line.split('\t') + ['', ''])[:3]
        days[d] = (s, n)
    for d, s, n in _days_rows(cwd, f"{base['pin']}..{pin}"):
        days[d] = (s, n)
    _apply_redates(days, _cl_redates(cwd, f"{base['pin']}..{pin}"))
    _write_days(f['days'], days)
    got_lines, new_sums = _overlay_stats(cwd, [v for _, v in overlay.values() if v not in lines])
    lines.update(got_lines)
    sums.update(new_sums)
    _write_overlay(f, [(k, v, p) for p, (k, v) in overlay.items()], lines, sums)
    if rebuild:
        tree = []
        for line in _git_bytes(['-c', 'core.quotePath=false', 'ls-tree', '-r', pin], cwd).decode('utf-8', 'replace').splitlines():
            meta, _, path = line.partition('\t')
            p = meta.split()
            if len(p) == 3 and p[1] == 'blob':
                tree.append((path, p[2]))
        _write_atomic(f['decisions'], b''.join(_decision_lines_full(corpus, pin, cwd, tree)))
        _write_bloom(f)
    else:
        _write_atomic(f['decisions'], _sorted_merge(b['decisions'], new_lines))
        _write_bloom(f, b['bloom'], new_lines)
    return {'v': CASELAW_INDEX_V, 'corpus': corpus, 'pin': pin, 'files': files, 'example': example, 'days': len(days),
            'from': base['pin']}


def caselaw_vouched(paths: list[str]) -> frozenset:
    """Of these checked-out case-law corpora, those the case-law index built for their pins vouches for (each was read
    at its pin when the index was built): a reader can serve them without asking each checkout whether it has its
    pin, which cost a file-system walk per corpus on every call. Empty when no index matches the pins."""
    import hashlib
    key = ('cl-vouched', _head() + '|' + ','.join(sorted(paths)))
    if key not in _CACHE:
        pinned = sorted((p, tip(p) or '') for p in paths)
        h = hashlib.sha1('\n'.join(f'{c}@{p}' for c, p in pinned).encode('utf-8')).hexdigest()[:16]
        try:
            idx = json.loads((_store() / f'cl-set-v{CASELAW_INDEX_V}-{h}.json').read_text(encoding='utf-8'))
            got = frozenset(c for c, info in idx.get('corpora', {}).items() if info.get('pin') == tip(c))
        except (OSError, ValueError, AttributeError):
            got = frozenset()
        _CACHE[key] = got
    return _CACHE[key]  # type: ignore[return-value]


def _cl_served() -> list[tuple[str, str, Path]]:
    """(corpus, pinned commit, checkout) of every case-law corpus served and readable, without a git process when each
    checkout is at the commit the tree pins (read from its .git files)."""
    out = []
    for c in manifest()['corpora']:
        if not is_caselaw(c):
            continue
        cwd = ROOT / c['path']
        if not (cwd / '.git').exists() or not _readable(c['path'], cwd):
            continue
        pin = reachable_tip(c['path'])
        if pin == 'HEAD':
            pin = _head_from_files(cwd) or git('rev-parse', 'HEAD', cwd=cwd).strip()
        out.append((c['path'], pin, cwd))
    return out


def _objects_dir(cwd: Path) -> str | None:
    dirs = _gitdirs(cwd)
    return str(dirs[1] / 'objects') if dirs else None


def caselaw_index(build: str = 'no') -> dict | None:
    """The index of the case-law corpora served, at their pins: a summary (per corpus: pin, files, example, latest
    decision, its decision days' bytes in the days file, its Bloom filter's bytes, its docket file, its objects
    folder), with the days, overlay and Bloom files beside it. build: 'no' gives it only if it is built; 'join' also
    joins it when every corpus's record is there (a second or less); 'yes' also reads any corpus not yet read."""
    import hashlib
    corpora = manifest()['corpora']
    quick = ('caselaw-index-quick', f'{_head()}|{id(corpora)}|{len(corpora)}')
    if build != 'yes' and quick in _CACHE:  # asked once per corpus by some calls (list_jurisdictions): once a process
        return _CACHE[quick]  # type: ignore[return-value]
    store = _store()

    def load(h: str) -> dict | None:
        try:
            idx = json.loads((store / f'cl-set-v{CASELAW_INDEX_V}-{h}.json').read_text(encoding='utf-8'))
            if idx.get('v') == CASELAW_INDEX_V and all((store / idx[k]).exists() for k in ('days_file', 'overlay_file', 'bloom_file', 'sums_file')):
                idx['dir'] = str(store)
                return idx
        except (OSError, ValueError, KeyError):
            pass
        return None

    # With each checkout at the commit the tree pins (the usual case) the hash comes from the pins alone, and no file
    # of any checkout is read: the index was built from those commits, read in the checkouts then.
    pinned = sorted((c['path'], tip(c['path']) or '') for c in corpora if is_caselaw(c) and (ROOT / c['path'] / '.git').exists())
    if pinned and build != 'yes':
        idx = load(hashlib.sha1('\n'.join(f'{c}@{p}' for c, p in pinned).encode('utf-8')).hexdigest()[:16])
        if idx is not None:
            _CACHE[quick] = idx
            return idx
    served = _cl_served()
    if not served:
        _CACHE[quick] = None
        return None
    h = hashlib.sha1('\n'.join(f'{c}@{p}' for c, p, _ in sorted(served)).encode('utf-8')).hexdigest()[:16]
    key = ('caselaw-index', h)
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    idx = load(h)
    if idx is not None:
        _CACHE[key] = _CACHE[quick] = idx
        return idx
    if build == 'no':
        return None
    if build == 'join' and not all(_cl_files(c, p)['json'].exists() for c, p, _ in served):
        return None
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as pool:
        records = list(pool.map(carry(lambda s: caselaw_record(*s)), served))
    stem = f'cl-set-v{CASELAW_INDEX_V}-{h}'
    corpora: dict[str, dict] = {}
    days_parts, bloom_parts, overlay, sums = [], [], [], []
    at_days = at_bloom = 0
    for (c, p, cwd), rec in zip(served, records):
        f = _cl_files(c, p)
        days = f['days'].read_bytes()
        last = days.rstrip(b'\n').rsplit(b'\n', 1)[-1].decode('utf-8') if days.strip() else ''
        bloom = f['bloom'].read_bytes()
        corpora[c] = {'pin': p, 'files': rec['files'], 'example': rec['example'], 'days': [at_days, at_days + len(days)],
                      'latest': last.split('\t') if last else None, 'decisions': f['decisions'].name,
                      'bloom': [at_bloom, int.from_bytes(bloom[4:12], 'little'), bloom[12]], 'objects': _objects_dir(cwd)}
        days_parts.append(days)
        at_days += len(days)
        bloom_parts.append(bloom[13:])
        at_bloom += len(bloom) - 13
        for line in f['overlay'].read_text(encoding='utf-8').splitlines():
            k, blob, _, n = line.split('\t')
            overlay.append(f'{k}\t{c}\t{blob}\t{n}\n')
        sums += f['sums'].read_text(encoding='utf-8').splitlines(keepends=True)
    _write_atomic(store / f'{stem}.days.tsv', b''.join(days_parts))
    _write_atomic(store / f'{stem}.sums.tsv', ''.join(sorted(set(sums))).encode('utf-8'))
    _write_atomic(store / f'{stem}.bloom', b''.join(bloom_parts))
    _write_atomic(store / f'{stem}.overlay.tsv', ''.join(sorted(overlay)).encode('utf-8'))
    idx = {'v': CASELAW_INDEX_V, 'hash': h, 'corpora': corpora, 'days_file': f'{stem}.days.tsv',
           'overlay_file': f'{stem}.overlay.tsv', 'bloom_file': f'{stem}.bloom', 'sums_file': f'{stem}.sums.tsv'}
    _write_atomic(store / f'cl-set-v{CASELAW_INDEX_V}-{h}.json', json.dumps(idx, ensure_ascii=False).encode('utf-8'))
    for old in sorted(store.glob(f'cl-set-v{CASELAW_INDEX_V}-*.json'), key=lambda p: p.stat().st_mtime)[:-4]:
        for ext in ('.json', '.days.tsv', '.overlay.tsv', '.bloom', '.sums.tsv'):
            (store / (old.name[:-5] + ext)).unlink(missing_ok=True)
    idx['dir'] = str(store)
    _CACHE[key] = _CACHE[quick] = idx
    return idx


def _mm_lines(path: Path, start: int, end: int, prefix: bytes, last_le: bool = False):
    """Lines of a sorted file between byte offsets that start with `prefix` (binary search); with last_le, the last
    line whose text sorts at or before `prefix` instead. `path` may be an mmap already open."""
    import mmap
    if end <= start:
        return [] if not last_le else None
    if isinstance(path, mmap.mmap):
        return _mm_search(path, start, end, prefix, last_le)
    with open(path, 'rb') as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        return _mm_search(mm, start, end, prefix, last_le)


def _mm_search(mm, start: int, end: int, prefix: bytes, last_le: bool):
    lo, hi = start, end
    if last_le:
        # the first line whose first len(prefix) bytes sort after prefix; the line before it is the answer
        while lo < hi:
            mid = (lo + hi) // 2
            s = mm.rfind(b'\n', start, mid) + 1 if mid > start else start
            s = max(s, start)
            e = mm.find(b'\n', s, end)
            e = end if e < 0 else e
            if mm[s:s + len(prefix)] <= prefix:
                lo = e + 1
            else:
                hi = s
        if lo <= start:
            return None
        s = mm.rfind(b'\n', start, lo - 1) + 1
        s = max(s, start)
        return mm[s:lo - 1].decode('utf-8', 'replace')
    while lo < hi:
        mid = (lo + hi) // 2
        s = mm.rfind(b'\n', start, mid) + 1 if mid > start else start
        s = max(s, start)
        e = mm.find(b'\n', s, end)
        e = end if e < 0 else e
        if mm[s:e] + b'\n' < prefix:
            lo = e + 1
        else:
            hi = s
    out, pos = [], lo
    while pos < end:
        e = mm.find(b'\n', pos, end)
        e = end if e < 0 else e
        line = mm[pos:e]
        if not line.startswith(prefix):
            break
        out.append(line.decode('utf-8', 'replace'))
        pos = e + 1
    return out


def latest_decisions(date: str, corpora: list[str]) -> dict[str, tuple[str, str, str] | None]:
    """latest_decision for many case-law corpora: from the case-law index when it is built (no git process), else
    one git log per corpus, eight at a time."""
    idx = caselaw_index('join')
    if idx is not None:
        import mmap
        days_file = Path(idx['dir']) / idx['days_file']
        out: dict[str, tuple[str, str, str] | None] = {}
        rest = []
        fh = open(days_file, 'rb')  # one file, opened once, whatever the number of corpora
        mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) if days_file.stat().st_size else None
        for c in corpora:
            info = idx['corpora'].get(c)
            if info is None:
                rest.append(c)
                continue
            latest = info.get('latest')
            if latest and latest[0] <= date:
                d, s, n = (latest + ['', ''])[:3]
            else:
                line = _mm_lines(mm, info['days'][0], info['days'][1], date.encode('utf-8'), last_le=True) if mm else None
                if not line:
                    out[c] = None
                    continue
                d, s, n = (line.split('\t') + ['', ''])[:3]
            out[c] = (n, d, s)
        if mm is not None:
            mm.close()
        fh.close()
        if rest:
            out.update(_latest_each(date, rest))
        return out
    return _latest_each(date, corpora)


def _latest_each(date: str, corpora: list[str]) -> dict[str, tuple[str, str, str] | None]:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as pool:
        return dict(zip(corpora, pool.map(carry(lambda p: latest_decision(p, date)), corpora)))


def caselaw_overlay_rows(keys: list[str]) -> list[tuple[str, str]] | None:
    """(corpus, blob) of every judgment overlay file the case-law corpora served hold for these keys (a law path
    without .jsonl: "united-states/federal/usc/title-11/362"), from the index; None when it is not built."""
    idx = caselaw_index('join')
    if idx is None:
        return None
    return [(e['corpus'], e['blob']) for e in caselaw_overlay_entries(keys, idx)]


def caselaw_overlay_entries(keys: list[str], idx: dict | None = None) -> list[dict] | None:
    """Every judgment overlay file the case-law corpora served hold for these keys, as {corpus, blob, lines, summary}
    (summary: rows, rows by day decided, the latest SUM_TAIL rows; for a file of SUM_ROWS rows or more, else None).
    None when the index is not built."""
    idx = idx or caselaw_index('join')
    if idx is None:
        return None
    import mmap
    path = Path(idx['dir']) / idx['overlay_file']
    size = path.stat().st_size
    out = []
    if not size:
        return out
    with open(path, 'rb') as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        for k in keys:
            for line in _mm_lines(mm, 0, size, f'{k}\t'.encode('utf-8')):
                _, corpus, blob, n = line.split('\t')
                out.append({'corpus': corpus, 'blob': blob, 'lines': int(n), 'summary': None})
    long = [e for e in out if e['lines'] >= SUM_ROWS]
    sums = Path(idx['dir']) / idx['sums_file']
    if long and sums.stat().st_size:
        with open(sums, 'rb') as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for e in long:
                got = _mm_lines(mm, 0, len(mm), f"{e['blob']}\t".encode('ascii'))
                if got:
                    e['summary'] = json.loads(got[0].split('\t', 1)[1])
    return out


def read_blobs_of(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """(corpus, text) of blobs held by several case-law corpora, read by one git process: the first corpus's
    `git cat-file --batch` with the others' object folders as alternates."""
    return [(c, t) for (c, _), t in zip(rows, read_texts_of(rows)) if t is not None]


# corpora one git process reads through alternates: each alternate's packs are opened on its first object, about
# 10 ms each, so the overlays of 130 US courts took 1.3 s in one process (US speed gate, 2026-11-08); in parts of 16,
# eight at a time, the opening is shared out.
CAT_DIRS = 16


BLOB_CACHE_MAX = 32 << 20  # bytes: a blob up to this size that read_texts_of reads is kept in the store, by its id


def read_texts_of(rows: list[tuple[str, str]]) -> list[str | None]:
    """The text of each (corpus, object) given (a blob id, or <commit>:<path>), None where it is missing, read by one
    git process for all the corpora (read_blobs_of). A blob, named by its id, is kept in the store once read (an id
    names one text for ever): the 130 overlay files of 11 U.S.C. 362 in as many US courts cost 0.5 s of git on each
    call, opening 130 object stores (US speed gate, 2026-11-09)."""
    if not rows:
        return []
    import os
    store = _store() / 'blobs'
    out: list[str | None] = [None] * len(rows)
    todo = []
    for i, (c, obj) in enumerate(rows):
        if _HEX40.fullmatch(obj):
            try:
                out[i] = (store / obj[:2] / obj).read_bytes().decode('utf-8', 'replace')
                continue
            except OSError:
                pass
        todo.append(i)
    if todo:
        got = _read_texts_git([rows[i] for i in todo])
        for i, text in zip(todo, got):
            out[i] = text
            obj = rows[i][1]
            if text is not None and _HEX40.fullmatch(obj) and len(text) <= BLOB_CACHE_MAX:
                try:  # a cache: a store that cannot be written to reads the blob again next time
                    dest = store / obj[:2] / obj
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    tmp = dest.with_name(f'{obj}.{os.getpid()}.tmp')
                    tmp.write_bytes(text.encode('utf-8'))
                    os.replace(tmp, dest)
                except OSError:
                    pass
    return out


_HEX40 = re.compile(r'[0-9a-f]{40}')
_COMMIT_PATH = re.compile(r'[0-9a-f]{40}:.+')


def rows_upto(corpus: str, blob: str, date: str, n: int) -> list[str] | None:
    """The last `n` rows of an overlay file decided on or before `date`, in the order of their day and then the row
    itself (as judgments_counted picks them), from the file sorted once by day and kept in the store beside the blob
    (<blob>.byday: "<decided> TAB <row>" lines): a long file's summary keeps only its latest rows, so a date before them
    read the whole file on each call (art. 1.022 of the Brazilian CPC: two files of 46 MB, 0.6 s of git and the parse
    of 614,000 rows, Brazil speed gate 2026-11-09). None when the blob cannot be read."""
    import mmap
    import os
    if not _HEX40.fullmatch(blob):
        return None
    path = _store() / 'blobs' / blob[:2] / f'{blob}.byday'
    if not path.exists():
        text = read_texts_of([(corpus, blob)])[0]
        if text is None:
            return None
        rows = []
        for line in text.encode('utf-8').splitlines():
            m = _DECIDED_ROW.search(line)
            if m:
                rows.append((m.group(1), line))
        rows.sort()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
            tmp.write_bytes(b''.join(d + b'\t' + line + b'\n' for d, line in rows))
            os.replace(tmp, path)
        except OSError:
            return [line.decode('utf-8', 'replace') for d, line in rows if d.decode() <= date][-n:]
    size = path.stat().st_size
    if not size or n <= 0:
        return []
    key = date.encode('ascii')
    with open(path, 'rb') as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        lo, hi = 0, size  # the start of the first line decided after the date
        while lo < hi:
            mid = (lo + hi) // 2
            st = mm.rfind(b'\n', 0, mid) + 1
            en = mm.find(b'\n', st)
            en = size if en < 0 else en
            if mm[st:st + 10] <= key:
                lo = en + 1
            else:
                hi = st
        end, out = min(lo, size), []
        pos = end - 1  # the newline that ends the last row on or before the date
        while pos > 0 and len(out) < n:
            st = mm.rfind(b'\n', 0, pos) + 1
            out.append(mm[st:pos].split(b'\t', 1)[1].decode('utf-8', 'replace'))
            pos = st - 1
    return out[::-1]


def _read_texts_git(rows: list[tuple[str, str]]) -> list[str | None]:
    idx = caselaw_index('no') or {'corpora': {}}
    import os
    out: list[str | None] = []
    groups: list[list[tuple[str, str]]] = [[]]
    dirs: list[list[str]] = [[]]
    for c, blob in rows:  # one process for all, unless the alternates would pass the environment's size (32 KB on Windows)
        d = (idx['corpora'].get(c) or {}).get('objects') or _objects_dir(ROOT / c) or ''
        if d not in dirs[-1] and (sum(len(x) + 1 for x in dirs[-1]) + len(d) > 20_000 or len(dirs[-1]) >= CAT_DIRS):
            groups.append([])
            dirs.append([])
        if d not in dirs[-1]:
            dirs[-1].append(d)
        groups[-1].append((c, blob))
    def one(gd):
        group, ds = gd
        return _cat_batch(ROOT / group[0][0], [b for _, b in group], env={'GIT_ALTERNATE_OBJECT_DIRECTORIES': os.pathsep.join(ds[1:])})
    if len(groups) == 1:
        parts = [one((groups[0], dirs[0]))]
    else:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(min(8, len(groups))) as pool:
            parts = list(pool.map(carry(one), zip(groups, dirs)))
    for got in parts:
        out += [data.decode('utf-8', 'replace') if kind == b'blob' and data is not None else None for kind, data in got]
    return out


def bloom_candidates(key: str) -> list[tuple[str, str]] | None:
    """(corpus, its docket file) of the case-law corpora whose Bloom filter may hold a key: the only docket files a
    lookup opens. None when the index is not built."""
    idx = caselaw_index('join')
    if idx is None:
        return None
    import mmap
    k = key.encode('utf-8')
    out = []
    path = Path(idx['dir']) / idx['bloom_file']
    if path.stat().st_size == 0:
        return []
    with open(path, 'rb') as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        for c, info in idx['corpora'].items():
            off, m, nk = info['bloom']
            if all(mm[off + (p >> 3)] & (1 << (p & 7)) for p in _bloom_positions(k, m, nk)):
                out.append((c, str(Path(idx['dir']) / info['decisions'])))
    return out


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
    if ix.get('focused'):  # a read of single decisions: the corpus's dated commits without the per-file index
        ix = _light_index(corpus, cwd, ix['pin'])
    key = ('corpus-events', f"{corpus}@{_at(ix)}")
    if key not in _CACHE:
        _CACHE[key] = _Events(Event(r[0], corpus, r[0], r[1], r[5], r[4], r[3]) for r in ix['rows'] if r[5])
    return _CACHE[key]  # type: ignore[return-value]


def _light_index(corpus: str, cwd: Path, sha: str) -> dict:
    """Every commit of a case-law corpus as the corpus index keeps it (rows, unknown kinds) but without its files: one
    `git log` of the messages, no per-commit file list, which is what makes the whole index slow (the Cour de
    cassation: ~20 s against ~100+ s). What the record notes need (where the record starts and ends, changes ahead)
    for a read of one decision (focus()). Kept on disk beside the indexes, keyed by the pin."""
    key = ('index-light', f'{corpus}@{sha}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    import pickle
    store = _store()
    path = store / f"{corpus.replace('/', '~')}.v{INDEX_VERSION}.{sha[:12]}.light"
    data = None
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
        if data.get('v') != _index_version() or data.get('pin') != sha:
            data = None
    except Exception:
        data = None
    if data is None:
        info = corpus_info(corpus)
        fmt = '--format=%x1d%H%x1f%an%x1f%aI%x1f%s%x1f%(trailers:only,unfold)%x1e'
        raw = git('log', '--reverse', fmt, sha, cwd=cwd)
        rows, unknown = [], set()
        for chunk in raw.split('\x1d')[1:]:
            head = chunk.partition('\x1e')[0]
            commit, author, when, subject, block = head.split('\x1f', 4)
            row, odd = _derive(info, commit, author, when, subject, block)
            if odd:
                unknown.add(odd)
            rows.append(row)
        data = {'v': _index_version(), 'pin': sha, 'rows': rows, 'unknown': unknown, 'at': f'{sha}~light'}
        try:
            import os
            store.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
            with open(tmp, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(tmp, path)
        except OSError:
            pass
    _CACHE[key] = data
    return data


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
    ix = _index(corpus)
    if ix.get('focused'):  # a few files' commits, read for one call: not kept
        return [_moved_fix(corpus, r[9]) for r in ix['rows'] if r[9]]
    # Once per reading of the index: every read of a provision asks (file_commit), and each pass went through every
    # commit of the corpus.
    key = ('corrections', f"{corpus}@{_at(ix)}")
    got = _CACHE.get(key)
    if got is None:
        got = _CACHE[key] = tuple(_moved_fix(corpus, r[9]) for r in ix['rows'] if r[9])
    return list(got)  # type: ignore[arg-type]


def _earlier_names(corpus: str, rel: str) -> set[str]:
    """A file's path now and every path a documentation commit moved it from (moves() inverted)."""
    mv = moves(corpus)
    if not mv:
        return {rel}
    key = ('moved-from', f"{corpus}@{_at(_index(corpus))}")
    if key not in _CACHE:
        inv: dict[str, list[str]] = {}
        for old, new in mv.items():
            inv.setdefault(new, []).append(old)
        _CACHE[key] = inv
    return {rel, *_CACHE[key].get(rel, [])}  # type: ignore[union-attr]


def _folder_moves(corpus: str) -> dict[str, str]:
    """old folder -> new folder, from the file moves of a layout commit (japan-law's 129AC0000000089/art-005.md ->
    act/1896/089/art-005.md gives 129AC0000000089 -> act/1896/089), every folder a moved file sat in: the folders of
    the old and new path, and theirs, as far up as the two paths keep the same names below them. Never by stripping
    only the shared tail: armenia's law/52/x.md -> law/1961/52/x.md would read as a move of law -> law/1961."""
    mv = moves(corpus)
    key = ('folder-moves', f"{corpus}@{_at(_index(corpus))}")
    if key not in _CACHE:
        out: dict[str, str] = {}
        for old, new in mv.items():
            a, b = old.split('/')[:-1], new.split('/')[:-1]  # the folders the file sat in
            while a and b and a != b:
                out.setdefault('/'.join(a), '/'.join(b))
                if a[-1] != b[-1] or len(a) == 1 or len(b) == 1:
                    break  # the folder itself was renamed (slug -> number): nothing above it moved with it
                a, b = a[:-1], b[:-1]
        _CACHE[key] = out
    return _CACHE[key]  # type: ignore[return-value]


def _moved_fix(corpus: str, fix: dict) -> dict:
    """A correction as the paths are now: its Files: and Act-path: name the paths of its own day, and a later
    documentation commit may have moved them (a layout move). Unchanged when nothing moved."""
    mv = moves(corpus)
    if not mv:
        return fix
    out = dict(fix)
    out['files'] = [mv.get(f, f) for f in fix.get('files') or []]
    if fix.get('act_path'):
        out['act_path'] = _folder_moves(corpus).get(fix['act_path'], fix['act_path'])
    return out


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
    return _correction_end(corpus, fix, rel, correction_cap(corpus, rel, fix['from']))


def _correction_end(corpus: str, fix: dict, rel: str, cap: str | None) -> str:
    """correction_end, given the cap the file's act's end sets (correction_cap), or None for none."""
    cap = cap or '9999-12-31'  # never past the file's act's end
    if fix.get('to'):
        return min(fix['to'], cap)
    folder = lambda f: f.rsplit('/', 1)[0] if '/' in f else f  # noqa: E731
    paths = [fix['act_path']] if fix.get('act_path') else sorted({folder(f) for f in fix['files']}) or [folder(rel)]
    nxt = act_next(corpus, paths, fix['from'])
    if not nxt:
        return cap
    import datetime as dt
    return min((dt.date.fromisoformat(nxt) - dt.timedelta(days=1)).isoformat(), cap)


def overlay_ends(corpus: str) -> list[tuple]:
    """For each correction of file_index's overlays, in their order: (end, own). `own` is {file: correction_end} for
    the files whose last day is their own, and `end` the last day of every other file the correction covers (None
    when each file has its own). A correction's end is one day for all its files, except under an act that
    data/acts.json ends on a day (correction_cap) or where the correction names no range, act or files and so ends
    with each file's own folder. Asked once a file, for each correction and each tree, it was most of building the
    tree of a past date: 16 million calls and 115 of the 127 s for Japan's 443,000 files (profiled 2026-11-11). Once
    per reading of the index."""
    ix = _index(corpus)
    key = ('overlay-ends', f'{corpus}@{_at(ix)}')
    got = _CACHE.get(key)
    if got is None:
        ended = {f for f, e in act_ends(corpus).items() if e['day']}
        got = []
        for fix, _, files in file_index(corpus)[1]:
            shared = bool(fix.get('to') or fix.get('act_path') or fix['files'])
            end, own = None, {}
            for path in files:
                capped, i = not shared, path.find('/')
                while not capped and i > 0:  # under an act with a dated end: its cap is the file's own
                    capped = path[:i] in ended
                    i = path.find('/', i + 1)
                if capped:
                    own[path] = correction_end(corpus, fix, path)
                elif end is None:
                    end = _correction_end(corpus, fix, path, None)
            got.append((end, own))
        _CACHE[key] = got
    return got  # type: ignore[return-value]


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
    first = events[0].in_force if events else None
    for c in manifest()['corpora']:  # case law is not in the timeline: its record starts where its corpus.json says
        start = str(c.get('history_from') or '')[:10]
        if is_caselaw(c) and ISO_DAY.match(start) and (ROOT / c['path'] / '.git').exists():
            first = min(first or start, start)
    return Moment(date) if first and first <= date else None


def corpus_on(date: str, corpus: str) -> str | None:
    """The corpus commit in force on `date`: the last of its dated commits before the first one dated after `date`
    (a prefix, as the corpora record changes in the order they took force)."""
    events = corpus_events(corpus)

    def latest_so_far():  # the latest in-force day up to each event: it first passes a date at the first event after it
        out, top = [], ''
        for e in events:
            if e.in_force > top:
                top = e.in_force
            out.append(top)
        return tuple(out)
    import bisect
    i = bisect.bisect_right(_kept(events, 'latest-so-far', latest_so_far), date)  # the first event dated after `date`
    return events[i - 1].corpus_commit if i else None


def in_order(corpus: str) -> bool:
    """Whether a corpus's history is in in-force order with no corrections: then the commit-order prefix (corpus_on)
    is exactly the corpus as in force on a date, and no tree has to be built."""
    events = corpus_events(corpus)

    def out_of_order():
        last = ''
        for e in events:
            if e.kind == 'documentation':
                continue
            if e.in_force < last:
                return 'yes'
            last = e.in_force
        return 'no'
    if _kept(events, 'out-of-order', out_of_order) == 'yes':
        return False
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
    import time
    began = time.monotonic()
    kept = None if ix.get('focused') else _file_index_kept(corpus, ix)
    if kept is not None:
        got = _file_index_read(kept)
        if got is not None:
            _CACHE[key] = got
            return got
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
    mv = moves(corpus)  # Files: names paths as they were that day; the index keys them as they are now
    wanted = {order: [f for f in r[9]['files'] if mv.get(f, f) not in touched.get(order, {})] for order, r in enumerate(rows) if r[9]}
    at = _named_at(ix, cwd, wanted)
    for order, r in enumerate(rows):
        fix = r[9]
        if not fix:
            continue
        files = dict(touched.get(order, {}))
        files.update({mv.get(p, p): v for p, v in at.get(order, {}).items()})  # named but unchanged: their text at the correction commit is the tip's
        if fix['files']:
            names = {mv.get(f, f) for f in fix['files']}
            files = {p: v for p, v in files.items() if p in names}
        overlays.append((_moved_fix(corpus, fix), order, files))
    _CACHE[key] = (index, overlays)
    if kept is not None and time.monotonic() - began >= FILE_INDEX_KEEP_S:
        _file_index_write(kept, (index, overlays))
    return index, overlays


# A corpus whose file index took this long to work out keeps it on disk, beside its index: Japan's acts (41,177
# corrections naming 5.8 million paths) took 17 minutes in every fresh process, which is how long a server's new copy
# then took to start. Keyed by what it is worked out from: the index's reading, the moved paths, and this file itself
# (a change to the rules here makes a new key, so no kept answer outlives the code that made it).
FILE_INDEX_KEEP_S = 2.0
FILE_INDEX_KEPT = 2  # kept files per corpus (two server copies may read different pins)
_SOURCE_ID: list = []


def _file_index_kept(corpus: str, ix: dict) -> Path | None:
    import hashlib
    try:
        if not _SOURCE_ID:
            _SOURCE_ID.append(hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:10])
        made_from = hashlib.sha1(repr((sorted(moves(corpus).items()), sorted(str(b) for b in notice_blobs(corpus)),
                                       bool(act_ends(corpus)))).encode('utf-8', 'replace')).hexdigest()[:10]
        return _store() / f"file-index-v1-{corpus.replace('/', '~')}-{_at(ix)[:12]}-{_SOURCE_ID[0]}-{made_from}.pickle"
    except (OSError, ValueError, SystemExit):
        return None


def _file_index_read(path: Path):
    import pickle
    try:
        with open(path, 'rb') as f:
            got = pickle.load(f)
    except (OSError, ValueError, EOFError, pickle.UnpicklingError, AttributeError, ImportError, IndexError):
        return None
    return got if isinstance(got, tuple) and len(got) == 2 and isinstance(got[0], dict) and isinstance(got[1], list) else None


def _file_index_write(path: Path, value) -> None:
    import os
    import pickle
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f'{path.name}.{os.getpid()}.{threading.get_ident()}.tmp')
        with open(tmp, 'wb') as f:
            pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)
        stem = path.name.split('-')  # file-index-v1-<corpus>-<at>-<source>-<made from>.pickle
        same = sorted(path.parent.glob('-'.join(stem[:-3]) + '-*.pickle'), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in same[FILE_INDEX_KEPT:]:
            if old != path:
                old.unlink(missing_ok=True)
    except OSError:
        pass


NAMED_TREE_MIN = 200  # a correction naming this many unchanged paths is read with one recursive ls-tree (_named_at)


def _named_at(ix: dict, cwd: Path, wanted: dict[int, list[str]]) -> dict[int, dict[str, tuple]]:
    """row -> {path: (blob, mode)} for the paths a correction names but does not change: each as `git ls-tree` lists
    it at that commit. One `git cat-file --batch-check` gives every blob; the mode is the file's own last version in
    the index when that version has the same blob. Anything else (a folder, a path moved or withdrawn, a version the
    index does not hold) is asked of `git ls-tree`, one commit at a time, as before."""
    rows = ix['rows']
    out: dict[int, dict[str, tuple]] = {}
    odd = set(ix.get('moves', {})) | set(ix.get('moves', {}).values()) | set(ix.get('withdrawn', {}))
    # A correction that restates a whole code under Files: (Texas: 54,826 paths in 7 corrections, about 3 ms each
    # as <commit>:<path>, since git resolves each from the root tree; audit row 54) is read with one recursive
    # `git ls-tree` of the folders it names, and the named paths picked out of it. What that does not list (a
    # folder, a path missing at that commit) goes the per-path way below.
    wanted = dict(wanted)
    for order, named in list(wanted.items()):
        if len(named) < NAMED_TREE_MIN:
            continue
        want = set(named)
        tops = sorted({f.split('/', 1)[0] for f in want})
        for line in git('ls-tree', '-r', rows[order][0], '--', *tops, cwd=cwd).splitlines():
            meta, _, path = line.partition('\t')
            path = _unquote(path)
            if path in want:
                mode, _, blob = meta.split()
                out.setdefault(order, {})[path] = (blob, mode)
                want.discard(path)
        wanted[order] = [f for f in named if f in want]
    queries = [(order, f) for order, named in wanted.items() for f in named]
    if not queries:
        return out
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
        for k in [k for k in list(_CACHE) if k[0] == 'tree']:  # its trees went with it; built again when next asked
            _CACHE.pop(k, None)
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
    ix = _index(corpus)
    # The tree changes only on the days _tree_days lists, so it is built, and kept, for the last of them on or
    # before `date`: one tree per day the corpus changed, not one per date asked (and not a new one each morning).
    days = _tree_days(corpus, ix)
    if days is not None:
        import bisect
        i = bisect.bisect_right(days, date)
        if not i:
            return None  # before every version and correction: nothing is in force
        date = days[i - 1]
    key = ('tree', f'{corpus}@{_at(ix)}@{date}')
    _trees_alive()  # a swept store drops the cached trees, so the one asked for is built again below
    got = _CACHE.get(key, _MISSING)
    if got is not _MISSING:
        return got  # type: ignore[return-value]
    # One build of a tree at a time: its git index file is named after the key, and two dates asked at once may now
    # be the same day's tree.
    with _TREE_LOCKS[hash(key) % len(_TREE_LOCKS)]:
        return _built_tree(date, corpus, key)


_TREE_LOCKS = tuple(threading.Lock() for _ in range(64))


def _tree_days(corpus: str, ix: dict) -> tuple | None:
    """Every day on which corpus_tree's answer can change, in order: the in-force day of each version of each file
    (file_index: act ends included), the first day of each correction, and the day after its last day for each file
    it covers. corpus_tree picks a version by `day <= date` and applies a correction when `from <= date <= end`, so two
    dates with the same last such day on or before them give the same tree. None when an end is not a calendar day
    (its day after cannot be named): each date then has its own tree, as before. Once per reading of the index."""
    key = ('tree-days', f'{corpus}@{_at(ix)}')
    got = _CACHE.get(key)
    if got is None:
        import datetime as dt
        index, overlays = file_index(corpus)
        days = {v[0] for versions in index.values() for v in versions}
        try:
            ends = set()
            for (fix, _, files), (end, own) in zip(overlays, overlay_ends(corpus)):
                days.add(fix['from'])
                ends.update(own.values())
                if len(own) < len(files):
                    ends.add(end)
            for end in ends:
                if end < '9999-12-31':  # no date asked is after it
                    days.add((dt.date.fromisoformat(end) + dt.timedelta(days=1)).isoformat())
            got = tuple(sorted(days))
        except (ValueError, OverflowError):
            got = False
        _CACHE[key] = got
    return None if got is False else got  # type: ignore[return-value]


def _built_tree(date: str, corpus: str, key: tuple) -> str | None:
    """corpus_tree's tree for a day it changes on, built unless another thread has just built it."""
    got = _CACHE.get(key, _MISSING)
    if got is not _MISSING:
        return got  # type: ignore[return-value]
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
    for (fix, order, files), (end, own) in zip(overlays, overlay_ends(corpus)):
        if fix['from'] > date or (not own and (end is None or date > end)):  # (no file: nothing to lay over)
            continue
        for path, (blob, mode) in files.items():
            if date > own.get(path, end):
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
    return sorted(k[1] for k, ok in list(_CACHE.items()) if k[0] == 'readable' and not ok)


_BEHIND = ('{corpus} is behind the tree: its checkout does not have the commit the tree pins ({pin}), so it is left '
           'out. Run: git submodule update --init -- {corpus}  (or for every corpus: git submodule update --init)')


def behind() -> dict[str, str]:
    """The corpora left out of a whole-tree read because their checkout lacks the commit the tree pins: corpus ->
    that commit."""
    return {k[1]: v for k, v in list(_CACHE.items()) if k[0] == 'behind'}  # type: ignore[misc]


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
    return sorted(k[1] for k, ok in list(_CACHE.items()) if k[0] == 'full-history' and not ok)


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
        _CACHE[key] = {c['path'].split('/')[0] for c in _whole_manifest()['corpora']} | {str(c.get('iso_path') or '').split('/')[0] for c in _whole_manifest()['corpora'] if c.get('iso_path')}
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
        for c in _whole_manifest()['corpora']:
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


# Case law: corpora of court decisions, not of law (lexifina/*-caselaw: the Swiss courts, the Dutch courts, ...).
# Each decision is one file and one commit (Kind: court), dated the day it was given. They are read like any corpus,
# but lists and searches of law leave them out unless they are named: "switzerland" takes in Swiss law, and
# "switzerland/caselaw", "switzerland/bund/caselaw", "caselaw" or the canton's case law takes in the decisions.
CASELAW_KINDS = {'judgments', 'decisions', 'caselaw', 'case law', 'case-law', 'court', 'courts'}


def is_caselaw(corpus: dict) -> bool:
    """Whether a manifest entry is a body of court decisions: corpus.json's `kind`, or a corpus at <...>/caselaw."""
    return str(corpus.get('kind') or '').strip().lower() in CASELAW_KINDS or corpus['path'].rstrip('/').endswith('/caselaw')


def names_caselaw(name: str) -> bool:
    """Whether a name asks for case law ("caselaw", "switzerland/caselaw", "switzerland/bund/caselaw/...")."""
    plain = _plain(name)
    return plain in CASELAW_KINDS or bool(re.search(r'(^|/)case-?law(/|$)', plain))


def takes_in(corpus: dict, name: str) -> bool:
    """matches(), with case law taken in only when the name asks for it: `countries.py add switzerland` and `laws ...
    switzerland` mean Swiss law, not a million decisions. "<country>/caselaw" ("switzerland/caselaw",
    "netherlands/caselaw") takes in every case-law corpus of that country, "caselaw" every one in the tree."""
    if not is_caselaw(corpus):
        return matches(corpus, name)
    if not names_caselaw(name):
        return False
    plain = _plain(name)
    if plain in CASELAW_KINDS:
        return True
    if matches(corpus, name):
        return True
    above = re.sub(r'/?case-?law(/.*)?$', '', plain)  # "switzerland/caselaw" -> "switzerland"
    return bool(above) and matches(corpus, above)


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
GIT_DIFF_SECONDS = 60  # one git diff of long files (_GitDiffs) is waited for this long; then difflib, as without git
waiting = None  # set by a reader (the MCP server's checkpoint): called while waiting for git; raises to stop the wait


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
            # The real subprocess module: under the MCP server `subprocess` is a namespace with run() only, Popen
            # raised AttributeError here, and every long file was matched by difflib (most of a minute on one).
            self.proc = _subprocess.Popen([*cmd, 'diff', *_GIT_DIFF_OPTIONS, 'a', 'b'], cwd=d, env=env,
                                          stdout=self.out, stderr=_subprocess.DEVNULL, stdin=_subprocess.DEVNULL)
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
        import time
        stop = time.monotonic() + GIT_DIFF_SECONDS
        try:
            while True:  # a bounded wait: stopped with the call (waiting), and never longer than GIT_DIFF_SECONDS
                try:
                    code = self.proc.wait(0.25)
                    break
                except _subprocess.TimeoutExpired:
                    if waiting is not None:
                        waiting()
                    if time.monotonic() > stop:
                        self.close()
                        return [None] * len(self.pairs)
        except BaseException:
            self.close()
            raise
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
    blame_path = rel
    names = _earlier_names(corpus, rel)
    if len(names) > 1:
        # Moved by a layout commit. git blame's own rename pairing may follow another act's identical file, so blame
        # never crosses the move: only a file whose last version is from before it, by the name it had then.
        blame_path = next((n for n in sorted(names - {rel}) if read_object(corpus, f'{seq[-1][0]}:{n}') is not None), None)
        if blame_path is None:
            return None
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
        porcelain = git('blame', '--line-porcelain', seq[-1][0], '--', blame_path, cwd=corpus_dir(corpus))
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


_BY_PATH: dict = {}  # id(a manifest) -> (the manifest, how many corpora it had, {path: its entry}), for corpus_info


def corpus_info(corpus: str) -> dict:
    """A corpus's entry in the manifest (StopIteration when it has none, as a search of the list gave). Looked up by
    path in a table made once per manifest: asked many times a call, and a scan of the list read every corpus."""
    m = manifest()
    corpora = m['corpora']
    hit = _BY_PATH.get(id(m))
    if hit is None or hit[0] is not m or hit[1] != len(corpora):
        table: dict[str, dict] = {}
        for c in corpora:
            table.setdefault(c['path'], c)  # the first of a path, as the scan found
        if len(_BY_PATH) >= 16:  # a few manifests at a time (a host's scoped calls each have their own)
            _BY_PATH.clear()
        hit = _BY_PATH[id(m)] = (m, len(corpora), table)  # holds the manifest, so its id is not used again meanwhile
    found = hit[2].get(corpus)
    if found is None:
        return next(c for c in corpora if c['path'] == corpus)
    return found


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
    given = events if events is not None else corpus_events(corpus)

    def read():  # one pass, kept with a kept list: own events, the first by day, their days in order, all baselines?
        mine = [e for e in given if e.corpus == corpus and e.kind != 'documentation']
        return (mine, min(mine, key=lambda e: e.in_force) if mine else None, tuple(sorted(e.in_force for e in mine)),
                all(e.kind == 'baseline' for e in mine))
    own, first, days, only_baselines = _kept(given, ('caveats', corpus), read)
    import bisect
    info = corpus_info(corpus)
    out = []
    if (ROOT / corpus / '.git').exists() and not _readable(corpus, ROOT / corpus):
        return [_UNREADABLE.format(corpus=corpus)]
    if own:
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
        last = days[bisect.bisect_right(days, today) - 1] if days and days[0] <= today else None
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
    # Starting texts only read as current text, unless the corpus says each is its act as enacted (audit row 79: the
    # Indonesian builder credits each Perda as enacted to the publisher, Kind: publisher, dated by the Perda's own day).
    current_only = info.get('history') == 'current-only' or (
        info.get('history') != 'as-enacted' and own and only_baselines)
    if current_only and (not covered or date < covered):
        out.append(f"{corpus}: this record holds only the text as the publisher gave it on the day it was read; an "
                   "earlier date shows that text only from that day, not as the law was in force before.")
    if own and _metadata_only(corpus):
        out.append(f"{corpus}: this record lists acts (titles, numbers, dates) without their text, so what it shows "
                   "is a catalogue entry, not the law.")
    ahead = len(days) - bisect.bisect_right(days, today)
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
    # Court decisions have no Modifies:/Applies:/transitional rules to hold: the note is about law, so it is not given
    # for a case-law corpus (found by the NL speed gate, 2026-11-06).
    if own and missing and info.get('history') not in ('metadata-only',) and not is_caselaw({'path': corpus, **info}):
        out.append(f"{corpus}: this record changes the text on each change's in-force date only; it does not hold "
                   f"{', '.join(missing)}, so the text shown may not be the whole law that applied on {date}.")
    ix_ = _index(corpus) if own else None
    if ix_ is not None and ix_.get('focused'):  # a read of single decisions: the corpus's kinds, read lightly
        ix_ = _light_index(corpus, ROOT / corpus, ix_['pin'])
    odd = ix_['unknown'] if own else set()
    if odd:
        out.append(f"{corpus}: commit kind(s) not recognised, read as laws: {', '.join(sorted(odd))}.")
    return out


def freshness_note(date: str, path: str) -> str:
    """How current the record is for `path` (data/freshness.tsv, and the corpus's own per-act row when it publishes
    one and is checked out), when `date` is on or after the last check against the official source: a later change
    at the source would not be in the record yet. '' for an earlier date, or when there is no freshness data."""
    import freshness
    rows = freshness.read_rows(ROOT)
    row, inner = freshness.corpus_of(path, rows)
    if not row:
        return ''
    act = freshness.act_row(ROOT / row['path'], inner) if row.get('per_act') == 'yes' and inner else None
    last = (act or row).get('last_verified') or ''
    if last and date < last:
        return ''
    return freshness.note(path, root=ROOT)


# Kind words for a version that revises or amends an act already in force: China's Law（修订） (a full revision) and
# 修正 (an amendment). An act whose record starts at such a version was in force before it, so the record starts
# there, as at a publisher's starting text (#17: 50 Chinese acts, 标准化法 and 证券法 among them). Only these: other
# corpora write "amendment" for an amending law kept as its own act (Azerbaijan, 1,025 acts), which starts there.
_REVISION_WORDS = ('修订', '修正')
# The In-force-basis of a version dated by the consolidation that first shows it, not by its law's commencement
# (trinidad-and-tobago-law: "...; a change first shown here took effect on or before it"). An act whose record starts
# at such a version may have been in force before it: 41 Trinidad subsidiary-legislation folders start with an
# amending Act first shown in a Revised Edition or consolidation (27 of them in the 1980 edition as at December 1990).
_FIRST_SHOWN = 'first shown here took effect on or before it'


def _in_force_basis(corpus: str, commit: str) -> str:
    """A commit's In-force-basis trailer, read from the commit itself ('' without one), as read_object reads a file."""
    if not hasattr(subprocess, 'Popen'):
        done = subprocess.run(['git', 'cat-file', 'commit', commit], cwd=corpus_dir(corpus), capture_output=True)
        kind, data = (b'commit', done.stdout) if done.returncode == 0 else (None, None)
    else:
        kind, data = _batch_read(corpus, corpus_dir(corpus), commit)
    if kind != b'commit' or not data:
        return ''
    message = data.decode('utf-8', 'replace').replace('\r\n', '\n').partition('\n\n')[2]
    return trailers(message).get('In-force-basis', '')


def record_floor(path: str) -> dict | None:
    """The version where a file's record starts without the provision starting there, or None: its first version
    when that is a starting text (baseline), or when it came with the first version of its act (the file's folder)
    and that version's Kind names a revision or an amendment (_REVISION_WORDS; the row then has `kind_written`) or
    its In-force-basis says it is dated by the consolidation that first shows it (_FIRST_SHOWN; the row then has
    `in_force_basis`)."""
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
    if first['kind'] != 'law' or not folder:
        return None
    if any(w in raw for w in _REVISION_WORDS):
        extra = {'kind_written': raw}
    else:
        basis = _in_force_basis(corpus, first['commit']) if isinstance(first.get('order'), int) else ''
        if _FIRST_SHOWN not in basis:
            return None
        extra = {'in_force_basis': basis}
    key = ('act-start', f"{corpus}@{_at(ix)}:{folder}")
    if key not in _CACHE:  # the first in-force day of any file of the act
        rows, pre = ix['rows'], folder + '/'
        _CACHE[key] = min((rows[o][5] for f, vs in ix['files'].items() if f.startswith(pre) for o, *_ in vs
                           if rows[o][5] and rows[o][4] != 'documentation'), default=None)
    return dict(first, **extra) if _CACHE[key] == first['in_force'] else None


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


CLOSE_PATHS_ALL = 5_000  # a corpus of up to this many files is searched whole for names like a mistyped one


def _close_paths(rel: str, files) -> list[str]:
    """Up to three names like a path that is not in the record. A small corpus is compared whole, as before. A large
    one is compared where a mistyped path would be: the files of its own folder, or, when the folder itself is not
    there, the files of the folders beside it whose names are like it. Comparing every name took 17 to 25 s for one
    wrong path in France's 812,000 files or Romania's 1.2 million (1.7 s in Ireland's 38,000), on the one thread a
    server answers on."""
    if len(files) <= CLOSE_PATHS_ALL:
        return difflib.get_close_matches(rel, list(files), n=3, cutoff=0.6)
    folder, _, name = rel.rpartition('/')
    pool = [f for f in files if f.startswith(folder + '/')] if folder else [f for f in files if '/' not in f]
    if not pool and folder:
        above, _, last = folder.rpartition('/')
        prefix = above + '/' if above else ''
        beside = {f[len(prefix):].split('/', 1)[0] for f in files if f.startswith(prefix) and '/' in f[len(prefix):]}
        for like in difflib.get_close_matches(last, sorted(beside), n=3, cutoff=0.6):
            pool += [f for f in files if f.startswith(f'{prefix}{like}/')]
    if len(pool) > CLOSE_PATHS_ALL:  # a folder of very many files: those whose names are closest in length first
        pool = sorted(pool, key=lambda f: (abs(len(f) - len(rel)), f))[:CLOSE_PATHS_ALL]
    return difflib.get_close_matches(rel, pool, n=3, cutoff=0.6)


def explain_missing(date: str, path: str) -> str:
    """Why there is no text: a mistyped path, before the record, not yet in force, or repealed."""
    corpus, rel = corpus_of(path)
    files = _index(corpus)['files']
    if rel not in files:
        close = _close_paths(rel, files)
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
                ", the first consolidation to show it, so in force on or before that day (In-force-basis)"
                if floor.get('in_force_basis') else
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
                f", as the corpus's data/acts.json records; " + _end_removal(latest_that_day) + f".{again}"
                + _not_reenacting(latest_that_day))
    return f"{path} was not in force on {date}: it was removed on {gone['in_force']} ({gone['law']}).{again}"


def _end_removal(end_row: dict) -> str:
    """Whether the record itself removes the files of an act data/acts.json ends: a correction deleting them from the
    end day (or later) does (spain-law's repeals, audit row 64); else the end comes from data/acts.json alone."""
    day_ = end_row.get('record_removes')
    if not day_:
        return 'the record did not remove the file itself'
    if day_ == end_row['in_force']:
        return 'the record removes the file from that day'
    return f'the record removes the file from {day_}'


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
    partial = partial_end_note(date, path)
    if partial:
        out.append(partial)
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


USAGE = {'world': 1, 'show': 2, 'blame': 2, 'words': 2, 'today': 2, 'diff': 3, 'log': 1, 'laws': 2, 'caselaw-index': 0}


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


def log_rows(path: str) -> list[dict]:
    """history() in the order the versions took force: by in-force day, then commit order. Rows appended later (a
    Redates:, a version found late, spain-law's same-day restatements) sit at their day, not at the end; on one day
    the later commit stays last, as it wins the day (file_commit), and an act's end row (order + 0.5) stays just
    after the commit that ended it."""
    return sorted(history(path), key=lambda h: (h['in_force'], h['order']))


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
            # The commit's Enacted/Published are the first-credited law's: the corrected law's own, or none.
            row['enacted'], row['published'] = (None, None) if credit_fix[1] else law_dates(corpus, credit_fix[0])
        if fix:
            row.update({'corrects': fix['corrects'], 'until': fix['to'], 'supersedes': fix['supersedes'],
                        'reason': fix['reason']})
        out.append(row)
    seen = {r['commit'] for r in out}
    names = _earlier_names(corpus, rel)  # Files: names the path of its own day, before any layout move
    for order, r in enumerate(rows):
        fix = r[9]
        if fix and r[0] not in seen and any(n in fix['files'] for n in names):
            out.append({'commit': r[0], 'law': r[1], 'in_force': fix['from'], 'kind': 'correction', 'enacted': None,
                        'published': None, 'order': order, 'corrects': fix['corrects'], 'until': fix['to'],
                        'supersedes': fix['supersedes'], 'reason': fix['reason']})
    end = act_end(corpus, rel)
    if end and end['day'] and out:
        commit, order = _end_commit(corpus, end)
        # The act-end rule (after_end): a version dated after the end re-enacts the file only if its law was enacted
        # on or after the end, is not the law that ended the act, and is not a repeal note. A correction is cut at
        # the end too (correction_cap): one starting after it applies only once a later version re-enacted the file.
        kept, dropped, removes = [], [], None
        for h in out:
            deletes = 'blob' in h and h['blob'] is None and not h.get('repeal_notice')
            if h.get('corrects') and deletes and h['in_force'] >= end['day']:
                # A correction that deletes the file from the end day on (spain-law c0980c9: Corrects: <act>
                # <repeal day>..) is the record carrying out the end, not a later version to weigh (audit row 64).
                removes = min(removes or h['in_force'], h['in_force'])
                continue
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
        if removes:
            out[-1]['record_removes'] = removes  # the day a correction deletes the file: the end carried out
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
    whole line once its number is set aside), or None when the corpus turns the rule off (`"repeal_notice": false`).
    Case law has none: a decision is not a repeal notice, and scanning New York's 249,000 appellate decisions for one
    took 44 s (list_provisions of a year's folder, which passed 120 s and so never kept its result)."""
    if is_caselaw({'path': corpus, 'kind': corpus_info(corpus).get('kind')}):
        return None
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
            if folder in out:
                # The scope of the end (audit row 53): the provisions it covers, where the row lists them, else whether
                # the corpus marks it unresolved (spain-law: 350 BOE notes such as "Norma derogada ... excepto los
                # arts. 30 y 32"), and the file holding the publisher's note.
                covers = a.get('lifecycle_repealed_provisions')
                if isinstance(covers, list) and covers:
                    out[folder]['covers'] = [str(c).strip('/') for c in covers if str(c).strip('/')]
                if a.get('lifecycle_scope_unresolved') is True:
                    out[folder]['unresolved'] = True
                if isinstance(a.get('lifecycle_notice'), str) and a['lifecycle_notice'].strip('/'):
                    out[folder]['notice'] = a['lifecycle_notice'].strip('/')
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
    """The end data/acts.json records for the act holding a file (its longest folder), or None. None too where that
    end does not reach the file (partial_end): every reader ends a file through here."""
    e = _act_end_row(corpus, rel)
    return e if e is not None and _end_reaches(e, rel) else None


def _act_end_row(corpus: str, rel: str) -> dict | None:
    ends = act_ends(corpus)
    if not ends:
        return None
    parts = rel.split('/')
    for i in range(len(parts) - 1, 0, -1):
        e = ends.get('/'.join(parts[:i]))
        if e:
            return e
    return None


def _end_reaches(end: dict, rel: str) -> bool:
    """Whether an act's end (act_ends) ends this file: where the row lists the provisions it covers, only those (by
    file or folder, relative to the act); else every file, unless the corpus marks its scope unresolved."""
    inner = rel[len(end['act']) + 1:]
    if end.get('covers') is not None:
        return any(inner == c or inner.startswith(c + '/') for c in end['covers'])
    return not end.get('unresolved')


def partial_end(corpus: str, rel: str) -> dict | None:
    """The end data/acts.json records for a file's act when it does not end this file (_end_reaches), else None."""
    e = _act_end_row(corpus, rel)
    return e if e is not None and not _end_reaches(e, rel) else None


SAVING_WORDS = re.compile(r'\b(?:excepto|salvo|a\s+excepci[oó]n|con\s+la\s+excepci[oó]n|except|save\s+for)\b', re.I)
_MONTHS_ES = {m: n for n, m in enumerate(('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                                          'septiembre', 'octubre', 'noviembre', 'diciembre'), 1)}
EFFECT_DAY_ES = re.compile(r'con\s+efectos?\s+(?:de(?:sde)?\s+)?(?:el\s+)?(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', re.I)


def partial_end_note(date: str, path: str) -> str:
    """What to say of a file whose act data/acts.json ends but whose end does not reach it (partial_end), on a date: the
    end and why the file is not ended, with the publisher's wording of a repeal that saves provisions. From the end's
    day, or an earlier day the wording gives the repeal effect from ("con efectos de 3 de diciembre de 2025" where the
    row has the day the saved part ends). '' before that, or when the end reaches the file."""
    corpus, rel = corpus_of(path)
    end = partial_end(corpus, rel)
    if not end:
        return ''
    wording = ''
    if end.get('notice'):
        text = read_object(corpus, f"{_index(corpus)['pin']}:{end['act']}/{end['notice']}") or ''
        wording = ' '.join(re.sub(r'^[#>\s]+', '', line) for line in text.splitlines()).strip()
        wording = wording if SAVING_WORDS.search(wording) else ''
    if not wording and SAVING_WORDS.search(end['by']):
        wording = end['by']
    wording = wording[:600].rstrip(' .') + ('...' if len(wording) > 600 else '')
    days = [end['day']] if end['day'] else []
    for d, month, year in EFFECT_DAY_ES.findall(wording):
        if month.lower() in _MONTHS_ES:
            iso = f'{year}-{_MONTHS_ES[month.lower()]:02d}-{int(d):02d}'
            if ISO_DAY.fullmatch(iso) and _days(iso, iso) is not None:
                days.append(iso)
    if days and date < min(days):
        return ''
    noun = {'repealed': 'repeal', 'expired': 'expiry', 'annulled': 'annulment'}.get(end['how'], 'end')
    said = (f"{path}: data/acts.json records its act ({end['act']}) as {end['how']}"
            + (f" on {end['day']}" if end['day'] else '') + (f" by {end['by']}" if end['by'] else ''))
    if end.get('covers') is not None:
        return (f"{said}, and lists the provisions that {noun} covers (lifecycle_repealed_provisions); this one is not "
                "among them, so the text is read as the record has it.")
    why = (f"the publisher's note says it saves some provisions: \"{wording}\"" if wording else
           f"it may not cover every provision")
    return (f"{said}, but marks the scope of that {noun} unresolved (lifecycle_scope_unresolved): {why}. The record "
            f"does not say which provisions it ends, so it ends none of them here: the text shown may no longer be in "
            f"force on {date}" + (f" (the {noun} took effect from {min(days)})" if days else '') + '.')


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
# treaty, uncredited (a change no law is named for), end (a version that ends with no successor and no law named:
# France's 5,527 "Fin de vigueur" commits), documentation. A word not listed is read as a law and named in the
# caveats, never silently.
_LAW_KINDS = {'', 'law', 'decree', 'amendment', 'act', 'amending law', 'lov', 'lbk', 'laki', 'ustawa', 'zakon',
              'rozporządzenie', 'legal notice', 'ordinance', 'several', 'enacted', 'original', 'version', 'repeal',
              'asmade', 'as made', 'disallow'}  # Australia's Register: an instrument as made; a disallowance
_START_KINDS = {'baseline', 'consolidated', 'current', 'current-only', 'current-text', 'publisher', 'consolidation',
                'first published version (publisher)', 'tekst jednolity (current text)',
                'start'}  # start: Liechtenstein's oldest version available of an act, the history before it to come
_UNCREDITED_KINDS = {'unexplained', 'change no law explains', 'republication', 'obwieszczenie'}
_COURT_KINDS = {'orzeczenie', 'nález'}  # rulings of the Polish and Slovak constitutional courts
# An end of validity no law is named for: as a Kind:, or as the author and subject of a commit with no Kind (france-law's
# "Fin de vigueur": "These versions end on this day and LEGI gives no successor; no text is credited").
_END_KINDS = {'end', 'end of validity', 'fin de vigueur'}
# Words in the longer Kind values corpora write (Australia, Canada, Hong Kong, Poland, Portugal and others).
_START_WORDS = ('first version in the database', 'oldest version available', 'publisher-text', 'record starts here')
_UNCREDITED_WORDS = ('editorial', 'notes only', 'style only', 'no act named', 'no law named', 'no amending law',
                     'not identified', 'several candidate laws', 'credited to neither', 'no change to the',
                     'without a change', 'no change in the text', 'removed from the consolidation', 'layout',
                     'typesetting', 'reprint', 'reverted',  # reverted: Monaco's earlier text put back, "aucune loi"
                     'unattributed', 'not attributable')  # Australia's Register: a compilation no one instrument made
_CORRECTION_WORDS = ('retificação', 'rectificação', 'ispravak', 'sprostowanie')
_LAW_WORDS = ('law', 'act', 'decree', 'decreto', 'regulation', 'instrument', 'notice', 'order in council', 'lei',
              'zákon', 'zakon', 'закон', 'ustav', 'uredba', 'constitution', 'constituicao', 'конституция',
              'referendum', 'reform', 'amend', 'enact', 'lov', 'lag', 'laki', 'expiry', 'replacement',
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


def law_dates(corpus: str, label: str) -> tuple[str | None, str | None]:
    """(enacted, published) of a law named by its credit label, as the corpus records them, for a credit corrected by
    data/credits.csv (credited): data/laws.csv's row of that label or key (enacted, published), else normas.tsv's
    row of the norm the label starts with (spain-law: fecha_disposicion, fecha_publicacion), else the law's own
    commits (Enacted:/Published: of one it is the author of). (None, None) when the record gives neither: the dates
    of the commit, which are the first-credited law's, are never shown for the corrected one."""
    import csv
    import io
    ix = _index(corpus)
    pin = ix['pin']
    key = ('law-dates', f'{corpus}@{_at(ix)}')
    if key not in _CACHE:
        _CACHE[key] = {'laws': None, 'normas': None, 'commits': None}
    seen = _CACHE[key]
    pick = lambda e, p: (e or None, p or None) if (e or p) else None  # noqa: E731
    if seen['laws'] is None:
        seen['laws'] = {}
        for r in csv.DictReader(io.StringIO(read_object(corpus, f'{pin}:data/laws.csv') or '')):
            dates = pick((r.get('enacted') or '').strip(), (r.get('published') or '').strip())
            for name in {(r.get('label') or '').strip(), (r.get('key') or '').strip()} - {''}:
                if dates:
                    seen['laws'].setdefault(name, dates)
    if label in seen['laws']:
        return seen['laws'][label]
    if seen['normas'] is None:
        seen['normas'] = {}
        lines = (read_object(corpus, f'{pin}:normas.tsv') or '').splitlines()
        cols = lines[0].split('\t') if lines else []
        if 'id' in cols:
            for line in lines[1:]:
                r = dict(zip(cols, line.split('\t')))
                dates = pick((r.get('fecha_disposicion') or '').strip(), (r.get('fecha_publicacion') or '').strip())
                if dates:
                    seen['normas'][r['id']] = dates
    norm = label.split(' ', 1)[0]
    if norm in seen['normas']:
        return seen['normas'][norm]
    if seen['commits'] is None:
        seen['commits'] = {}
        for r in ix['rows']:
            if r[4] != 'documentation' and r[5] and (r[7] or r[8]):
                seen['commits'].setdefault(r[1], (r[7], r[8]))
    return seen['commits'].get(label, (None, None))


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
    if k in _END_KINDS:
        return 'end', None
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
          'court': '{} (court ruling, not a law)', 'treaty': '{} (treaty)', 'uncredited': '{} (no law named for this change)',
          'end': '{} (end of validity; no law named)'}


def credit(author: str, kind: str) -> str:
    """How blame and words credit a version: a law by its name; anything else says what it is."""
    return CREDIT.get(kind, '{}').format(author)


INDEX_VERSION = 11  # raise when what the index keeps changes: old indexes are then rebuilt


def _index_version() -> str:
    """INDEX_VERSION and a fingerprint of the tables a commit's kind is read with: the index keeps each commit's kind,
    so an index built before a Kind word was added kept calling it unknown (Romania's "referendum" note, 3 November
    2026, long after the word was known). A change to the tables now rebuilds the index by itself."""
    import hashlib
    tables = repr([sorted(t) for t in (_LAW_KINDS, _START_KINDS, _UNCREDITED_KINDS, _COURT_KINDS, _END_KINDS)]
                  + [list(t) for t in (_START_WORDS, _UNCREDITED_WORDS, _CORRECTION_WORDS, _LAW_WORDS)] + [MAINTAINER])
    return f'{INDEX_VERSION}-{hashlib.sha256(tables.encode("utf-8")).hexdigest()[:12]}'


def _derive(info: dict, commit: str, author: str, when: str, subject: str, block: str) -> tuple[tuple, str | None]:
    """One commit as the index keeps it: (commit, author, date, subject, kind, in force or None, Kind as written,
    enacted, published, correction or None), and the Kind word when it is not one the tools know."""
    every = trailer_values(block)
    t = {k: v[0] for k, v in every.items()}
    raw = (t.get('Kind') or '').strip()
    kind, unknown = kind_of(raw, author)
    if not raw and author.strip().lower() in _END_KINDS and subject.strip().lower() == author.strip().lower():
        kind = 'end'  # france-law's "Fin de vigueur": versions that end with no successor, credited to no law
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


REDATES = re.compile(r'^Redates:\s*([0-9a-f]{7,40})\s+(?:(enacted)\s+)?(\d{4}-\d{2}-\d{2}|no-date)\s*$', re.M)


def _redate(data: dict, rows: list, block: str) -> None:
    """A dated version's date, corrected by a later commit (corpus standard; an append-only corpus cannot change the
    commit itself). One `Redates: <commit> <YYYY-MM-DD>` trailer per version gives the day it took force;
    `Redates: <commit> no-date` says the source gives none, so the version is text as of its recorded day. With
    `Retroactive: yes; <provision>` the versions took force before their act was made, as that provision says.
    `Redates: <commit> enacted <YYYY-MM-DD>|no-date` corrects the day its law was made instead (the value its
    Enacted/Adopted/Made... trailer gives: ENACTED, the row's `enacted`), or says the record gives none."""
    retro = trailer_lines(block).get('Retroactive', '').strip().lower().startswith('yes')
    for target, field, day in REDATES.findall(block):
        at = data['pos'].get(target) if len(target) == 40 else \
            next((i for c, i in data['pos'].items() if c.startswith(target)), None)
        if at is None:
            continue
        r = rows[at]
        if field:  # enacted
            rows[at] = r[:7] + (None if day == 'no-date' else day,) + r[8:]
            data.setdefault('redated_enacted', {})[r[0]] = (r[7], day)
        elif day == 'no-date':
            if r[4] == 'law':
                rows[at] = r[:4] + ('baseline',) + r[5:]
        else:
            rows[at] = r[:5] + (day,) + r[6:]
            if r[9]:  # an overlay correction (Corrects: <act> <from>..<to>): its text applies from the corrected day
                rows[at] = rows[at][:9] + ({**r[9], 'from': day},)
        if not field:
            data.setdefault('redated', {})[r[0]] = (r[5], day)
        if retro:
            data.setdefault('retroactive', set()).add(r[0])


def _rename_repair(changes: str) -> dict[str, str]:
    """old -> new for the exact renames of a documentation commit that moves folders, re-paired by folder. git pairs
    files of identical text arbitrarily (two acts' identical closing article: argentina-general-villegas-city-law's
    ordenanza-00-2025/art-036.md was paired with ordenanza-6507-2024's new path), which would give one act the
    other's history. Each old folder moves to one new folder, learnt from its files whose text is unique in the commit;
    within a group of identical files each old path then takes the same file name under its folder's new place, and a
    file left over takes the new path left over. {} when every pair already agrees."""
    pairs = []
    for line in changes.splitlines():
        if line.startswith(':') and '\t' in line:
            meta, *ps = line.split('\t')
            m = meta.split()
            if m[4].startswith('R') and len(ps) == 2:
                pairs.append((_unquote(ps[0]), _unquote(ps[1]), m[3]))
    if len(pairs) < 2:
        return {}
    from collections import Counter, defaultdict

    def split(old: str, new: str) -> tuple[str, str, str]:
        a, b = old.split('/'), new.split('/')
        tail = []
        while len(a) > 1 and len(b) > 1 and a[-1] == b[-1]:
            tail.insert(0, a.pop())
            b.pop()
        return '/'.join(a), '/'.join(b), '/'.join(tail)
    by_blob = defaultdict(list)
    for p in pairs:
        by_blob[p[2]].append(p)
    votes: dict[str, Counter] = defaultdict(Counter)
    for old, new, blob in pairs:
        if len(by_blob[blob]) == 1:  # text found once: git had only one way to pair it
            of, nf, _ = split(old, new)
            votes[of][nf] += 1
    target = {of: c.most_common(1)[0][0] for of, c in votes.items()}
    out: dict[str, str] = {}
    for blob, group in by_blob.items():
        if len(group) < 2:
            continue
        news = {new for _, new, _ in group}
        left, given = [], {}
        for old, new, _ in group:
            of, _, tail = split(old, new)
            parts = old.split('/')
            # the old folder: the longest prefix of the old path that has a known target
            want = None
            for i in range(len(parts) - 1, 0, -1):
                f = '/'.join(parts[:i])
                if f in target:
                    want = f'{target[f]}/' + '/'.join(parts[i:])
                    break
            if want in news and want not in given.values():
                given[old] = want
            else:
                left.append((old, new))
        rest = [n for n in sorted(news) if n not in given.values()]
        if len(left) == 1 and len(rest) == 1:
            given[left[0][0]] = rest[0]
        else:
            for old, new in left:  # no better knowledge: git's pairing, if still free
                if new in rest:
                    given[old] = new
                    rest.remove(new)
        for old, new, _ in group:
            if old in given and given[old] != new:
                out[old] = given[old]
    return out


def _extend(corpus: str, cwd: Path, data: dict, revs: str, skip: frozenset = frozenset(),
            paths: tuple = (), keep: bool = False) -> None:
    """Add the commits in `revs` to a corpus index, oldest first: one `git log --raw` for every commit and file.
    Commits in `skip` are left out (a forked future branch's copies of main's commits: _future_index). With `paths`,
    only the commits that touch those files, and only their changes (a case-law decision read on its own:
    _focused_index)."""
    info = corpus_info(corpus)
    fmt = '--format=%x1d%H%x1f%an%x1f%aI%x1f%s%x1f%(trailers:only,unfold)%x1e'
    # keep: the log of two fixed commits (a future branch read beside main, _future_index, in every process) is kept
    # on disk, gzipped: reading Brazil's future branch took 1.1 s of each call (2026-11-08).
    disk = _store() / f'future-log-v1-{_cl_name(corpus)}-{revs.replace("..", "-")}.txt.gz' if keep and not paths and re.fullmatch(r'[0-9a-f]{40}\.\.[0-9a-f]{40}', revs) else None
    raw = None
    if disk is not None and disk.exists():
        import gzip
        try:
            raw = gzip.decompress(disk.read_bytes()).decode('utf-8')
        except (OSError, ValueError, EOFError):
            raw = None
    if raw is None:
        raw = git('log', '--reverse', '--raw', '--find-renames=100%', '--no-abbrev', fmt, revs,
                  *(['--', *paths] if paths else []), cwd=cwd)
        if disk is not None:
            import gzip
            try:
                _write_atomic(disk, gzip.compress(raw.encode('utf-8'), 6))
                for old in sorted(_store().glob(f'future-log-v1-{_cl_name(corpus)}-*.txt.gz'), key=lambda f: f.stat().st_mtime)[:-3]:
                    old.unlink(missing_ok=True)
            except OSError:
                pass
    legacy = None
    rows, files = data['rows'], data['files']
    put_back = dict(data.get('withdrawn_versions') or {})  # path -> the versions a documentation commit withdrew
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
        repair = _rename_repair(changes) if row[4] == 'documentation' else {}
        for line in changes.splitlines():
            if not line.startswith(':') or '\t' not in line:
                continue
            meta, *paths = line.split('\t')
            f = meta.split()
            if f[4].startswith('R') and len(paths) == 2:
                old, new = _unquote(paths[0]), _unquote(paths[1])
                new = repair.get(old, new)
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
            if data['moves'] and path in data['moves'] and row[4] != 'documentation':
                # A law commit read after a documentation commit moved its path (a future branch that forked before
                # a layout move, read over the moved main: japan-law's mishiko): its version is the moved file's.
                seen_ = {path}
                while path in data['moves'] and data['moves'][path] not in seen_:
                    path = data['moves'][path]
                    seen_.add(path)
            if row[4] == 'documentation' and f[4].startswith('D'):
                # Deleted by a commit that is not a law: withdrawn (romania-law's Withdraws:, an act that never
                # belonged). Its versions leave the record on every day; read by in-force day alone, the act stayed
                # in force on every past date. A later law may add the path again.
                put_back[path] = files.pop(path, [])
                data['withdrawn'][path] = commit
                continue
            if row[4] == 'documentation' and path in put_back:
                # Added again by a commit that is not a law: the withdrawal undone (spain-law 645ca52 recorded every
                # file as deleted by mistake, 57854db put them all back): the file keeps its versions.
                files[path] = put_back.pop(path) + files.get(path, [])
                data['withdrawn'].pop(path, None)
            files.setdefault(path, []).append((order, None if f[4].startswith('D') else f[3], f[1]))
    if put_back or data.get('withdrawn_versions'):
        data['withdrawn_versions'] = put_back  # a new dict: a future branch's index never changes main's
    _publisher_changes(info, rows)


def _publisher_changes(info: dict, rows: list) -> None:
    """Audit row 62: a dated commit read as a law whose author is a name the same corpus gives its starting texts or
    its changes no law is named for (or the manifest's publisher) is the publisher's change, not a law: Ireland's
    "Law Reform Commission, Revised Acts" (615 commits), Tasmania, Canada, Sweden, Monaco, Nauru. Read as uncredited."""
    names = {r[1] for r in rows if r[4] in ('baseline', 'uncredited')}
    publisher = str(info.get('publisher') or '').strip().lower()
    for i, r in enumerate(rows):
        if r[4] == 'law' and r[5] and (r[1] in names or (publisher and r[1].strip().lower() == publisher)):
            rows[i] = r[:4] + ('uncredited',) + r[5:]


INDEX_SEEN_S = 2.0  # how long _main_index answers without looking at the corpus again (as a server's _look does)
_INDEX_SEEN: dict = {}


def _main_index(corpus: str) -> dict:
    """The corpus read once at the commit the tree pins: every commit (rows, in history order) and every version of
    every file (files: path -> [(row, blob or None for a deletion, mode)]). Kept on disk in the tree's git folder
    (global-law-cache), keyed by the pin: a pin that moved forward adds only the new commits, so after the first read
    a corpus costs one file load, not a walk of its history."""
    # Asked again within INDEX_SEEN_S of an answer, at the same HEAD, the index in hand is given without looking at
    # the corpus's folder and pin again. Those looks are 36 microseconds, and a tree of a corpus with many corrections
    # asks 12 million times (act_ends for every file under every correction): Japan's acts took 500 s to build a
    # day's tree in a fresh process, 450 s of them here.
    import time
    now, head = time.monotonic(), _head()
    seen = _INDEX_SEEN.get(corpus)
    if seen is not None and now - seen[0] < INDEX_SEEN_S and seen[1] == head:
        got = _CACHE.get(seen[2])
        if got is not None:
            return got  # type: ignore[return-value]
    cwd = corpus_dir(corpus)
    sha = tip(corpus)
    if not sha:
        raise SystemExit(f'{corpus} is not pinned in this tree')
    key = ('index', f'{corpus}@{sha}')
    if key in _CACHE:
        _INDEX_SEEN[corpus] = (now, head, key)
        return _CACHE[key]  # type: ignore[return-value]
    focused = _focused_index(corpus, cwd, sha)
    if focused is not None:
        return focused
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


class _Focus(threading.local):
    """corpus -> the files a call reads (focus()), for the thread that set it: a reader that answers several calls at
    once (the MCP server under a host) must not see, or pop, another call's focus. A thread that works for a focused
    call takes the focus with it (carry())."""

    def __init__(self):
        self.by: dict[str, tuple[str, ...]] = {}

    def get(self, corpus, default=None):
        return self.by.get(corpus, default)

    def pop(self, corpus, default=None):
        return self.by.pop(corpus, default)

    def __setitem__(self, corpus, rels) -> None:
        self.by[corpus] = rels


_FOCUS = _Focus()
carry_more = None  # set by a reader (the MCP server): fn -> fn, called in the thread that hands the work out


def carry(fn):
    """fn to run in another thread (a pool worker) as part of this thread's work: with this thread's focus, and with
    whatever a reader adds through `carry_more` (the MCP server: its call's deadline and cancel event, so the git
    commands the worker starts stop with the call)."""
    by = dict(_FOCUS.by)
    if carry_more is not None:
        fn = carry_more(fn)

    def run(*a, **k):
        old = _FOCUS.by
        _FOCUS.by = dict(by)
        try:
            return fn(*a, **k)
        finally:
            _FOCUS.by = old
    return run


class focus:
    """`with focus(path, ...):` a read of single files. For a case-law corpus whose index is not built yet, the reads
    inside use an index of just those files' commits (_focused_index) instead of the whole corpus's: one decision
    is one file and usually one commit, while the corpus index walks every decision (the Cour de cassation's 530k
    commits took ~100 s cold, past the assistant tools' 120 s limit once the rest of a call was added; 2026-11-06).
    Laws are not affected: their reads need every commit (Redates:, restatements, act ends)."""

    def __init__(self, *paths: str):
        self.by = {}
        for p in paths:
            try:
                corpus, rel = corpus_of(p)
            except (SystemExit, Exception):
                continue
            self.by.setdefault(corpus, []).append(rel)
        self.saved = {}

    def __enter__(self):
        for corpus, rels in self.by.items():
            self.saved[corpus] = _FOCUS.get(corpus)
            _FOCUS[corpus] = tuple(sorted(set(rels)))
        return self

    def __exit__(self, *exc):
        for corpus, old in self.saved.items():
            if old is None:
                _FOCUS.pop(corpus, None)
            else:
                _FOCUS[corpus] = old
        return False


def _focused_index(corpus: str, cwd: Path, sha: str) -> dict | None:
    """The index of only the focused files of a case-law corpus (focus()), when its whole index is not on disk for
    this pin yet; None otherwise (the whole index is then read or built as before). Same shape as _main_index's, its
    rows only the commits that touch those files, in history order, so each file's versions, kinds and dates read the
    same; kept in memory only, never written as the corpus's index."""
    rels = _FOCUS.get(corpus)
    if not rels:
        return None
    try:
        info = corpus_info(corpus)
    except Exception:
        return None
    if not is_caselaw({'path': corpus, **info}):
        return None
    name = corpus.replace('/', '~')
    store = _store()
    if (store / f'{name}.v{INDEX_VERSION}.{sha[:12]}.index').is_file():
        return None  # built already: one file load, and it holds everything
    key = ('index-focus', f'{corpus}@{sha}:{"|".join(rels)}')
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]
    if not _has_commit(corpus, cwd, sha):
        return None
    # 'at' keys every cache built from this index (_at), so nothing derived from a few files is later taken for the
    # whole corpus by a long-running reader (the assistant server).
    data = {'v': _index_version(), 'pin': sha, 'rows': [], 'files': {}, 'unknown': set(), 'moves': {}, 'withdrawn': {},
            'restates': {}, 'pos': {}, 'retroactive': set(), 'focused': rels,
            'at': f'{sha}~focus:{"|".join(rels)}'}
    _extend(corpus, cwd, data, sha, paths=rels)
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
            if (f.suffix == '.tmp' and age > 3600) or (f.suffix in ('.index', '.pickle', '.light') and (
                    this_version or not f.name.startswith(f'{name}.v') or age > 7 * 86400)):
                f.unlink()
        except OSError:
            pass


def _forget_other_pins(corpus: str, sha: str) -> None:
    """Drop what this process keeps for earlier pins of a corpus (a long-running reader, such as the MCP server, sees
    pins move several times an hour; each index of a large corpus holds hundreds of MB)."""
    mine = f'{corpus}@'
    for k in [k for k in list(_CACHE) if len(k) == 2 and isinstance(k[1], str) and k[1].startswith(mine)
              and not k[1].startswith(mine + sha)]:
        v = _CACHE.pop(k, None)
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
    """Why a corpus's future branch is not read, or not all of it, though the tree records it: the row was made for an
    earlier pin (the pin moved and data/future-pins.tsv was not written again with it), the checkout lacks the
    commit, a commit there only looks like a copy of a law on main (diverged), or the branch is behind main and some
    of its commits were made on text main has changed since (_unread). Then the reader shows main's text for those,
    and the note names the laws on the branch already in force that are not read, and how many. None when it is all
    read."""
    fp = future_pins().get(corpus)
    pin = tip(corpus)
    cwd = ROOT / corpus
    if not fp or not pin or not (cwd / '.git').exists() or not _readable(corpus, cwd):
        return None
    branch, fut, main_pin = fp
    if main_pin != pin:
        due = _future_due(corpus, pin, fut, None) if _has_commit(corpus, cwd, fut) else ''
        return (f"{corpus}: laws with a later in-force day are kept on its {branch} branch, but data/future-pins.tsv "
                f"records that branch for an earlier pin ({main_pin[:10]}, not {pin[:10]}), so it is not read: changes "
                "that took force after the last law on main may be missing until the file is written again."
                + (f" {due}" if due else ''))
    if not _has_commit(corpus, cwd, fut):
        return (f"{corpus}: laws with a later in-force day are kept on its {branch} branch ({fut[:10]}), which this "
                "checkout does not have, so changes that took force after the last law on main may be missing. "
                f"Run: git -C {corpus} fetch origin {branch}  (if the branch has moved on since: git -C {corpus} "
                f"fetch origin refs/tags/global-law/future-pinned-{fut})")
    check = _future_check(corpus, corpus_dir(corpus), pin, fut)
    diverged = check['diverged']
    if diverged:
        due = _future_due(corpus, pin, fut, None)
        return (f"{corpus}: laws with a later in-force day are kept on its {branch} branch ({fut[:10]}), but "
                f"{len(diverged)} commit(s) there carry the author, date and message of a law on main and change "
                f"different text (first: {diverged[0][:10]}), so the branch is not read: main alone is shown, and "
                "changes that took force after the last law on main may be missing until the branch is rebuilt."
                + (f" {due}" if due else ''))
    if check['unread']:
        due = _future_due(corpus, pin, fut, set(check['unread']))
        if due:
            return (f"{corpus}: its {branch} branch ({fut[:10]}) is behind main: some of its laws were made on text "
                    "main has changed since, and are not read, as read they would undo main's change; main's text is "
                    f"shown for them until the branch is rebuilt. {due}")
    return None


def _future_due(corpus: str, pin: str, fut: str, only: set | None) -> str:
    """'N change(s) in force by <today> ... not read: <day> <subject>; ...' for the commits of pin..fut that are not
    read (`only`, or else every one but the copies of main's laws) whose in-force day has come; '' if none has."""
    cwd = corpus_dir(corpus)
    skip = _future_check(corpus, cwd, pin, fut)['skip'] if only is None else frozenset()
    trailer = corpus_info(corpus).get('in_force_trailer') or 'In-force'
    import datetime as dt
    today = dt.date.today().isoformat()
    due = []
    for line in git('log', '--reverse', f'--format=%H%x1f%(trailers:key={trailer},valueonly,separator=)%x1f%s',
                    f'{pin}..{fut}', cwd=cwd).splitlines():
        sha, day, subject = (line.split('', 2) + ['', ''])[:3]
        day = day.strip()[:10]
        if (sha in only if only is not None else sha not in skip) and ISO_DAY.match(day) and day <= today:
            due.append(f'{day} {subject.strip()} ({sha[:10]})')
    if not due:
        return ''
    more = f' (and {len(due) - 5} more)' if len(due) > 5 else ''
    return (f"{len(due)} change(s) in force by {today} are on that branch and not read: "
            + '; '.join(due[:5]) + more + '.')


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


def _blobs_at(cwd: Path, sha: str, paths) -> dict[str, str] | None:
    """{path: blob id} in a commit's tree for those of `paths` it has (trees only, git ls-tree); None if git fails."""
    have: dict[str, str] = {}
    paths = sorted(set(paths))
    for i in range(0, len(paths), 200):  # keep the command line short
        out = subprocess.run(['git', '--literal-pathspecs', 'ls-tree', '-r', '-z', '--full-tree', sha, '--',
                              *paths[i:i + 200]], cwd=cwd, capture_output=True)
        if out.returncode:
            return None
        for entry in out.stdout.decode('utf-8', 'replace').split('\0'):
            meta, _, path = entry.partition('\t')
            if path:
                have[path] = meta.split()[2]
    return have


def _holds(cwd: Path, sha: str, change: frozenset) -> bool:
    """Whether a commit's tree has each path of `change` (another commit's _tree_changes) at that commit's blob, or
    lacks it where that commit deletes it: the commit carries the other's change, though it may change more, or have
    had the same text already. Trees only (git ls-tree), never blobs."""
    want = {path: blob for path, _, blob in change}
    have = _blobs_at(cwd, sha, want)
    if have is None:
        return False
    return all(have.get(path, ZERO_SHA) == blob for path, blob in want.items())


def _replays(cwd: Path, pin: str, fut: str, trailer: str = 'In-force') -> tuple[frozenset, tuple]:
    """Commits of pin..fut that copy a main commit made after the fork: a forked future branch replays main's laws so
    that it reads whole on its own; read beside main they would be doubles. A copy has the main commit's author line,
    raw date and message, and leaves each path the main commit changes at the main commit's blob (the same change,
    or text the branch had already; a file more written or removed on the branch is left out with the copy).
    Returns (copies, diverged): diverged are the commits with a main commit's author, date and message whose tree
    holds other text at a path that commit changes (a "copy" which, read on, would undo main's change): the caller
    does not read such a branch. Such a commit followed on the branch by a true copy of the same main commit (the
    branch's own earlier version of a law that main published later, then replayed by append_future.py) is
    superseded: it is left out with the copies, so main's text stands. So is a branch commit of its own (another
    message) whose every change main already holds at the pin, each made by a main commit after the fork with the
    same in-force day: the branch's earlier build of a law main has since published (audit row 59, Czechia)."""
    fork = git('merge-base', pin, fut, cwd=cwd).strip()
    fmt = f'--format=%x1d%H%x1f%an <%ae> %ad%x1f%(trailers:key={trailer},valueonly,separator=)%x1f%B'

    def keyed(*revs: str) -> dict:
        out = {}
        for chunk in git('log', '--date=raw', fmt, *revs, cwd=cwd).split('\x1d')[1:]:
            sha, author, day, body = chunk.split('\x1f', 3)
            out[sha] = ((author, body.strip()), day.strip()[:10])
        return out
    main_after = keyed(pin, f'^{fork}') if fork else {}
    branch = keyed(fut, f'^{pin}')
    on_main: dict[tuple, list[str]] = {}
    for sha, (k, _) in main_after.items():
        on_main.setdefault(k, []).append(sha)
    candidates = {sha: on_main[k] for sha, (k, _) in branch.items() if k in on_main}
    changed = _tree_changes(cwd, [*candidates, *(m for ms in candidates.values() for m in ms)])
    copies = frozenset(sha for sha, ms in candidates.items()
                       if any(changed.get(sha) == changed.get(m) for m in ms)  # the same change: no more to ask
                       or any(_holds(cwd, sha, changed.get(m, frozenset())) for m in ms))
    superseded = frozenset(
        sha for sha in candidates if sha not in copies
        and any(c != sha and set(candidates[c]) & set(candidates[sha])
                and subprocess.run(['git', 'merge-base', '--is-ancestor', sha, c], cwd=cwd).returncode == 0
                for c in copies))
    published = frozenset(_published(cwd, pin, main_after, {s: v for s, v in branch.items() if s not in candidates}))
    return (copies | superseded | published,
            tuple(sha for sha in candidates if sha not in copies and sha not in superseded))


def _published(cwd: Path, pin: str, main_after: dict, own: dict) -> list[str]:
    """Branch commits of their own (`own`: sha -> (key, in-force day)) that main has since published under another
    message: every path the commit changes is at the commit's blob in the pin's tree (absent, for a deletion), and a
    main commit after the fork (`main_after`, the same shape) makes that very change with the same in-force day.
    Read beside main they would log and list main's law a second time; main alone gives the same text."""
    dated = {s: d for s, (_, d) in own.items() if ISO_DAY.match(d)}
    if not dated or not main_after:
        return []
    made: dict[tuple, set] = {}
    for sha, ch in _tree_changes(cwd, list(main_after)).items():
        for path, _, blob in ch:
            made.setdefault((path, blob), set()).add(main_after[sha][1])
    return [sha for sha, ch in _tree_changes(cwd, list(dated)).items()
            if ch and all(dated[sha] in made.get((path, blob), ()) for path, _, blob in ch) and _holds(cwd, pin, ch)]


def _unread(cwd: Path, pin: str, fut: str, skip: frozenset) -> tuple:
    """Commits of a forked branch (pin..fut, less `skip`) that are not read beside main because they were made on
    text main has since changed (a branch behind main: its builder has not replayed main's later laws), so that read,
    they would undo main's change. A commit is read only if, at each path it changes, the text it starts from (its
    parent's blob, or none) or the text it leaves is one the merged reading holds there: main's at the pin, or one a
    branch commit read before it left. Its version is then main's text with the branch's change made to it, or a text
    the reading has already (Czechia's own build of 199/2026 leaves main's text of the act and amends two others); a
    later commit at the same path that starts from an unread one's text is not read either."""
    seq = []
    for chunk in git('log', '--reverse', '--raw', '--no-renames', '--no-abbrev', '--format=%x1d%H', f'{pin}..{fut}',
                     cwd=cwd).split('\x1d')[1:]:
        sha, *lines = chunk.strip().split('\n')
        ch = []
        for line in lines:
            if line.startswith(':') and '\t' in line:
                meta, _, path = line.partition('\t')
                f = meta.split()
                ch.append((_unquote(path), f[2], f[3]))
        seq.append((sha.strip(), ch))
    paths = {p for sha, ch in seq if sha not in skip for p, _, _ in ch}
    at_pin = _blobs_at(cwd, pin, paths) if paths else {}
    if at_pin is None:
        return tuple(sha for sha, _ in seq if sha not in skip)
    allowed = {p: {at_pin.get(p, ZERO_SHA)} for p in paths}
    unread = []
    for sha, ch in seq:
        if sha in skip:
            continue
        if all(old in allowed[p] or new in allowed[p] for p, old, new in ch):
            for p, _, new in ch:
                allowed[p].add(new)
        else:
            unread.append(sha)
    return tuple(unread)


def _future_check(corpus: str, cwd: Path, pin: str, fut: str) -> dict:
    """Whether a recorded future commit descends from the pin (linear), and if not, which of its commits are copies
    of main's (skipped when read) and which only look like copies (diverged: the branch is not read). Once a process,
    and only once the checkout has the commit."""
    key = ('future-check', f'{corpus}@{pin}+{fut}')
    if key not in _CACHE:
        # Kept on disk too, keyed by both commits (a check of two fixed commits never changes): read in every fresh
        # process it cost 1.4 s a call on Swiss law and 9 s on law.py world with three forked branches (2026-11-07).
        trailer = corpus_info(corpus).get('in_force_trailer') or 'In-force'
        disk = _store() / f'future-check-v1-{_cl_name(corpus)}-{pin[:16]}-{fut[:16]}-{trailer}.json'
        got = None
        try:
            raw = json.loads(disk.read_text(encoding='utf-8'))
            if raw.get('pin') == pin and raw.get('fut') == fut:
                got = {'linear': bool(raw['linear']), 'skip': frozenset(raw['skip']), 'diverged': tuple(raw['diverged']),
                       'unread': tuple(raw['unread'])}
        except (OSError, ValueError, KeyError, TypeError):
            got = None
        if got is None:
            linear = subprocess.run(['git', 'merge-base', '--is-ancestor', pin, fut], cwd=cwd,
                                    capture_output=True).returncode == 0
            skip, diverged = (frozenset(), ()) if linear else _replays(cwd, pin, fut, trailer)
            unread = () if linear or diverged else _unread(cwd, pin, fut, skip)
            got = {'linear': linear, 'skip': skip, 'diverged': diverged, 'unread': unread}
            try:
                _write_atomic(disk, json.dumps({'pin': pin, 'fut': fut, 'linear': linear, 'skip': sorted(skip),
                                                'diverged': list(diverged), 'unread': list(unread)}).encode('utf-8'))
            except (OSError, TypeError):
                pass
        _CACHE[key] = got
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
        for k in [k for k in list(_CACHE) if len(k) == 2 and isinstance(k[1], str) and k[1].startswith(mine)
                  and not k[1].startswith(mine + fut)]:
            _CACHE.pop(k, None)
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
    for k in [k for k in list(_CACHE) if len(k) == 2 and isinstance(k[1], str)
              and (k[0] == 'timeline' or (k[1].startswith(at) and not k[1].startswith(at + '+')
                                          and k != ('index', at)))]:
        _CACHE.pop(k, None)
    _CACHE.pop(('index', f'{at}+{fut}'), None)
    _CACHE.pop(('future-missing', f'{at}+{fut}'), None)


def recheck_missing_futures() -> bool:
    """For readers of every corpus at once (timeline), which do not go through _index on a cache hit, and for the
    MCP server's own caches: whether any recorded future commit the checkout lacked when it was last read is there
    now (its main-only caches are then dropped). One line to each such corpus's batch reader."""
    arrived = False
    for k in [k for k in list(_CACHE) if k[0] == 'future-missing']:
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
    linear, skip = check['linear'], check['skip'] | frozenset(check['unread'])
    over = dict(data)
    over['rows'] = list(data['rows'])
    over['files'] = _FilesOver(data['files'])
    for k in ('unknown', 'moves', 'withdrawn', 'restates', 'pos', 'retroactive', 'redated', 'redated_enacted'):
        if k in data:
            over[k] = type(data[k])(data[k])
    before = len(over['rows'])
    _extend(corpus, cwd, over, f'{pin}..{fut}', skip=skip, keep=True)
    over['at'] = f'{pin}+{fut}'
    over['future'] = {'branch': branch, 'sha': fut, 'linear': linear, 'commits': len(over['rows']) - before,
                      'replays_skipped': len(check['skip']), 'unread': len(check['unread'])}
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
        # The pieces are read with seek() then read() on the one file: two threads reading at once took each other's
        # place in it (UnpicklingError, EOFError "Ran out of input"). One reader at a time.
        self._reading = threading.Lock()

    def close(self) -> None:
        if self._f in _OPEN_INDEXES:
            _OPEN_INDEXES.remove(self._f)
        self._f.close()

    def _read(self, at: int, n: int) -> bytes:
        """`n` bytes of the file from `at` (fewer at its end). Where the system has pread the file's own position is
        left alone: it belongs to the open file, which a process forked from this one shares, so a seek() here and a
        read() there would take each other's place as two threads once did."""
        import os
        pread = getattr(os, 'pread', None)
        if pread is None:  # Windows
            self._f.seek(at)
            return self._f.read(n)
        fd, parts, got = self._f.fileno(), [], 0
        while got < n:
            part = pread(fd, n - got, at + got)
            if not part:
                break
            parts.append(part)
            got += len(part)
        return parts[0] if len(parts) == 1 else b''.join(parts)

    def _piece(self, i: int) -> dict:
        if i not in self._shards:
            with self._reading:
                if i not in self._shards:
                    at, n = self._offsets[i]
                    raw = self._read(at, n)
                    if len(raw) != n:
                        raise OSError(f'{self._path}: index cut short')
                    self._shards[i] = _unpickle(raw)
        return self._shards[i][0]

    def _all(self) -> list[tuple[str, list]]:
        """Every (path, versions), in the order they were indexed."""
        if self._ordered is None:
            with self._reading:
                if self._ordered is None:
                    self._ordered = self._all_read()
        return self._ordered

    def _all_read(self) -> list[tuple[str, list]]:
        if len(self._shards) < len(self._offsets):
            for i, (at, n) in enumerate(self._offsets):
                if i not in self._shards:
                    self._shards[i] = _unpickle(self._read(at, n))
        placed: list = [None] * sum(len(self._shards[i][1]) for i in self._shards)
        for files, places in self._shards.values():
            for kv, at in zip(files.items(), places):
                placed[at] = kv
        return placed

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
        if sha and len(sha) == 40 and sha == _head_from_files(cwd):
            # The commit the checkout is at, read from its .git files: there, without a git process. Asking each of
            # 170 case-law corpora's readers on every call made a call's cost grow with the number of corpora.
            _CACHE[key] = True
        elif hasattr(subprocess, 'Popen'):
            _CACHE[key] = _batch_read(corpus, cwd, f'{sha}^{{commit}}')[0] == b'commit'
        else:
            _CACHE[key] = subprocess.run(['git', 'cat-file', '-e', f'{sha}^{{commit}}'], cwd=cwd,
                                         capture_output=True).returncode == 0
    return bool(_CACHE[key])


def read_object(corpus: str, spec: str) -> str | None:
    """A file's text by blob id or <commit>:<path>, or None. One long-lived `git cat-file --batch` per corpus, so
    reading many files costs no process each; where processes can only be run one at a time, one `git cat-file`."""
    # A blob id, or a full commit id and a path, names one text for ever: kept in the store once read, so a call that
    # reads a few versions from several corpora starts no reader for them (check_precedent on art. 22¹ k.p.: 12 reads,
    # 0.5 s of its 1.1 s, Poland speed gate 2026-11-09).
    kept = None
    if _HEX40.fullmatch(spec) or _COMMIT_PATH.fullmatch(spec):
        import hashlib
        name = spec if ':' not in spec else hashlib.sha1(spec.encode('utf-8')).hexdigest() + '.at'
        kept = _store() / 'blobs' / name[:2] / name
        try:
            return kept.read_bytes().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
        except OSError:
            pass
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
    if kept is not None and len(data) <= BLOB_CACHE_MAX:
        try:
            import os
            kept.parent.mkdir(parents=True, exist_ok=True)
            tmp = kept.with_name(f'{kept.name}.{os.getpid()}.tmp')
            tmp.write_bytes(data)
            os.replace(tmp, kept)
        except OSError:
            pass
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
    for k in [k for k in list(_CACHE) if k[0] == 'index']:
        _CACHE.pop(k, None)


def read_version(path: str, commit: str) -> str | None:
    """The text a version of a file gives (None for a version that deletes it)."""
    if not commit:
        return None
    corpus, rel = corpus_of(path)
    row = next((h for h in reversed(history(path)) if h['commit'] == commit and 'blob' in h), None)
    if row is not None:
        return read_object(corpus, row['blob']) if row['blob'] else None
    found = read_object(corpus, f'{commit}:{rel}')
    if found is None:  # a version from before a layout move: the file had its earlier name at that commit
        for name in sorted(_earlier_names(corpus, rel) - {rel}):
            found = read_object(corpus, f'{commit}:{name}')
            if found is not None:
                break
    return found


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
    if last is not None and last['kind'] == 'correction' and not last.get('restates'):
        # A Kind: correction commit carries the In-force day of the version it corrects (the US case-law repos'
        # 99,364 corrections: a decision's text redone from CAP's head matter, a court renamed), so it wins that day;
        # stepping only to it credited every line of the opinion to the correction. The day's earlier versions come
        # first, in commit order, so the correction is credited only with the lines it changed.
        return [h['commit'] for h in hist
                if h['in_force'] == day and h['order'] < last['order'] and h.get('blob') and not h.get('corrects')
                and not h.get('ends') and not h.get('repeal_notice')]
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
        # "<some kind of act> are metadata only" names a part of a record with text, not the record (romania's README:
        # "decisions about criminal matters are metadata only" put the catalogue note on every Civil Code article).
        _CACHE[key] = bool(re.search(r'(?<!are )metadata only|no law text|catalogue only', text, re.I))
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
    at = {'show': 1, 'blame': 1, 'words': 1, 'today': 1, 'log': 0, 'diff': 2}.get(command)
    with focus(args[at]) if at is not None else focus():  # one file read: a decision needs no whole-corpus index
        _run(command, args)


def _run(command: str, args: list[str]) -> None:
    note = lambda lines: [print(f'Note: {line}', file=sys.stderr) for line in lines]  # noqa: E731
    if command == 'caselaw-index':
        import time
        t = time.time()
        idx = caselaw_index('yes')
        n = len(idx['corpora']) if idx else 0
        print(f'case-law index: {n} corpora' + (f" ({idx['hash']})" if idx else ' (no case law checked out)') + f', {time.time() - t:.1f} s')
        return
    if command == 'world':
        events = timeline()
        print(f'The law on {args[0]}' + ('' if root_on(args[0], events) else ' (nothing in force yet)') + ':')
        by_corpus: dict[str, list[Event]] = {}
        for e in events:  # once, not once per corpus: the timeline holds every corpus's commits
            by_corpus.setdefault(e.corpus, []).append(e)
        # Case law is not in the timeline: its latest decisions from the case-law index (caselaw_index), else one git log
        # per corpus (latest_decision), eight at a time.
        cases = [c['path'] for c in manifest()['corpora'] if is_caselaw(c) and (ROOT / c['path'] / '.git').exists()]
        decided = latest_decisions(args[0], cases)
        for corpus in manifest()['corpora']:
            own = by_corpus.get(corpus['path'], [])
            last = [e for e in own if e.in_force <= args[0] and e.kind not in ('documentation', 'end')]
            state = (f'{last[-1].law}, in force {last[-1].in_force}' if last else 'not yet in the record') \
                if (ROOT / corpus['path'] / '.git').exists() else 'not checked out'
            if corpus['path'] in decided:
                given = decided[corpus['path']]
                state = f'{given[0]} (latest decision), given {given[1]}' if given else 'no decision yet in the record'
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
        for h in log_rows(args[0]):
            dates = '; '.join(f'{k} {h[k]}' for k in ('enacted', 'published') if h[k])
            label = {'baseline': 'version of', 'correction': 'corrected', 'printing': 'printed'}.get(h.get('kind'), 'in force')
            if 'blob' in h and h['blob'] is None and h.get('kind') != 'correction':
                label = 'ended'  # the version that removes the provision: its end, not a text in force
            if h.get('ends'):
                label = h['ends']
            if h.get('repeal_notice'):
                label = 'repealed'
            who = credit(h['law'], h['kind']) if h.get('kind') in ('uncredited', 'end') else h['law']
            print(f"{label} {h['in_force']}  {who}" + (f'  ({dates})' if dates else '')
                  + (f"  [repeal notice: {h['repeal_notice']}]" if h.get('repeal_notice') else '')
                  + (f"  [act {h['act']}, from data/acts.json; {_end_removal(h)}]" if h.get('record_removes') else
                     f"  [act {h['act']}, from data/acts.json]" if h.get('ends') else '')
                  + (f"  [not re-enacted by: {'; '.join(h['not_reenacting'])}]" if h.get('not_reenacting') else '')
                  + (f"  [date doubtful: {h['date_doubtful']}]" if h.get('date_doubtful') else ''))
        note(n for n in [partial_end_note(day('today'), args[0])] if n)
    elif command == 'laws':
        if args[0] > args[1]:
            args[0], args[1] = args[1], args[0]
        name = args[2] if len(args) > 2 else ''
        # Only laws taking effect: starting texts (the text as a publisher gave it on the day it was read), corrections,
        # printings, court rulings, treaties and changes no law is named for are not laws taking effect that day.
        left_out: dict[str, int] = {}
        # Only the corpora the prefix takes in are read, not every corpus checked out.
        # A name takes in what countries.py and the MCP tools take in: a country, state, city, ISO code or old path.
        chosen = {c['path'] for c in manifest()['corpora'] if (not name and not is_caselaw(c)) or (name and takes_in(c, name))}
        decisions = bool(chosen) and all(is_caselaw(c) for c in manifest()['corpora'] if c['path'] in chosen)
        if name and not chosen:
            import difflib
            folders = sorted({c['path'].split('/')[0] for c in manifest()['corpora']}
                             | {c['path'].split('/')[1] for c in manifest()['corpora'] if c['path'].count('/') >= 2}
                             - GENERIC_LEVELS)
            near = difflib.get_close_matches(name.strip().lower().replace(' ', '-'), folders, n=3)
            raise SystemExit(f'No body of law in this tree matches {name!r}.' + (f" Did you mean {', '.join(near)}?" if near
                             else '') + f' {countries_cmd()} lists them.')
        # A name whose corpora are not checked out (the usual state after `countries.py add` of other countries) has
        # no law to list: say so, as show does, rather than an empty list that reads as "no law took force".
        absent = sorted(c for c in chosen if not (ROOT / c / '.git').exists()) if name else []
        events = sorted((e for c in chosen for e in law_events(c)), key=lambda e: e.in_force) if name else timeline()
        for e in events:
            if args[0] <= e.in_force <= args[1] and e.corpus in chosen and e.kind != 'documentation':
                if decisions and e.kind == 'court':  # a case-law name: the decisions given in the window
                    print(f'{e.in_force}  {e.corpus:<24} {e.law} (court decision)')
                elif e.kind == 'law':
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
                 'uncredited': 'changes no law is named for',
                 'end': 'ends of validity no law is named for (versions that end with no successor)'}
        note(f'not listed, as they are not laws taking effect: {n} {names.get(k, k)}' for k, n in sorted(left_out.items()))
        skipped = sorted(c['path'] for c in manifest()['corpora'] if is_caselaw(c) and c['path'] not in chosen
                         and (not name or matches(c, name)))
        note([f"case law is not listed (court decisions, not laws): {', '.join(skipped)}; name it to list its "
              f"decisions, e.g. laws {args[0]} {args[1]} {skipped[0].rsplit('/caselaw', 1)[0]}/caselaw"] if skipped else [])
        note(n for n in (future_note(c) for c in sorted(chosen)) if n)
        note(_UNREADABLE.format(corpus=c) for c in unreadable() if c in chosen)
        note(_BEHIND.format(corpus=c, pin=p[:10]) for c, p in sorted(behind().items()) if c in chosen)
        note(_SHALLOW.format(corpus=c) for c in shallow() if c in chosen)
        note(f'{c} is not checked out, so its laws are not listed; run: {countries_cmd()} add {c}' for c in absent)
        if absent and len(absent) == len(chosen):
            raise SystemExit(f'No body of law matching {name!r} is checked out here, so no law can be listed.')
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
