"""Figure: for each of the six restatements, what became of the provisions in force at the old locations the day
before, as the official tables and the record say. One bar per restatement, split into mapped to a new section,
kept as a statutory note or omitted with a stated reason, and accounted for by nothing.

    python tools/figure.py  ->  results/recodification.svg
"""
import os, sys, csv, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import BASE

R = os.path.join(BASE, 'results')
rows = {r['title']: r for r in csv.DictReader(open(os.path.join(R, 'per_title.tsv'), encoding='utf-8'), delimiter='\t')}
lean = open(os.path.join(R, 'lean_run.txt'), encoding='utf-8').read()
m = re.search(r'46A\.tsv: old (\d+); mapped (\d+); omitted (\d+); unaccounted (\d+)', lean)
app = tuple(int(x) for x in m.groups())

bars = []
for t, year in [('36', 1998), ('40', 2002), ('46', 2006), ('51', 2010), ('41', 2011), ('54', 2014)]:
    r = rows[t]
    if t == '46':
        # the record does not hold 46 App.; its provisions are those the table names (each section or range once)
        n, mp, om, un = app
        lab = f'Title 46 ({year})'
        sub = f'{n:,} App. provisions named in the table; plus 404 sections of title 46 itself'
    else:
        n = int(r['old_provisions'])
        mp = int(r['mapped'])
        om = int(r['omitted_with_reason']) + int(r['kept_as_note']) + int(r['explained_only_by_code_notes'])
        un = int(r['unaccounted'])
        lab = f'Title {t} ({year})'
        sub = f'{n:,} provisions in force at the old locations the day before'
    bars.append((lab, sub, n, mp, om, un, r['law']))

W, X0, X1 = 1400, 330, 1180
Y0, RH = 200, 74
H = Y0 + RH * len(bars) + 150
F = "IBM Plex Sans,system-ui,sans-serif"
M = "JetBrains Mono,ui-monospace,monospace"
col = {'map': '#2a3a4c', 'om': '#ffb35c', 'un': '#ff6a55'}
o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
     f'aria-label="For six titles of the US Code restated as positive law between 1998 and 2014, the share of old '
     f'provisions the official tables map to a new section, omit with a reason, or leave unaccounted">',
     f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
     f'<text x="44" y="60" font-family="{F}" font-size="24" fill="#9aa6b5">Six titles restated: where every old provision went</text>']
tot = sum(b[2] for b in bars)
stats = [(f'{tot:,}', 'OLD PROVISIONS'), (f'{sum(b[3] for b in bars):,}', 'MAPPED'),
         (f'{sum(b[4] for b in bars):,}', 'OMITTED, WITH A REASON'), (f'{sum(b[5] for b in bars)}', 'UNACCOUNTED')]
for i, (v, s) in enumerate(stats):
    xx = 44 + i * 250
    o.append(f'<text x="{xx}" y="120" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
    o.append(f'<text x="{xx}" y="142" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
for i, (lab, sub, n, mp, om, un, law) in enumerate(bars):
    y = Y0 + i * RH
    o.append(f'<text x="44" y="{y + 20}" font-family="{F}" font-weight="600" font-size="17" fill="#eef1f5">{lab}</text>')
    o.append(f'<text x="44" y="{y + 40}" font-family="{M}" font-size="11" fill="#8b97a6">{law}</text>')
    x = X0
    for v, c in ((mp, 'map'), (om, 'om'), (un, 'un')):
        w = (X1 - X0) * v / n
        if c == 'un' and v:
            w = max(w, 4)
        o.append(f'<rect x="{x:.1f}" y="{y + 6}" width="{w:.1f}" height="26" fill="{col[c]}"/>')
        x += w
    o.append(f'<text x="{X0}" y="{y + 52}" font-family="{F}" font-size="12" fill="#8b97a6">{sub}</text>')
    o.append(f'<text x="{X1 + 16}" y="{y + 18}" font-family="{M}" font-size="12" fill="#c9d1db">{mp:,} / {om:,}'
             f'{" / " if un else ""}<tspan fill="#ff6a55">{un if un else ""}</tspan></text>')
lx, ly = 44, Y0 + RH * len(bars) + 20
for i, (lab, c) in enumerate([('mapped to a new section', 'map'), ('kept as a note, or omitted with a stated reason', 'om'),
                              ('in no table row', 'un')]):
    xx = lx + [0, 260, 680][i]
    o.append(f'<rect x="{xx}" y="{ly}" width="12" height="12" rx="2" fill="{col[c]}"/>')
    o.append(f'<text x="{xx + 20}" y="{ly + 11}" font-family="{F}" font-size="13" fill="#c9d1db">{lab}</text>')
o.append(f'<text x="44" y="{ly + 56}" font-family="{F}" font-size="16" fill="#d6dbe2">The one provision in no row is '
         f'40 U.S.C. 207b-2, Capitol Police bonuses; it lives on at 2 U.S.C. 1927. Lean checks every row against the record.</text>')
o.append(f'<text x="44" y="{ly + 82}" font-family="{F}" font-size="13" fill="#8b97a6">Title 46: the record does not hold '
         f'the Appendix, so its provisions are those the table names. Title 46 keeps 396 of its own 404 sections; Code notes account for the other 8.</text>')
o.append('</svg>')
open(os.path.join(R, 'recodification.svg'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o))
print([(b[0], b[2:6]) for b in bars])
