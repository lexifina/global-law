"""Figure: the overrides the audit confirmed, each an arc from the day the court decided to the day the law that
rewrote the words it read came into force. Supreme Court decisions above the axis, lower courts below.

    python figure.py   -> overrides.svg
"""
import csv, datetime, os
O = os.path.expanduser('~/Documents/us-caselaw-lean-work/uses/overrides')
rows = list(csv.DictReader(open(f'{O}/confirmed.tsv', encoding='utf-8'), delimiter='\t'))
W, X0, X1 = 1400, 90, 1340
AX = 470
Y_MIN, Y_MAX = 1995, 2026
F = "IBM Plex Sans,system-ui,sans-serif"
M = "JetBrains Mono,ui-monospace,monospace"
def x(day):
    d = datetime.date(int(day[:4]), int(day[4:6]), int(day[6:8]))
    t = d.year + (d.timetuple().tm_yday - 1) / 365.25
    return X0 + (X1 - X0) * (t - Y_MIN) / (Y_MAX - Y_MIN)
H = 860
sup = [r for r in rows if r['tier'] == 'S']
low = [r for r in rows if r['tier'] != 'S']
o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
     f'aria-label="Arcs from the day a court decided to the day Congress rewrote the words it read, for the {len(rows)} overrides the audit confirmed">',
     f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
     f'<text x="44" y="60" font-family="{F}" font-size="24" fill="#9aa6b5">Congress answering the courts: decision, then the law that rewrote the words it read</text>']
stats = [(f"{len(rows)}", "OVERRIDES CONFIRMED"), (f"{len(sup)}", "SUPREME COURT"), (f"{len(low)}", "OTHER COURTS")]
for i, (v, s) in enumerate(stats):
    xx = 44 + i * 260
    o.append(f'<text x="{xx}" y="120" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
    o.append(f'<text x="{xx}" y="142" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
o.append(f'<line x1="{X0}" x2="{X1}" y1="{AX}" y2="{AX}" stroke="#2a3a4c" stroke-width="2"/>')
def arcs(rs, up, col):
    for r in sorted(rs, key=lambda r: r['decided']):
        a, b = x(r['decided']), x(r['law_day'])
        h = max(14, (b - a) * 0.55)
        s = -1 if up else 1
        o.append(f'<path d="M{a:.1f},{AX} C{a:.1f},{AX + s * h:.1f} {b:.1f},{AX + s * h:.1f} {b:.1f},{AX}" fill="none" stroke="{col}" stroke-width="2" stroke-opacity=".85"/>')
        o.append(f'<circle cx="{a:.1f}" cy="{AX}" r="3.5" fill="{col}"/>')
        o.append(f'<circle cx="{b:.1f}" cy="{AX}" r="3.5" fill="#eef1f5"/>')
arcs(sup, True, '#ff6a55')
arcs(low, False, '#ffb35c')
for y in range(Y_MIN, Y_MAX + 1):
    xx = x(f'{y}0101')
    if y % 5 == 0:
        o.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{AX - 6}" y2="{AX + 6}" stroke="#7d8896"/>')
        o.append(f'<rect x="{xx - 17:.1f}" y="{AX + 12}" width="34" height="16" rx="3" fill="#0f1720"/>')
        o.append(f'<text x="{xx:.1f}" y="{AX + 24}" text-anchor="middle" font-family="{M}" font-size="11" fill="#7d8896">{y}</text>')
notes = [('20080101', -1, 175, 'ADA Amendments Act (2008): Sutton, Toyota'),
         ('20090520', 1, 150, 'Fraud Enforcement and Recovery Act (2009): Allison Engine and five lower-court decisions'),
         ('20210105', 1, 60, 'FGM Act (2021): "erred"')]
for d, s_, h, t in notes:
    xx = x(d)
    yy = AX + s_ * h
    anchor = 'start' if xx > 1100 else ('end' if s_ > 0 else 'middle')
    if s_ > 0:
        o.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{AX + 8}" y2="{yy + 4:.1f}" stroke="#7d8896" stroke-dasharray="3 3"/>')
        xx += 6 if anchor == 'start' else -6
    o.append(f'<text x="{xx:.1f}" y="{yy + (18 if s_ > 0 else -8):.1f}" text-anchor="{anchor}" font-family="{F}" font-size="13" fill="#c9d1db">{t}</text>')
o.append(f'<text x="{X0}" y="{AX - 230}" font-family="{F}" font-size="14" fill="#ff6a55">Supreme Court decisions</text>')
o.append(f'<text x="{X0}" y="{AX + 230}" font-family="{F}" font-size="14" fill="#ffb35c">Courts of appeals, district and other courts</text>')
o.append(f'<text x="44" y="{H - 40}" font-family="{F}" font-size="16" fill="#d6dbe2">Each arc starts at the decision (colored dot) and ends when the law came into force (white dot). The audit read every one.</text>')
o.append('</svg>')
open(f'{O}/overrides.svg', 'w', encoding='utf-8', newline='\n').write('\n'.join(o))
print(len(rows), len(sup), len(low))
