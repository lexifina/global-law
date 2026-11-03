#!/usr/bin/env python3
"""Measure the tools on this clone and record the run: speed, correctness checks and the state of the tree.

  python performance/bench.py                 run, append the run to performance/runs.jsonl, rewrite index.html
  python performance/bench.py --no-record     run and print, record nothing

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
TODAY = dt.date.today().isoformat()


def run(args: list[str], timeout: int = 1800) -> tuple[float, int, str]:
    t = time.time()
    try:
        done = subprocess.run(args, cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
        return round(time.time() - t, 2), done.returncode, (done.stdout + done.stderr)[-400:]
    except subprocess.TimeoutExpired:
        return float(timeout), -1, 'timed out'


def cli(*args: str, timeout: int = 1800) -> tuple[float, int, str]:
    return run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'law.py'), *args], timeout)


def cache_file(corpus: str) -> Path:
    store = Path(law.git('rev-parse', '--path-format=absolute', '--git-path', 'global-law-cache').strip())
    return store / (corpus.replace('/', '~') + '.pickle')


def main(argv: list[str]) -> int:
    record = '--no-record' not in argv
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
        'timings': {}, 'checks': {}, 'notes': [],
    }
    t, checks = result['timings'], result['checks']

    # 1. tests that need no corpus
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
        secs, code, _ = run([sys.executable, '-X', 'utf8', '-c', f'import sys; sys.path.insert(0, "tools"); import law; '
                             f'law._index({corpus!r})'], 3600)
        t[f'index cold: {corpus}'] = secs
        secs, code, _ = run([sys.executable, '-X', 'utf8', '-c', f'import sys; sys.path.insert(0, "tools"); import law; '
                             f'law._index({corpus!r})'], 600)
        t[f'index warm: {corpus}'] = secs
        if kept.exists():
            kept.unlink()
    checks['checkouts at their pins'] = 'pass' if not behind else f'{len(behind)} behind: {behind[:5]}'

    # 3. fixed provisions, one process per command, as a reader runs them
    for corpus, rel, past in BENCH:
        if corpus not in here or corpus in behind:
            continue
        p = f'{corpus}/{rel}'
        for name, args in (('show today', ('show', TODAY, p)), ('show past', ('show', past, p)), ('log', ('log', p)),
                           ('blame past', ('blame', past, p)), ('words today', ('words', TODAY, p)),
                           ('diff', ('diff', past, TODAY, p))):
            secs, code, tail = cli(*args)
            t[f'{name}: {p}'] = secs
            if code not in (0, 1) or 'Traceback' in tail:
                result['notes'].append(f'{name} {p}: exit {code}: {tail[-160:]}')
    secs, code, tail = cli('world', TODAY, timeout=3600)
    t['world (every corpus checked out)'] = secs
    if code:
        result['notes'].append(f'world: exit {code}: {tail[-160:]}')
    secs, code, tail = cli('laws', '2026-01-01', TODAY, timeout=3600)
    t['laws 2026 (every corpus checked out)'] = secs

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
    secs, code, tail = run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'describe.py'), '--check'], 1800)
    checks['describe.py --check'] = 'pass' if code == 0 else f'drift or error: {tail[-200:]}'
    t['describe.py --check'] = secs

    print(json.dumps(result, indent=1, ensure_ascii=False))
    if record:
        with open(HERE / 'runs.jsonl', 'a', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + '\n')
        subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'report.py')], cwd=ROOT)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
