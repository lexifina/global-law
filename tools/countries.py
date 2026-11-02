#!/usr/bin/env python3
"""Choose the countries this clone holds and the MCP server serves. Standard library only.

Each body of law is a git submodule, so a clone can fetch only the countries you need: the whole tree is several GB,
one country is usually a few hundred MB or less. The MCP server serves the corpora checked out, and of those only the
jurisdictions chosen with `only`, if any.

  python3 tools/countries.py                      every jurisdiction: checked out, served, or neither
  python3 tools/countries.py add germany spain    check these out (git downloads only them)
  python3 tools/countries.py only germany         serve only these (checking out any not yet here)
  python3 tools/countries.py only --all           serve every corpus checked out

A name is a country folder ("germany", "united kingdom"), an ISO code ("de"), a level ("united-states/federal") or a
corpus path. On Windows, run it with `py` or `python`. A running MCP server sees a change within a few seconds.
"""
from __future__ import annotations

import difflib
import subprocess
import sys

import law

CONFIG = 'global-law.jurisdictions'  # in the clone's own .git/config: never committed, never shared


def corpora() -> list[dict]:
    return law.manifest()['corpora']


def checked_out(corpus: dict) -> bool:
    return (law.ROOT / corpus['path'] / '.git').exists()


def chosen() -> list[str]:
    raw = law.git('config', '--get', CONFIG, check=False)
    return [n.strip() for n in raw.split(',') if n.strip()]


def resolve(names: list[str]) -> list[dict]:
    """The corpora the names take in; stops with a suggestion for a name that takes in none."""
    found: list[dict] = []
    for name in names:
        hits = [c for c in corpora() if law.matches(c, name)]
        if not hits:
            folders = sorted({c['path'].split('/')[0] for c in corpora()})
            near = difflib.get_close_matches(name.strip().lower().replace(' ', '-'), folders, n=3)
            raise SystemExit(f'No body of law in this tree matches {name!r}.'
                             + (f" Did you mean {', '.join(near)}?" if near else '') + ' Run with no arguments to list them.')
        found += [c for c in hits if c not in found]
    return found


def add(found: list[dict]) -> bool:
    """Check out the corpora not yet here; whether any was."""
    todo = [c['path'] for c in found if not checked_out(c)]
    if not todo:
        print('Already checked out: ' + ', '.join(c['path'] for c in found))
        return False
    print('Checking out ' + ', '.join(todo) + ' (only these are downloaded) ...', flush=True)
    done = subprocess.run(['git', 'submodule', 'update', '--init', '--', *todo], cwd=law.ROOT)
    if done.returncode:
        raise SystemExit('git could not check them out; see its message above (a private repository needs access).')
    return True


def show() -> None:
    names = chosen()
    rows = []
    for c in corpora():
        here = checked_out(c)
        served = here and (not names or any(law.matches(c, n) for n in names))
        rows.append((c['path'], 'served' if served else 'checked out, not chosen' if here else 'not checked out', c['name']))
    width = max(len(p) for p, _, _ in rows)
    for path, state, name in rows:
        print(f'{path:<{width}}  {state:<24} {name[:70]}')
    served = sum(1 for _, s, _ in rows if s == 'served')
    print(f'\n{served} of {len(rows)} served by the MCP server'
          + (f" (chosen: {', '.join(names)})" if names else '') + '. Add one with: python3 tools/countries.py add <country>')


def main(argv: list[str]) -> None:
    sys.stdout.reconfigure(encoding='utf-8')  # names of laws are not ASCII; Windows consoles default to cp1252
    if not argv or argv[0] in ('list', 'ls'):
        return show()
    command, names = argv[0], argv[1:]
    if command == 'add' and names:
        if not add(resolve(names)):
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
