#!/usr/bin/env python3
"""Draws the charts at the top of performance/README.md and tests/README.md, in a light and a dark version.

  python performance/charts.py

performance/chart-{light,dark}.svg: how long each command took across the corpora of one run in runs.jsonl (the
newest run that tried each command three times), with its budget from bench.py. tests/chart-{light,dark}.svg: the
tests in tests/, counted per file and grouped by what they check. Standard library only.
"""
from __future__ import annotations

import ast
import json
import math
import re
import statistics
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
THEME = {
    'light': {'surface': '#fcfcfb', 'ink': '#0b0b0b', 'ink2': '#52514e', 'muted': '#8a8984', 'grid': '#e9e8e4',
              'series': '#2a78d6', 'track': '#e3e2dd'},
    'dark': {'surface': '#1a1a19', 'ink': '#f0efec', 'ink2': '#c3c2b7', 'muted': '#8f8e87', 'grid': '#2c2c2a',
             'series': '#3987e5', 'track': '#30302d'},
}
W = 880


def svg(width: int, height: int, body: list[str], t: dict, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{escape(title)}" font-family="{FONT}">\n'
            f'<title>{escape(title)}</title>\n'
            f'<rect width="{width}" height="{height}" rx="12" fill="{t["surface"]}"/>\n' + '\n'.join(body) + '\n</svg>\n')


def text(x, y, s, size=13, fill='#000', weight=400, anchor='start', family=None) -> str:
    fam = f' font-family="{family}"' if family else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{fam}>{escape(s)}</text>')


# ---------------------------------------------------------------- performance

ROWS = [  # (label, command, timing-key prefix, budget key in bench.BUDGET)
    ('A provision today', 'show', 'show today', 'show today'),
    ('A provision on a past date', 'show', 'show past', 'show past'),
    ('Its history', 'log', 'log:', 'log'),
    ('The law behind each line', 'blame', 'blame past', 'blame past'),
    ('The law behind each word', 'words', 'words today', 'words today'),
    ('What changed between two dates', 'diff', 'diff:', 'diff'),
    ('A corpus read for the first time', 'index', 'index cold', None),
    ('A corpus read again', 'index', 'index warm', 'index warm'),
    ('The last law everywhere on a day', 'world', 'world (', 'world (every corpus checked out)'),
    ('The laws that took effect in a year', 'laws', 'laws 2026', 'laws 2026 (every corpus checked out)'),
]


def budgets() -> dict:
    src = (ROOT / 'performance' / 'bench.py').read_text(encoding='utf-8')
    m = re.search(r'^BUDGET = (\{.*?\})', src, re.S | re.M)
    return ast.literal_eval(m.group(1))


def performance_chart(mode: str) -> tuple[str, dict]:
    t = THEME[mode]
    runs = [json.loads(line) for line in (ROOT / 'performance' / 'runs.jsonl').read_text(encoding='utf-8').splitlines()
            if line.strip()]
    run = next(r for r in reversed(runs) if not r.get('quick') and r.get('tries', 1) >= 3)
    budget = budgets()
    rows = []
    for label, cmd, prefix, bkey in ROWS:
        vals = [v for k, v in run['timings'].items() if k.startswith(prefix)]
        if vals:
            rows.append((label, cmd, min(vals), statistics.median(vals), max(vals), budget.get(bkey) if bkey else None))
    lo, hi = 0.1, 100.0
    x0, x1 = 300, W - 120

    def X(v):
        return x0 + (math.log10(max(v, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)

    top, rh = 128, 34
    h = top + rh * len(rows) + 56
    day = run['when'][:10]
    n = len(run['corpora_measured'])
    b = [text(28, 42, 'How fast the tools answer on your own clone', 20, t['ink'], 600),
         text(28, 66, f'One run on {day}: {n} corpora, each command tried three times. A one-time indicator, not a '
                      f'record over time.', 13, t['ink2'])]
    # legend
    ly = 96
    b.append(f'<rect x="28" y="{ly - 4}" width="34" height="6" rx="3" fill="{t["track"]}"/>')
    b.append(text(70, ly + 2, 'fastest to slowest corpus', 12, t['ink2']))
    b.append(f'<circle cx="252" cy="{ly - 1}" r="5.5" fill="{t["series"]}" stroke="{t["surface"]}" stroke-width="2"/>')
    b.append(text(264, ly + 3, 'median', 12, t['ink2']))
    b.append(f'<rect x="330" y="{ly - 9}" width="2" height="16" fill="{t["ink2"]}"/>')
    b.append(text(340, ly + 3, 'budget: the longest a reader should wait', 12, t['ink2']))
    # grid
    for v, lab in ((0.1, '0.1 s'), (0.3, '0.3 s'), (1, '1 s'), (3, '3 s'), (10, '10 s'), (30, '30 s'), (100, '100 s')):
        x = X(v)
        b.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{top + rh * len(rows) - 6}" stroke="{t["grid"]}" '
                 f'stroke-width="1"/>')
        b.append(text(x, top + rh * len(rows) + 14, lab, 11, t['muted'], anchor='middle'))
    for i, (label, cmd, mn, med, mx, bud) in enumerate(rows):
        y = top + i * rh + 10
        b.append(text(28, y + 4, label, 13, t['ink']))
        b.append(text(x0 - 14, y + 4, cmd, 12, t['muted'], anchor='end', family=MONO))
        b.append(f'<rect x="{X(mn) - 3:.1f}" y="{y - 3}" width="{max(X(mx) - X(mn) + 6, 6):.1f}" height="6" rx="3" '
                 f'fill="{t["track"]}"/>')
        if bud:
            b.append(f'<rect x="{X(bud) - 1:.1f}" y="{y - 9}" width="2" height="18" fill="{t["ink2"]}"/>')
        b.append(f'<circle cx="{X(med):.1f}" cy="{y}" r="5.5" fill="{t["series"]}" stroke="{t["surface"]}" '
                 f'stroke-width="2"/>')
        b.append(text(x1 + 16, y + 4, f'{med:.1f} s' if med >= 0.95 else f'{med:.2f} s', 12, t['ink2']))
    b.append(text(28, h - 18, 'Times include starting Python and git. The hosted service keeps warm caches and text '
                              'snapshots, so it answers faster.', 11, t['muted']))
    data = {'day': day, 'corpora': n, 'rows': [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]}
    return svg(W, h, b, t, 'How fast the tools answer on your own clone'), data


# ---------------------------------------------------------------- tests

GROUPS = [
    ('The MCP server', ['test_mcp.py', 'test_folder_map.py', 'test_judgments.py']),
    ('Reading the law with law.py', ['test_law_fixtures.py', 'test_law.py']),
    ('Case law', ['test_caselaw.py', 'test_caselaw_us.py', 'test_caselaw_fr.py', 'test_caselaw_de.py',
                  'test_caselaw_nl.py', 'test_caselaw_pl.py', 'test_caselaw_br.py', 'test_caselaw_fi.py',
                  'test_caselaw_at.py', 'test_caselaw_index.py', 'test_us_citation_links.py']),
    ('Checks on the record', ['test_freshness.py', 'test_check_corpus.py', 'test_verify.py', 'test_describe.py']),
]


def count_tests(path: Path) -> int:
    return sum(1 for n in ast.walk(ast.parse(path.read_text(encoding='utf-8')))
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test'))


def tests_chart(mode: str) -> tuple[str, dict]:
    t = THEME[mode]
    files = {p.name: count_tests(p) for p in sorted((ROOT / 'tests').glob('test*.py'))}
    listed = {f for _, fs in GROUPS for f in fs}
    other = sorted(set(files) - listed)
    groups = [(g, sorted((f for f in fs if f in files), key=lambda f: -files[f])) for g, fs in GROUPS]
    groups += [('Other', other)] if other else []
    total = sum(files.values())
    biggest = max(files.values())
    x0, x1 = 250, W - 90
    top, rh, gh = 112, 22, 34
    gap = 16
    h = top + sum(gh + rh * len(fs) for _, fs in groups) + gap * (len(groups) - 1) + 30
    b = [text(28, 46, f'{total:,} tests', 30, t['ink'], 600),
         text(28, 72, f'in {len(files)} files, grouped by what they check. Most build a small corpus of their own, so '
                      f'they need no country checked out.', 13, t['ink2'])]
    y = top
    for i, (g, fs) in enumerate(groups):
        y += gap if i else 0
        n = sum(files[f] for f in fs)
        b.append(text(28, y + 6, g, 14, t['ink'], 600))
        b.append(text(W - 28, y + 6, f'{n:,}', 14, t['ink'], 600, anchor='end'))
        b.append(f'<line x1="28" y1="{y + 14}" x2="{W - 28}" y2="{y + 14}" stroke="{t["grid"]}" stroke-width="1"/>')
        y += gh
        for f in fs:
            v = files[f]
            w = max((x1 - x0) * v / biggest, 3)
            b.append(text(44, y + 4, f, 12, t['ink2'], family=MONO))
            b.append(f'<rect x="{x0}" y="{y - 6}" width="{w:.1f}" height="12" rx="4" fill="{t["series"]}"/>')
            b.append(text(x0 + w + 8, y + 4, str(v), 12, t['ink2']))
            y += rh
    data = {'total': total, 'groups': [(g, [(f, files[f]) for f in fs]) for g, fs in groups]}
    return svg(W, h, b, t, f'{total} tests, grouped by what they check'), data


if __name__ == '__main__':
    for mode in ('light', 'dark'):
        p, _ = performance_chart(mode)
        (ROOT / 'performance' / f'chart-{mode}.svg').write_text(p, encoding='utf-8', newline='\n')
        s, _ = tests_chart(mode)
        (ROOT / 'tests' / f'chart-{mode}.svg').write_text(s, encoding='utf-8', newline='\n')
    print('wrote performance/chart-{light,dark}.svg and tests/chart-{light,dark}.svg')
