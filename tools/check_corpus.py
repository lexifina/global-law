"""The checks every country law repo must pass before global-law pins it. Standard library only.

  python tools/check_corpus.py <repo folder or URL> [...] [--until 2026-10-28] [--pin <sha>]

Country builders run it on their own repo before pushing; global-law's builder runs the same checks on every repo it
finds and leaves out (with the reason, in manifest.json `not_pinned`) any repo that fails. Fatal problems keep a repo
out; warnings are reported but do not. The fields it checks are those in MCP.md ("How a corpus describes itself").
Needs only git and Python: a URL is cloned bare into a temporary folder. Several repos, or a global-law checkout
(every corpus its manifest.json lists that is checked out there), are checked in one run and counted at the end.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED = ('corpus',)  # without a path the repo cannot be placed; the rest have defaults, so they only warn
EXPECTED = ('name', 'language', 'history_from', 'record_to', 'in_force_trailer')
# current-only: the source keeps no past versions (Fiji); dated as last updated. replayed: past versions were rebuilt
# by applying each amending act to the text, and only some dates are checked against an official text (`verification`).
# as-enacted: each law as first published, with later amendments not applied (a gazette is all the source has).
# metadata-only: catalogue entries only, no law text (tools/describe.py writes it for such repos), so nothing is dated.
HISTORY = ('in-force', 'current-only', 'replayed', 'as-enacted', 'metadata-only')
PLACEHOLDER = 'sources, before any law'
NO_CORPUS_JSON = 'no corpus.json'  # every problem for a missing corpus.json starts with this, so a run can count them
DATE_TRAILERS = ('In-force', 'In-Kraft', 'Corrected', 'Enacted', 'Made', 'Adopted', 'Signed', 'Published',
                 'Text-as-of')
# Consolidated: canonically the day the publisher's consolidated text took force, with its link in Source:. Most
# corpora built before 4 November 2026 wrote the link itself here, and their history is append-only, so readers and
# this check take either: tools/law.py dates a change by it only when it is a date, mcp_server.py cites it when a link.
DATE_OR_LINK_TRAILERS = ('Consolidated',)
ISO_DAY = re.compile(r'\d{4}-\d{2}-\d{2}')
LINK = re.compile(r'https?://\S')
ACT_DATES = ('Enacted', 'Made', 'Adopted', 'Dated', 'Signed')  # the act's own date, when the corpus gives one
MAINTAINER = 'Lexifina'  # the author whose Redates: and corrections readers apply (tools/law.py MAINTAINER)
# Redates: <commit> <YYYY-MM-DD>|no-date, as tools/law.py REDATES reads it (one per line, in the trailer block)
REDATES = re.compile(r'^Redates:\s*([0-9a-f]{7,40})\s+(\d{4}-\d{2}-\d{2}|no-date)\s*$')
# data/acts.json `status`: readers end an act that is repealed or expired, and never one in force or not yet in force
ACT_STATUSES = ('in force', 'not yet in force', 'repealed', 'expired', 'annulled')
ACT_DATE_FIELDS = ('repealed', 'expired', 'annulled', 'in_force')
STARTING_KINDS = ('baseline', 'consolidated', 'current', 'current-only', 'current-text', 'publisher', 'consolidation',
                  'first published version (publisher)')


def _known_kinds():
    """tools/law.py's kind_of, which says whether readers know a Kind word; None if law.py is not beside this file."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import law  # noqa: PLC0415
    except Exception:
        return None
    return law.kind_of


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8', errors='replace')


def problems(repo: Path, until: str, pin: str | None = None, corpus_json: dict | None = None,
             legacy: bool = False, in_force_trailer: str | None = None,
             work_in_progress: bool = False) -> tuple[list[str], list[str]]:
    """(fatal, warnings) for a bare or working repo. `pin` is the commit global-law pins now; `legacy` is a corpus
    still on the builder's fallback entry, which is excused from corpus.json until it ships one. `work_in_progress`
    is a wip branch read for global-law's preview: its builder writes REPRODUCE.md and corpus.json last, so their
    absence is a warning there, while dates and order are checked as for main."""
    fatal: list[str] = []
    warn: list[str] = []
    log = git('log', '--first-parent', '--reverse', '--format=%H%x1f%an%x1f%s%x1f%B%x1e', cwd=repo)
    if log.returncode:
        return [f'not a readable git repo: {log.stderr.strip()[:200]}'], []
    commits = [r.strip('\n').split('\x1f', 3) for r in log.stdout.split('\x1e') if r.strip()]
    if len(commits) <= 1 and (not commits or commits[0][2].endswith(PLACEHOLDER)):
        return ['placeholder: sources only, no law yet'], []

    files = set(git('ls-tree', '--name-only', 'HEAD', cwd=repo).stdout.split())
    if 'REPRODUCE.md' not in files:
        (warn if work_in_progress else fatal).append('no REPRODUCE.md at the root (every repo records how it was made)')
    if corpus_json is None and 'corpus.json' in files:
        try:
            corpus_json = json.loads(git('show', 'HEAD:corpus.json', cwd=repo).stdout)
        except json.JSONDecodeError as e:
            fatal.append(f'corpus.json is not valid JSON: {e}')
            corpus_json = {}
    # A build.py repo describes itself in jurisdiction.json and data/repo.json, and the reader (tools/law.py
    # with_unlisted) takes its name and code from them, with defaults for the rest: a warning, not a failure.
    descriptor = 'jurisdiction.json' in files or git('cat-file', '-e', 'HEAD:data/repo.json', cwd=repo).returncode == 0
    if not corpus_json and descriptor:
        warn.append('no corpus.json: described by jurisdiction.json and data/repo.json, so readers take the name and '
                    'code from them and use defaults for the rest (no language, coverage or record dates, the In-force '
                    'trailer, no citation rule)')
    elif not corpus_json and not legacy:
        (warn if work_in_progress else fatal).append('no corpus.json at the root')
    elif not corpus_json:
        warn.append("no corpus.json: still on the builder's fallback entry, so readers use its defaults")
    cj = corpus_json or {}
    missing = [k for k in REQUIRED if not cj.get(k)]
    if cj and missing:
        (warn if legacy else fatal).append(f"corpus.json lacks {', '.join(missing)}")
    lacking = [k for k in EXPECTED if not cj.get(k)]
    if cj and lacking:
        warn.append(f"corpus.json lacks {', '.join(lacking)} (defaults are used)")
    if cj.get('corpus') and not re.fullmatch(r'[a-z]{2}(/[a-z0-9-]+){2}', cj['corpus']):
        fatal.append(f"corpus path {cj['corpus']!r} is not <iso>/<level>/<name>")
    history = cj.get('history', 'in-force')
    if history not in HISTORY:
        fatal.append(f"corpus.json history {cj['history']!r} is not one of {', '.join(HISTORY)}")
    if cj and 'citation' not in cj:  # only of a corpus.json that exists: the descriptor warning above covers the rest
        warn.append('corpus.json has no citation rule, so citations of this law are not recognised')
    elif 'citation' in cj:
        warn.extend(citation_problems(cj['citation']))

    # A legacy corpus has no corpus.json, so the builder's fallback entry names its trailer (Germany: In-Kraft).
    trailer = cj.get('in_force_trailer') or in_force_trailer or 'In-force'
    baseline = cj.get('baseline_trailer') or (cj.get('dates') or {}).get('baseline_trailer')
    for field in ('baseline_trailer', 'correction_trailer'):
        key = cj.get(field) or (cj.get('dates') or {}).get(field)
        if key and not re.fullmatch(r'[A-Z][A-Za-z0-9-]*', str(key)):
            warn.append(f'corpus.json {field} {key!r} is not a trailer key (one word, such as Consolidated), so '
                        'readers never find it')
    last, future, dated, early = '', 0, 0, []
    before_act, ancient, not_dates, odd_kinds, no_corrects = [], [], {}, {}, []
    neither: dict[str, list[str]] = {}  # a date-or-link trailer that holds neither
    link_only: list[str] = []  # no in-force day, and a baseline trailer holding a link: readers cannot date it
    days: dict[str, int] = {}
    starting = 0
    known = _known_kinds()
    seen: set[str] = set()  # commits above this one: a Redates: can only reach back (tools/law.py _redate)
    redates: dict[str, list[str]] = {'author': [], 'malformed': [], 'target': [], 'retro': []}
    # Versions the maintainer redated `no-date`: readers take them as text as of their day, a starting text.
    no_date = {m.group(1) for _, author, _, body in commits if author == MAINTAINER for line in body.splitlines()
               if (m := REDATES.match(line.strip())) and m.group(2) == 'no-date'}
    no_date_prefixes = tuple(c for c in no_date if len(c) < 40)
    for sha, author, subject, body in commits:
        redates_lines = [line.strip() for line in body.splitlines() if line.startswith('Redates:')]
        if redates_lines and author != MAINTAINER:
            redates['author'].append(sha)  # readers apply only the maintainer's
        for line in redates_lines:
            m = REDATES.match(line)
            if not m:
                redates['malformed'].append(sha)
            elif not (m.group(1) in seen if len(m.group(1)) == 40 else any(c.startswith(m.group(1)) for c in seen))                     and git('merge-base', '--is-ancestor', m.group(1), f'{sha}^', cwd=repo).returncode:
                # not above it on the first-parent line, nor on a branch merged before it
                redates['target'].append(f'{sha[:7]}->{m.group(1)[:7]}')
        retro = next((line.partition(':')[2].strip() for line in body.splitlines() if line.startswith('Retroactive:')),
                     None)
        if retro is not None and not retro.lower().startswith('yes'):
            redates['retro'].append(sha)
        seen.add(sha)
        t = {}
        for line in body.splitlines():
            key, sep, value = line.partition(': ')
            if sep and key and ' ' not in key and key[0].isupper():
                t.setdefault(key, value.strip())
        doc = t.get('Kind', '').lower() == 'documentation' or author == 'Lexifina'
        kind = t.get('Kind', '').strip().lower()
        # Date-named trailers hold dates (YYYY-MM-DD); a link belongs in Text-source: or Source: (corpus standard).
        for key in DATE_TRAILERS:
            if key in t and not ISO_DAY.match(t[key]):
                not_dates.setdefault(key, []).append(sha)
        for key in DATE_OR_LINK_TRAILERS:
            if key in t and not ISO_DAY.match(t[key]) and not LINK.match(t[key]):
                neither.setdefault(key, []).append(sha)
        if baseline and not doc and baseline in t and not ISO_DAY.match(t[baseline]) and not t.get(trailer) \
                and not ISO_DAY.match(t.get('Text-as-of', '')):
            link_only.append(sha)
        if not doc and known is not None and kind and known(kind)[1] is not None:
            odd_kinds.setdefault(kind, []).append(sha)
        if kind == 'correction' and 'Corrects' not in t:
            no_corrects.append(sha)
        when = t.get(trailer) or (t.get(baseline) if baseline and re.match(r'\d{4}-\d{2}-\d{2}', t.get(baseline, '')) else None)
        if when is None:
            continue
        dated += 1
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', when[:10]) or len(when) not in (10,):
            fatal.append(f'{sha[:7]}: {trailer} {when!r} is not YYYY-MM-DD')
            continue
        if doc:
            continue
        own = next((t[k][:10] for k in ACT_DATES if re.match(r'\d{4}-\d{2}-\d{2}', t.get(k, ''))), None)
        if own and when[:10] < own and not t.get('Retroactive', '').lower().startswith('yes'):
            before_act.append(sha)  # in force before the act itself was made, with no Retroactive: saying why
        elif when[:10] < (cj.get('earliest') or '1500-01-01'):
            ancient.append(sha)
        days[when[:10]] = days.get(when[:10], 0) + 1
        if kind in STARTING_KINDS or 'Text-as-of' in t or sha in no_date or sha.startswith(no_date_prefixes or ('-',)):
            starting += 1
        if when < last:
            # An end block: an older act or version found late and appended after later-dated commits (main only
            # grows by fast-forward). Readers resolve each provision by its In-force trailer, not commit order
            # (tools/law.py file_commit), so this is reported, not refused.
            early.append(sha)
        last = max(last, when)
        if when > until:
            future += 1
    if not dated:
        # A metadata-only corpus holds catalogue entries, not law text: it has nothing to date.
        (warn if history == 'metadata-only' else fatal).append(f'no commit carries the {trailer} trailer')
    if early:
        warn.append(f'{len(early)} commit(s) are in force before a commit above them (end blocks appended after later '
                    f'dates, first {early[0][:7]}); readers order by {trailer}, so this is allowed')
    if future:
        warn.append(f'{future} commit(s) on main are in force after {until}; readers apply each from its {trailer} '
                    'date only, but a future branch keeps main the law in force today')
    if before_act:
        warn.append(f'{len(before_act)} commit(s) are in force before the act itself was made (Enacted/Made/Signed), '
                    f'with no Retroactive: trailer, first {before_act[0][:7]}: a date taken from the wrong field?')
    if ancient:
        warn.append(f"{len(ancient)} commit(s) are in force before {cj.get('earliest') or '1500'}, first {ancient[0][:7]}; "
                    'set corpus.json earliest if the record really reaches that far back')
    total = sum(days.values())
    if total >= 20:
        day_, n = max(days.items(), key=lambda kv: kv[1])
        if n / total >= 0.3 and starting < n:
            warn.append(f'{n} of {total} dated commits ({n * 100 // total}%) take force on one day, {day_}, and are not '
                        'marked as starting texts: if that is the day the text was read, write Text-as-of (and '
                        'In-force-basis: source gives no date), not an in-force date')
    for key, shas in sorted(not_dates.items()):
        warn.append(f'{len(shas)} commit(s) have a {key}: trailer that is not a date (first {shas[0][:7]}); a link '
                    'belongs in Source: or Text-source:')
    for key, shas in sorted(neither.items()):
        warn.append(f'{len(shas)} commit(s) have a {key}: trailer that is neither a date (canonical) nor a link '
                    f'(first {shas[0][:7]})')
    if link_only:
        warn.append(f'{len(link_only)} commit(s) have no {trailer} day and a {baseline}: trailer (the corpus.json '
                    f'baseline_trailer) holding a link, not a date, so readers cannot date them (first '
                    f'{link_only[0][:7]}); write the date there and the link in Source:')
    if odd_kinds:
        warn.append('Kind values readers do not know (read as laws): ' +
                    ', '.join(f'{k!r} ({len(v)})' for k, v in sorted(odd_kinds.items(), key=lambda kv: -len(kv[1]))[:12]))
    if no_corrects:
        warn.append(f'{len(no_corrects)} correction(s) have no Corrects: trailer, so readers apply each as an ordinary '
                    f'version from its In-force date, first {no_corrects[0][:7]}')

    if redates['author']:
        warn.append(f"{len(redates['author'])} commit(s) carry Redates: by an author other than {MAINTAINER}, which "
                    f"readers ignore (first {redates['author'][0][:7]}); append them again as {MAINTAINER}")
    if redates['malformed']:
        warn.append(f"{len(redates['malformed'])} commit(s) have a Redates: line that is not "
                    f"'Redates: <commit> <YYYY-MM-DD>|no-date', which readers ignore (first {redates['malformed'][0][:7]})")
    if redates['target']:
        # A warning, not a failure: readers skip it, and an append-only history cannot take it back, only redate again.
        warn.append(f"{len(redates['target'])} Redates: name(s) no commit above them in the history, which readers "
                    f"ignore (first {redates['target'][0]})")
    if redates['retro']:
        warn.append(f"{len(redates['retro'])} commit(s) have a Retroactive: trailer that does not start with 'yes', "
                    f"which readers ignore (first {redates['retro'][0][:7]}); write 'Retroactive: yes; <provision>'")
    if 'data' in files:
        acts_fatal, acts_warn = acts_problems(repo)
        fatal.extend(acts_fatal)
        warn.extend(acts_warn)

    stale = stale_at_head(repo, trailer, until) if early else []
    if stale:
        warn.append(f'{len(stale)} file(s) hold an older version at HEAD than the one in force on {until} (an older '
                    f'version appended after a newer one, and the newer text not written again), e.g. {stale[0]}: '
                    'readers by date are right, but GitHub and plain git show outdated text; write the in-force text '
                    'again after appending an older version')

    if pin:
        if git('cat-file', '-e', f'{pin}^{{commit}}', cwd=repo).returncode:
            fatal.append(f'history rewritten: the pinned commit {pin[:7]} is no longer in the repo (main must be append-only)')
        elif git('merge-base', '--is-ancestor', pin, 'HEAD', cwd=repo).returncode:
            fatal.append(f'history rewritten: the pinned commit {pin[:7]} is not an ancestor of main (main must be append-only)')
    return fatal, warn


def acts_problems(repo: Path) -> tuple[list[str], list[str]]:
    """(fatal, warnings) for data/acts.json at HEAD, which readers use to end a repealed or expired act's files
    (tools/law.py act_ends): it must parse as {"acts": [...]}, its dates must be YYYY-MM-DD and each path a folder."""
    shown = git('show', 'HEAD:data/acts.json', cwd=repo)
    if shown.returncode:
        return [], []
    try:
        acts = json.loads(shown.stdout).get('acts')
    except (json.JSONDecodeError, AttributeError):
        acts = None
    if not isinstance(acts, list):
        return ['data/acts.json is not {"acts": [...]} JSON, so readers end no act it records'], []
    folders = set(git('ls-tree', '-r', '-d', '--name-only', 'HEAD', cwd=repo).stdout.splitlines())
    no_path, no_folder, statuses = [], [], {}
    bad_dates: dict[str, list[str]] = {}
    for i, a in enumerate(acts):
        folder = str(a.get('path') or a.get('slug') or '').strip('/') if isinstance(a, dict) else ''
        if not folder:
            no_path.append(str(i))
            continue
        if folder not in folders:
            no_folder.append(folder)
        for key in ACT_DATE_FIELDS:
            d = a.get(key)
            if d not in (None, '') and not (isinstance(d, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', d)):
                bad_dates.setdefault(key, []).append(f'{folder}: {d!r}')
        status = str(a.get('status') or '').strip().lower()
        if status and status not in ACT_STATUSES:
            statuses.setdefault(status, []).append(folder)
    warn = []
    if no_path:
        warn.append(f'data/acts.json: {len(no_path)} entr(ies) have no path, so readers skip them (first index '
                    f'{no_path[0]})')
    if no_folder:
        warn.append(f'data/acts.json: {len(no_folder)} path(s) name no folder at HEAD, so they end no file (first '
                    f'{no_folder[0]!r})')
    for key, bad in sorted(bad_dates.items()):
        warn.append(f'data/acts.json: {len(bad)} {key} date(s) are not YYYY-MM-DD (first {bad[0]})'
                    + ('; readers then record the end without its day' if key in ('repealed', 'expired') else ''))
    if statuses:
        warn.append(f"data/acts.json: status values readers do not know ({', '.join(ACT_STATUSES)} are): " +
                    ', '.join(f'{k!r} ({len(v)})' for k, v in sorted(statuses.items(), key=lambda kv: -len(kv[1]))[:12]))
    return [], warn


def stale_at_head(repo: Path, trailer: str, until: str) -> list[str]:
    """Files whose last-committed version (what HEAD shows) is not the version in force on `until`: the version with
    the latest in-force date on or before it. Only possible once commits are out of in-force order."""
    log = git('log', '--reverse', '--raw', '--find-renames=100%', '--no-abbrev', '--first-parent',
              '--format=%x1d%an%x1f%(trailers:only,unfold)%x1e', cwd=repo)
    if log.returncode:
        return []
    files: dict[str, list] = {}
    for order, chunk in enumerate(log.stdout.split('\x1d')[1:]):
        head, _, changes = chunk.partition('\x1e')
        author, block = head.split('\x1f', 1)
        t = dict(re.findall(r'^([A-Z][A-Za-z0-9-]*): (.*)$', block, re.M))
        doc = author == 'Lexifina' or t.get('Kind', '').lower() == 'documentation'
        when = (t.get(trailer) or '')[:10]
        for line in changes.splitlines():
            if not line.startswith(':'):
                continue
            meta, *paths = line.split('\t')
            f = meta.split()
            if f[4].startswith('R') and doc:
                files[paths[1]] = files.pop(paths[0], [])
                continue
            files.setdefault(paths[-1], []).append((order, when, doc, None if f[4].startswith('D') else f[3],
                                                    t.get('Kind', '').lower()))
    out = []
    for path, vs in files.items():
        dated = [v for v in vs if v[1] and not v[2] and v[1] <= until]
        if not dated:
            continue
        in_force = max(dated, key=lambda v: (v[1], v[0]))
        last = max(vs, key=lambda v: v[0])
        if last[3] != in_force[3] and last[1] and last[1] <= until and not last[2] and last[4] != 'correction':
            out.append(path)
    return out


def citation_problems(rule: object) -> list[str]:
    """A citation rule must work where it is used: `file` is a Python regex with two groups, and `cites` runs in
    `git grep -E`, POSIX extended syntax, which has no lookbehind, lookahead or \\d. A rule git rejects fails
    silently in the MCP server, so it is reported here."""
    if not isinstance(rule, dict) or not isinstance(rule.get('file'), str) or not isinstance(rule.get('cites'), str):
        return ['citation must be {"file": "...", "cites": "..."}']
    out = []
    try:
        if re.compile(rule['file']).groups < 2:
            out.append('citation.file needs two groups: (folder, number)')
    except re.error as e:
        out.append(f'citation.file is not a valid regex: {e}')
    pattern = rule['cites'].replace('{n}', '1')
    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / 'sample.txt'
        sample.write_text('Article 1\n', encoding='utf-8')
        done = subprocess.run(['git', 'grep', '-E', '-q', '--no-index', pattern, '--', sample.name], capture_output=True,
                              encoding='utf-8', errors='replace', cwd=tmp)
        if done.returncode not in (0, 1):
            out.append('citation.cites is not valid for git grep -E (POSIX extended: no lookbehind, lookahead or \\d): '
                       + (done.stderr.strip().splitlines() or [''])[-1][:160])
    return out


def previous_pins(url: str = 'https://github.com/lexifina/global-law.git') -> dict[str, str]:
    """The commit global-law currently pins for each corpus, keyed by the corpus repo's name (so renamed paths
    still match). Empty if global-law cannot be read."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        if git('init', '-q', '--bare', cwd=repo).returncode or git('fetch', '-q', '--depth', '1', url, 'main', cwd=repo).returncode:
            return {}
        try:
            manifest = json.loads(git('show', 'FETCH_HEAD:manifest.json', cwd=repo).stdout)
        except json.JSONDecodeError:
            return {}
        links = {}
        for line in git('ls-tree', '-r', 'FETCH_HEAD', cwd=repo).stdout.splitlines():
            mode, kind, sha, path = line.split(None, 3)
            if kind == 'commit':
                links[path] = sha
        pins: dict[str, str] = {}
        for c in manifest.get('corpora', []):
            if c['path'] not in links:
                continue
            old = c['url'].rstrip('/').removesuffix('.git').rsplit('/', 1)[1]
            pins[old] = links[c['path']]
            pins['path:' + c['path']] = links[c['path']]
        return pins


def pin_held_by(repo: Path, pins: dict[str, str]) -> str | None:
    """The global-law pin this repo holds, whatever the repo is called now. A repo renamed since global-law recorded
    its URL (swiss-law → switzerland-law) is found by the pinned commit it contains, so its append-only check is not
    skipped. Only git, no network: the commits are already in the clone."""
    shas = sorted({v for k, v in pins.items() if k.startswith('path:')})
    if not shas:
        return None
    done = subprocess.run(['git', 'cat-file', '--batch-check'], cwd=repo, input='\n'.join(shas) + '\n',
                          capture_output=True, encoding='utf-8', errors='replace')
    held = [line.split()[0] for line in done.stdout.splitlines() if line.endswith(' commit') or ' commit ' in line]
    return held[0] if len(held) == 1 else None


def targets(args: list[str]) -> tuple[list[str], int]:
    """The repos to check: each argument, or for a global-law checkout (a folder holding manifest.json) every corpus
    its manifest lists that is checked out there. Also the number listed but not checked out."""
    out, absent = [], 0
    for a in args:
        manifest = Path(a) / 'manifest.json'
        if re.match(r'https?://|git@', a) or not manifest.is_file():
            out.append(a)
            continue
        for c in json.loads(manifest.read_text(encoding='utf-8')).get('corpora', []):
            if (Path(a) / c['path'] / '.git').exists():
                out.append(str(Path(a) / c['path']))
            else:
                absent += 1
    return out, absent


def check_one(target: str, until: str, pin_arg: str | None, pins: dict[str, str]) -> tuple[list[str], list[str]]:
    """Check one repo folder or URL and print its result; (fatal, warnings)."""
    with tempfile.TemporaryDirectory() as tmp:
        if re.match(r'https?://|git@', target):
            if git('clone', '-q', '--bare', target, tmp, cwd=Path('.')).returncode:
                print(f'FAIL: cannot clone {target}')
                return [f'cannot clone {target}'], []
            repo = Path(tmp)
            name = target.rstrip('/').removesuffix('.git').rsplit('/', 1)[1]
        else:
            repo = Path(target).resolve()
            url = git('config', '--get', 'remote.origin.url', cwd=repo).stdout.strip()
            name = url.rstrip('/').removesuffix('.git').rsplit('/', 1)[-1] if url else target
        pin = pin_arg or pins.get(name) or pin_held_by(repo, pins)
        fatal, warn = problems(repo, until, pin)
    for w in warn:
        print(f'warning: {w}')
    for f in fatal:
        print(f'FAIL: {f}')
    print(f"{name}: {'FAIL' if fatal else 'pass'} ({len(fatal)} problem(s), {len(warn)} warning(s)"
          + (f'; checked against global-law pin {pin[:7]}' if pin else '; not yet pinned by global-law') + ')')
    return fatal, warn


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('repo', nargs='+', help='repo folders or URLs, or a global-law checkout (its checked-out corpora)')
    ap.add_argument('--until', default=None, help='the build date (default today)')
    ap.add_argument('--pin', default=None, help='the commit global-law pins now (default: read from global-law); '
                                                'one repo only')
    a = ap.parse_args()
    import datetime as dt
    until = a.until or dt.date.today().isoformat()
    repos, absent = targets(a.repo)
    if a.pin and len(repos) != 1:
        raise SystemExit('--pin is the pin of one repo')
    pins = {} if a.pin else previous_pins()
    results = [check_one(r, until, a.pin, pins) for r in repos]
    if len(results) > 1 or absent:
        failed = sum(1 for f, _ in results if f)
        no_cj = sum(1 for f, w in results if any(x.startswith(NO_CORPUS_JSON) for x in f + w))
        print(f'\n{len(results)} corpora checked: {len(results) - failed} pass, {failed} fail; {no_cj} of '
              f'{len(results)} have no corpus.json'
              + (f'; {absent} listed in manifest.json are not checked out here' if absent else ''))
    sys.exit(1 if any(f for f, _ in results) else 0)


if __name__ == '__main__':
    main()
