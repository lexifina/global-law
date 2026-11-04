"""Every recorded judgment can be read by check_precedent. Needs no corpus checked out.

  python -m unittest tests.test_judgments -v

The MCP server skips a line it cannot read without saying so, so a mistake in a judgments file would only show as a
judgment that is never checked. These tests read the files the way the server does and name the line at fault.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def here(path: str) -> str:
    """The server's own mapping of an old path to the tree's naming. Imported here, not at the top: importing the
    server narrows law.manifest() to the corpora it serves, which other test modules read when they load."""
    sys.path.insert(0, str(ROOT / 'tools'))
    sys.dont_write_bytecode = True
    import mcp_server
    return mcp_server.here(path)

FIELDS = {'decided', 'text_date', 'name', 'court', 'citation', 'url', 'how', 'law_commit'}
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')


def files() -> list[Path]:
    return sorted((ROOT / 'judgments').rglob('*.jsonl'))


def problems(path: Path) -> list[str]:
    """What is wrong with one judgments file, line by line, in the terms check_precedent reads it."""
    out = []
    rel = path.relative_to(ROOT / 'judgments').as_posix()
    provision = here(rel.removesuffix('.jsonl') + '.md')
    corpora = [c['path'] for c in json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['corpora']]
    if not any(provision.startswith(c + '/') for c in corpora):
        out.append(f'{rel}: no corpus in manifest.json holds {provision}; the file must sit at '
                   'judgments/<the provision\'s path, without .md>.jsonl')
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            j = json.loads(line)
        except json.JSONDecodeError as e:
            out.append(f'{rel}:{n}: not JSON ({e.msg}); check_precedent skips it')
            continue
        if not isinstance(j, dict):
            out.append(f'{rel}:{n}: not a JSON object')
            continue
        if not (isinstance(j.get('decided'), str) and DATE.fullmatch(j['decided'])):
            out.append(f'{rel}:{n}: "decided" must be a YYYY-MM-DD date; check_precedent skips it')
        if 'text_date' in j and not (isinstance(j['text_date'], str) and DATE.fullmatch(j['text_date'])):
            out.append(f'{rel}:{n}: "text_date" must be a YYYY-MM-DD date')
        for need in ('name', 'court', 'citation'):
            if not str(j.get(need) or '').strip():
                out.append(f'{rel}:{n}: "{need}" is missing')
        extra = set(j) - FIELDS
        if extra:
            out.append(f'{rel}:{n}: unknown field(s) {sorted(extra)}; known: {sorted(FIELDS)}')
    return out


class Judgments(unittest.TestCase):
    def test_every_judgment_line_is_readable(self):
        found = [p for f in files() for p in problems(f)]
        self.assertEqual(found, [], '\n'.join(found))

    def test_a_bad_line_is_named(self):
        """The checks themselves: a broken line and a line without its date are both reported."""
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT / 'judgments') as tmp:
            p = Path(tmp) / 'x.jsonl'
            p.write_text('{"decided": "2020-01-01", "name": "A", "court": "B", "citation": "C"}\n'
                         '{"decided": "2021-01-01", "name": broken\n'
                         '{"name": "no date"}\n', encoding='utf-8')
            found = problems(p)
        self.assertTrue(any(':2: not JSON' in f for f in found), found)
        self.assertTrue(any(':3: "decided"' in f for f in found), found)
        self.assertFalse(any(':1:' in f for f in found), found)


if __name__ == '__main__':
    unittest.main()
