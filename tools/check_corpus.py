"""The checks every country law repo must pass before global-law pins it. Standard library only.

  python scripts/global-law/check_corpus.py <repo folder or URL> [--until 2026-10-28] [--pin <sha>]

Country builders run it on their own repo before pushing; global-law's builder runs the same checks on every repo it
finds and leaves out (with the reason, in manifest.json `not_pinned`) any repo that fails. Fatal problems keep a repo
out; warnings are reported but do not. The rules are those in git_for_law.md ("corpus.json standard").
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
HISTORY = ('in-force', 'current-only', 'replayed', 'as-enacted')
PLACEHOLDER = 'sources, before any law'


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
    if not corpus_json and not legacy:
        (warn if work_in_progress else fatal).append('no corpus.json at the root')
    cj = corpus_json or {}
    missing = [k for k in REQUIRED if not cj.get(k)]
    if cj and missing:
        (warn if legacy else fatal).append(f"corpus.json lacks {', '.join(missing)}")
    lacking = [k for k in EXPECTED if not cj.get(k)]
    if cj and lacking:
        warn.append(f"corpus.json lacks {', '.join(lacking)} (defaults are used)")
    if cj.get('corpus') and not re.fullmatch(r'[a-z]{2}(/[a-z0-9-]+){2}', cj['corpus']):
        fatal.append(f"corpus path {cj['corpus']!r} is not <iso>/<level>/<name>")
    if cj.get('history', 'in-force') not in HISTORY:
        fatal.append(f"corpus.json history {cj['history']!r} is not one of {', '.join(HISTORY)}")
    if 'citation' not in cj:
        warn.append('corpus.json has no citation rule, so citations of this law are not recognised')
    else:
        warn.extend(citation_problems(cj['citation']))

    # A legacy corpus has no corpus.json, so the builder's fallback entry names its trailer (Germany: In-Kraft).
    trailer = cj.get('in_force_trailer') or in_force_trailer or 'In-force'
    baseline = cj.get('baseline_trailer') or (cj.get('dates') or {}).get('baseline_trailer')
    last, future, dated = '', 0, 0
    for sha, author, subject, body in commits:
        t = {}
        for line in body.splitlines():
            key, sep, value = line.partition(': ')
            if sep and key and ' ' not in key and key[0].isupper():
                t.setdefault(key, value.strip())
        doc = t.get('Kind', '').lower() == 'documentation' or author == 'Lexifina'
        when = t.get(trailer) or (t.get(baseline) if baseline and re.match(r'\d{4}-\d{2}-\d{2}', t.get(baseline, '')) else None)
        if when is None:
            continue
        dated += 1
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', when[:10]) or len(when) not in (10,):
            fatal.append(f'{sha[:7]}: {trailer} {when!r} is not YYYY-MM-DD')
            continue
        if doc:
            continue
        if when < last:
            fatal.append(f'{sha[:7]}: in force {when}, before the commit above it ({last}); main must be in in-force order')
        last = max(last, when)
        if when > until:
            future += 1
    if not dated:
        fatal.append(f'no commit carries the {trailer} trailer')
    if future:
        warn.append(f'{future} commit(s) on main are in force after {until}; they belong on a future branch, and '
                    f'global-law pins only the history before the first of them')

    if pin:
        if git('cat-file', '-e', f'{pin}^{{commit}}', cwd=repo).returncode:
            fatal.append(f'history rewritten: the pinned commit {pin[:7]} is no longer in the repo (main must be append-only)')
        elif git('merge-base', '--is-ancestor', pin, 'HEAD', cwd=repo).returncode:
            fatal.append(f'history rewritten: the pinned commit {pin[:7]} is not an ancestor of main (main must be append-only)')
    return fatal, warn


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
            # A renamed repo (swiss-law → switzerland-law) still answers at its old URL; key the pin by its current
            # name too, or the renamed repo looks unpinned and its append-only check is silently skipped.
            now = current_name(old)
            if now and now != old:
                pins[now] = links[c['path']]
            pins['path:' + c['path']] = links[c['path']]
        return pins


def current_name(name: str, org: str = 'lexifina') -> str | None:
    """The repo's name today, following GitHub's rename redirect (gh CLI), or None if it cannot be read."""
    done = subprocess.run(['gh', 'api', f'repos/{org}/{name}', '--jq', '.name'], capture_output=True, encoding='utf-8')
    return done.stdout.strip() or None if done.returncode == 0 else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('repo')
    ap.add_argument('--until', default=None, help='the build date (default today)')
    ap.add_argument('--pin', default=None, help='the commit global-law pins now (default: read from global-law)')
    a = ap.parse_args()
    import datetime as dt
    until = a.until or dt.date.today().isoformat()
    target = a.repo
    tmp = None
    if re.match(r'https?://|git@', target):
        tmp = tempfile.TemporaryDirectory()
        if git('clone', '-q', '--bare', target, tmp.name, cwd=Path('.')).returncode:
            raise SystemExit(f'cannot clone {target}')
        repo = Path(tmp.name)
        name = target.rstrip('/').removesuffix('.git').rsplit('/', 1)[1]
    else:
        repo = Path(target).resolve()
        url = git('config', '--get', 'remote.origin.url', cwd=repo).stdout.strip()
        name = url.rstrip('/').removesuffix('.git').rsplit('/', 1)[-1] if url else repo.name
    pin = a.pin or previous_pins().get(name)
    fatal, warn = problems(repo, until, pin)
    for w in warn:
        print(f'warning: {w}')
    for f in fatal:
        print(f'FAIL: {f}')
    print(f"{name}: {'FAIL' if fatal else 'pass'} ({len(fatal)} problem(s), {len(warn)} warning(s)"
          + (f'; checked against global-law pin {pin[:7]}' if pin else '; not yet pinned by global-law') + ')')
    sys.exit(1 if fatal else 0)


if __name__ == '__main__':
    main()
