"""The figures README.md and MCP.md state, written from the server's own constants.

A figure in the documentation sits between two markers, `<!-- fig:NAME -->300<!-- /fig -->`, which GitHub does not
show. This script rewrites each marked span from its source, so a limit changed in mcp_server.py changes the
documentation with it:

  python tools/doc_figures.py           rewrite the marked figures
  python tools/doc_figures.py --check   say which are stale, and exit 1 if any is (tests/test_mcp.py DocFigures)

Counts of the tree (corpora, provisions, commits) change with every pin, so the documentation does not state them:
it points at list_jurisdictions or `tools/countries.py`, which count at the time of asking. A figure no file can
supply (a download size) is given with the day it was measured, or left out.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ('README.md', 'MCP.md')
SPAN = re.compile(r'<!-- fig:([a-z_]+) -->(.*?)<!-- /fig -->', re.S)


def _n(value: int) -> str:
    return f'{value:,}'


def figures() -> dict[str, str]:
    """Every figure the documentation may mark, by name, as it should read now."""
    sys.path.insert(0, str(ROOT / 'tools'))
    sys.dont_write_bytecode = True
    import mcp_server as m
    return {
        'tools': str(len(m.TOOLS)),
        'text_limit': _n(m.MAX_TEXT),
        'brief_limit': _n(m.MAX_BRIEF),
        'citations_limit': _n(m.MAX_CITATIONS),
        'page_chars': _n(m.PAGE_CHARS),
        'page_least': _n(m.PAGE_LEAST),
        'page_most': _n(m.PAGE_MOST),
        'answer_chars': _n(m.MAX_ANSWER),
        'call_seconds': _n(m.GIT_TIMEOUT),
        'words_max': _n(m.WORDS_MAX),
        'words_seconds': _n(m.WORDS_SECONDS),
        'restore_seconds': _n(m.RESTORE_SECONDS),
        'stuck_seconds': _n(m.STUCK_SECONDS),
        'message_mb': _n(m.MAX_LINE // 1_000_000),
    }


def rewrite(text: str, values: dict[str, str]) -> tuple[str, list[str]]:
    """The text with every marked figure set from `values`, and a line for each that changed or has no source."""
    found = []

    def one(match: re.Match) -> str:
        name, old = match.group(1), match.group(2)
        if name not in values:
            found.append(f'fig:{name} has no source in tools/doc_figures.py')
            return match.group(0)
        if old != values[name]:
            found.append(f'fig:{name} reads {old!r}, should be {values[name]!r}')
        return f'<!-- fig:{name} -->{values[name]}<!-- /fig -->'

    return SPAN.sub(one, text), found


def run(check: bool) -> list[str]:
    values, stale = figures(), []
    for name in DOCS:
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        new, found = rewrite(text, values)
        stale += [f'{name}: {line}' for line in found]
        if not check and new != text:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(new)
    return stale


if __name__ == '__main__':
    check = '--check' in sys.argv[1:]
    lines = run(check)
    print('\n'.join(lines) or 'Every marked figure is current.')
    sys.exit(1 if check and lines else 0)
