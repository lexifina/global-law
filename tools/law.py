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
        _CACHE[key] = json.loads(git('show', 'HEAD:manifest.json'))
    return _CACHE[key]  # type: ignore[return-value]


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
    paragraphs = [p for p in re.split(r'\n\s*\n', body.strip()) if p.strip()]
    for para in reversed(paragraphs):
        lines = [l for l in para.splitlines() if l.strip()]
        found = [_TRAILER.match(l) for l in lines]
        if lines and sum(1 for m in found if m) >= max(1, len(lines) // 2):
            out: dict[str, list[str]] = {}
            for m in found:
                if m:
                    out.setdefault(m.group(1), []).append(m.group(2).strip())
            return out
    return {}


def trailers(body: str) -> dict[str, str]:
    """The first value of each trailer; trailers_all() keeps every value."""
    return {k: v[0] for k, v in trailers_all(body).items()}


def timeline() -> list[Event]:
    """Root commits that move a corpus, oldest first (first parent only). Parsed once per HEAD: with thousands of
    root commits this is the slow part of every read, and a long-running caller (the MCP server) still sees a new
    commit, because the cache is keyed by HEAD."""
    key = ('timeline', _head())
    if key not in _CACHE:
        _CACHE[key] = _timeline()
    return list(_CACHE[key])  # type: ignore[arg-type]


def _timeline() -> list[Event]:
    raw = git('log', '--first-parent', '--reverse', '--format=%H%x1f%s%x1f%B%x1e')
    events = []
    for record in raw.split('\x1e'):
        if not record.strip():
            continue
        commit, subject, body = record.strip('\n').split('\x1f', 2)
        t = trailers(body)
        if 'Corpus' in t:
            kind = t.get('Kind', 'law')
            if t.get('Law', '') == 'Lexifina':
                kind = 'documentation'  # a corpus's own docs commit; builds before 2026-10-29 filed some as laws
            events.append(Event(commit, t['Corpus'], t['Corpus-commit'], t.get('Law', ''), t['In-force'], kind, subject))
    return events


def root_on(date: str, events: list[Event] | None = None) -> str | None:
    """The last root commit whose change was in force on `date`. The timeline is in in-force order, so this is a
    prefix: the first event after the date ends it."""
    found = None
    for event in events if events is not None else timeline():
        if event.in_force > date:
            break
        found = event.commit
    return found


def corpus_of(path: str) -> tuple[str, str]:
    for corpus in sorted(manifest()['corpora'], key=lambda c: -len(c['path'])):
        prefix = corpus['path'] + '/'
        if path.startswith(prefix):
            return corpus['path'], path[len(prefix):]
    raise SystemExit(f'{path} is not inside a corpus; see manifest.json')


def pinned(root_commit: str | None, corpus: str) -> str | None:
    if root_commit is None:
        return None
    line = git('ls-tree', root_commit, '--', corpus).split()
    sha = line[2] if len(line) >= 3 and line[1] == 'commit' else None
    if sha is None or not (ROOT / corpus / '.git').exists() or _has_commit(corpus, sha):
        return sha
    return _readable_pin(root_commit, corpus, sha)


def _has_commit(corpus: str, sha: str) -> bool:
    key = ('has', corpus + ':' + sha)
    if key not in _CACHE:
        done = subprocess.run(['git', 'cat-file', '-e', sha + '^{commit}'], cwd=ROOT / corpus, capture_output=True)
        _CACHE[key] = done.returncode == 0
    return _CACHE[key]  # type: ignore[return-value]


def _readable_pin(root_commit: str, corpus: str, missing: str) -> str:
    """A pin the corpus no longer holds. Rewriting a corpus's history (as on 2026-10-29) gives its documentation
    commits new ids, while law commits keep theirs; a root commit built before then can pin an id that is gone, and
    reading through it made every provision look repealed. A documentation commit changes no law text, so the corpus
    reads the same through the last earlier pin that still exists. A missing law commit has no such stand-in, and
    stops the read rather than giving a wrong answer."""
    events = timeline()
    upto = next((i for i, e in enumerate(events) if e.commit == root_commit), len(events) - 1)
    for event in reversed(events[:upto + 1]):
        if event.corpus != corpus:
            continue
        if _has_commit(corpus, event.corpus_commit):
            return event.corpus_commit
        if event.kind != 'documentation':
            raise SystemExit(f'{corpus}: the tree pins commit {event.corpus_commit} ({event.law}, in force '
                             f'{event.in_force}), which this checkout of the corpus does not hold. Fetch it '
                             f'(git -C {corpus} fetch origin) or update the tree; the text on that date cannot be read.')
    raise SystemExit(f'{corpus}: the tree pins commit {missing}, which this checkout of the corpus does not hold, '
                     'and no earlier pin of it exists either. Update the tree and its submodules.')


def corpus_dir(corpus: str) -> Path:
    path = ROOT / corpus
    if not (path / '.git').exists():
        raise SystemExit(f'{corpus} is not checked out; run: git submodule update --init')
    return path


def text_on(date: str, path: str) -> str | None:
    corpus, rel = corpus_of(path)
    sha = pinned(root_on(date), corpus)
    if sha is None:
        return None
    done = subprocess.run(['git', 'show', f'{sha}:{rel}'], cwd=corpus_dir(corpus), capture_output=True, encoding='utf-8')
    return done.stdout if done.returncode == 0 else None


def blame_rows(date: str, path: str) -> list[tuple[str, str, str]]:
    """(corpus commit, law, line) for every line of the file as it stood on `date`."""
    corpus, rel = corpus_of(path)
    sha = pinned(root_on(date), corpus)
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


def words_on(date: str, path: str) -> list[tuple[str, str]]:
    """(law, run of text) for the file as it stood on `date`, credited word by word. git blame credits whole lines;
    here each version of the file is compared with the one before, word by word, and words that survive keep the law
    that first wrote them. Text moved within the file usually keeps its author; text that is rewritten in place is
    credited to the law that rewrote it. Unchanged lines are matched first, so only changed stretches are compared
    word by word, which keeps long sections fast."""
    corpus, rel = corpus_of(path)
    sha = pinned(root_on(date), corpus)
    if sha is None:
        return []
    cwd = corpus_dir(corpus)
    lines: list[str] = []
    authors: list[list[str]] = []  # per line, one law per token
    for record in git('log', '--reverse', '--format=%H%x1f%an', sha, '--', rel, cwd=cwd).splitlines():
        commit, law = record.split('\x1f', 1)
        shown = subprocess.run(['git', 'show', f'{commit}:{rel}'], cwd=cwd, capture_output=True, encoding='utf-8')
        new_lines = shown.stdout.splitlines(keepends=True) if shown.returncode == 0 else []
        new_authors: list[list[str]] = []
        for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, lines, new_lines, autojunk=False).get_opcodes():
            if op == 'equal':
                new_authors += authors[a0:a1]
                continue
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
    events = timeline()
    a, b = pinned(root_on(date_a, events), corpus), pinned(root_on(date_b, events), corpus)
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
    info = corpus_info(corpus)
    trailer = info['in_force_trailer']
    dated_by = [(info[k], kind) for k, kind in (('baseline_trailer', 'baseline'), ('correction_trailer', 'correction')) if info.get(k)]
    raw = git('log', '--reverse', '--format=%H%x1f%an%x1f%aI%x1f%B%x1e', '--', rel, cwd=corpus_dir(corpus))
    # The tree's own dating of each corpus commit: it dates a starting edition with no trailer of its own (the US
    # 2017 edition) as the baseline, so a file that starts there is not reported as starting with its first amendment.
    placed = {e.corpus_commit: e for e in timeline() if e.corpus == corpus}
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
        if not in_force and sha in placed and placed[sha].kind == 'baseline':
            in_force, kind = placed[sha].in_force, 'baseline'
        if not in_force:
            continue  # documentation and an undated starting edition
        # A publisher's correction is never a law, whatever In-force says (In-force only places it in the order).
        if t.get('Kind', '').strip().lower() == 'correction' or (info.get('correction_trailer') or '') in t:
            kind = 'correction'
        elif t.get('Kind', '').strip().lower() in ('baseline', 'consolidated', 'current', 'current-only'):
            kind = 'baseline'  # a starting text the corpus labels as such (Turkey: Kind: consolidated)
        out.append({'commit': sha, 'law': author, 'in_force': in_force, 'kind': kind,
                    'enacted': next((t[k] for k in ENACTED if k in t), None),
                    'published': next((t[k] for k in PUBLISHED if k in t), None)})
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
        commit = root_on(args[0], events)
        print(f'Root commit on {args[0]}: {commit or "(nothing in force yet)"}')
        for corpus in manifest()['corpora']:
            last = [e for e in events if e.corpus == corpus['path'] and e.in_force <= args[0] and e.kind != 'documentation']
            state = f'{last[-1].law}, in force {last[-1].in_force}' if last else 'not yet in the record'
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
