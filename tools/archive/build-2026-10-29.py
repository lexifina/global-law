"""Build the global-law superproject from the per-corpus law repos. Standard library only.

  python scripts/global-law/build.py <out> --date 2026-10-28 [--local ~/Documents] [--site-data FILE]

By default each corpus is read from a fresh bare clone of its published repo, so every pin can be fetched by anyone
who clones this one. `--local DIR` reads unpublished checkouts instead, for trying a corpus rebuild before it is
pushed; do not publish a build made that way.

Each corpus (the US Code, the Grundgesetz, the UK SEND provisions) stays its own repo with its own history, and
becomes a submodule at a path that names its jurisdiction: country (ISO 3166-1), then level (federal, a state's ISO
3166-2 code, ...), then the corpus. The root history interleaves every corpus's commits in the order the changes took
force, one root commit per corpus commit, each moving that corpus's pin. A root commit is therefore the state of all
the law in the tree at one moment. Rebuilding from the same corpus commits gives the same hashes; republishing after a
corpus is rebuilt means a force-push.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMITTER = ('Lexifina', 'global-law@lexifina.com')

JURISDICTIONS = {
    '': {'name': 'Git for Global Law', 'level': 'world'},
    'de': {'name': 'Germany', 'level': 'country', 'code': 'DE'},
    'de/bund': {'name': 'Bund (federal law)', 'level': 'federal', 'legislature': 'Bundestag and Bundesrat'},
    'gb': {'name': 'United Kingdom', 'level': 'country', 'code': 'GB'},
    'gb/uk': {'name': 'UK Parliament and UK ministers', 'level': 'national',
              'note': 'Devolved legislatures go beside this as gb/sct, gb/wls and gb/nir.'},
    'us': {'name': 'United States', 'level': 'country', 'code': 'US'},
    'us/federal': {'name': 'Federal law', 'level': 'federal', 'legislature': 'Congress',
                   'note': 'States go beside this by ISO 3166-2 code, for example us/ca.'},
    # Not a country: the European Union sits beside the countries, under ISO 3166's exceptionally reserved code EU.
    # Its law applies in the member states alongside their own; their folders do not nest under it.
    'eu': {'name': 'European Union', 'level': 'union', 'code': 'EU',
           'note': 'A supranational union, not a country. EU law (treaties, regulations, directives) as consolidated on EUR-Lex.'},
    'eu/union': {'name': 'Union law', 'level': 'union', 'legislature': 'European Parliament and Council'},
    'ch': {'name': 'Switzerland', 'level': 'country', 'code': 'CH'},
    'ch/bund': {'name': 'Bund (federal law)', 'level': 'federal', 'legislature': 'Federal Assembly',
                'note': 'Cantons go beside this by ISO 3166-2 code, for example ch/zh.'},
}

CORPORA = [
    {'path': 'de/bund/grundgesetz', 'repo': 'grundgesetz', 'url': 'https://github.com/lexifina/germany-law.git',
     'name': 'Grundgesetz für die Bundesrepublik Deutschland', 'label': 'Germany', 'language': 'de',
     'coverage': '1949 to the 69th amendment, matching the official text of 28 October 2026', 'in_force_trailer': 'In-Kraft',
     'record_to': '2026-10-28', 'record_note': 'Checked against gesetze-im-internet.de on 28 October 2026.'},
    {'path': 'gb/uk/send', 'repo': 'uk-law-history', 'url': 'https://github.com/lexifina/united-kingdom-law.git',
     'name': 'Special educational needs: Children and Families Act 2014 Part 3 and the SEND Regulations 2014 (selected provisions)',
     'label': 'UK', 'language': 'en', 'coverage': '2014 to 2021', 'in_force_trailer': 'In-force',
     'record_to': '2026-10-28', 'record_note': 'Checked against legislation.gov.uk on 28 October 2026.'},
    {'path': 'us/federal/usc', 'repo': 'us-code-history', 'url': 'https://github.com/lexifina/united-states-law.git',
     'name': 'United States Code, titles 1, 3, 4, 9, 11, 13, 17, 35 and 39', 'label': 'US', 'language': 'en',
     'coverage': 'the 2017 edition (current through 2018-01-12) to release point 119-134', 'in_force_trailer': 'In-force',
     'record_to': '2026-04-01', 'record_note': 'It follows the Code through release point 119-134 (release points 119-87 to 119-134 changed nothing in these titles); later laws are not in it.'},
    {'path': 'ch/bund/swiss-law', 'repo': 'swiss-law', 'url': 'https://github.com/lexifina/switzerland-law.git',
     'name': 'Swiss federal law: the Federal Constitution, the Data Protection Act and the Debt Enforcement and Bankruptcy Act',
     'label': 'Switzerland', 'language': 'de', 'coverage': 'each act from its first structured version on Fedlex (2019 onward)',
     'in_force_trailer': 'In-force', 'baseline_trailer': 'Consolidated', 'correction_trailer': 'Corrected',
     'record_to': '2026-10-28', 'record_note': 'Three acts, checked against Fedlex on 28 October 2026; the whole Classified Compilation is being built.'},
]


def git(*args: str, cwd: Path, env: dict | None = None, data: str | None = None) -> str:
    done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8', input=data,
                          env={**os.environ, **(env or {})})
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


_TRAILER = re.compile(r'^([A-Z][A-Za-z0-9-]*): (.*)$')


def trailers_all(body: str) -> dict[str, list[str]]:
    """Every trailer, with repeated keys kept in order; only the last paragraph counts, as in `git interpret-trailers`
    (the same rule as tools/law.py)."""
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
    return {k: v[0] for k, v in trailers_all(body).items()}


BASELINE_KINDS = ('baseline', 'consolidated', 'current', 'current-only')  # Kind: values that mean a starting text

# Parsed corpus histories, kept between builds beside the output folder. A corpus whose HEAD, pin, cut-off date and
# description are unchanged, read by the same builder code, is not read from git again: publish_loop.py rebuilds every
# few minutes, and most of the corpora have not moved since the last build.
PARSE_CACHE: Path | None = None


def cached(name: str, what: str, key: list, compute):
    if PARSE_CACHE is None:
        return compute()
    import hashlib
    code = b''.join(p.read_bytes() for p in (Path(__file__).resolve(), HERE / 'check_corpus.py'))
    digest = hashlib.sha256(json.dumps([key, hashlib.sha256(code).hexdigest()], sort_keys=True, default=str).encode()).hexdigest()
    path = PARSE_CACHE / f'{name}.{what}.json'
    try:
        saved = json.loads(path.read_text(encoding='utf-8'))
        if saved.get('key') == digest:
            return saved['value']
    except (OSError, ValueError):
        pass
    value = compute()
    PARSE_CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'key': digest, 'value': value}, ensure_ascii=False), encoding='utf-8')
    return value


def corpus_commits(corpus: dict, repo: Path) -> list[dict]:
    raw = git('log', '--first-parent', '--reverse', '--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%s%x1f%B%x1e', cwd=repo)
    out = []
    for i, record in enumerate(r for r in raw.split('\x1e') if r.strip()):
        sha, name, email, date, subject, body = record.strip('\n').split('\x1f', 5)
        ta = trailers_all(body)
        t = {k: v[0] for k, v in ta.items()}
        in_force = t.get(corpus['in_force_trailer'])
        kind = 'law'
        # A corpus may date its starting text and the publisher's corrections with trailers of their own
        # (Switzerland: Consolidated, Corrected), so those keep their real place in the in-force order.
        for key, k in (('baseline_trailer', 'baseline'), ('correction_trailer', 'correction')):
            if not in_force and corpus.get(key) and t.get(corpus[key]):
                in_force, kind = t[corpus[key]][:10], k
        if not in_force:
            # A printing that differs from the laws behind it (US "Printed text differs") changes the text, so it is
            # not documentation; it is dated by its commit, which the corpus sets to the edition's date.
            kind = 'baseline' if i == 0 else 'printing' if 'Printed-in' in t else 'documentation'
        # The corpus's own word wins: a commit it calls documentation (Kind: documentation), or one written by
        # Lexifina rather than by a law, is documentation even when it carries an in-force date for its placement.
        if t.get('Kind', '').strip().lower() == 'documentation' or name == 'Lexifina':
            kind = 'documentation'
        # A publisher's correction is never a law, even when it carries In-force for its place in the order
        # (Luxembourg 1252a0c: Kind: correction, Corrected:, In-force:). Found by lexifina-a7.
        elif t.get('Kind', '').strip().lower() == 'correction' or (corpus.get('correction_trailer') and corpus['correction_trailer'] in t):
            kind = 'correction'
        # A starting text the corpus labels as such (Turkey's current-only acts: Kind: consolidated) is a baseline,
        # not a law taking effect, even with In-force set for its place in the order.
        elif t.get('Kind', '').strip().lower() in BASELINE_KINDS:
            kind = 'baseline'
        out.append({'sha': sha, 'name': name, 'email': email, 'date': date, 'subject': subject,
                    'in_force': in_force or date[:10], 'kind': kind,
                    'refs': {k: t[k] for k in ('Gesetz', 'Law', 'Affecting', 'Enacted', 'Made', 'Verkündet', 'Verkuendet') if k in t},
                    # Every law a commit names, one per trailer line (Malta lists each on its own Affecting: line).
                    'affecting': ta.get('Affecting', [])})
    # A documentation commit has no in-force date of its own; dated by its commit (the build day), it would hold every
    # later law of its corpus back to that day in the merged order (Luxembourg's 2026-08-29 correction came after four
    # docs commits and landed after 2026-10-28; found by git-smol-countries-3). It takes the place of the law before
    # it, or, at the start of a corpus, of the first law after it.
    laws = [c['in_force'] for c in out if c['kind'] != 'documentation']
    prev = laws[0] if laws else None
    for c in out:
        if c['kind'] == 'documentation':
            c['in_force'] = prev or c['in_force']
        else:
            prev = c['in_force']
    return out


# Repos that hold law but cannot be pinned yet, with why; recorded in manifest.json, never silently dropped.
SKIPPED: list[dict] = []
PLACEHOLDER = 'sources, before any law'  # the subject of a country repo's scaffold commit (scripts/world-law)
import check_corpus  # noqa: E402  (scripts/global-law/check_corpus.py, beside this file)
PINS: dict[str, str] = {}  # what global-law pins now, by corpus repo name; filled in main()
UNTIL = ''  # the build date; filled in main()
WORLD = HERE.parent / 'world-law'  # countries.json and the sources register


def check_stream(corpus: dict, commits: list[dict], until: str) -> list[dict]:
    """Refuse a corpus whose dates cannot be trusted, and drop laws not yet in force on the build date.

    Every commit needs an ISO in-force date and the dates must never go back: global-law keeps each corpus's own
    order, so a corpus out of order would put the whole tree out of order. Laws adopted but not yet in force belong
    on a branch of their own (corpus.json `has_future_branch`), never on main; any that reach main are left out here
    so that main only ever holds what is in force by the build date."""
    last = ''
    for c in commits:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', c['in_force']):
            raise SystemExit(f"{corpus['path']}: commit {c['sha'][:7]} has in-force date {c['in_force']!r}, not YYYY-MM-DD")
        if c['kind'] not in ('documentation', 'printing') and c['in_force'] < last:
            raise SystemExit(f"{corpus['path']}: commit {c['sha'][:7]} goes back in time ({c['in_force']} after {last})")
        if c['kind'] not in ('documentation', 'printing'):
            last = c['in_force']
    # Keep the history only up to the first law not yet in force. A pin names a whole tree, so a commit kept after a
    # dropped one (a later docs commit) would carry the future text into the pinned state.
    kept = []
    for c in commits:
        if c['kind'] not in ('documentation', 'printing') and c['in_force'] > until:
            break
        kept.append(c)
    if len(kept) < len(commits):
        print(f"{corpus['path']}: stopped before {len(commits) - len(kept)} commits from the first one in force after "
              f"{until}; such laws belong on the corpus's future branch", file=sys.stderr)
    return kept


def is_placeholder(repo: Path) -> bool:
    """A country repo that holds only its scaffold commit (sources, no law), or nothing yet: it is never pinned. A repo
    created a moment ago by a builder has no commits at all, and `git log` would fail on it."""
    if subprocess.run(['git', 'rev-parse', '--verify', '-q', 'HEAD'], cwd=repo, capture_output=True).returncode:
        return True
    subjects = git('log', '--format=%s', cwd=repo).splitlines()
    if len(subjects) <= 1 and (not subjects or subjects[0].endswith(PLACEHOLDER)):
        return True
    # A scaffold followed only by status notes ("build in progress", "paused, not yet law"): every commit is written
    # by Lexifina, and a law commit never is (its author is the law or the publisher).
    return set(git('log', '--format=%an', cwd=repo).splitlines()) == {'Lexifina'}


def read_json(repo: Path, path: str) -> dict | None:
    try:
        return json.loads(git('show', f'HEAD:{path}', cwd=repo))
    except (RuntimeError, json.JSONDecodeError):
        return None


def read_corpus_json(repo: Path) -> dict | None:
    return read_json(repo, 'corpus.json')


def from_corpus_json(cj: dict, url: str, country: dict) -> dict:
    """The manifest entry for a corpus, from the corpus.json it ships (see git_for_law.md, "corpus.json standard")."""
    dates = cj.get('dates') or {}
    entry = {
        'path': cj['corpus'], 'url': url, 'name': cj.get('name') or country['name'],
        'label': cj.get('label') or country['name'], 'language': cj.get('language') or '',
        'coverage': cj.get('coverage') or (f"from {cj['history_from']}" if cj.get('history_from') else ''),
        'in_force_trailer': cj.get('in_force_trailer') or 'In-force',
        'baseline_trailer': cj.get('baseline_trailer') or dates.get('baseline_trailer'),
        'correction_trailer': cj.get('correction_trailer') or dates.get('correction_trailer'),
        # record_to is the last change the record holds; checked_on is the day it was checked against the source.
        # A date between the two is covered: nothing changed, so it must not be reported as past the record.
        'history_from': cj.get('history_from'), 'record_to': cj.get('record_to') or cj.get('built'),
        'checked_on': cj.get('checked_on') or cj.get('built'),
        'record_note': cj.get('record_note'), 'has_future_branch': cj.get('has_future_branch'),
        # 'current-only': the source publishes only today's text, so earlier dates show it as last updated.
        'history': cj.get('history'),
        # 'replayed': which dates were checked against an official text, in the corpus's own words.
        'verification': cj.get('verification') if isinstance(cj.get('verification'), str) else None,
        'tool': cj.get('tool'), 'citation': cj.get('citation'), 'scope': cj.get('scope'), 'corpus_json': True,
    }
    return {k: v for k, v in entry.items() if v is not None}


def slugify(name: str) -> str:
    """A country's folder name: its English name in ASCII, lower case, hyphenated (Côte d'Ivoire -> cote-d-ivoire)."""
    import unicodedata
    ascii_name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', ascii_name.lower()).strip('-')


def countries() -> list[dict]:
    return json.loads((WORLD / 'countries.json').read_text(encoding='utf-8'))['countries']


ORG = 'lexifina'
NOT_LAW = ('global-law',)  # this repository and its MCP companions also end in -law
# Repos that hold law but are not pinned until their builders follow the shared rules (git_for_law.md).
# Empty since 2026-10-28: the user asked for every country that holds law to be in the tree (Paraguay was held here).
HOLD: dict[str, str] = {
    'nauru-law': 'being rebuilt from 2 acts to the whole RONLAW corpus; pinned at the head its builder announces',
    'bermuda-law': 'being rebuilt from 6 acts to all consolidated laws; pinned at the head its builder announces',
    'canada-ontario-law': 'being rebuilt from 4 statutes to every Ontario statute; pinned at the head its builder announces',
}
# The repos built to the "gitlaw_common" contract on another machine (South America) were still being force-rewritten
# on 2026-10-28: Argentina's pinned commit left its history within an hour of a build, which breaks fresh clones. They
# were held until that machine ships corpus.json and appends only. The user asked on 2026-10-28 for them to be pinned
# anyway; a later rewrite of theirs is re-pinned by the next build (they are not under the append-only check, below).
HOLD_GITLAW_COMMON = False
# Full rebuilds announced to global-law before they were force-pushed: the repo name and the new head that replaced
# the pinned history. Only that exact head is excused from the append-only check; any later rewrite is refused again.
REWRITES_AGREED = {
    'germany-law': '6f3913a35a8ed38c01d9f1919fa1e3af0ba01f9f',  # GG plus all federal law, lexifina-ee, 2026-10-28
    'switzerland-law': '06696ea19cf23d362f02ac688ff59df3fdb14aab',  # the whole SR, lexifina-0d, 2026-10-28
    'malta-law': '7d25128590327a1ec6845f2ecd179b223bcf6a8f',  # crediting fixes, gitlaw-high-to-low, 2026-10-28
    'armenia-law': '3f01702f5e6b6d78e4f47db55ddb863d8126c80f',  # capitalised-heading fix, gitlaw-high-to-low, 2026-10-28
    'turkey-law': '7bd09670654aa06019eb03d4cae668be80b62705',  # in-force history for 280 laws, gitlaw-high-to-low, 2026-10-28
}


def github_repos() -> set[str] | None:
    """Names of the organisation's law repos on GitHub (gh CLI), or None when gh is not available."""
    done = subprocess.run(['gh', 'repo', 'list', ORG, '--limit', '1000', '--json', 'name,pushedAt'],
                          capture_output=True, encoding='utf-8')
    if done.returncode:
        print('gh is not available; reading only the repos named in countries.json', file=sys.stderr)
        return None
    PUSHED.clear()
    PUSHED.update({r['name']: r['pushedAt'] for r in json.loads(done.stdout)})
    return {n for n in PUSHED if (n.endswith('-law') or n.endswith('-regulations')) and not n.startswith(NOT_LAW)}


# When GitHub last saw a push to each repo (from the same `gh repo list` call). A kept clone whose recorded push time is
# unchanged is not fetched again: most of the ~210 repos do not change between two builds.
PUSHED: dict[str, str] = {}


def discover(out: Path, local: Path | None) -> list[tuple[dict, Path]]:
    """Every country repo that holds law, read from its corpus.json, or from FALLBACK until it ships one.

    Country repos still at their scaffold commit (sources, no law) are skipped: the tree lists the country, but there
    is nothing to pin. A repo with law but neither a corpus.json nor a fallback entry is an error, not a silent skip."""
    fallback = {c['url'].rstrip('/').removesuffix('.git').rsplit('/', 1)[1]: c for c in CORPORA}
    by_path = {c['path']: c for c in countries()}
    # Countries are built on more than one machine, so the organisation on GitHub is the source of truth for which
    # repos exist; countries.json adds the country each repo belongs to. A repo on GitHub that countries.json does not
    # know is still read, and placed by the path its corpus.json declares.
    candidates = [(c, r.rstrip('/') + '.git') for c in countries() for r in [c['repo'], *c.get('more_repos', [])]]
    on_github = github_repos()
    if on_github is not None:
        known = {url.removesuffix('.git').rsplit('/', 1)[1] for _, url in candidates}
        candidates = [(c, url) for c, url in candidates if url.removesuffix('.git').rsplit('/', 1)[1] in on_github]
        candidates += [(None, f'https://github.com/{ORG}/{name}.git') for name in sorted(on_github - known)]
    if on_github is not None and not local:
        # Fetch in parallel: each is a separate network round trip, and there are about 200.
        from concurrent.futures import ThreadPoolExecutor
        todo = [(url, CACHE / url.removesuffix('.git').rsplit('/', 1)[1]) for _, url in candidates]
        def get(job: tuple[str, Path]) -> None:
            url, path = job
            # The push time as listed before fetching: a push during the fetch leaves a newer time for the next build.
            stamp, pushed = path / 'global-law-pushed-at', PUSHED.get(path.name)
            if not path.exists():
                git('clone', '-q', '--bare', url, str(path), cwd=out)
            elif pushed and stamp.exists() and stamp.read_text(encoding='ascii').strip() == pushed:
                return  # kept from the last build and not pushed to since
            else:
                # Fetch what changed, following force-pushes, and drop deleted branches and tags.
                try:
                    git('fetch', '-q', '--prune', '--prune-tags', '--force', url, '+refs/heads/*:refs/heads/*',
                        '+refs/tags/*:refs/tags/*', cwd=path)
                except RuntimeError:  # a clone cut short by a stopped build: start it again
                    shutil.rmtree(path, onexc=lambda func, p, _e: (os.chmod(p, 0o666), func(p)))
                    git('clone', '-q', '--bare', url, str(path), cwd=out)
            if pushed:
                stamp.write_text(pushed + '\n', encoding='ascii')
        with ThreadPoolExecutor(4) as pool:  # 4, not more: hundreds of short git processes have crashed this machine
            list(pool.map(get, todo))
    found = []
    for country, url in candidates:
        name = url.removesuffix('.git').rsplit('/', 1)[1]
        if local and (local / name).exists():
            repo = local / name
        else:
            repo = CACHE / name
            if on_github is None and subprocess.run(['git', 'ls-remote', '--exit-code', url, 'HEAD'], capture_output=True).returncode:
                continue  # no such repo yet
            if not repo.exists():
                git('clone', '-q', '--bare', url, str(repo), cwd=out)
        default = default_ref(repo)
        use_ref(repo, default)  # a preview build may have left HEAD on wip
        # The preview branch shows work in progress: a repo's wip branch where it holds dated law that passes the
        # preflight, its main otherwise. main never reads wip.
        if (PREVIEW and default != WIP_REF and git_ok('rev-parse', '-q', '--verify', WIP_REF, cwd=repo)
                and not git_ok('merge-base', '--is-ancestor', WIP_REF, default, cwd=repo)):  # wip has work main lacks
            use_ref(repo, WIP_REF)
            corpus, reason = examine(country, url, name, repo, fallback, by_path, preview=True)
            if corpus:
                corpus['ref'] = 'wip'
                found.append((corpus, repo))
                continue
            use_ref(repo, default)
        corpus, reason = examine(country, url, name, repo, fallback, by_path, preview=False)
        if corpus:
            found.append((corpus, repo))
        elif reason:
            SKIPPED.append({'repo': url, 'reason': reason})
    return sorted(found, key=lambda pair: pair[0]['path'])


WIP_REF = 'refs/heads/wip'
PREVIEW = False  # set by --preview: build the preview branch from wip where it holds law
CACHE: Path = Path()  # the corpus clones; set in main()


def git_ok(*args: str, cwd: Path) -> bool:
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True).returncode == 0


def default_ref(repo: Path) -> str:
    """The branch a corpus publishes on (its GitHub default, normally main), remembered beside the clone, because a
    preview build points the clone's HEAD at wip."""
    saved = repo / 'global-law-default-head'
    if saved.exists():
        return saved.read_text(encoding='ascii').strip()
    ref = subprocess.run(['git', 'symbolic-ref', 'HEAD'], cwd=repo, capture_output=True, encoding='utf-8').stdout.strip()
    ref = 'refs/heads/main' if ref in ('', WIP_REF) else ref
    saved.write_text(ref + '\n', encoding='ascii')
    return ref


def use_ref(repo: Path, ref: str) -> None:
    subprocess.run(['git', 'symbolic-ref', 'HEAD', ref], cwd=repo, capture_output=True)


def examine(country: dict | None, url: str, name: str, repo: Path, fallback: dict, by_path: dict,
            preview: bool) -> tuple[dict | None, str | None]:
    """The corpus a repo's current HEAD describes, or why it cannot be pinned (None for a placeholder)."""
    if is_placeholder(repo):
        return None, None
    if name in HOLD and not preview:
        return None, HOLD[name]
    cj = read_corpus_json(repo)
    if cj and cj.get('corpus'):
        country = country or by_path.get(cj['corpus'].split('/')[0]) or {
            'path': cj['corpus'].split('/')[0], 'name': cj['corpus'].split('/')[0].upper()}
        corpus = from_corpus_json(cj, url, country)
    elif name in fallback:
        corpus = {**{k: v for k, v in fallback[name].items() if k != 'repo'}, 'url': url, 'corpus_json': False}
    elif (rj := read_json(repo, 'data/repo.json')) is not None and not HOLD_GITLAW_COMMON:
        # The "gitlaw_common" contract of the repos built on the other machine (South America): data/repo.json and
        # jurisdiction.json instead of corpus.json. Their `Consolidated:` trailer is a URL, so no baseline trailer.
        jur = read_json(repo, 'jurisdiction.json') or {}
        iso = (jur.get('path') or rj.get('country') or name.split('-')[0]).lower()
        country = country or by_path.get(iso) or {'path': iso, 'name': rj.get('name') or iso.upper()}
        corpus = {'path': f'{iso}/national/acts', 'url': url, 'name': rj.get('name') or country['name'],
                  'label': country.get('name') or rj.get('name'), 'language': rj.get('language', ''),
                  'coverage': '', 'in_force_trailer': 'In-force', 'record_to': git('log', '-1', '--format=%cs', cwd=repo).strip(),
                  'record_note': f"Built to the gitlaw_common contract (data/repo.json); publisher: {rj.get('publisher', 'not stated')}.",
                  'has_future_branch': bool(rj.get('future_branch')), 'corpus_json': False, 'contract': 'gitlaw_common'}
    elif preview and country:
        # Work in progress with no corpus.json yet (its builder writes the docs last): placed by countries.json.
        corpus = {'path': f"{country['path']}/national/acts", 'url': url, 'name': country['name'], 'label': country['name'],
                  'language': '', 'coverage': 'work in progress (no corpus.json yet)', 'in_force_trailer': 'In-force',
                  'record_to': git('log', '-1', '--format=%cs', cwd=repo).strip(), 'corpus_json': False}
    else:
        built_elsewhere = HOLD_GITLAW_COMMON and read_json(repo, 'data/repo.json') is not None
        return None, ('built on another machine (gitlaw_common) and still force-rewritten; '
                      'pinned once it ships corpus.json and appends only' if built_elsewhere
                      else 'holds law but has no corpus.json yet')
    if country is None:
        country = by_path.get(corpus['path'].split('/')[0], {'path': corpus['path'].split('/')[0]})
    if not corpus['path'].startswith(country['path'] + '/'):
        return None, f"corpus path {corpus['path']} is not under {country['path']}/"
    # The shared preflight (check_corpus.py), the same one country builders run before they push: append-only
    # against what global-law pins now, in-force order, ISO dates, REPRODUCE.md, corpus.json.
    pin = PINS.get(name)
    if pin and REWRITES_AGREED.get(name) == git('rev-parse', 'HEAD', cwd=repo).strip():
        pin = None
    if corpus.get('contract') == 'gitlaw_common' or preview:
        pin = None  # rewritten freely (the other machine's repos, and every wip branch): pinned at whatever it is now
    head = git('rev-parse', 'HEAD', cwd=repo).strip()
    fatal, warnings = cached(name + ('@wip' if preview else ''), 'preflight', [head, UNTIL, pin, corpus], lambda: check_corpus.problems(
        repo, UNTIL, pin, read_corpus_json(repo), legacy=not corpus.get('corpus_json', True),
        in_force_trailer=corpus['in_force_trailer'], work_in_progress=preview))
    if fatal:
        return None, '; '.join(fatal)
    if warnings:
        corpus['warnings'] = warnings
    # A local build merged over GitHub's placeholder ("bust the hold", 2026-10-29: scripts/world-law/bypass_placeholder.sh)
    # is provisional until its builder relates the two histories; it is pinned, but never silently.
    if 'BYPASSED TEMPORARILY' in git('log', '-1', '--format=%s', 'HEAD', cwd=repo):
        corpus['provisional'] = ('uploaded over the placeholder repository by a merge (scripts/world-law/'
                                 'bypass_placeholder.sh); its history is not yet related to what GitHub held')
    return corpus, None


def jurisdiction_tree(corpora: list[dict]) -> dict[str, dict]:
    """Every country in the world tree, with the levels the corpora sit in. JURISDICTIONS adds detail where known."""
    tree: dict[str, dict] = {'': JURISDICTIONS['']}
    names = {}
    for c in countries():
        info = {'name': c['name'], 'level': 'country', 'code': c['code']}
        if c.get('note'):
            info['note'] = c['note']
        info['repo'] = c['repo']
        info['build'] = c['build']
        tree[c['path']] = {**info, **JURISDICTIONS.get(c['path'], {})}
        names[c['path']] = c['name']
    for path, info in JURISDICTIONS.items():
        tree.setdefault(path, info)
    for corpus in corpora:
        iso = corpus['path'].split('/')[0]
        tree.setdefault(iso, {'name': names.get(iso, iso.upper()), 'level': 'country', 'code': iso.upper()})
        level = corpus['path'].rsplit('/', 1)[0]
        if level not in tree:
            country = level.split('/')[0]
            tree[level] = {'name': f"{names.get(country, country.upper())}: {level.split('/', 1)[1]} law", 'level': level.split('/', 1)[1]}
    return dict(sorted(tree.items()))


_REGISTER: dict | None = None


def sources_page(country_path: str) -> str | None:
    """SOURCES.md for a country folder, from the World Law Sources register (scripts/world-law)."""
    global _REGISTER
    sys.path.insert(0, str(WORLD))
    import build_countries as bc  # noqa: E402  (scripts/world-law/build_countries.py)
    reg = _REGISTER = _REGISTER or json.loads((WORLD / 'register.json').read_text(encoding='utf-8'))
    country = next((c for c in countries() if c['path'] == country_path), None)
    if country is None:
        return None  # a corpus placed by its own corpus.json under a code countries.json does not list
    rows = bc.rows_for(reg['sources'], country['name'], country['code'])
    return bc.sources_md(country['name'], rows, reg['kinds'])


def leaf_tags(repo: Path) -> dict[str, list[str]]:
    tags: dict[str, list[str]] = {}
    for line in git('tag', '--format=%(objectname) %(*objectname) %(refname:short)', cwd=repo).splitlines():
        parts = line.split()
        sha, name = (parts[1], parts[2]) if len(parts) == 3 else (parts[0], parts[1])
        tags.setdefault(sha, []).append(name)
    return tags


def merge(streams: list[list[dict]]) -> list[tuple[int, dict]]:
    """Interleave the corpora by in-force date, keeping each corpus's own order."""
    heads, out = [0] * len(streams), []
    while True:
        ready = [(streams[i][h]['in_force'], i) for i, h in enumerate(heads) if h < len(streams[i])]
        if not ready:
            return out
        _, i = min(ready)
        out.append((i, streams[i][heads[i]]))
        heads[i] += 1


def commit(out: Path, tree: str, parent: str | None, message: str, author: tuple[str, str], date: str) -> str:
    env = {'GIT_AUTHOR_NAME': author[0], 'GIT_AUTHOR_EMAIL': author[1], 'GIT_AUTHOR_DATE': date,
           'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': date}
    args = ['commit-tree', tree] + (['-p', parent] if parent else [])
    # Bytes, not text: on Windows a text-mode pipe turns each "\n" into "\r\n", which put CRs into every commit
    # message until 28 October 2026 (found by lexifina-0d).
    done = subprocess.run(['git', *args], cwd=out, capture_output=True, input=message.encode('utf-8'),
                          env={**os.environ, **env})
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.decode('utf-8', 'replace').strip()}")
    return done.stdout.decode('ascii').strip()


def person(name: str, email: str) -> str:
    """A name and email as git stores them; git itself drops '<' and '>' from names, which fast-import refuses."""
    return f"{name.replace('<', '').replace('>', '').strip()} <{email}>"


def raw_date(when: dt.datetime) -> str:
    """A date in git's raw form (seconds and offset), which `git commit-tree` stores for an ISO date."""
    offset = int((when.utcoffset() or dt.timedelta()).total_seconds()) // 60
    sign = '-' if offset < 0 else '+'
    return f'{int(when.timestamp())} {sign}{abs(offset) // 60:02d}{abs(offset) % 60:02d}'


def write(out: Path, rel: str, text: str) -> None:
    path = out / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode('utf-8'))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    ap.add_argument('--local', type=Path, help='read corpus checkouts from this folder instead of their published repos')
    ap.add_argument('--site-data', type=Path, help='also write the timeline as JSON for the /watch/global-law page')
    # Required, never "today": a rebuild on another day must give the same hashes.
    ap.add_argument('--date', required=True, help='date of the closing documentation commit, e.g. 2026-10-28')
    ap.add_argument('--preview', action='store_true',
                    help="the preview branch: pin each corpus's wip branch where it holds law that passes the preflight")
    ap.add_argument('--cache', type=Path, help='corpus clones to use instead of OUT/.git/corpus-cache (shared with a main build)')
    a = ap.parse_args()
    global PREVIEW, CACHE
    PREVIEW = a.preview

    out = a.out.resolve()
    if out.exists() and any(out.iterdir()):
        # Its own output, finished or not: a manifest, or the corpus cache a build that stopped part way leaves behind.
        if not (out / 'manifest.json').exists() and not (out / '.git' / 'corpus-cache').exists():
            raise SystemExit(f'{out} exists and is not a global-law build; refusing to replace it')
        def writable(func, path, _exc):  # git object files are read-only on Windows
            os.chmod(path, 0o666)
            func(path)
        # The corpus clones are kept (fetched, not cloned again: about 210 repos); everything else is rebuilt.
        cache = out / '.git' / 'corpus-cache'
        kept = out.parent / f'.{out.name}-corpus-cache'
        if cache.exists() and not kept.exists():
            cache.rename(kept)
        # Empty the folder rather than remove it: another program may have it open as its working directory.
        for child in out.iterdir():
            shutil.rmtree(child, onexc=writable) if child.is_dir() and not child.is_symlink() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    git('init', '-q', '-b', 'main', cwd=out)
    if (kept := out.parent / f'.{out.name}-corpus-cache').exists():
        kept.rename(out / '.git' / 'corpus-cache')
    git('config', 'core.autocrlf', 'false', cwd=out)
    CACHE = a.cache.resolve() if a.cache else out / '.git' / 'corpus-cache'
    CACHE.mkdir(parents=True, exist_ok=True)

    # The corpora: every country repo that holds law, read from its corpus.json (scripts/world-law/countries.json).
    # A corpus whose dates cannot be trusted is left out of this build (and listed), not allowed to stop it.
    found, streams, tags = [], [], []
    global UNTIL, PARSE_CACHE
    UNTIL = a.date
    # Beside the build that owns the corpus clones, so a preview build sharing them shares the parsed histories too.
    owner = CACHE.parent.parent if a.cache else out
    PARSE_CACHE = owner.parent / f'.{owner.name}-parse-cache'
    PINS.update(check_corpus.previous_pins())  # so a rewritten corpus history is caught, not pinned
    for c, repo in discover(out, a.local):
        name = c['url'].rstrip('/').removesuffix('.git').rsplit('/', 1)[1] + ('@wip' if c.get('ref') == 'wip' else '')
        key = [git('rev-parse', 'HEAD', cwd=repo).strip(), a.date, c]
        try:
            stream = cached(name, 'stream', key, lambda: check_stream(c, corpus_commits(c, repo), a.date))
        except SystemExit as why:
            SKIPPED.append({'repo': c['url'], 'reason': str(why)})
            continue
        found.append((c, repo))
        streams.append(stream)
        # Tags can move without HEAD moving, so their key is every tag's name and target.
        tag_key = [subprocess.run(['git', 'show-ref', '--tags', '-d'], cwd=repo, capture_output=True,
                                  encoding='utf-8').stdout]  # exits 1 when there are no tags
        tags.append(cached(name, 'tags', tag_key, lambda: leaf_tags(repo)))
    for s in SKIPPED:
        print(f"not pinned: {s['repo']}: {s['reason']}", file=sys.stderr)
    corpora = [c for c, _ in found]
    tree = jurisdiction_tree(corpora)
    # Readable country folders (user, 2026-10-28: "more than 2 letters so it's easier to understand which is which"):
    # germany/ for de/, united-states/ for us/. The corpora keep ISO paths in their own corpus.json; the ISO code and
    # the original path stay in jurisdiction.json and manifest.json (`code`, `iso_path`), so tools can map either way.
    folder = {c['path']: slugify(c['name']) for c in countries()}
    folder.setdefault('eu', 'european-union')
    # A territory not in countries.json (Åland, AX) is named from its own corpus.json label, never left as a code.
    for c in corpora:
        code = c['path'].split('/')[0]
        if code not in folder and c.get('label'):
            folder[code] = slugify(c['label'])
    if len(set(folder.values())) != len(folder):
        raise SystemExit('two countries share a folder name; see slugify()')
    place = lambda p: '/'.join([folder.get(p.split('/')[0], p.split('/')[0]), *p.split('/')[1:]]) if p else p  # noqa: E731
    for c in corpora:
        c['code'], c['iso_path'], c['path'] = c['path'].split('/')[0].upper(), c['path'], place(c['path'])
    tree = dict(sorted((place(p), {**info, 'iso_path': p} if p else info) for p, info in tree.items()))

    # Commit 1, at the start of git time: the jurisdiction tree and the corpus list, no law yet.
    manifest = {'title': 'Git for Global Law' + (' (preview: work in progress)' if PREVIEW else ''),
                **({'branch': 'preview', 'preview_rule': "Each corpus is pinned at its wip branch where that holds law "
                    "which passes the preflight, and at its main otherwise; `ref` says which. wip text has not passed "
                    "its builder's final checks."} if PREVIEW else {}),
                'scheme': 'country (its English name; the ISO 3166-1 code is `code`) / level (federal, national, or an ISO 3166-2 subdivision) / corpus',
                'date_rule': 'Root commits are in in-force order; the In-force trailer is authoritative (git cannot store dates before 1970).',
                'future_rule': f'Only laws in force by {a.date} are pinned; laws adopted but not yet in force stay on each corpus\'s future branch.',
                'countries': sum(1 for p, info in tree.items() if p and '/' not in p and info.get('level') == 'country'),
                'awaiting_corpus_json': [c['path'] for c in corpora if not c.get('corpus_json')],
                'not_pinned': SKIPPED,
                'corpora': [{k: v for k, v in c.items() if k not in ('repo', 'corpus_json')} for c in corpora]}
    write(out, 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    for path, info in tree.items():
        children = sorted({p for p in tree if p and p.rsplit('/', 1)[0] == path and p != path} if path else
                          {p for p in tree if p and '/' not in p})
        here = [c['path'] for c in corpora if c['path'].rsplit('/', 1)[0] == path]
        body = {**info, 'path': path or '.', 'jurisdictions': children, 'corpora': here}
        write(out, f'{path}/jurisdiction.json' if path else 'jurisdiction.json', json.dumps(body, ensure_ascii=False, indent=2) + '\n')
        if path and '/' not in path and (page := sources_page(info['iso_path'])):
            write(out, f'{path}/SOURCES.md', page)
    write(out, '.gitmodules', ''.join(f'[submodule "{c["path"]}"]\n\tpath = {c["path"]}\n\turl = {c["url"]}\n' for c in corpora))
    git('add', '-A', cwd=out)
    head = commit(out, git('write-tree', cwd=out).strip(), None,
                  'Git for Global Law: jurisdictions and corpora, before any law\n\nThe tree of jurisdictions and the list of corpora. Each later commit is one law taking\neffect in one corpus, in the order the changes took force.\n',
                  COMMITTER, '1970-01-01T00:00:00Z')

    # One root commit per corpus commit, in in-force order, each moving that corpus's pin. They are written by one
    # git fast-import: three git processes per commit took over an hour for 40,000 commits on Windows. The commits are
    # byte-identical to the ones `git commit-tree` made (same trees, messages, people and dates), so hashes are unchanged.
    last = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    count, events, chunks = 0, [], []
    for i, leaf in merge(streams):
        c = corpora[i]
        # Never earlier than its parent, so `git log --before` stays a prefix of the history.
        when = max(dt.datetime.fromisoformat(leaf['date'].replace('Z', '+00:00')), last)
        if leaf['kind'] == 'documentation' and count:
            when = last  # its own date is the build day, which would push every later root commit's date to it
        message = (f"{c['label']}: {leaf['subject']}\n\n{leaf['name']}, in {c['name']}.\n\n"
                   f"Corpus: {c['path']}\nCorpus-commit: {leaf['sha']}\nLaw: {leaf['name']}\n"
                   f"In-force: {leaf['in_force']}\nKind: {leaf['kind']}\n").encode('utf-8')
        count += 1
        chunks.append(f"commit refs/heads/global-law-build\nmark :{count}\n"
                      f"author {person(leaf['name'], leaf['email'])} {raw_date(when)}\n"
                      f"committer {person(*COMMITTER)} {raw_date(when)}\ndata {len(message)}\n".encode('utf-8'))
        chunks.append(message)
        chunks.append(((f'from {head}\n' if count == 1 else '') + f"M 160000 {leaf['sha']} {c['path']}\n\n").encode('utf-8'))
        for name in tags[i].get(leaf['sha'], []):
            chunks.append(f"reset refs/tags/{c['path']}/{name}\nfrom :{count}\n\n".encode('utf-8'))
        last = when
        events.append({'inForce': leaf['in_force'], 'corpus': c['path'], 'law': leaf['name'], 'subject': leaf['subject'],
                       'kind': leaf['kind'], 'root': count, 'leaf': leaf['sha'], 'refs': leaf['refs'],
                       'affecting': leaf['affecting']})
    if count:
        marks_file = out / '.git' / 'global-law-marks'
        done = subprocess.run(['git', 'fast-import', '--quiet', '--done', f'--export-marks={marks_file}'], cwd=out,
                              input=b''.join(chunks) + b'done\n', capture_output=True)
        if done.returncode:
            raise RuntimeError(f"git fast-import: {done.stderr.decode('utf-8', 'replace').strip()}")
        sha = dict(line.split()[:2] for line in marks_file.read_text(encoding='ascii').splitlines())
        for e in events:
            e['root'] = sha[f":{e['root']}"]
        head = sha[f':{count}']
        marks_file.unlink()
        git('update-ref', '-d', 'refs/heads/global-law-build', cwd=out)
        git('read-tree', head, cwd=out)  # the index the closing commit adds to: the last root commit's tree

    # Closing commit: the documentation and the tools, dated the build day.
    docs = [(src, src.relative_to(HERE / 'repo').as_posix()) for src in sorted((HERE / 'repo').rglob('*'))
            if src.is_file() and '__pycache__' not in src.parts
            and not any(part.startswith('.') for part in src.relative_to(HERE / 'repo').parts[:-1])]  # build caches
    docs.append((Path(__file__).resolve(), 'tools/build.py'))  # the builder ships with what it built
    docs.append((HERE / 'check_corpus.py', 'tools/check_corpus.py'))  # and the preflight every corpus must pass
    # REPRODUCE.md names the commits pinned, the number of commits and the files' blob hashes as of this build.
    pins = ''.join(f"| `{c['path']}` | {c['url'].removesuffix('.git')} | `{git('ls-tree', head, '--', c['path'], cwd=out).split()[2]}` |\n"
                   for c in corpora)
    blob = lambda p: git('hash-object', str(p), cwd=out).strip()  # noqa: E731
    fill = {'{{PINS}}': pins.rstrip('\n'), '{{COMMITS}}': str(count + 2), '{{BUILD_BLOB}}': blob(Path(__file__).resolve()),
            '{{LAW_BLOB}}': blob(HERE / 'repo/tools/law.py'), '{{TEST_BLOB}}': blob(HERE / 'repo/tests/test_law.py'),
            '{{TESTS}}': str((HERE / 'repo/tests/test_law.py').read_text(encoding='utf-8').count('\n    def test_'))}
    for src, rel in docs:
        if rel in ('REPRODUCE.md', 'README.md'):
            text = src.read_text(encoding='utf-8')
            for key, value in fill.items():
                text = text.replace(key, value)
            if PREVIEW and rel == 'README.md':
                wip = sorted(c['path'] for c in corpora if c.get('ref') == 'wip')
                text = text.replace('\n', '\n\n> **Preview branch: work in progress.** Each country is pinned at its `wip` '
                                    'branch where that holds law which passes the preflight, and at its `main` otherwise. '
                                    'Text on `wip` has not passed its builder\'s final checks. Use `main` for the checked '
                                    f'record. From `wip` here ({len(wip)}): ' + ', '.join(f'`{p}`' for p in wip) + '.\n', 1)
            write(out, rel, text)
        else:
            data = src.read_bytes()
            try:  # text ships with LF line ends, as before; anything else (images) byte for byte
                data = data.decode('utf-8').replace('\r\n', '\n').encode('utf-8')
            except UnicodeDecodeError:
                pass
            (out / rel).parent.mkdir(parents=True, exist_ok=True)
            (out / rel).write_bytes(data)
    # Named, not `add -A`: the corpus folders are not checked out and would drop the pins. One git call for all;
    # NUL-separated, so Windows text-mode stdin cannot turn the separators into CRLF.
    git('add', '--pathspec-from-file=-', '--pathspec-file-nul', cwd=out, data='\0'.join(rel for _, rel in docs))
    head = commit(out, git('write-tree', cwd=out).strip(), head,
                  'README, tools and tests: how to read the tree on any date\n', COMMITTER,
                  max(dt.datetime.fromisoformat(f'{a.date}T12:00:00+00:00'), last + dt.timedelta(seconds=1)).isoformat())
    git('update-ref', 'refs/heads/main', head, cwd=out)
    git('reset', '-q', '--hard', 'main', cwd=out)
    print(f'{count} corpus commits from {len(corpora)} corpora in {manifest["countries"]} countries -> {out} ({head[:7]})')
    if a.site_data:
        data = {'head': head, 'built': a.date, 'jurisdictions': [{'path': p, **info} for p, info in tree.items()],
                'corpora': [{k: v for k, v in c.items() if k not in ('repo', 'in_force_trailer', 'corpus_json')} for c in corpora],
                'events': events}
        a.site_data.parent.mkdir(parents=True, exist_ok=True)
        a.site_data.write_bytes((json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
        print(f'site data -> {a.site_data}')


if __name__ == '__main__':
    main()
