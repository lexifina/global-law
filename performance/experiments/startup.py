#!/usr/bin/env python3
"""Experiment: what does a short read cost before it reads any law? Times two versions of law.py on the fixed
provisions of bench.py, end to end as a reader runs them (a new process each time, the median of --tries), and counts
the git processes each command starts (GIT_TRACE2). Their answers are compared byte for byte. Results go to
startup.json beside this script; the write-up is startup.md.

  python performance/experiments/startup.py OLD_LAW_PY [--tries 5]

OLD_LAW_PY is the earlier law.py, copied into tools/ under another name (it finds the tree from its own folder), for
example: git show 3d32f2a:tools/law.py > tools/_law_old.py
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'performance'))
from bench import BENCH, TODAY  # noqa: E402


def once(script: str, args: list[str], trace: Path | None) -> tuple[float, str, int | None]:
    env = {**os.environ, 'GIT_TRACE2': str(trace)} if trace else None
    t = time.perf_counter()
    done = subprocess.run([sys.executable, '-X', 'utf8', script, *args], cwd=ROOT, capture_output=True, env=env)
    secs = time.perf_counter() - t
    procs = None
    if trace and trace.exists():
        procs = sum(1 for line in trace.read_text(encoding='utf-8', errors='replace').splitlines()
                    if line.split()[2:3] == ['version'])
        trace.unlink()
    return secs, (done.stdout + done.stderr).decode('utf-8', 'replace'), procs


def main(argv: list[str]) -> int:
    old = str(Path(argv[0]).resolve())
    tries = int(argv[argv.index('--tries') + 1]) if '--tries' in argv else 5
    new = str(ROOT / 'tools' / 'law.py')
    trace = Path(tempfile.gettempdir()) / f'startup-{os.getpid()}.trace'
    cases = []
    for corpus, rel, past in BENCH:
        if not (ROOT / corpus / '.git').exists():
            continue
        p = f'{corpus}/{rel}'
        cases += [(f'show today: {p}', ['show', TODAY, p]), (f'log: {p}', ['log', p]),
                  (f'blame past: {p}', ['blame', past, p]), (f'words today: {p}', ['words', TODAY, p])]
    cases += [('world', ['world', TODAY]), ('laws 2026', ['laws', '2026-01-01', TODAY])]
    for script in (old, new):  # warm both caches first: each keeps its own index files
        for _, args in cases:
            once(script, args, None)
    rows = {}
    for name, args in cases:
        r = {}
        for label, script in (('old', old), ('new', new)):
            got = [once(script, args, trace if i == 0 else None) for i in range(tries)]
            r[label + '_s'] = round(statistics.median(g[0] for g in got), 2)
            r[label + '_git'] = got[0][2]
            r[label + '_out'] = got[0][1]
        r['same'] = r.pop('old_out') == r.pop('new_out')
        rows[name] = r
        print(f"{name[:70]:<72}{r['old_s']:>6.2f}s{r['new_s']:>7.2f}s  git {r['old_git']}->{r['new_git']}"
              f"{'' if r['same'] else '  ANSWER DIFFERS'}", flush=True)
    Path(__file__).with_suffix('.json').write_text(json.dumps({'tries': tries, 'rows': rows}, indent=1),
                                                    encoding='utf-8', newline='\n')
    return 0 if all(r['same'] for r in rows.values()) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
