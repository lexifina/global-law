#!/usr/bin/env python3
"""Write performance/index.html from performance/runs.jsonl (every bench run) and performance/findings.json (what
each deep test found and what became of it). Standard library only; the page needs no network: the charts are inline
SVG, each with the table it is drawn from below it.

  python performance/report.py
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUDGET = {'show today': 3, 'show past': 3, 'log': 3, 'blame past': 5, 'words today': 10, 'diff': 3}  # as bench.py
COMMANDS = ['show today', 'show past', 'log', 'blame past', 'words today', 'diff']
STATUSES = [('clean', 'Clean'), ('fixed', 'Fixed'), ('handed', 'Handed to a builder'), ('open', 'Open')]


def esc(x: object) -> str:
    return html.escape(str(x))


def fmt(v: float) -> str:
    return f'{v:,.0f}' if v >= 100 else f'{v:.1f}' if v >= 1 else f'{v:.2f}'


def short_name(path: str) -> str:
    """A provision path as a short label: country, then the file."""
    parts = path.split('/')
    return f'{parts[0]} · {"/".join(parts[3:])}' if len(parts) > 3 else path


class Log:
    """A log10 scale from lo to hi seconds onto x0..x1, with ticks at 0.1, 1, 10, 100, 1000."""

    def __init__(self, lo: float, hi: float, x0: float, x1: float):
        self.a, self.b = math.floor(math.log10(lo)), math.ceil(math.log10(hi))
        self.x0, self.x1 = x0, x1

    def __call__(self, v: float) -> float:
        return self.x0 + (math.log10(max(v, 10 ** self.a)) - self.a) / (self.b - self.a) * (self.x1 - self.x0)

    def ticks(self, y0: float, y1: float) -> str:
        out = ''
        for e in range(self.a, self.b + 1):
            x = self(10 ** e)
            label = {-2: '0.01 s', -1: '0.1 s', 0: '1 s', 1: '10 s', 2: '100 s', 3: '1,000 s', 4: '10,000 s'}.get(e, f'1e{e}')
            out += (f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y0}" y2="{y1}" class="grid"/>'
                    f'<text x="{x:.1f}" y="{y1 + 16}" class="tick" text-anchor="middle">{label}</text>')
        return out


def legend(items: list[tuple[str, str]]) -> str:
    return '<div class="legend">' + ''.join(
        f'<span class="key"><span class="sw" style="background:var({var})"></span>{esc(name)}</span>'
        for var, name in items) + '</div>'


def dumbbell(rows: list[dict]) -> str:
    """Before and after for each speed row that has numbers, on one log axis."""
    rows = [r for r in rows if r.get('before_s') and r.get('after_s')]
    if not rows:
        return ''
    left, right, top, step = 190, 700, 12, 34
    h = top + step * len(rows) + 24
    sc = Log(min(r['after_s'] for r in rows), max(r['before_s'] for r in rows), left, right)
    body = sc.ticks(top - 4, h - 26)
    for i, r in enumerate(rows):
        y = top + step * i + step / 2
        xb, xa = sc(r['before_s']), sc(r['after_s'])
        times = r['before_s'] / r['after_s']
        tip = esc(f"{r['short']}: {fmt(r['before_s'])} s before, {fmt(r['after_s'])} s after ({times:,.0f}× faster)")
        body += (f'<g class="hit" data-tip="{tip}"><rect x="0" y="{y - step / 2:.1f}" width="760" height="{step}" fill="transparent"/>'
                 f'<text x="{left - 12}" y="{y + 4:.1f}" class="label" text-anchor="end">{esc(r["short"])}</text>'
                 f'<line x1="{xa:.1f}" x2="{xb:.1f}" y1="{y:.1f}" y2="{y:.1f}" class="link"/>'
                 f'<circle cx="{xb:.1f}" cy="{y:.1f}" r="5.5" class="dot" style="fill:var(--before)"/>'
                 f'<circle cx="{xa:.1f}" cy="{y:.1f}" r="5.5" class="dot" style="fill:var(--after)"/>'
                 f'<text x="{right + 14}" y="{y + 4:.1f}" class="value">{times:,.0f}× faster</text></g>')
    return (legend([('--before', 'Before'), ('--after', 'After')]) +
            f'<svg viewBox="0 0 800 {h}" role="img" aria-label="Seconds before and after each fix, log scale">{body}</svg>')


def heat_color(v: float, lo: float, hi: float) -> tuple[str, bool]:
    """A step of the blue ramp by log seconds; True when the cell needs light text."""
    ramp = ['--seq-100', '--seq-200', '--seq-300', '--seq-400', '--seq-500', '--seq-600', '--seq-700']
    t = (math.log10(max(v, lo)) - math.log10(lo)) / max(1e-9, math.log10(hi) - math.log10(lo))
    i = min(len(ramp) - 1, int(t * len(ramp)))
    return ramp[i], i >= 3


def heatmap(run: dict) -> str:
    """Seconds for each command on each fixed provision in one run."""
    t = run.get('timings', {})
    provisions = []
    for k in t:
        if ': ' in k and k.split(': ', 1)[0] in COMMANDS:
            p = k.split(': ', 1)[1]
            if p not in provisions:
                provisions.append(p)
    if not provisions:
        return ''
    vals = [t[f'{c}: {p}'] for p in provisions for c in COMMANDS if f'{c}: {p}' in t]
    lo, hi = 0.5, max(vals)
    left, cw, ch, top = 330, 86, 26, 30
    w, h = left + cw * len(COMMANDS) + 4, top + ch * len(provisions) + 4
    body = ''.join(f'<text x="{left + cw * j + cw / 2}" y="{top - 10}" class="tick" text-anchor="middle">{esc(c)}</text>'
                   for j, c in enumerate(COMMANDS))
    for i, p in enumerate(provisions):
        y = top + ch * i
        body += f'<text x="{left - 10}" y="{y + ch / 2 + 4}" class="label" text-anchor="end">{esc(short_name(p))}</text>'
        for j, c in enumerate(COMMANDS):
            v = t.get(f'{c}: {p}')
            x = left + cw * j
            if v is None:
                continue
            var, dark = heat_color(v, lo, hi)
            over = v > BUDGET.get(c, 1e9)
            note = f' (over its {BUDGET[c]} s budget)' if over else ''
            body += (f'<g class="hit" data-tip="{esc(f"{c} on {p}: {fmt(v)} s{note}")}">'
                     f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="3" style="fill:var({var})"/>'
                     + (f'<rect x="{x + 2.5}" y="{y + 2.5}" width="{cw - 5}" height="{ch - 5}" rx="2" class="over"/>'
                        if over else '') +
                     f'<text x="{x + cw / 2}" y="{y + ch / 2 + 4}" text-anchor="middle" class="cell{" on" if dark else ""}">'
                     f'{fmt(v)}</text></g>')
    key = ('<div class="legend"><span class="key">Seconds, darker is slower:</span>' + ''.join(
        f'<span class="key"><span class="sw" style="background:var(--seq-{s})"></span></span>' for s in
        (100, 200, 300, 400, 500, 600, 700)) + f'<span class="key">{fmt(lo)} s or less … {fmt(hi)} s</span>'
        '<span class="key"><span class="sw over-key"></span>over its budget</span></div>')
    return key + f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Seconds per command and provision">{body}</svg>'


def index_bars(run: dict) -> str:
    """Index from nothing and loaded, per corpus, in one run."""
    t = run.get('timings', {})
    corpora = [k.split(': ', 1)[1] for k in t if k.startswith('index cold: ')]
    if not corpora:
        return ''
    corpora.sort(key=lambda c: -t[f'index cold: {c}'])
    left, right, top, step = 230, 700, 10, 30
    h = top + step * len(corpora) + 26
    hi = max(max(t[f'index cold: {c}'], t.get(f'index warm: {c}', 0)) for c in corpora)
    nice = next(n for n in (5, 10, 20, 30, 50, 100, 200, 500, 1000, 3600) if n >= hi)
    x = lambda v: left + v / nice * (right - left)
    body = ''
    for k in range(6):
        v = nice * k / 5
        body += (f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top - 4}" y2="{h - 26}" class="grid"/>'
                 f'<text x="{x(v):.1f}" y="{h - 10}" class="tick" text-anchor="middle">{v:g} s</text>')
    for i, c in enumerate(corpora):
        y = top + step * i
        cold, warm = t[f'index cold: {c}'], t.get(f'index warm: {c}')
        tip = esc(f'{c}: {fmt(cold)} s from nothing' + (f', {fmt(warm)} s loaded' if warm is not None else ''))
        body += (f'<g class="hit" data-tip="{tip}"><rect x="0" y="{y}" width="800" height="{step}" fill="transparent"/>'
                 f'<text x="{left - 10}" y="{y + step / 2 + 4}" class="label" text-anchor="end">{esc(c)}</text>'
                 f'<path d="{bar(left, x(cold), y + 4, 10)}" style="fill:var(--cold)"/>')
        if warm is not None:
            body += f'<path d="{bar(left, x(warm), y + 16, 10)}" style="fill:var(--warm)"/>'
        body += f'<text x="{x(cold) + 6:.1f}" y="{y + 13}" class="value">{fmt(cold)}</text></g>'
    return (legend([('--cold', 'From nothing (cold)'), ('--warm', 'Loaded from the cache (warm)')]) +
            f'<svg viewBox="0 0 800 {h}" role="img" aria-label="Index seconds per corpus">{body}</svg>')


def bar(x0: float, x1: float, y: float, hgt: float) -> str:
    """A horizontal bar, square at the baseline, 4px round at its end."""
    r = min(4, max(0, x1 - x0), hgt / 2)
    return (f'M{x0:.1f},{y}H{x1 - r:.1f}Q{x1:.1f},{y} {x1:.1f},{y + r}V{y + hgt - r}'
            f'Q{x1:.1f},{y + hgt} {x1 - r:.1f},{y + hgt}H{x0:.1f}Z')


TREND = [('world (every corpus checked out)', 'world', '--s1'), ('laws 2026 (every corpus checked out)', 'laws', '--s2'),
         ('median show today', 'show, today (median)', '--s3'), ('median blame past', 'blame, past date (median)', '--s4')]


def trend_value(run: dict, key: str) -> float | None:
    t = run.get('timings', {})
    if key.startswith('median '):
        vs = sorted(v for k, v in t.items() if k.startswith(key[7:] + ': '))
        return vs[len(vs) // 2] if vs else None
    return t.get(key)


def trend(runs: list[dict]) -> str:
    """The headline timings across every run, one log axis."""
    pts = [(i, key, trend_value(r, key)) for i, r in enumerate(runs) for key, _, _ in TREND]
    vals = [v for _, _, v in pts if v]
    if not vals:
        return ''
    left, right, top, bottom = 60, 760, 14, 200
    lo, hi = min(vals), max(vals)
    a, b = math.floor(math.log10(lo)), math.ceil(math.log10(hi))
    y = lambda v: bottom - (math.log10(v) - a) / max(1, b - a) * (bottom - top)
    n = len(runs)
    x = lambda i: left + (i + 0.5) * (right - left) / n if n < 3 else left + i * (right - left) / (n - 1)
    body = ''
    for e in range(a, b + 1):
        v = 10 ** e
        body += (f'<line x1="{left}" x2="{right}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/>'
                 f'<text x="{left - 8}" y="{y(v) + 4:.1f}" class="tick" text-anchor="end">{v:g} s</text>')
    for i, r in enumerate(runs):
        body += (f'<text x="{x(i):.1f}" y="{bottom + 18}" class="tick" text-anchor="middle">'
                 f'{esc(r["when"][5:10])} · {esc(r["tree"][:7])}</text>')
    ends = []
    for key, name, var in TREND:
        series = [(i, trend_value(r, key)) for i, r in enumerate(runs)]
        series = [(i, v) for i, v in series if v]
        if len(series) > 1:
            body += (f'<polyline points="{" ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in series)}" class="line" '
                     f'style="stroke:var({var})"/>')
        for i, v in series:
            body += (f'<g class="hit" data-tip="{esc(f"{name}, run {i + 1}: {fmt(v)} s")}">'
                     f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="12" fill="transparent"/>'
                     f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="5" class="dot" style="fill:var({var})"/></g>')
        if series:
            i, v = series[-1]
            ends.append((y(v), x(i), f'{name} {fmt(v)} s'))
    last_y = -1e9
    for yy, xx, text in sorted(ends):  # end labels, pushed apart so none overlap
        yy = max(yy, last_y + 15)
        last_y = yy
        body += f'<text x="{xx + 10:.1f}" y="{yy + 4:.1f}" class="value">{esc(text)}</text>'
    note = '' if n > 1 else '<p class="sub">One run so far: each later run adds a point on every line.</p>'
    return (legend([(v, nm) for _, nm, v in TREND]) + note +
            f'<svg viewBox="0 0 800 {bottom + 30}" role="img" aria-label="Headline timings by run, log scale">{body}</svg>')


def status_bars(tests: list[dict]) -> str:
    """For each deep test, its findings split by what became of them."""
    if not tests:
        return ''
    left, right, top, step = 300, 760, 6, 30
    h = top + step * len(tests) + 6
    most = max(len(t['items']) for t in tests)
    unit = (right - left) / most
    body = ''
    for i, t in enumerate(tests):
        y = top + step * i
        body += f'<text x="{left - 10}" y="{y + 17}" class="label" text-anchor="end">{esc(t["title"][:46])}</text>'
        x0 = left
        for key, name in STATUSES:
            k = sum(1 for it in t['items'] if it['status'] == key)
            if not k:
                continue
            wdt = k * unit - 2
            body += (f'<g class="hit" data-tip="{esc(f"{t["title"]}: {k} {name.lower()}")}">'
                     f'<rect x="{x0:.1f}" y="{y + 5}" width="{wdt:.1f}" height="16" rx="3" style="fill:var(--st-{key})"/>'
                     f'<text x="{x0 + wdt / 2:.1f}" y="{y + 17}" text-anchor="middle" class="cell on">{k}</text></g>')
            x0 += k * unit
    return (legend([(f'--st-{k}', n) for k, n in STATUSES]) +
            f'<svg viewBox="0 0 800 {h}" role="img" aria-label="Findings of each deep test by status">{body}</svg>')


CSS = '''
:root { --paper:#f6f6f3; --sheet:#fcfcfb; --ink:#1c2228; --muted:#5f6a72; --rule:#d9dddb; --ok:#1e6a52; --ok-soft:#e1efe8;
  --bad:#a3322b; --bad-soft:#f8e3e1; --warn:#95590a; --warn-soft:#fbefdc;
  --grid:#e1e0d9; --axis:#898781; --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#6250d6;
  --before:#eb6834; --after:#2a78d6; --cold:#2a78d6; --warm:#1baf7a;
  --st-clean:#0ca30c; --st-fixed:#2a78d6; --st-handed:#c98500; --st-open:#d03b3b;
  --seq-100:#cde2fb; --seq-200:#9ec5f4; --seq-300:#6da7ec; --seq-400:#3987e5; --seq-500:#256abf; --seq-600:#184f95; --seq-700:#0d366b; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --paper:#12181c; --sheet:#1a1a19; --ink:#e5ebee;
  --muted:#9ba8b0; --rule:#2d3942; --ok:#5dc3a2; --ok-soft:#173329; --bad:#ef8a80; --bad-soft:#3d1d1b; --warn:#e2a54d;
  --warn-soft:#3a2a12; --grid:#2c2c2a; --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#9085e9;
  --before:#d95926; --after:#3987e5; --cold:#3987e5; --warm:#199e70; --st-fixed:#3987e5;
  --seq-100:#0d366b; --seq-200:#104281; --seq-300:#184f95; --seq-400:#256abf; --seq-500:#3987e5; --seq-600:#6da7ec; --seq-700:#b7d3f6;
  color-scheme: dark; } }
:root[data-theme="dark"] { --paper:#12181c; --sheet:#1a1a19; --ink:#e5ebee; --muted:#9ba8b0; --rule:#2d3942; --ok:#5dc3a2;
  --ok-soft:#173329; --bad:#ef8a80; --bad-soft:#3d1d1b; --warn:#e2a54d; --warn-soft:#3a2a12; --grid:#2c2c2a; --s1:#3987e5;
  --s2:#d95926; --s3:#199e70; --s4:#9085e9; --before:#d95926; --after:#3987e5; --cold:#3987e5; --warm:#199e70;
  --st-fixed:#3987e5; --seq-100:#0d366b; --seq-200:#104281; --seq-300:#184f95; --seq-400:#256abf; --seq-500:#3987e5;
  --seq-600:#6da7ec; --seq-700:#b7d3f6; color-scheme: dark; }
body { margin:0; background:var(--paper); color:var(--ink); font:15px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width:1100px; margin:0 auto; padding:32px 16px 64px; }
h1 { font-size:1.9rem; margin:0 0 6px; } h2 { margin:40px 0 8px; border-top:2px solid var(--ink); padding-top:12px; }
h3 { margin:26px 0 6px; font-size:1.05rem; }
p, li { max-width:80ch; } .sub { color:var(--muted); font-size:12px; font-weight:400; }
.wrap { overflow-x:auto; background:var(--sheet); border:1px solid var(--rule); border-radius:6px; }
.chart { background:var(--sheet); border:1px solid var(--rule); border-radius:6px; padding:12px 14px 6px; margin:10px 0 14px; }
.chart svg { display:block; width:100%; height:auto; overflow:visible; }
.chart .grid { stroke:var(--grid); stroke-width:1; } .chart .link { stroke:var(--axis); stroke-width:2; }
.chart .line { fill:none; stroke-width:2; stroke-linejoin:round; stroke-linecap:round; }
.chart .dot { stroke:var(--sheet); stroke-width:2; }
.chart text { fill:var(--ink); font-size:12px; } .chart .tick { fill:var(--muted); font-size:11px; }
.chart .value { fill:var(--muted); font-size:11.5px; } .chart .cell { fill:#0b0b0b; font-size:11.5px; font-variant-numeric:tabular-nums; }
.chart .cell.on { fill:#fff; } .chart .over { fill:none; stroke:var(--st-open); stroke-width:2.5; }
.over-key { background:transparent; border:2.5px solid var(--st-open); box-sizing:border-box; }
.attn { background:var(--sheet); border:1px solid var(--rule); border-left:4px solid var(--st-open); border-radius:6px;
  padding:10px 16px; margin:14px 0; } .attn.ok { border-left-color:var(--st-clean); } .attn ul { margin:6px 0; }
.ctx { color:var(--muted); font-size:13px; }
.chart .hit:hover .dot, .chart .hit:hover rect[rx] { filter:brightness(1.12); }
.legend { display:flex; flex-wrap:wrap; gap:6px 16px; font-size:12.5px; color:var(--muted); margin:0 0 6px; }
.key { display:inline-flex; align-items:center; gap:6px; } .sw { width:12px; height:12px; border-radius:3px; display:inline-block; }
details { margin:4px 0 0; } summary { cursor:pointer; color:var(--muted); font-size:13px; }
table { border-collapse:collapse; width:100%; font-size:13.5px; }
th, td { text-align:left; vertical-align:top; padding:7px 10px; border-bottom:1px solid var(--rule); }
td.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.ok { background:var(--ok-soft); color:var(--ok); } td.bad { background:var(--bad-soft); color:var(--bad); }
td.na { color:var(--muted); }
.tag { display:inline-block; padding:1px 7px; border-radius:4px; font-size:12px; }
.tag.fixed { background:var(--ok-soft); color:var(--ok); } .tag.open { background:var(--bad-soft); color:var(--bad); }
.tag.clean { background:var(--ok-soft); color:var(--ok); } .tag.handed { background:var(--warn-soft); color:var(--warn); }
code { font-family:ui-monospace, Consolas, monospace; font-size:.9em; }
#tip { position:fixed; pointer-events:none; background:var(--ink); color:var(--paper); font-size:12.5px; padding:5px 9px;
  border-radius:5px; max-width:340px; display:none; z-index:10; }
'''

JS = '''
const tip = document.getElementById('tip');
document.querySelectorAll('.hit').forEach(g => {
  g.addEventListener('mousemove', e => { tip.textContent = g.dataset.tip; tip.style.display = 'block';
    const x = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8); tip.style.left = x + 'px'; tip.style.top = (e.clientY + 14) + 'px'; });
  g.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
});
'''


def main() -> None:
    runs = [json.loads(l) for l in (HERE / 'runs.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()] \
        if (HERE / 'runs.jsonl').exists() else []
    found = json.loads((HERE / 'findings.json').read_text(encoding='utf-8')) if (HERE / 'findings.json').exists() else {}
    metrics = sorted({k for r in runs for k in r.get('timings', {})})
    checks = sorted({k for r in runs for k in r.get('checks', {})})
    last = runs[-8:]

    def cell(v):
        if v is None:
            return '<td class="na">–</td>'
        return f'<td class="num">{v:.1f}</td>' if isinstance(v, (int, float)) else f'<td>{esc(v)}</td>'

    head = ''.join(f'<th>{esc(r["when"][:16].replace("T", " "))}<br><span class="sub">{esc(r["tree"])} · '
                   f'{r.get("corpora_checked_out", "?")} corpora</span></th>' for r in last)
    timing_rows = ''.join(f'<tr><td>{esc(m)}</td>' + ''.join(cell(r.get('timings', {}).get(m)) for r in last) + '</tr>'
                          for m in metrics)
    check_rows = ''.join(
        f'<tr><td>{esc(c)}</td>' + ''.join(
            (lambda v: f'<td class="{"ok" if v == "pass" else "bad" if v else "na"}">{esc(v or "–")}</td>')(
                r.get('checks', {}).get(c)) for r in last) + '</tr>' for c in checks)
    notes = ''.join(f'<li><b>{esc(r["when"][:16])}</b>: {esc(n)}</li>' for r in last for n in r.get('notes', []))
    n_pass = sum(1 for v in (runs[-1].get('checks', {}).values() if runs else []) if v == 'pass')
    n_checks = len(runs[-1].get('checks', {})) if runs else 0

    before_after = ''.join(
        f'<tr><td>{esc(x["what"])}</td><td class="num">{esc(x["before"])}</td><td class="num">{esc(x["after"])}</td>'
        f'<td>{esc(x.get("where", ""))}</td></tr>' for x in found.get('speed', []))
    deep = ''
    for test in found.get('deep_tests', []):
        items = ''.join(
            f'<tr><td><span class="tag {esc(i["status"])}">{esc(i["status"])}</span></td><td>{esc(i["finding"])}</td>'
            f'<td>{esc(i.get("evidence", ""))}</td><td>{esc(i.get("action", ""))}</td></tr>' for i in test['items'])
        deep += (f'<h3>{esc(test["when"])}: {esc(test["title"])}</h3><p>{esc(test.get("how", ""))}</p>'
                 f'<div class="wrap"><table><thead><tr><th>Status</th><th>Finding</th><th>Evidence</th>'
                 f'<th>What was done</th></tr></thead><tbody>{items}</tbody></table></div>')
    latest = runs[-1] if runs else {}
    failed = [f'{k}: {v}' for k, v in latest.get('checks', {}).items() if v != 'pass']
    slower = latest.get('regressions', [])
    over = latest.get('over_budget', [])
    if runs and (failed or slower or over):
        attention = ('<div class="attn"><b>Needs attention in the latest run</b><ul>' +
                     ''.join(f'<li>Check failed: {esc(x)}</li>' for x in failed) +
                     ''.join(f'<li>Slower than the last run on the same corpora: {esc(x)}</li>' for x in slower) +
                     ''.join(f'<li>Over budget: {esc(x)}</li>' for x in over) + '</ul></div>')
    elif runs:
        attention = '<div class="attn ok"><b>Latest run: every check passes, nothing slower, nothing over budget.</b></div>'
    else:
        attention = ''
    context = ''
    if runs:
        context = (f'<p class="ctx">Latest run: {esc(latest.get("machine", ""))}; law.py {esc(latest.get("law_py", "?"))}; '
                   f'{latest.get("tries", 1)} tr{"y" if latest.get("tries", 1) == 1 else "ies"} a command, median kept'
                   f'{"; quick run" if latest.get("quick") else ""}. Index caches: '
                   + esc(', '.join(f'{c.split("/")[0]} {mb:g} MB' for c, mb in sorted(latest.get('cache_mb', {}).items(),
                                                                                       key=lambda x: -x[1])[:6]) or '–')
                   + '.</p>')
    experiments = ''.join(
        f'<h3>{esc(e["when"])}: {esc(e["title"])}</h3><p>{esc(e.get("question", ""))}</p>'
        f'<p><b>Result.</b> {esc(e.get("result", ""))}</p><p><b>Decision.</b> {esc(e.get("decision", ""))}</p>'
        f'<p class="ctx">Write-up: <a href="{esc(e["file"])}">{esc(e["file"])}</a>'
        + (f'; script: <code>{esc(e["script"])}</code>' if e.get('script') else '') + '</p>'
        for e in found.get('experiments', []))

    def chart(svg: str) -> str:
        return f'<div class="chart">{svg}</div>' if svg else ''

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Global Law Performance</title>
<style>{CSS}</style></head><body><main>
<h1>Global law: performance and test record</h1>
<p>Every run of <code>python performance/bench.py</code> on a clone of this repository, newest last, and what each deep
test found. A run measures only the corpora checked out in that clone, so compare runs of the same corpora (each column
says how many). Times are seconds. This page is written by <code>performance/report.py</code> from
<code>runs.jsonl</code> and <code>findings.json</code>; hover a mark for its value.</p>
<p><b>{len(runs)} run{"s" if len(runs) != 1 else ""}</b>{f", the latest on {esc(latest['when'][:10])} at tree {esc(latest['tree'])} with {latest.get('corpora_checked_out')} corpora: {n_pass} of {n_checks} checks pass" if runs else ""}.</p>

{attention}
{context}
<h2>Speed: before and after</h2>
<p>Each fix, the time before (orange) and after (blue). The scale is logarithmic: each gridline is ten times the last.</p>
{chart(dumbbell(found.get('speed', [])))}
<details><summary>Table</summary><div class="wrap"><table><thead><tr><th>What</th><th>Before</th><th>After</th><th>Where measured</th></tr></thead>
<tbody>{before_after}</tbody></table></div></details>

<h2>Headline timings, by run</h2>
{chart(trend(runs))}

<h2>Latest run: each command on each fixed provision</h2>
<p>One process per command, as a reader runs it, so each time includes starting Python and loading the corpus's index.
Budgets: show, log and diff 3 s; blame 5 s; words 10 s.</p>
{chart(heatmap(latest))}

<h2>Latest run: reading each corpus's history</h2>
<p>Building the index from nothing, and loading it again from the cache. Where a loaded time is above the time from nothing, see the run's notes below.</p>
{chart(index_bars(latest))}

<h2>Checks, by run</h2>
<div class="wrap"><table><thead><tr><th>Check</th>{head}</tr></thead><tbody>{check_rows}</tbody></table></div>
<h2>Timings, by run (seconds)</h2>
<details><summary>All {len(metrics)} timings</summary>
<div class="wrap"><table><thead><tr><th>Measure</th>{head}</tr></thead><tbody>{timing_rows}</tbody></table></div></details>
{f"<h2>Notes from the runs</h2><ul>{notes}</ul>" if notes else ""}
{f"<h2>Experiments</h2><p>What was tried to make a slow path faster, what each try gave, and what was kept.</p>{experiments}" if experiments else ""}
<h2>Deep tests</h2>
<p>What each deep test of the repository found, and what became of it.</p>
{chart(status_bars(found.get('deep_tests', [])))}
{deep}
</main><div id="tip" role="tooltip"></div><script>{JS}</script></body></html>
'''
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    print(f'performance/index.html: {len(runs)} run(s), {len(metrics)} timings, {len(checks)} checks')


if __name__ == '__main__':
    main()
