#!/usr/bin/env python3
"""Measure the tools on this clone and record the run: speed, correctness checks and the state of the tree.

  python performance/bench.py                 run, append the run to performance/runs.jsonl, rewrite index.html
  python performance/bench.py --no-record     run and print, record nothing
  python performance/bench.py --quick         one try of each command, no fixture tests or describe --check

It exits 1 when a check fails or a timing regressed against the last run on the same corpora (more than 1.5 times
and 1 second slower), so a scheduled job can watch it; the run is still recorded.

It reads only the corpora checked out here (python tools/countries.py add <country> adds one), so runs on different
clones measure different things: each run records which corpora it read, the machine and the tree commit. Compare
runs of the same corpora. Standard library and git only.

What it measures, for each corpus in BENCH that is checked out (and up to MAX_OTHER others):
  - the index: built from nothing (cold) and loaded (warm);
  - show, log, blame, words and diff on fixed provisions, at today and at a past date, as a separate process each,
    as a reader would run them;
  - world and laws over every corpus checked out.
What it checks:
  - the tests that need no corpus (tests/test_law_fixtures.py);
  - for a sample of files in each corpus: the text read for today is the file at the pinned commit (unless a later
    version is not yet in force, or a correction applies), and blame covers exactly the lines shown;
  - tools/verify.py on the last 200 commits, and tools/describe.py --check (needs the network);
  - each corpus's checkout holds the commit the tree pins.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import law  # noqa: E402

# Fixed provisions, so runs compare: (corpus, provision path inside it, a past date to read it on).
BENCH = [
    ('united-states/federal/usc', 'title-11/1182.md', '2022-07-01'),
    ('antigua-and-barbuda/national/acts', 'companies-act/art-002.md', '2000-01-01'),
    ('czechia/national/acts', 'sb/2007/378.md', '2018-11-23'),
    ('czechia/national/acts', 'sb/1995/247.md', '1996-01-01'),
    ('romania/national/acts', 'lege/2003/571/art-047.md', '2016-06-01'),
    ('france/national/acts', 'codes/code-de-procedure-penale/R251.md', '2016-01-01'),
    ('germany/bund/acts', 'grundgesetz/artikel/1.md', '1990-01-01'),
    ('switzerland/bund/acts', '101/art-001.md', '2000-01-01'),
    ('new-zealand/national/acts', 'companies-act/sec-001.md', '2010-01-01'),
    ('italy/lazio/acts', 'lr-1971-001/art-001.md', '2000-01-01'),
    ('canada/federal/acts', 'S-15.3/schedule-1.md', '2024-11-15'),
]
MAX_OTHER = 8
SAMPLE = 30
REPEAT = 3  # each command is run this many times and the median kept: process start-up varies a lot on some machines
# What a reader should wait at most, in seconds, for one command (median of the tries).
BUDGET = {'show today': 3, 'show past': 3, 'log': 3, 'blame past': 5, 'words today': 10, 'diff': 3,
          'index warm': 3, 'world (every corpus checked out)': 60, 'laws 2026 (every corpus checked out)': 60}
SLOWER, SLOWER_BY = 1.5, 1.0  # a regression: this many times the last run's time, and this many seconds more
TODAY = dt.date.today().isoformat()


def run(args: list[str], timeout: int = 1800, env: dict | None = None) -> tuple[float, int, str]:
    t = time.time()
    try:
        done = subprocess.run(args, cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace', timeout=timeout,
                              env=env)
        return round(time.time() - t, 2), done.returncode, (done.stdout + done.stderr)[-400:]
    except subprocess.TimeoutExpired:
        return float(timeout), -1, 'timed out'


def cli(*args: str, timeout: int = 1800, tries: int = 1) -> tuple[float, int, str, int | None]:
    """law.py as a reader runs it; with tries > 1, the median time of that many runs. The last item is how many git
    processes the command started, counted by git itself (GIT_TRACE2: one "version" line a process) on the first try:
    starting a process is the slowest part of a short read on some machines."""
    import tempfile
    trace = Path(tempfile.gettempdir()) / f'global-law-bench-{os.getpid()}.trace'
    trace.unlink(missing_ok=True)
    got = []
    for i in range(tries):
        env = {**os.environ, 'GIT_TRACE2': str(trace)} if i == 0 else None
        got.append(run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'law.py'), *args], timeout, env))
    procs = None
    if trace.exists():
        procs = sum(1 for line in trace.read_text(encoding='utf-8', errors='replace').splitlines()
                    if line.split()[2:3] == ['version'])
        trace.unlink(missing_ok=True)
    times = sorted(g[0] for g in got)
    return times[len(times) // 2], got[-1][1], got[-1][2], procs


def budget_of(name: str) -> float | None:
    return BUDGET.get(name.split(': ', 1)[0]) if ': ' in name else BUDGET.get(name)


def regressions(result: dict, earlier: list[dict]) -> list[str]:
    """Timings well above the last run that measured the same corpora."""
    same = [r for r in earlier if r.get('corpora_measured') == result['corpora_measured']]
    if not same:
        return []
    last = same[-1]['timings']
    return [f'{k}: {last[k]:.1f} s -> {v:.1f} s' for k, v in result['timings'].items()
            if k in last and v > last[k] * SLOWER and v - last[k] > SLOWER_BY]


def cache_file(corpus: str) -> Path:
    return law._store() / (corpus.replace('/', '~') + '.index')


def main(argv: list[str]) -> int:
    record = '--no-record' not in argv
    quick = '--quick' in argv
    tries = 1 if quick else REPEAT
    random.seed(1)
    here = [c['path'] for c in law.manifest()['corpora'] if (ROOT / c['path'] / '.git').exists()]
    bench_corpora = sorted({c for c, _, _ in BENCH if c in here})
    others = [c for c in here if c not in bench_corpora][:MAX_OTHER]
    result: dict = {
        'when': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tree': law.git('rev-parse', 'HEAD').strip()[:12],
        'machine': f'{platform.system()} {platform.release()}, Python {platform.python_version()}, '
                   f'{os.cpu_count()} cpus',
        'corpora_checked_out': len(here),
        'corpora_measured': bench_corpora + others,
        'law_py': law.git('hash-object', str(ROOT / 'tools' / 'law.py')).strip()[:12],
        'quick': quick, 'tries': tries,
        'pins': {c: (law.tip(c) or '')[:12] for c in bench_corpora + others},
        'timings': {}, 'checks': {}, 'notes': [], 'cache_mb': {}, 'git_processes': {},
    }
    t, checks = result['timings'], result['checks']

    # 1. tests that need no corpus
    if not quick:
        secs, code, tail = run([sys.executable, '-X', 'utf8', '-m', 'unittest', 'tests.test_law_fixtures'], 1800)
        checks['fixture tests'] = 'pass' if code == 0 else f'FAIL: {tail[-200:]}'
        t['fixture tests'] = secs

    # 2. per corpus: index cold and warm, behind its pin
    behind = []
    for corpus in bench_corpora + others:
        pin = law.tip(corpus)
        if subprocess.run(['git', 'cat-file', '-e', f'{pin}^{{commit}}'], cwd=ROOT / corpus, capture_output=True).returncode:
            behind.append(corpus)
            continue
        f = cache_file(corpus)
        kept = f.with_suffix('.bench-keep')
        if f.exists():
            shutil.move(str(f), str(kept))
        f.with_suffix('.pickle').unlink(missing_ok=True)  # the one-piece index law.py read until 4 November 2026
        secs, code, _ = run([sys.executable, '-X', 'utf8', '-c', f'import sys; sys.path.insert(0, "tools"); import law; '
                             f'law._index({corpus!r})'], 3600)
        t[f'index cold: {corpus}'] = secs
        secs, code, _ = run([sys.executable, '-X', 'utf8', '-c', f'import sys; sys.path.insert(0, "tools"); import law; '
                             f'law._index({corpus!r})'], 600)
        t[f'index warm: {corpus}'] = secs
        if kept.exists():
            kept.unlink()
        if f.exists():
            result['cache_mb'][corpus] = round(f.stat().st_size / 1e6, 1)
    checks['checkouts at their pins'] = 'pass' if not behind else f'{len(behind)} behind: {behind[:5]}'

    # 3. fixed provisions, one process per command, as a reader runs them
    for corpus, rel, past in BENCH:
        if corpus not in here or corpus in behind:
            continue
        p = f'{corpus}/{rel}'
        for name, args in (('show today', ('show', TODAY, p)), ('show past', ('show', past, p)), ('log', ('log', p)),
                           ('blame past', ('blame', past, p)), ('words today', ('words', TODAY, p)),
                           ('diff', ('diff', past, TODAY, p))):
            secs, code, tail, procs = cli(*args, tries=tries)
            t[f'{name}: {p}'] = secs
            result['git_processes'][f'{name}: {p}'] = procs
            if code not in (0, 1) or 'Traceback' in tail:
                result['notes'].append(f'{name} {p}: exit {code}: {tail[-160:]}')
    secs, code, tail, procs = cli('world', TODAY, timeout=3600)
    t['world (every corpus checked out)'] = secs
    result['git_processes']['world (every corpus checked out)'] = procs
    if code:
        result['notes'].append(f'world: exit {code}: {tail[-160:]}')
    secs, code, tail, procs = cli('laws', '2026-01-01', TODAY, timeout=3600)
    t['laws 2026 (every corpus checked out)'] = secs
    result['git_processes']['laws 2026 (every corpus checked out)'] = procs

    # 4. correctness on samples, in this process
    wrong, blamed = [], []
    for corpus in bench_corpora + others:
        if corpus in behind:
            continue
        ix = law._index(corpus)
        rows = ix['rows']
        files = [f for f, vs in ix['files'].items() if f.endswith('.md') and not f.endswith('README.md')
                 and any(rows[o][5] and rows[o][4] != 'documentation' for o, _, _ in vs)]
        for f in random.sample(files, min(SAMPLE, len(files))):
            p = f'{corpus}/{f}'
            hist = law.history(p)
            now = law.text_on(TODAY, p)
            head = law.read_object(corpus, f"{ix['pin']}:{f}")
            if head != now and not any(h['in_force'] > TODAY or h.get('corrects') for h in hist):
                wrong.append(p)
            if now is not None and [l for _, _, l in law.blame_rows(TODAY, p)] != now.splitlines():
                blamed.append(p)
    law.close_readers()
    checks['text today = pinned file (sample)'] = 'pass' if not wrong else f'{len(wrong)} differ: {wrong[:5]}'
    checks['blame covers the text (sample)'] = 'pass' if not blamed else f'{len(blamed)} differ: {blamed[:5]}'

    # 5. the tree
    secs, code, tail = run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'verify.py')], 1800)
    checks['verify.py, last 200 commits'] = 'pass' if code == 0 else f'FAIL: {tail[-200:]}'
    t['verify.py, last 200 commits'] = secs
    if not quick:
        secs, code, tail = run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'describe.py'), '--check'], 1800)
        checks['describe.py --check'] = 'pass' if code == 0 else f'drift or error: {tail[-200:]}'
        t['describe.py --check'] = secs

    # 6. against the budgets and the last comparable run
    result['over_budget'] = [f'{k}: {v:.1f} s (budget {budget_of(k):g} s)' for k, v in t.items()
                             if budget_of(k) is not None and v > budget_of(k)]
    runs_file = HERE / 'runs.jsonl'
    earlier = [json.loads(l) for l in runs_file.read_text(encoding='utf-8').splitlines() if l.strip()] \
        if runs_file.exists() else []
    result['regressions'] = regressions(result, earlier)

    print(json.dumps(result, indent=1, ensure_ascii=False))
    if record:
        with open(HERE / 'runs.jsonl', 'a', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + '\n')
        subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'report.py')], cwd=ROOT)
    failed = [k for k, v in checks.items() if v != 'pass']
    for line in [f'check failed: {k}' for k in failed] + [f'slower: {r}' for r in result['regressions']]:
        print(line, file=sys.stderr)
    return 1 if failed or result['regressions'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
