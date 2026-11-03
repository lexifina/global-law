#!/usr/bin/env python3
"""Rewrite manifest.json and every jurisdiction.json from the tree as it is: every corpus the tree pins, described by
its own repository at the pinned commit. Standard library only; needs no corpus checked out (it reads each corpus's
corpus.json, data/repo.json and jurisdiction.json from GitHub at the pinned commit).

  python tools/describe.py            rewrite the files in this checkout (then commit them)
  python tools/describe.py --check    say what would change, change nothing (exit 1 if anything would)

A corpus is listed in manifest.json with its path, repository, name, code, language, coverage and dates, from its own
corpus.json where it has one, else from data/repo.json and jurisdiction.json. Every folder that holds a corpus, or a
folder that does, gets a jurisdiction.json naming its level, its code and what is inside it. Fields an earlier build
wrote and nothing here replaces are kept.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_KEYS = ('name', 'label', 'language', 'coverage', 'history', 'history_from', 'record_to', 'checked_on',
               'in_force_trailer', 'baseline_trailer', 'correction_trailer', 'citation', 'scope', 'acts', 'publisher',
               'future_branch', 'verification', 'record_note')


def git(*args: str) -> str:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout


def fetch(repo: str, sha: str, name: str) -> dict:
    url = f'https://raw.githubusercontent.com/{repo}/{sha}/{name}'
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
        except (OSError, ValueError):
            pass
    return {}


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
    code = (rj.get('country') or jj.get('code') or cj.get('code') or '')
    if code:
        entry['code'] = code.upper()
    if jj.get('path') and 'iso_path' not in entry:
        entry['iso_path'] = f"{jj['path']}/acts"
    entry.setdefault('in_force_trailer', 'In-force')
    entry['described_by'] = 'corpus.json' if cj else ('data/repo.json' if rj else ('jurisdiction.json' if jj else 'path'))
    return entry, jj


def main(argv: list[str]) -> int:
    check = '--check' in argv
    head = git('rev-parse', 'HEAD').strip()
    old = json.loads(git('show', 'HEAD:manifest.json'))
    moved = {}
    try:
        for line in git('show', 'HEAD:data/moved-paths.tsv').splitlines():
            if line and not line.startswith('#'):
                a, b = line.split('\t')[:2]
                moved[a] = b
    except subprocess.CalledProcessError:
        pass
    before = {moved.get(c['path'], c['path']): c for c in old.get('corpora', [])}
    tree = pins()
    with ThreadPoolExecutor(16) as ex:
        found = dict(zip(tree, ex.map(lambda p: describe(p, *tree[p]), tree)))
    corpora = []
    for path in sorted(tree):
        entry, _ = found[path]
        merged = {**before.get(path, {}), **entry}  # what this build knows wins; what only the old build knew is kept
        merged['path'] = path
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
    for folder, body in folders.items():
        body.setdefault('name', folder.rsplit('/', 1)[-1].replace('-', ' ').title())
        body.setdefault('level', 'subdivision')
        body['path'] = folder
        body['jurisdictions'] = sorted(f for f in folders if f.rsplit('/', 1)[0] == folder and '/' in f)
        body['corpora'] = sorted(p for p in tree if p.rsplit('/', 1)[0] == folder)
    world = read('')
    world['jurisdictions'] = sorted(set(world.get('jurisdictions', [])) | {f for f in folders if '/' not in f})

    manifest = {**old,
                'date_rule': 'Each corpus is read from its own history at the commit the tree pins: the In-force trailer '
                             'of each commit is authoritative (git cannot store dates before 1970). Root commits up to '
                             '2 November 2026 are in in-force order; since then each one moves pins forward.',
                'future_rule': "Most corpora keep laws not yet in force on a future branch; a few keep them on main, "
                               "dated ahead, and the tools show them only from that date.",
                'countries': len([f for f in world['jurisdictions'] if '/' not in f]),
                'awaiting_corpus_json': sorted(c['path'] for c in corpora if c.get('described_by') != 'corpus.json'),
                'described_at': head,
                'corpora': corpora}
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
    return 1 if check and changed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
