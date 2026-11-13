#!/usr/bin/env python3
"""Rewrite manifest.json and every jurisdiction.json from the tree as it is: every corpus the tree pins, described by
its own repository at the pinned commit. Standard library only; needs no corpus checked out (it reads each corpus's
corpus.json, data/repo.json and jurisdiction.json from GitHub at the pinned commit).

  python tools/describe.py            rewrite the files in this checkout (then commit them)
  python tools/describe.py --check    say what would change, change nothing (exit 1 if anything would)

A corpus is listed in manifest.json with its path, repository, name, code, language, coverage and dates, from its own
corpus.json where it has one, else from data/repo.json and jurisdiction.json. A corpus with no corpus.json gets its
history, history_from, record_to, checked_on, acts and coverage from what its build publishes (data/commits.csv,
registry/data/ for acts appended later, REPRODUCE.md, the README's "metadata only" or "as enacted" note outside its
tables), and `derived` names those fields; a history data/repo.json declares is kept as declared, never derived. A corpus that states no history from the standard's values takes the measured one in
data/history-measured.tsv (also named in `derived`). future_branch names the branch tools/law.py reads laws not yet
in force from, as data/future-pins.tsv records it (tools/future_pins.py); a future branch the repository has that is
not read (behind main, or diverged) is named future_branch_unread instead. Every folder that holds a corpus, or a folder that does, gets a jurisdiction.json naming its level, its code
and what is inside it. Fields an earlier build wrote and nothing here replaces are kept. A file that GitHub fails to
serve (anything but a 404) stops the run with exit 2 and nothing written: it would otherwise read as a missing file.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import future_pins  # noqa: E402  (FUTURE_NAMES, pick_branch: which branch counts)
from freshness import own_freshness  # noqa: E402  (a corpus's own per-act freshness, summarised)
CORPUS_KEYS = ('name', 'label', 'language', 'coverage', 'history', 'history_from', 'record_to', 'checked_on',
               'in_force_trailer', 'baseline_trailer', 'correction_trailer', 'citation', 'scope', 'acts', 'publisher',
               'future_branch', 'verification', 'record_note', 'effects', 'freshness_days', 'kind', 'overlay',
               'source', 'licence', 'credit')
HISTORY_VALUES = ('in-force', 'replayed', 'as-enacted', 'current-only', 'metadata-only')  # CORPUS-STANDARD.md
MEASURED: dict[str, tuple[str, str]] = {}  # path -> (history, coverage note), from data/history-measured.tsv


def git(*args: str) -> str:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout


class FetchError(RuntimeError):
    """A file that could not be read for a reason other than its absence: describing the corpus from what was read
    would write a wrong description (a missing commits.csv reads as a corpus of no acts), so the run stops."""


def _get(url: str, accept: str = '') -> bytes | None:
    """The body at a GitHub URL; None when GitHub says there is nothing there (404); FetchError on anything else
    after five tries."""
    headers = {'Authorization': f'token {TOKEN}'} if TOKEN else {}  # a private corpus answers 404 without one
    if accept:
        headers['Accept'] = accept
    error = ''
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            error = f'HTTP {e.code}'
        except (OSError, ValueError) as e:
            error = str(e) or type(e).__name__
        time.sleep(2 ** attempt)
    raise FetchError(f'{url}: {error}')


def fetch_text(repo: str, sha: str, name: str) -> str:
    """A file of a corpus at a commit; '' when the corpus has no such file."""
    body = _get(f'https://raw.githubusercontent.com/{repo}/{sha}/{name}')
    return '' if body is None else body.decode('utf-8')


def first_in_force(repo: str, sha: str, trailers: tuple[str, ...] = ('In-force',)) -> str:
    """The day the first commit of a corpus's history at `sha` (its root commit) is dated by, in the first of
    `trailers` it carries (In-force, or a baseline's Consolidated), or ''."""
    api = f'https://api.github.com/repos/{repo}/commits?sha={sha}&per_page=1'
    with urllib.request.urlopen(urllib.request.Request(api, headers={'Authorization': f'token {TOKEN}'} if TOKEN else {}),
                                timeout=90) as r:
        last = re.search(r'[?&]page=(\d+)>; rel="last"', r.headers.get('Link') or '')
        page = json.loads(r.read()) if not last else json.loads(_get(f'{api}&page={last.group(1)}') or b'[]')
    message = page[0]['commit']['message'] if page else ''
    for trailer in trailers:
        day = re.search(rf'^{re.escape(trailer)}:\s*(\d{{4}}-\d{{2}}-\d{{2}})', message, re.M)
        if day:
            return day.group(1)
    return ''


def remote_heads(repo: str) -> set[str]:
    """The branches a corpus repository has on GitHub (git ls-remote --heads); FetchError when it cannot be asked."""
    for attempt in range(4):
        r = subprocess.run(['git', 'ls-remote', '--heads', f'https://github.com/{repo}.git'], capture_output=True,
                           encoding='utf-8', timeout=120, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
        if r.returncode == 0:
            return {line.split('refs/heads/', 1)[1] for line in r.stdout.splitlines() if 'refs/heads/' in line}
        time.sleep(2 ** attempt)
    raise FetchError(f'git ls-remote --heads {repo}: {r.stderr.strip()[:200]}')


def fetch(repo: str, sha: str, name: str) -> dict:
    try:
        return json.loads(fetch_text(repo, sha, name) or '{}')
    except ValueError:
        return {}


METADATA_ONLY = re.compile(r'metadata only|no law text|catalogue only', re.I)
# The shared builder's README for a record of each act as enacted ("**Each Perda as enacted, not yet a history of
# amendments.** ... its amendments are not applied ..."): its commits are the publisher's, Kind: publisher, so the rows
# alone read as current text only (audit row 79: 19 Indonesian corpora).
AS_ENACTED = re.compile(r'\bas enacted, not (?:yet )?a history of amendments|\bamendments are not applied\b', re.I)
RETRIEVED = re.compile(r'written by the build on (\d{4}-\d{2}-\d{2}), the day the source data was retrieved')
ISO_DAY = re.compile(r'\d{4}-\d{2}-\d{2}$')


def says_metadata_only(readme: str) -> bool:
    """The README says the repository holds no law text. Table rows are left out: a row about one data file (court
    judgments kept as "links and metadata only", a catalogue folder with "no law text") says nothing about the
    repository's law, and matched Romania's 50,000 dated versions."""
    return any(METADATA_ONLY.search(line) for line in readme.splitlines() if not line.lstrip().startswith('|'))


def _rows(text: str) -> list[dict]:
    return [r for r in csv.DictReader(io.StringIO(text))
            if (r.get('branch') or 'main') == 'main' and ISO_DAY.match(r.get('day') or '')]


def says_as_enacted(readme: str) -> bool:
    """The README says each act is held as enacted, later amendments not applied (outside its tables)."""
    return any(AS_ENACTED.search(line) for line in readme.splitlines() if not line.lstrip().startswith('|'))


def from_build(repo: str, sha: str, declared: str | None = None) -> dict:
    """What a corpus with no corpus.json says about its own record in the files its build publishes: data/commits.csv
    (one row per commit on main: day, kind, law, acts), REPRODUCE.md (the day the source was retrieved) and the README
    (a "metadata only" note). Acts appended to a corpus after its first build are documented apart, under registry/
    (registry/data/commits.csv, registry/data/versions.json: each act with its dated versions, and registry/REPRODUCE.md),
    and the appender restores the first build's data/ as it was, so both are read: data/ alone undercounts such a corpus
    (Serbia: 1 act in data/commits.csv, 9,749 in all). history is in-force when an act on main has more than one
    version; as-enacted when nearly every act's only version is credited to the law that made it; current-only when
    the only versions are the text as the publisher gave it; metadata-only when the README says the repository holds
    no law text, as-enacted when it says each act is held as enacted. A history the corpus declares (`declared`, from
    data/repo.json) is taken as it is: it is never guessed over, and the coverage line describes it."""
    readme, reproduce = fetch_text(repo, sha, 'README.md'), fetch_text(repo, sha, 'REPRODUCE.md')
    rows = _rows(fetch_text(repo, sha, 'data/commits.csv'))
    retrieved_days = RETRIEVED.findall(reproduce)
    registry = fetch(repo, sha, 'registry/data/versions.json')
    if registry:
        rows += _rows(fetch_text(repo, sha, 'registry/data/commits.csv'))
        retrieved_days += RETRIEVED.findall(fetch_text(repo, sha, 'registry/REPRODUCE.md'))
    cutoff = max(retrieved_days, default='')
    seen = {(act, r['day']) for r in rows for act in re.split(r'[\s;|]+', (r.get('acts') or '').strip()) if act}
    for act in registry.get('acts', []) if isinstance(registry.get('acts'), list) else []:
        key = act.get('slug') or act.get('path') or ''
        days = sorted(v['from'] for v in act.get('versions', []) if ISO_DAY.match(str(v.get('from') or ''))
                      and (not cutoff or v['from'] <= cutoff))  # a version dated after retrieval is not on main
        for i, day in enumerate(days):
            if key and (key, day) not in seen:  # one row per version, as commits.csv would write it
                seen.add((key, day))
                rows.append({'day': day, 'kind': 'start' if i == 0 else 'law', 'law': key, 'acts': key})
    out: dict = {}
    if declared in HISTORY_VALUES:
        out['history'] = declared
    elif says_metadata_only(readme):
        out['history'] = 'metadata-only'
    if rows:
        acts: dict[str, int] = {}
        for r in rows:
            for act in re.split(r'[\s;|]+', (r.get('acts') or '').strip()):
                if act:
                    acts[act] = acts.get(act, 0) + 1
        starts = [r for r in rows if r.get('kind') == 'start']
        days = sorted(r['day'] for r in rows)
        out['acts'] = len(acts)
        out['history_from'] = days[0]
        if 'history' not in out:
            if any(n > 1 for n in acts.values()):
                out['history'] = 'in-force'
            elif starts and sum(1 for r in starts if r.get('law')) >= 0.9 * len(starts) or says_as_enacted(readme):
                out['history'] = 'as-enacted'
            else:
                out['history'] = 'current-only'
        kind = {'current-only': '; current text only, as the publisher gave it',
                'metadata-only': '; catalogue entries only, no law text',
                'as-enacted': '; each act as enacted, later changes not applied'}.get(out['history'], '')
        out['coverage'] = f"{len(acts)} acts, {len(rows)} dated versions from {days[0]} to {days[-1]}{kind}"
    if cutoff:
        out['record_to'] = out['checked_on'] = cutoff
    elif rows:
        out['record_to'] = max(r['day'] for r in rows)
    if out:
        out['derived'] = sorted(k for k in out if not (k == 'history' and declared in HISTORY_VALUES))
    return out


def _token() -> str:
    """A GitHub token, if one is at hand (GITHUB_TOKEN or GH_TOKEN, else `gh auth token`): reads of public corpora
    need none, a private corpus does. Never printed."""
    import os
    tok = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not tok:
        try:
            tok = subprocess.run(['gh', 'auth', 'token'], capture_output=True, encoding='utf-8', timeout=20).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            tok = ''
    return tok


TOKEN = ''
LEVELS_WHOLE = ('national', 'federal', 'bund', 'union', 'uk')  # the folder for a whole country's (or the EU's) law
# ISO 3166-2 codes of subdivisions whose corpora name none of their own (or only their country's)
SUBDIVISION_CODES = {
    'australia/australian-capital-territory': 'AU-ACT', 'australia/northern-territory': 'AU-NT',
    'australia/south-australia': 'AU-SA', 'australia/tasmania': 'AU-TAS', 'australia/western-australia': 'AU-WA',
    'canada/newfoundland-and-labrador': 'CA-NL', 'canada/northwest-territories': 'CA-NT', 'canada/ontario': 'CA-ON',
    'united-states/arizona': 'US-AZ', 'united-states/california': 'US-CA', 'united-states/district-of-columbia': 'US-DC',
    'united-states/guam': 'US-GU', 'united-states/indiana': 'US-IN', 'united-states/new-jersey': 'US-NJ',
    'united-states/northern-mariana-islands': 'US-MP', 'united-states/utah': 'US-UT',
}


def pins() -> dict[str, tuple[str, str]]:
    """corpus path -> (commit pinned, owner/repo)."""
    links = {l.split('\t', 1)[1]: l.split()[2] for l in git('ls-tree', '-r', 'HEAD').splitlines() if l.split()[1] == 'commit'}
    names, urls = {}, {}
    for line in git('config', '--blob', 'HEAD:.gitmodules', '--get-regexp', r'^submodule\..*\.(path|url)$').splitlines():
        key, _, value = line.partition(' ')
        (names if key.endswith('.path') else urls)[key.rsplit('.', 1)[0]] = value
    url_of = {p: urls.get(n, '') for n, p in names.items()}
    out = {}
    for path, sha in links.items():
        url = url_of.get(path, '').removesuffix('.git').rstrip('/')
        out[path] = (sha, '/'.join(url.split('/')[-2:]))
    return out


def describe(path: str, sha: str, repo: str) -> tuple[dict, dict]:
    cj, rj, jj = fetch(repo, sha, 'corpus.json'), fetch(repo, sha, 'data/repo.json'), fetch(repo, sha, 'jurisdiction.json')
    entry = {'path': path, 'url': f'https://github.com/{repo}.git'}
    if cj:
        entry.update({k: cj[k] for k in CORPUS_KEYS if k in cj})
        if re.fullmatch(r'[a-z0-9-]+', str(entry.get('name', ''))):  # a repository slug is not a name
            entry.pop('name')
        if cj.get('corpus'):
            entry['iso_path'] = cj['corpus']
    else:
        if rj.get('name') or jj.get('name'):
            entry['name'] = rj.get('name') or jj['name']
        if rj.get('publisher'):
            entry['record_note'] = f"Publisher: {rj['publisher']}."
            entry['publisher'] = rj['publisher']
        if rj.get('future_branch'):
            entry['future_branch'] = rj['future_branch']
        # history: the corpus's own declaration in data/repo.json (corpus standard), over anything derived
        for k, v in from_build(repo, sha, rj.get('history')).items():  # never overrides a stated field
            entry.setdefault(k, v)
    own = own_freshness(fetch(repo, sha, 'data/freshness.json'))
    if own:
        entry['freshness'] = own
    if entry.get('history') not in HISTORY_VALUES:
        # A history that is none of the standard's values: a phrase is kept as the coverage note, the measured value
        # (data/history-measured.tsv) stands in until the corpus states one.
        if entry.get('history') and not entry.get('coverage'):
            entry['coverage'] = entry['history']
        entry.pop('history', None)
        if path in MEASURED:
            history, coverage = MEASURED[path]
            entry['history'] = history
            if coverage and coverage not in entry.get('record_note', ''):
                entry['record_note'] = ' '.join(filter(None, [entry.get('record_note', ''), f'History: {coverage}.']))
            entry['derived'] = sorted(set(entry.get('derived', [])) | {'history'})
    code = (rj.get('country') or jj.get('code') or cj.get('code') or '')
    if code:
        entry['code'] = code.upper()
    if jj.get('path') and 'iso_path' not in entry:
        entry['iso_path'] = f"{jj['path']}/acts"
    leaf = path.rsplit('/', 1)[-1]
    if entry.get('iso_path') and entry['iso_path'].rsplit('/', 1)[-1] != leaf:
        # the corpus's own id names another folder (us/arizona/statutes for united-states/arizona/acts): the ISO path
        # follows the folder the tree puts it in, as every other corpus's does
        entry['iso_path'] = f"{entry['iso_path'].rsplit('/', 1)[0]}/{leaf}"
    year = re.fullmatch(r'\d{4}', str(entry.get('history_from') or ''))
    if year:  # a bare year: the day is the first In-force date of the history pinned, when it falls in that year
        day = first_in_force(repo, sha, tuple(filter(None, (entry.get('in_force_trailer') or 'In-force',
                                                            entry.get('baseline_trailer')))))
        if day.startswith(year.group(0)):
            entry['history_from'] = day
            entry['derived'] = sorted(set(entry.get('derived', [])) | {'history_from'})
        else:
            print(f'warning: {path}: history_from {year.group(0)} is a bare year and its first commit is dated '
                  f'{day or "nothing"}', file=sys.stderr)
    entry['_branches'] = remote_heads(repo)
    entry.setdefault('in_force_trailer', 'In-force')
    entry['described_by'] = 'corpus.json' if cj else ('data/repo.json' if rj else ('jurisdiction.json' if jj else 'path'))
    return entry, jj


def subdivision_code(code: str | None, country: str, depth: int) -> str:
    """A code below the country as ISO 3166-2 writes it (US-CO, not CO): a bare two-letter code of a subdivision gets
    its country's prefix, so it cannot be read as another country's code (CO is Colombia, AS American Samoa)."""
    code = (code or '').upper()
    if depth >= 1 and country and re.fullmatch(r'[A-Z0-9]{1,3}', code) and code != country:
        return f'{country}-{code}'
    return code


def main(argv: list[str]) -> int:
    global TOKEN
    check = '--check' in argv
    TOKEN = _token()
    old = json.loads(git('show', 'HEAD:manifest.json'))
    moved = {}
    try:
        for line in git('show', 'HEAD:data/moved-paths.tsv').splitlines():
            if line and not line.startswith('#'):
                a, b = line.split('\t')[:2]
                moved[a] = b
    except subprocess.CalledProcessError:
        pass
    try:
        for line in git('show', 'HEAD:data/history-measured.tsv').splitlines():
            if line and not line.startswith('#'):
                f = line.split('\t') + ['', '']
                MEASURED[f[0]] = (f[1], f[3])
    except subprocess.CalledProcessError:
        pass
    read_future: dict[str, str] = {}  # corpus -> the future branch tools/law.py reads (data/future-pins.tsv)
    try:
        for line in git('show', 'HEAD:data/future-pins.tsv').splitlines():
            if line and not line.startswith('#'):
                f = line.split('\t')
                read_future[f[0]] = f[1]
    except subprocess.CalledProcessError:
        pass
    before = {moved.get(c['path'], c['path']): c for c in old.get('corpora', [])}
    tree = pins()
    try:
        with ThreadPoolExecutor(24) as ex:
            found = dict(zip(tree, ex.map(lambda p: describe(p, *tree[p]), tree)))
    except FetchError as e:  # never describe a corpus from a file that was there but could not be read
        print(f'error: {e}; nothing written', file=sys.stderr)
        return 2
    corpora = []
    for path in sorted(tree):
        entry, _ = found[path]
        branches = entry.pop('_branches')
        merged = {**before.get(path, {}), **entry}  # what this build knows wins; what only the old build knew is kept
        merged['path'] = path
        # future_branch is the branch tools/law.py reads: data/future-pins.tsv's, which tools/future_pins.py writes
        # only for a branch that has caught up with the pin. A future branch the repository has (the one the corpus
        # names, else the first of future_pins.FUTURE_NAMES, as future_pins.py picks it) that is not read, because
        # it is behind main or diverged, is future_branch_unread: its laws are not in any answer.
        stated = merged.get('future_branch') or merged.get('future_branch_unread')
        if path in read_future:
            merged['future_branch'] = read_future[path]  # in place, so the manifest keeps its key order
            merged.pop('future_branch_unread', None)
        else:
            merged.pop('future_branch', None)
            unread = future_pins.pick_branch(sorted(branches), stated)
            if unread:
                merged['future_branch_unread'] = unread
            else:
                merged.pop('future_branch_unread', None)
        corpora.append(merged)

    # jurisdiction.json for every folder that holds a corpus or a folder that does
    files = set(git('ls-tree', '-r', '--name-only', 'HEAD').splitlines())

    def read(folder: str) -> dict:
        name = f'{folder}/jurisdiction.json' if folder else 'jurisdiction.json'
        return json.loads(git('show', f'HEAD:{name}')) if name in files else {}
    folders: dict[str, dict] = {}
    for path in tree:
        parts = path.split('/')
        for i in range(1, len(parts)):
            folder = '/'.join(parts[:i])
            if folder not in folders:
                folders[folder] = read(folder)
    for path in tree:  # a folder with no file of its own takes its corpus repository's description of itself
        _, jj = found[path]
        folder = path.rsplit('/', 1)[0]
        if jj and not folders[folder].get('name'):
            folders[folder].update({k: jj[k] for k in ('name', 'level', 'code') if k in jj})
            if jj.get('path'):
                folders[folder]['iso_path'] = jj['path']
    for path in tree:  # a folder that holds only other folders (a state with no corpus of its own, its cities in it)
        _, jj = found[path]
        parent = (jj or {}).get('parent') or ''
        container = path.rsplit('/', 2)[0] if path.count('/') >= 3 else None
        if container and '-' in parent and not folders[container].get('iso_path'):
            folders[container].update({'iso_path': parent, 'code': parent.upper(), 'level': 'subdivision'})
    def country_code(folder: str) -> str:
        return str(folders.get(folder.split('/')[0], {}).get('code') or '').upper()

    for folder, body in folders.items():
        body.setdefault('name', folder.rsplit('/', 1)[-1].replace('-', ' ').title())
        depth, leaf = folder.count('/'), folder.rsplit('/', 1)[-1]
        # One level vocabulary: "country" (or the EU's "supranational") only at the top; the folder for a whole
        # country's law is named by its own word (national, federal, bund, union, uk); anything below that is a
        # subdivision, whatever its repository called it (a place name, or "country").
        if depth == 0:
            body['level'] = body.get('level') if body.get('level') in ('country', 'supranational', 'world') else 'country'
        elif depth == 1 and leaf in LEVELS_WHOLE:
            body['level'] = leaf
        elif body.get('level') in (None, 'country', leaf) or body.get('level', '').replace(' ', '-') == leaf:
            body['level'] = 'subdivision'
        body['code'] = subdivision_code(body.get('code'), country_code(folder), depth)
        if depth >= 1 and leaf not in LEVELS_WHOLE and body['code'] in ('', country_code(folder)):
            # a subdivision with no code of its own, or its country's (Northwest Territories as CA)
            body['code'] = SUBDIVISION_CODES.get(folder, '')
        if not body['code']:
            body.pop('code')
        body['path'] = folder
        body['jurisdictions'] = sorted(f for f in folders if f.rsplit('/', 1)[0] == folder and '/' in f)
        body['corpora'] = sorted(p for p in tree if p.rsplit('/', 1)[0] == folder)
        # the kinds of history (CORPUS-STANDARD.md) the corpora in this folder or below it hold
        body['histories'] = sorted({c['history'] for c in corpora if c['path'].startswith(f'{folder}/') and c.get('history')})
    world = read('')
    # every country folder in the tree (one with only its SOURCES.md included); a folder no longer in it drops out
    world['jurisdictions'] = sorted({f for f in world.get('jurisdictions', []) if f'{f}/jurisdiction.json' in files}
                                    | {f for f in folders if '/' not in f})
    world['histories'] = sorted({c['history'] for c in corpora if c.get('history')})
    for c in corpora:  # a corpus's code and ISO path, in the same form as its folder's
        cc = country_code(c['path'])
        parts = c['path'].split('/')
        whole = len(parts) >= 3 and parts[1] in LEVELS_WHOLE  # federal or national law: the country's own code
        c['code'] = cc if whole and cc else subdivision_code(c.get('code'), cc, c['path'].count('/') - 1)
        if not whole and c['code'] in ('', cc):  # below the country, never the country's own code: its folder's
            c['code'] = folders.get(c['path'].rsplit('/', 1)[0], {}).get('code', '')
        if not c['code']:
            c.pop('code')
        if not c.get('iso_path') and cc:
            c['iso_path'] = '/'.join([cc.lower()] + c['path'].split('/')[1:])
    unread = [c['path'] for c in corpora if c.get('described_by') == 'path']
    if unread:  # nothing could be read from these repositories: private without a token, or gone
        print(f'warning: {len(unread)} corpus repositories gave no corpus.json, data/repo.json or jurisdiction.json '
              f'(private without a token, or missing), so they are described by their path only: {unread[:10]}',
              file=sys.stderr)

    # countries are the top-level folders of level "country" (the EU, level "supranational", is not one)
    listed = [f for f in world['jurisdictions'] if (folders.get(f) or read(f)).get('level', 'country') == 'country']
    holding = sorted({c['path'].split('/')[0] for c in corpora} & set(listed))
    with_text = {c['path'].split('/')[0] for c in corpora if c.get('history') != 'metadata-only'} & set(holding)
    manifest = {**old,
                'date_rule': 'Each corpus is read from its own history at the commit the tree pins: the In-force trailer '
                             'of each commit is authoritative (git cannot store dates before 1970). Root commits up to '
                             '2 November 2026 are in in-force order; since then each one moves pins forward.',
                'future_rule': "Most corpora keep laws not yet in force on a future branch; a few keep them on main, "
                               "dated ahead, and the tools show them only from that date.",
                'countries': len(with_text),
                'countries_rule': 'countries counts the country folders with at least one corpus that holds law '
                                  'text; countries_listed counts every country folder, countries_catalogue_only names '
                                  'those whose corpora hold catalogue entries only, countries_without_corpus those '
                                  'with no corpus yet (only SOURCES.md).',
                'countries_listed': len(listed),
                'countries_catalogue_only': sorted(set(holding) - with_text),
                'countries_without_corpus': sorted(set(listed) - set(holding)),
                'awaiting_corpus_json': sorted(c['path'] for c in corpora if c.get('described_by') != 'corpus.json'),
                'corpora': corpora}
    pinned_urls = {f"https://github.com/{repo}.git".lower() for _, repo in tree.values()}
    manifest['not_pinned'] = [n for n in old.get('not_pinned', [])
                              if str(n.get('repo', '')).removesuffix('/').lower() not in pinned_urls]
    if not manifest['not_pinned']:
        manifest.pop('not_pinned')
    manifest.pop('described_at', None)  # it named the commit described, which changed with every commit
    out = {'manifest.json': json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
           'jurisdiction.json': json.dumps(world, ensure_ascii=False, indent=2) + '\n'}
    for folder, body in folders.items():
        out[f'{folder}/jurisdiction.json'] = json.dumps(body, ensure_ascii=False, indent=2) + '\n'
    changed = []
    for name, text in out.items():
        p = ROOT / name
        current = p.read_text(encoding='utf-8').replace('\r\n', '\n') if p.exists() else None
        if current != text:
            changed.append(name)
            if not check:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(text.encode('utf-8'))
    print(f"{len(corpora)} corpora, {len(folders)} folders; {len(changed)} file(s) {'would change' if check else 'written'}")
    if check:
        for name in changed[:20]:
            print('  ', name)
    # each folder's front page (README.md) and its page/repos fields, from the files just written
    sys.path.insert(0, str(ROOT / 'tools'))
    import folder_readmes
    pages = folder_readmes.write(check)
    print(f"{len(pages)} folder page(s) {'would change' if check else 'written'}")
    if check:
        for name in pages[:20]:
            print('  ', name)
    return 1 if check and (changed or pages) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
