#!/usr/bin/env python3
"""Choose the countries this clone holds and the MCP server serves. Standard library only.

Each body of law is a git submodule, so a clone can fetch only the countries you need: the whole tree is several GB,
one country is usually a few hundred MB or less. The MCP server serves the corpora checked out, and of those only the
jurisdictions chosen with `only`, if any.

  python3 tools/countries.py                      every jurisdiction: checked out, served, or neither
  python3 tools/countries.py add germany spain    check these out (git downloads only them)
  python3 tools/countries.py add --no-files romania   the history only, no files written: much quicker for a corpus
                                                  of many files; `git -C <corpus> sparse-checkout disable` adds them
  python3 tools/countries.py only germany         serve only these (checking out any not yet here)
  python3 tools/countries.py only --all           serve every corpus checked out

A name is a country folder ("germany", "united kingdom"), an ISO code ("de"), a level ("united-states/federal") or a
corpus path. On Windows, run it with `py` or `python`. A running MCP server sees a change within a few seconds.
"""
from __future__ import annotations

import difflib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # law.py beside it, however Python was started (-I drops it)
import law  # noqa: E402

CONFIG = 'global-law.jurisdictions'  # in the clone's own .git/config: never committed, never shared


def corpora() -> list[dict]:
    return law.manifest()['corpora']


def checked_out(corpus: dict) -> bool:
    """Cloned and checked out. A clone whose checkout failed (a path too long for Windows) has no index yet: `add`
    finishes it rather than call it done."""
    here = law.ROOT / corpus['path']
    if not (here / '.git').exists():
        return False
    index = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'index'], cwd=here,
                           capture_output=True, encoding='utf-8')
    return index.returncode == 0 and Path(index.stdout.strip()).exists()


def chosen() -> list[str]:
    raw = law.git('config', '--get', CONFIG, check=False)
    return [n.strip() for n in raw.split(',') if n.strip()]


def resolve(names: list[str]) -> list[dict]:
    """The corpora the names take in; stops with a suggestion for a name that takes in none."""
    found: list[dict] = []
    for name in names:
        hits = [c for c in corpora() if law.matches(c, name)]
        if not hits:
            # Countries, and states, provinces and cities by their own names
            folders = sorted({c['path'].split('/')[0] for c in corpora()} | {c['path'].split('/')[1] for c in corpora()
                                                                      if c['path'].count('/') >= 2} - law.GENERIC_LEVELS)
            near = difflib.get_close_matches(name.strip().lower().replace(' ', '-'), folders, n=3)
            raise SystemExit(f'No body of law in this tree matches {name!r}.'
                             + (f" Did you mean {', '.join(near)}?" if near else '') + ' Run with no arguments to list them.')
        found += [c for c in hits if c not in found]
    return found


def add_without_files(path: str) -> subprocess.CompletedProcess:
    """A corpus's history without writing its files: the tools read the history, not the files, and writing a corpus
    of 160,000 files (Romania) takes much longer than fetching it. The checkout holds the README only (a sparse
    checkout); `git -C <corpus> sparse-checkout disable` writes every file later."""
    pin = law.tip(path)
    url = law.git('config', '-f', '.gitmodules', f'submodule.{path}.url').strip()
    law.git('submodule', 'init', '--', path)
    steps = [['git', 'clone', '-q', '--no-checkout', url, path],
             ['git', '-C', path, 'sparse-checkout', 'set', '--no-cone', '/README.md'],
             ['git', '-C', path, '-c', 'core.longpaths=true', 'checkout', '-q', '--detach', pin]]
    for step in steps:
        done = subprocess.run(step, cwd=law.ROOT, stderr=subprocess.PIPE, encoding='utf-8', errors='replace')
        if done.returncode:
            return done
    return done


def add(found: list[dict], files: bool = True) -> bool:
    """Check out the corpora not yet here; whether any was. `files=False` fetches each history without writing its
    files (add_without_files)."""
    todo = [c['path'] for c in found if not checked_out(c)]
    if not todo:
        print('Already checked out: ' + ', '.join(c['path'] for c in found))
        return False
    print('Checking out ' + ', '.join(todo) + ' (only these are downloaded' + ('' if files else '; no files written')
          + ') ...', flush=True)
    failed = []
    for path in todo:  # one at a time: a corpus git cannot check out does not stop the others
        if not files and not (law.ROOT / path / '.git').exists():
            done = add_without_files(path)
            if done.returncode:
                sys.stderr.write(done.stderr)
                failed.append((path, done.stderr))
            continue
        # core.longpaths: some corpora have file paths past Windows' 260-character limit (a Swiss commune's
        # regulations), which git for Windows refuses to write without it. Elsewhere it changes nothing.
        # A clone never checked out (no index: nothing of the user's to lose) needs --force: git sees its HEAD already
        # at the pinned commit and would leave it empty.
        force = ['--force'] if (law.ROOT / path / '.git').exists() else []
        done = subprocess.run(['git', '-c', 'core.longpaths=true', 'submodule', 'update', '--init', *force, '--', path],
                              cwd=law.ROOT, stderr=subprocess.PIPE, encoding='utf-8', errors='replace')
        if done.returncode:
            sys.stderr.write(done.stderr)
            failed.append((path, done.stderr))
    for path, err in failed:
        why = ('a file path is too long for Windows: run `git config --global core.longpaths true`, or clone to a '
               'shorter folder such as C:\\gl, then add it again' if 'too long' in err.lower() else
               'the repository needs access you do not have' if re.search(r'not found|authentication|permission denied', err, re.I) else
               'see git\'s message above (often the network: try again)')
        print(f'Could not check out {path}: {why}.', file=sys.stderr)
    if failed and len(failed) == len(todo):
        raise SystemExit(1)
    return True


# What each corpus's record holds, from its history in manifest.json: dated versions of the law, the current text
# only, or catalogue entries with no law text
RECORD = {'in-force': 'dated', 'replayed': 'dated', 'as-enacted': 'dated', 'current-only': 'current text',
          'metadata-only': 'catalogue only'}


def show() -> None:
    names = chosen()
    rows = []
    for c in corpora():
        here = checked_out(c)
        served = here and (not names or any(law.matches(c, n) for n in names))
        rows.append((c['path'], 'served' if served else 'checked out, not chosen' if here else 'not checked out',
                     RECORD.get(c.get('history'), ''), c['name']))
    width = max(len(p) for p, _, _, _ in rows)
    for path, state, record, name in rows:
        print(f'{path:<{width}}  {state:<24} {record:<14} {name[:70]}')
    served = sum(1 for _, s, _, _ in rows if s == 'served')
    print(f'\n{served} of {len(rows)} served by the MCP server'
          + (f" (chosen: {', '.join(names)})" if names else '') + '. Add one with: python3 tools/countries.py add <country>')


def main(argv: list[str]) -> None:
    sys.stdout.reconfigure(encoding='utf-8')  # names of laws are not ASCII; Windows consoles default to cp1252
    if not argv or argv[0] in ('list', 'ls'):
        return show()
    command, names = argv[0], [a for a in argv[1:] if a != '--no-files']
    files = '--no-files' not in argv
    if command == 'add' and names:
        if not add(resolve(names), files):
            return
    elif command == 'only' and names == ['--all']:
        law.git('config', '--unset', CONFIG, check=False)
        print('The MCP server now serves every corpus checked out.')
    elif command == 'only' and names:
        found = resolve(names)
        add(found)
        law.git('config', CONFIG, ','.join(names))
        print('The MCP server now serves only: ' + ', '.join(c['path'] for c in found))
    else:
        raise SystemExit(__doc__)
    print('A running MCP server sees the change within a few seconds.')


if __name__ == '__main__':
    main(sys.argv[1:])
