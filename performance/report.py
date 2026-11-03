#!/usr/bin/env python3
"""Write performance/index.html from performance/runs.jsonl (every bench run) and performance/findings.json (what
each deep test found and what became of it). Standard library only; the page needs no network.

  python performance/report.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def esc(x: object) -> str:
    return html.escape(str(x))


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

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Global Law Performance</title>
<style>
:root {{ --paper:#f6f6f3; --sheet:#fff; --ink:#1c2228; --muted:#5f6a72; --rule:#d9dddb; --ok:#1e6a52; --ok-soft:#e1efe8;
  --bad:#a3322b; --bad-soft:#f8e3e1; --warn:#95590a; --warn-soft:#fbefdc; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --paper:#12181c; --sheet:#192228; --ink:#e5ebee;
  --muted:#9ba8b0; --rule:#2d3942; --ok:#5dc3a2; --ok-soft:#173329; --bad:#ef8a80; --bad-soft:#3d1d1b; --warn:#e2a54d;
  --warn-soft:#3a2a12; color-scheme: dark; }} }}
body {{ margin:0; background:var(--paper); color:var(--ink); font:15px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width:1100px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:1.9rem; margin:0 0 6px; }} h2 {{ margin:36px 0 8px; border-top:2px solid var(--ink); padding-top:12px; }}
p, li {{ max-width:80ch; }} .sub {{ color:var(--muted); font-size:12px; font-weight:400; }}
.wrap {{ overflow-x:auto; background:var(--sheet); border:1px solid var(--rule); border-radius:6px; }}
table {{ border-collapse:collapse; width:100%; font-size:13.5px; }}
th, td {{ text-align:left; vertical-align:top; padding:7px 10px; border-bottom:1px solid var(--rule); }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
td.ok {{ background:var(--ok-soft); color:var(--ok); }} td.bad {{ background:var(--bad-soft); color:var(--bad); }}
td.na {{ color:var(--muted); }}
.tag {{ display:inline-block; padding:1px 7px; border-radius:4px; font-size:12px; }}
.tag.fixed {{ background:var(--ok-soft); color:var(--ok); }} .tag.open {{ background:var(--bad-soft); color:var(--bad); }}
.tag.clean {{ background:var(--ok-soft); color:var(--ok); }} .tag.handed {{ background:var(--warn-soft); color:var(--warn); }}
code {{ font-family:ui-monospace, Consolas, monospace; font-size:.9em; }}
</style></head><body><main>
<h1>Global law: performance and test record</h1>
<p>Every run of <code>python performance/bench.py</code> on a clone of this repository, newest last, and what each deep
test found. A run measures only the corpora checked out in that clone, so compare runs of the same corpora (each column
says how many). Times are seconds. This page is written by <code>performance/report.py</code> from
<code>runs.jsonl</code> and <code>findings.json</code>.</p>
<h2>Speed: before and after</h2>
<div class="wrap"><table><thead><tr><th>What</th><th>Before</th><th>After</th><th>Where measured</th></tr></thead>
<tbody>{before_after}</tbody></table></div>
<h2>Checks, by run</h2>
<div class="wrap"><table><thead><tr><th>Check</th>{head}</tr></thead><tbody>{check_rows}</tbody></table></div>
<h2>Timings, by run (seconds)</h2>
<div class="wrap"><table><thead><tr><th>Measure</th>{head}</tr></thead><tbody>{timing_rows}</tbody></table></div>
{f"<h2>Notes from the runs</h2><ul>{notes}</ul>" if notes else ""}
<h2>Deep tests</h2>
{deep}
</main></body></html>
'''
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    print(f'performance/index.html: {len(runs)} run(s), {len(metrics)} timings, {len(checks)} checks')


if __name__ == '__main__':
    main()
