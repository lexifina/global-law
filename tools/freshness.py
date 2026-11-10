"""How current is each corpus here, and is this repository being kept up to date? Standard library only.

Reading (offline, never connects anywhere):

    python tools/freshness.py romania/national/acts               # one corpus: status, last check, official source
    python tools/freshness.py romania/national/acts/lege/2009/287/art-1112.md
                                                                  # one provision: its corpus, and its act's own row
                                                                  # when the corpus publishes per-act freshness
    python tools/freshness.py --stale                             # corpora not checked within their threshold
    python tools/freshness.py --status unverified
    python tools/freshness.py --summary
    python tools/freshness.py --as-of 2026-12-01 --stale          # judge every check_due against another day

Writing (the pointer loop runs these in the same commit that moves the pins):

    python tools/freshness.py --write [--heads heads.json]        # data/freshness.json + data/freshness.tsv
    python tools/freshness.py --write-status heartbeat.json       # data/status.json

A corpus row says when the corpus was last checked against its official source (`last_verified`), how (`method`),
when the next check is due (`check_due`), and whether global-law already holds the corpus's newest commit. Statuses
follow the corpora that publish their own per-act freshness (romania/national/acts, data/freshness.json there):

    current             checked within its threshold, and global-law holds the corpus's newest commit
    pending-change      the corpus has a newer commit than the one pinned here (held by a check, or not yet pinned)
    stale               last checked longer ago than its threshold
    unverified          never checked against the official source after it was built
    source-unavailable  due for a check, but the official source is not answering the corpus's pipeline

A status is as of the day the files were written; this tool re-reads each `check_due` against today, so a corpus
whose check has fallen due since then shows as stale.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = 'global-law-freshness/1'
STATUSES = ('current', 'pending-change', 'stale', 'unverified', 'source-unavailable')
COLUMNS = ('path', 'level', 'status','last_verified', 'check_due', 'method', 'pinned', 'newest', 'acts', 'acts_current',
           'acts_pending', 'acts_stale', 'acts_unverified', 'per_act', 'official_source')
# Days a check stays good. A country's own law changes most and is read most; sub-national and municipal law is
# checked less often. A corpus may state its own (`freshness_days` in corpus.json, carried into manifest.json).
THRESHOLDS = {'national': 7, 'subnational': 30}
METHODS = {
    'act-checks': "the corpus checks each act against its official source and publishes the result per act "
                  "(the corpus's data/freshness.json); `last_verified` is the day of its latest check",
    'source-retrieval': "the corpus's build read the official source on that day (its REPRODUCE.md); later changes "
                        "at the source are not known until the next build",
    'stated': "the day the corpus states it was last checked (corpus.json `checked_on`)",
}
STATUS_TEXT = {
    'current': 'checked against the official source within its threshold, and global-law holds the newest commit',
    'pending-change': 'the corpus has a newer commit than the one pinned here: a check held it, or the next pass '
                      'will pin it',
    'stale': 'not checked against the official source within its threshold',
    'unverified': 'never checked against the official source after it was built',
    'source-unavailable': "due for a check, but the official source is not answering the corpus's pipeline",
}
SOURCE_DOWN = ('unavailable', 'down')


def day(s) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(s or '')[:10])
    except ValueError:
        return None


def today_utc() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date()


def level(entry: dict) -> str:
    """national for a country's own law (ISO 3166-1 code, or the EU), subnational for an ISO 3166-2 code."""
    code = str(entry.get('code') or '')
    return 'subnational' if '-' in code else 'national'


def threshold(entry: dict) -> int:
    try:
        return int(entry['freshness_days'])
    except (KeyError, TypeError, ValueError):
        return THRESHOLDS[level(entry)]


# ---------------------------------------------------------------------------------------------------------------
# Writing


def gitlinks(root: Path = ROOT, rev: str = 'HEAD') -> dict[str, str]:
    """path -> pinned commit, for every submodule in `rev`."""
    out = subprocess.run(['git', '-C', str(root), 'ls-tree', '-r', '-z', rev], capture_output=True, check=True).stdout
    pins = {}
    for item in out.decode('utf-8').split('\0'):
        meta, _, path = item.partition('\t')
        parts = meta.split()
        if len(parts) == 3 and parts[0] == '160000':
            pins[path] = parts[2]
    return pins


def act_count(acts) -> int | str:
    """A manifest's `acts` is a count, or (for a corpus that names them in corpus.json) the list of its acts."""
    if isinstance(acts, (list, tuple, dict)):
        return len(acts)
    return acts if isinstance(acts, int) else ''


def corpus_row(entry: dict, pinned: str | None, newest: str | None, today: dt.date) -> dict:
    """One corpus's freshness, from its manifest entry (describe.py carries the corpus's own freshness summary into
    `freshness`), the commit pinned here and, when known, the corpus's newest commit."""
    own = entry.get('freshness') or {}
    totals = (own.get('totals') or {}).get('by_status') or {}
    if own.get('checked_against_official_source'):
        last, method = day(own['checked_against_official_source']), 'act-checks'
    elif entry.get('checked_on') and 'checked_on' in (entry.get('derived') or []):
        last, method = day(entry['checked_on']), 'source-retrieval'
    elif entry.get('checked_on'):
        last, method = day(entry['checked_on']), 'stated'
    else:
        last, method = None, ''
    due = last + dt.timedelta(days=threshold(entry)) if last else None
    sources = own.get('sources') or []
    down = any(str(s.get('state', '')).lower() in SOURCE_DOWN or s.get('unavailable_since') for s in sources)
    if newest and pinned and newest != pinned:
        status = 'pending-change'
    elif last is None:
        status = 'unverified'
    elif today > due:
        status = 'source-unavailable' if down else 'stale'
    else:
        status = 'current'
    return {
        'path': entry['path'], 'level': level(entry), 'status': status, 'last_verified': last.isoformat() if last else '',
        'check_due': due.isoformat() if due else '', 'method': method, 'pinned': pinned or '',
        'newest': newest or '', 'acts': act_count(own.get('totals', {}).get('acts') or entry.get('acts')),
        'acts_current': totals.get('current', ''), 'acts_pending': totals.get('pending-change', ''),
        'acts_stale': totals.get('stale', ''), 'acts_unverified': totals.get('unverified', ''),
        'per_act': 'yes' if own else 'no', 'official_source': entry.get('publisher') or '',
    }


def summarise(rows: list[dict], manifest: dict, today: dt.date) -> dict:
    by_level: dict[str, dict] = {}
    entries = {c['path']: c for c in manifest['corpora']}

    def add(bucket: dict, r: dict) -> None:
        bucket['corpora'] = bucket.get('corpora', 0) + 1
        bucket.setdefault('by_status', {s: 0 for s in STATUSES})[r['status']] += 1
        last = day(r['last_verified'])
        if last and (today - last).days <= 7:
            bucket['verified_7d'] = bucket.get('verified_7d', 0) + 1
        if last and (today - last).days <= 30:
            bucket['verified_30d'] = bucket.get('verified_30d', 0) + 1

    totals: dict = {}
    for r in rows:
        add(totals, r)
        add(by_level.setdefault(level(entries.get(r['path'], {})), {}), r)
    for b in [totals, *by_level.values()]:
        n = b.get('corpora') or 1
        b['pct_verified_7d'] = round(100 * b.get('verified_7d', 0) / n, 1)
        b['pct_verified_30d'] = round(100 * b.get('verified_30d', 0) / n, 1)
    per_act = [r['path'] for r in rows if r['per_act'] == 'yes']
    return {
        'note': 'Freshness of every corpus here: when it was last checked against its official source, how, and '
                'whether global-law holds its newest commit. One row per corpus in data/freshness.tsv; '
                '`python tools/freshness.py <corpus or provision path>` reads them. A status is as of `as_of`; a '
                'corpus checked longer ago than its threshold has since become stale.',
        'schema': SCHEMA, 'as_of': today.isoformat(),
        'statuses': STATUS_TEXT, 'methods': METHODS,
        'thresholds': {k: {'days': v} for k, v in THRESHOLDS.items()},
        'columns': list(COLUMNS),
        'totals': totals, 'by_level': by_level,
        'per_act': {'corpora': per_act,
                    'note': 'these corpora publish a freshness row for every act; for a provision in one, '
                            '`python tools/freshness.py <provision path>` reads its act\'s row when the corpus is '
                            'checked out'},
    }


def own_freshness(f: dict) -> dict:
    """The summary of a corpus's own per-act freshness (its data/freshness.json, as romania/national/acts publishes
    it): the day of its latest check against the official source, the act counts by status and each source's state.
    {} when the corpus publishes none."""
    if not isinstance(f, dict) or not f.get('checked_against_official_source'):
        return {}
    t = f.get('totals') or {}
    keep = ('source', 'name', 'state', 'last_successful_check', 'last_successful_contact', 'unavailable_since')
    return {'schema': f.get('schema'), 'as_of': f.get('as_of'),
            'checked_against_official_source': f['checked_against_official_source'],
            'totals': {'acts': t.get('acts'), 'by_status': t.get('by_status') or {}},
            'sources': [{k: s[k] for k in keep if s.get(k) is not None}
                        for s in f.get('sources') or [] if isinstance(s, dict)]}


def write(root: Path = ROOT, heads: dict[str, str] | None = None, today: dt.date | None = None,
          pins: dict[str, str] | None = None, own: dict[str, dict] | None = None) -> dict:
    """data/freshness.json and data/freshness.tsv. `pins` (path -> commit) defaults to this checkout's gitlinks;
    `own` (path -> own_freshness summary) is newer per-act data than manifest.json carries, read by the pointer loop
    from each corpus's data/freshness.json at the commit it pins."""
    today = today or today_utc()
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    pins = gitlinks(root) if pins is None else pins
    heads, own = heads or {}, own or {}
    rows = [corpus_row({**c, 'freshness': own[c['path']]} if own.get(c['path']) else c,
                       pins.get(c['path']), heads.get(c['path']), today)
            for c in sorted(manifest['corpora'], key=lambda c: c['path'])]
    summary = summarise(rows, manifest, today)
    (root / 'data').mkdir(exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    (root / 'data' / 'freshness.tsv').write_bytes(buf.getvalue().encode('utf-8'))
    (root / 'data' / 'freshness.json').write_bytes(
        (json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    update_readme(root, summary, rows)
    return summary


STATUS_BLOCK = re.compile(r'(<!-- status-summary -->\r?\n).*?(\r?\n<!-- /status-summary -->)', re.S)


def status_line(status: dict, summary: dict) -> str:
    t = summary.get('totals') or {}
    f = status.get('freshness') or {}
    n = sum(f.values()) or t.get('corpora') or 0
    when = (status.get('last_published') or status.get('generated') or '')[:16].replace('T', ' ')
    upd = '**Updates: running**' if status.get('updates') == 'running' else '**Updates: stalled**'
    moved = (status.get('published_last_24h') or {}).get('corpora_moved', 0)
    p24 = status.get('published_last_24h') or {}
    held = status.get('held_back') or []
    down = status.get('official_sources_unavailable') or []
    last_ok = (status.get('last_successful_pass') or '')[:16].replace('T', ' ')
    return '\n'.join([
        f"{upd}: last published {when} UTC; status refreshed {(status.get('generated') or '')[:16].replace('T', ' ')} "
        "UTC.", '',
        '| | |', '| --- | --- |',
        f"| Last 24 hours | {p24.get('commits', 0)} commit{'' if p24.get('commits') == 1 else 's'}: {moved} corpus updates, {p24.get('corpora_added', 0)} "
        "corpora added |",
        f"| Last successful pass | {last_ok or '-'} UTC" + ('' if status.get('last_pass_ok', True) else
                                                            ' (the latest pass failed and is retried)') + ' |',
        f"| Held back by a check | {_names(held)} |",
        f"| Official sources not answering | " + (', '.join(f"{s.get('name')} (`{s.get('corpus')}`, since "
                                                           f"{str(s.get('unavailable_since'))[:10]})" for s in down)
                                                 or 'none') + ' |',
        f"| Freshness | {f.get('current', 0)} of {n} corpora current, {f.get('stale', 0)} stale, "
        f"{f.get('unverified', 0)} unverified ([FRESHNESS.md](FRESHNESS.md)) |"])


PAGES = ('README.md', 'FRESHNESS.md', 'MONITORING.md')  # the pages whose marked lines this tool rewrites


def _rewrite(root: Path, block: re.Pattern, line: str) -> bool:
    """Rewrite the line between `block`'s markers in every page that has them; False when none has."""
    found = False
    for name in PAGES:
        try:
            text = (root / name).read_bytes().decode('utf-8')
        except OSError:
            continue
        new = block.sub(lambda m: m.group(1) + line + m.group(2), text, count=1)
        if new != text:
            (root / name).write_bytes(new.encode('utf-8'))
        found = found or bool(block.search(text))
    return found


def update_readme_status(root: Path, status: dict, summary: dict) -> bool:
    return _rewrite(root, STATUS_BLOCK, status_line(status, summary))


def health(root: Path = ROOT, now: dt.datetime | None = None, max_age_h: float = 2.0) -> list[str]:
    """Problems a monitor should raise, from the published files alone: the status file not refreshed within
    `max_age_h` hours or updates stalled, freshness data older than a day, and official sources reported down
    (listed, but not a failure: the source is down, not this repository)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    out = []
    try:
        st = json.loads((root / 'data' / 'status.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return ['data/status.json is missing or unreadable']
    gen = _ts(st.get('generated'))
    if not gen or (now - gen).total_seconds() > max_age_h * 3600:
        out.append(f"data/status.json was last refreshed {st.get('generated')}, over {max_age_h:g} hours ago: "
                   "the update loop is not publishing")
    if st.get('updates') != 'running':
        out.append(f"updates: {st.get('updates')} (last successful pass {st.get('last_successful_pass')})")
    s = read_summary(root)
    as_of = day(s.get('as_of'))
    if not as_of or (now.date() - as_of).days > 1:
        out.append(f"data/freshness.json is as of {s.get('as_of')}: freshness is not being recomputed")
    for src in st.get('official_sources_unavailable') or []:
        out.append(f"official source unavailable: {src.get('name')} ({src.get('corpus')}) since "
                   f"{src.get('unavailable_since')}")
    return out


README_BLOCK = re.compile(r'(<!-- freshness-summary -->\r?\n).*?(\r?\n<!-- /freshness-summary -->)', re.S)


def _names(paths: list[str], most: int = 8) -> str:
    shown = ', '.join(f'`{p}`' for p in paths[:most])
    return shown + (f' and {len(paths) - most} more' if len(paths) > most else '') if paths else 'none'


def freshness_block(summary: dict, rows: list[dict]) -> str:
    """The generated part of FRESHNESS.md: the counts, a table by level, and the national corpora that need a check."""
    t = summary['totals']
    s = t.get('by_status', {})
    out = [f"**{s.get('current', 0)} of {t['corpora']} corpora current** on {summary['as_of']}: "
           f"{t['pct_verified_7d']}% checked against their official source in the last 7 days, "
           f"{t['pct_verified_30d']}% in the last 30.", '',
           '| | Corpora | Current | Pending a change | Stale | Unverified | Checked in 7 days |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name, b in [('All', t)] + sorted(summary.get('by_level', {}).items()):
        bs = b.get('by_status', {})
        out.append(f"| {name.capitalize()} | {b.get('corpora', 0)} | {bs.get('current', 0)} | "
                   f"{bs.get('pending-change', 0)} | {bs.get('stale', 0)} | {bs.get('unverified', 0)} | "
                   f"{b.get('pct_verified_7d', 0)}% |")
    stale = sorted((r for r in rows if r['status'] == 'stale'), key=lambda r: r.get('last_verified') or '')
    first = [r for r in stale if r.get('level') == 'national'] or stale
    out += ['', 'National law longest since a check: ' + (', '.join(f"`{r['path']}` ({r['last_verified']})"
                                                                     for r in first[:6]) or 'none') + '.', '',
            f"Never checked: {_names([r['path'] for r in rows if r['status'] == 'unverified'])}."]
    return '\n'.join(out)


def update_readme(root: Path, summary: dict, rows: list[dict] | None = None) -> bool:
    """Rewrite the generated part of FRESHNESS.md (between its freshness-summary markers)."""
    return _rewrite(root, README_BLOCK, freshness_block(summary, rows if rows is not None else read_rows(root)))


def write_status(heartbeat: dict, root: Path = ROOT, now: dt.datetime | None = None, stalled_after_min: int = 45,
                 rows: list[dict] | None = None, subjects: list[str] | None = None) -> dict:
    """data/status.json, the public part of the pointer loop's heartbeat: whether updates are running, the last
    publication, what moved in the last 24 hours, the corpora held back by a check, and each official source a corpus
    reports unavailable. No machine names, paths or internal errors."""
    now = now or dt.datetime.now(dt.timezone.utc)
    # running while a pass has succeeded recently: one failed pass (a network blip) is retried by the next one
    ok = _ts(heartbeat.get('last_success_at') or (heartbeat.get('at') if heartbeat.get('result') != 'error' else None))
    running = bool(ok) and (now - ok).total_seconds() <= stalled_after_min * 60
    since = (now - dt.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
    moved = pins_moved_since(root, since, subjects)
    rows = rows if rows is not None else read_rows(root)
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    sources = []
    for c in manifest['corpora']:
        for s in (c.get('freshness') or {}).get('sources') or []:
            if str(s.get('state', '')).lower() in SOURCE_DOWN or s.get('unavailable_since'):
                sources.append({'corpus': c['path'], 'name': s.get('name') or s.get('source'),
                                'state': 'unavailable', 'unavailable_since': s.get('unavailable_since'),
                                'last_successful_contact': s.get('last_successful_contact')
                                or s.get('last_successful_check')})
    held = heartbeat.get('gate_held') or {}
    status = {
        'schema': 'global-law-status/1',
        'generated': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'updates': 'running' if running else 'stalled',
        'last_pass': heartbeat.get('at'),
        'last_pass_ok': heartbeat.get('result') != 'error',
        'last_successful_pass': heartbeat.get('last_success_at'),
        'last_published': heartbeat.get('last_push_at'),
        'published_last_24h': moved,
        'held_back': sorted(held) if isinstance(held, dict) else [],
        'freshness': {s: sum(1 for r in rows if r['status'] == s) for s in STATUSES},
        'official_sources_unavailable': sources,
        'note': "As seen from Lexifina's pipeline. `updates` is running while the pointer loop completes a pass at "
                "least every 45 minutes. `held_back` lists corpora whose newest commit failed a check and is not "
                "pinned yet. An official source marked unavailable did not answer that corpus's pipeline; it may be "
                "up for others.",
    }
    (root / 'data' / 'status.json').write_bytes((json.dumps(status, ensure_ascii=False, indent=1) + '\n').encode())
    update_readme_status(root, status, read_summary(root))
    return status


def _ts(s) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except ValueError:
        return None


POINT = re.compile(r'(?:point|repin)\D*?(\d+) corpora|\((\d+) corpora\)', re.I)
ADD = re.compile(r'Add (\d+) corpora', re.I)


def pins_moved_since(root: Path, since: str, subjects: list[str] | None = None) -> dict:
    """Commits on this repository since `since`, and the corpora they added or moved, from their subjects (or the
    `subjects` given, by a caller with no checkout)."""
    if subjects is not None:
        log = subjects
    else:
        try:
            log = subprocess.run(['git', '-C', str(root), 'log', f'--since={since}', '--format=%s'],
                                 capture_output=True, encoding='utf-8', check=True).stdout.splitlines()
        except (OSError, subprocess.CalledProcessError):
            return {'commits': 0, 'corpora_moved': 0, 'corpora_added': 0}
    moved = added = 0
    for s in log:
        a = ADD.search(s)
        if a:
            added += int(a.group(1))
        m = re.search(r'point (\d+)', s, re.I) if a else POINT.search(s)
        if m:
            moved += int(next(g for g in m.groups() if g))
    return {'commits': len(log), 'corpora_moved': moved, 'corpora_added': added}


# ---------------------------------------------------------------------------------------------------------------
# Reading


def read_rows(root: Path = ROOT) -> list[dict]:
    try:
        with open(root / 'data' / 'freshness.tsv', encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f, delimiter='\t'))
    except OSError:
        return []


def read_summary(root: Path = ROOT) -> dict:
    try:
        return json.loads((root / 'data' / 'freshness.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def status_on(row: dict, today: dt.date) -> str:
    """The status on `today`: a current corpus whose check fell due before today is stale."""
    due = day(row.get('check_due'))
    if row['status'] == 'current' and due and today > due:
        return 'stale'
    return row['status']


def corpus_of(path: str, rows: list[dict]) -> tuple[dict | None, str]:
    """(the row of the corpus holding `path`, the path inside it)."""
    path = path.strip().strip('/')
    best = None
    for r in rows:
        if path == r['path'] or path.startswith(r['path'] + '/'):
            if best is None or len(r['path']) > len(best['path']):
                best = r
    return best, (path[len(best['path']):].strip('/') if best else '')


def act_row(corpus_root: Path, inner: str) -> dict | None:
    """The corpus's own freshness row for the act holding `inner` (a provision or folder inside the corpus), for a
    corpus that publishes per-act freshness (data/freshness/index.json and data/paths.json, as romania/national/acts
    does) and is checked out. None otherwise."""
    try:
        index = json.loads((corpus_root / 'data' / 'freshness' / 'index.json').read_text(encoding='utf-8'))
        paths = json.loads((corpus_root / 'data' / 'paths.json').read_text(encoding='utf-8')).get('paths', {})
    except (OSError, ValueError):
        return None
    folder = inner if not inner.endswith('.md') else inner.rsplit('/', 1)[0]
    by_folder = {p: a for a, p in paths.items()}
    while folder and folder not in by_folder:
        folder = folder.rsplit('/', 1)[0] if '/' in folder else ''
    if not folder:
        return None
    act = by_folder[folder]
    kind = folder.split('/')[0]
    years = [p for p in folder.split('/')[1:] if len(p) == 4 and p.isdigit()]
    first = f'{kind}/{years[0] if years else "undated"}'
    shards = index.get('shards', [])
    order = [s['file'] for s in shards if s.get('shard') == first]
    order += [s['file'] for s in shards if s.get('kind') == kind and s['file'] not in order]
    for rel in order:
        try:
            with open(corpus_root / rel, encoding='utf-8', newline='') as f:
                for row in csv.DictReader(f):
                    if row.get('act') == act:
                        return dict(row, folder=folder)
        except OSError:
            continue
    return None


def note(path: str, today: dt.date | None = None, root: Path = ROOT) -> str:
    """One line on how current the text at `path` is, for answers given on today's law; '' when there is no data."""
    today = today or today_utc()
    rows = read_rows(root)
    row, inner = corpus_of(path, rows)
    if not row:
        return ''
    st = status_on(row, today)
    src = row.get('official_source') or 'its official source'
    act = act_row(root / row['path'], inner) if row.get('per_act') == 'yes' and inner else None
    if act:
        a_st = act['status']
        due = day(act.get('check_due'))
        if a_st == 'current' and due and today > due:
            a_st = 'stale'
        line = f"{act['act']}: {a_st}, last verified against {src} on {act.get('last_verified') or 'never'}"
        if a_st == 'pending-change':
            line += (f"; the official source reports a change not in this record yet "
                     f"({act.get('newest_change') or 'not named'}, {act.get('newest_change_date') or 'undated'})")
        if act.get('official_url'):
            line += f"; check it at {act['official_url']}"
        return line + '.'
    if not row.get('last_verified'):
        # "since", not "never ... after": a corpus may say it was checked when it was built (germany/bund/acts: "Checked
        # against Gesetze im Internet on the record_to day"), and "never checked" beside that read as a contradiction.
        return f"{row['path']}: not checked against {src} since it was built; later changes may be missing."
    n = (today - day(row['last_verified'])).days
    line = f"{row['path']}: {st}, last checked against {src} on {row['last_verified']} ({n} days ago)"
    if st == 'pending-change':
        line += '; the corpus has a newer commit than the one pinned here'
    elif st != 'current':
        line += '; later changes may be missing'
    return line + '.'


def describe_row(row: dict, summary: dict, today: dt.date, root: Path, inner: str = '') -> str:
    st = status_on(row, today)
    lines = [row['path'], f"  status:          {st}"]
    if st != row['status']:
        lines.append(f"                   ({row['status']} when the data was written, {summary.get('as_of')})")
    lines.append(f"  meaning:         {STATUS_TEXT.get(st, '')}")
    last = day(row.get('last_verified'))
    if last:
        lines.append(f"  last verified:   {last} ({(today - last).days} days ago); next check due {row['check_due']}")
    if row.get('method'):
        lines.append(f"  method:          {row['method']}: {METHODS.get(row['method'], '')}")
    lines.append(f"  pinned:          {row.get('pinned') or '-'}"
                 + (f" (newest {row['newest']})" if row.get('newest') and row['newest'] != row.get('pinned') else ''))
    if row.get('per_act') == 'yes':
        lines.append(f"  acts:            {row.get('acts')} ({row.get('acts_current')} current, "
                     f"{row.get('acts_pending')} pending a change, {row.get('acts_stale')} stale, "
                     f"{row.get('acts_unverified')} unverified)")
    if row.get('official_source'):
        lines.append(f"  official source: {row['official_source']}")
    if inner:
        act = act_row(root / row['path'], inner)
        if act:
            lines.append(f"  act:             {act['act']} ({act['folder']}): {act['status']}, last verified "
                         f"{act.get('last_verified') or 'never'}")
            if act.get('newest_change') or act.get('newest_change_date'):
                lines.append(f"  newest change:   {act.get('newest_change') or '(not named)'} "
                             f"{act.get('newest_change_date') or ''}, "
                             f"{'in this record' if act.get('change_in_repo') == 'yes' else 'NOT in this record yet'}")
            if act.get('official_url'):
                lines.append(f"  check by hand:   {act['official_url']}")
        elif row.get('per_act') == 'yes':
            lines.append(f"  act:             add the corpus to read its act's row "
                         f"(python tools/countries.py add {row['path']})")
    lines.append(f"  data:            data/freshness.tsv (as of {summary.get('as_of')})")
    return '\n'.join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?', help='a corpus path, or a provision or folder inside one')
    ap.add_argument('--stale', action='store_true', help='list corpora not checked within their threshold')
    ap.add_argument('--status', choices=STATUSES, help='list corpora with this status')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--as-of', help='judge each check_due against this day (YYYY-MM-DD)')
    ap.add_argument('--write', action='store_true', help='write data/freshness.json and data/freshness.tsv')
    ap.add_argument('--heads', help="with --write: a JSON file {corpus path: the corpus's newest commit}")
    ap.add_argument('--write-status', metavar='HEARTBEAT', help="write data/status.json from the pointer loop's "
                                                                "heartbeat file")
    ap.add_argument('--health', action='store_true', help='list problems and exit 1 when updates have stalled or the '
                                                            'published files are out of date (the hourly monitor)')
    ap.add_argument('--repo', default=str(ROOT))
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    root = Path(a.repo)
    today = day(a.as_of) if a.as_of else today_utc()
    if today is None:
        ap.error('--as-of takes a day, YYYY-MM-DD')
    if a.health:
        problems = health(root)
        in_actions = 'GITHUB_ACTIONS' in os.environ
        for p in problems:
            print(f"::{'warning' if p.startswith('official source') else 'error'}::{p}" if in_actions else p)
        if not problems:
            print('ok: updates running; status and freshness files current')
        return 1 if any(not p.startswith('official source') for p in problems) else 0
    if a.write:
        heads = json.loads(Path(a.heads).read_text(encoding='utf-8')) if a.heads else None
        s = write(root, heads, today)
        print(json.dumps(s['totals'], ensure_ascii=False))
        return 0
    if a.write_status:
        print(json.dumps(write_status(json.loads(Path(a.write_status).read_text(encoding='utf-8')), root),
                         ensure_ascii=False, indent=1))
        return 0
    rows, summary = read_rows(root), read_summary(root)
    if not rows:
        print('data/freshness.tsv not found: this checkout has no freshness data', file=sys.stderr)
        return 1
    if a.summary:
        t = summary.get('totals', {})
        print(f"{t.get('pct_verified_7d')}% of {t.get('corpora')} corpora checked against their official source in "
              f"the last 7 days, {t.get('pct_verified_30d')}% in the last 30 (data as of {summary.get('as_of')})")
        counts = {s: 0 for s in STATUSES}
        for r in rows:
            counts[status_on(r, today)] += 1
        print(f'on {today}: ' + ', '.join(f'{n} {s}' for s, n in counts.items()))
        return 0
    if a.stale or a.status:
        want = 'stale' if a.stale else a.status
        n = 0
        for r in rows:
            if status_on(r, today) == want:
                n += 1
                print(f"{r['path']}\t{r.get('last_verified') or '-'}\t{r.get('method') or '-'}\t"
                      f"{r.get('official_source') or '-'}")
        print(f'{n} corpora {want} on {today}', file=sys.stderr)
        return 0
    if not a.path:
        ap.print_help()
        return 2
    row, inner = corpus_of(a.path, rows)
    if not row:
        print(f'{a.path}: in no corpus here', file=sys.stderr)
        return 1
    print(describe_row(row, summary, today, root, inner))
    return 0


if __name__ == '__main__':
    sys.exit(main())
