#!/usr/bin/env python3
"""Experiment: how should `words` and `blame` (when it replays versions) match the lines of one version of a file to
the next? Each method below replaces law._line_opcodes; the answer it gives is compared with plain difflib (the
method law.py used until 4 November 2026) and timed. Results go to line_matching.json beside this script; the write-up
is line_matching.md.

  python performance/experiments/line_matching.py              every method, the fixed slow files and a sample
  python performance/experiments/line_matching.py --sample 60  a larger sample of ordinary files
  python performance/experiments/line_matching.py --methods difflib,law.py --out line_matching_chosen.json
                                                               only the baseline and law.py as it is

Run it on a clone with the corpora of performance/bench.py checked out. Each method runs in its own process so caches
do not carry over; the indexes are built once first.
"""
from __future__ import annotations

import bisect
import difflib
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import law  # noqa: E402

SLOW = [  # the files the first bench run found slow, with the date it read them on
    ('2026-11-04', 'czechia/national/acts/sb/2007/378.md'),
    ('2026-11-04', 'czechia/national/acts/sb/1995/247.md'),
    ('2024-11-15', 'canada/federal/acts/S-15.3/schedule-1.md'),
    ('2000-01-01', 'switzerland/bund/acts/101/art-001.md'),
]
METHODS = ['difflib', 'trim', 'noblank', 'git-myers', 'git-histogram', 'anchor']


def sm(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()


def shift(ops, da, db):
    return [(op, a0 + da, a1 + da, b0 + db, b1 + db) for op, a0, a1, b0, b1 in ops]


def trimmed(middle):
    """Match the lines both versions share at the start and the end, then `middle` on the rest."""
    def run(a, b):
        n, lim = 0, min(len(a), len(b))
        while n < lim and a[n] == b[n]:
            n += 1
        m = 0
        while m < lim - n and a[-1 - m] == b[-1 - m]:
            m += 1
        ops = [('equal', 0, n, 0, n)] if n else []
        ops += shift(middle(a[n:len(a) - m], b[n:len(b) - m]), n, n)
        if m:
            ops.append(('equal', len(a) - m, len(a), len(b) - m, len(b)))
        return ops
    return run


def from_pins(a, b, pins):
    """Opcodes with the given (i, j) line pairs matched, and difflib in the gaps between them."""
    ops, pa, pb = [], 0, 0
    for i, j in list(pins) + [(len(a), len(b))]:
        ops += shift(sm(a[pa:i], b[pb:j]), pa, pb)
        if i < len(a):
            ops.append(('equal', i, i + 1, j, j + 1))
        pa, pb = i + 1, j + 1
    merged = []
    for op in ops:
        if merged and merged[-1][0] == op[0] and merged[-1][2] == op[1] and merged[-1][4] == op[3]:
            merged[-1] = (op[0], merged[-1][1], op[2], merged[-1][3], op[4])
        else:
            merged.append(op)
    return merged


def noblank(a, b):
    """difflib on the lines that are not blank; blank lines between matched lines matched by difflib after."""
    ia = [i for i, x in enumerate(a) if x.strip()]
    ib = [j for j, x in enumerate(b) if x.strip()]
    pins = []
    for op, a0, a1, b0, b1 in sm([a[i] for i in ia], [b[j] for j in ib]):
        if op == 'equal':
            pins += [(ia[a0 + k], ib[b0 + k]) for k in range(a1 - a0)]
    return from_pins(a, b, pins)


def anchor(a, b):
    """Patience: lines found once in each version, in their longest common order, then difflib between them."""
    if len(a) * len(b) <= 1_000_000:
        return sm(a, b)
    ca, cb = Counter(a), Counter(b)
    at_b = {x: j for j, x in enumerate(b) if cb[x] == 1}
    pairs = [(i, at_b[x]) for i, x in enumerate(a) if ca[x] == 1 and x in at_b]
    tails, ends, back = [], [], [-1] * len(pairs)
    for k, (_, j) in enumerate(pairs):
        pos = bisect.bisect_left(tails, j)
        back[k] = ends[pos - 1] if pos else -1
        if pos == len(tails):
            tails.append(j)
            ends.append(k)
        else:
            tails[pos], ends[pos] = j, k
    run, k = [], ends[-1] if ends else -1
    while k >= 0:
        run.append(pairs[k])
        k = back[k]
    return from_pins(a, b, run[::-1])


def git_diff(algorithm):
    """git's own line diff (`git diff --no-index`) of the two versions; difflib then only inside each changed hunk
    is not needed, since the callers compare changed lines word by word themselves."""
    def run(a, b):
        if not a or not b:
            return sm(a, b)
        with tempfile.TemporaryDirectory() as d:
            pa, pb = Path(d, 'a'), Path(d, 'b')
            for p, lines in ((pa, a), (pb, b)):
                p.write_bytes(''.join(x if x.endswith('\n') else x + '\n' for x in lines).encode('utf-8'))
            out = subprocess.run(['git', 'diff', '--no-index', '--no-color', '-U0', f'--diff-algorithm={algorithm}',
                                  'a', 'b'], cwd=d, capture_output=True).stdout.decode('utf-8', 'replace')
        ops, ia, ib = [], 0, 0
        for line in out.splitlines():
            if not line.startswith('@@ '):
                continue
            old, new = line.split()[1:3]
            a0, an = (int(x) for x in (old[1:] + ',1').split(',')[:2])
            b0, bn = (int(x) for x in (new[1:] + ',1').split(',')[:2])
            a0 = a0 if an == 0 else a0 - 1
            b0 = b0 if bn == 0 else b0 - 1
            if a0 > ia:
                ops.append(('equal', ia, a0, ib, b0))
            ops.append(('replace' if an and bn else 'delete' if an else 'insert', a0, a0 + an, b0, b0 + bn))
            ia, ib = a0 + an, b0 + bn
        if ia < len(a):
            ops.append(('equal', ia, len(a), ib, len(b)))
        return ops
    return run


IMPLEMENT = {'difflib': sm, 'trim': trimmed(sm), 'noblank': trimmed(noblank), 'git-myers': git_diff('myers'),
             'git-histogram': git_diff('histogram'), 'anchor': trimmed(anchor)}


def worker(method: str, cases: list[tuple[str, str]]) -> dict:
    """In its own process: each case read with `method`, timed; answers returned for comparison. The method
    'law.py' is law.py as it is, unpatched."""
    if method != 'law.py':
        law._line_opcodes = IMPLEMENT[method]
    law._git_blame_if_same = lambda path, seq: None  # time the replay, which is what the line matching serves
    out = {}
    for date, path in cases:
        t = time.time()
        runs = law.words_on(date, path)
        tw = time.time() - t
        t = time.time()
        rows = law.blame_rows(date, path)
        tb = time.time() - t
        out[f'{date} {path}'] = {'words_s': round(tw, 2), 'blame_s': round(tb, 2),
                                 'words': [[l, s] for l, s in runs], 'blame': [r[1] for r in rows]}
    law.close_readers()
    return out


def compare(base: dict, other: dict) -> dict:
    """Characters (not spaces) credited to another law by `words`, lines credited to another law by `blame`."""
    chars_b = [l for l, s in base['words'] for c in s if not c.isspace()]
    chars_o = [l for l, s in other['words'] for c in s if not c.isspace()]
    assert len(chars_b) == len(chars_o), 'the text itself differs'
    words_diff = sum(x != y for x, y in zip(chars_b, chars_o))
    blame_diff = sum(x != y for x, y in zip(base['blame'], other['blame']))
    return {'chars': len(chars_b), 'chars_differ': words_diff, 'lines': len(base['blame']), 'lines_differ': blame_diff}


def main(argv: list[str]) -> int:
    if argv[:1] == ['--worker']:
        print(json.dumps(worker(argv[1], json.loads(Path(argv[2]).read_text(encoding='utf-8')))))
        return 0
    size = int(argv[argv.index('--sample') + 1]) if '--sample' in argv else 30
    methods = argv[argv.index('--methods') + 1].split(',') if '--methods' in argv else METHODS + ['law.py']
    out_file = Path(__file__).with_name(argv[argv.index('--out') + 1]) if '--out' in argv else         Path(__file__).with_suffix('.json')
    random.seed(4)
    here = [c['path'] for c in law.manifest()['corpora'] if (ROOT / c['path'] / '.git').exists()]
    sample = []
    for corpus in sorted({p.split('/')[0] + '/' + p.split('/')[1] + '/' + p.split('/')[2] for _, p in SLOW} | set(here[:12])):
        if corpus not in here or corpus in law.behind():
            continue
        ix = law._index(corpus)
        many = [f for f, vs in ix['files'].items() if f.endswith('.md') and len(vs) >= 4]
        sample += [(time.strftime('%Y-%m-%d'), f'{corpus}/{f}')
                   for f in random.sample(many, min(max(1, size // 8), len(many)))]
    cases = [c for c in SLOW if (ROOT / '/'.join(c[1].split('/')[:3]) / '.git').exists()]
    cases += sample[:size]
    law.close_readers()
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as fh:
        json.dump(cases, fh)
    results = {}
    for method in methods:
        t = time.time()
        done = subprocess.run([sys.executable, '-X', 'utf8', __file__, '--worker', method, fh.name], cwd=ROOT,
                              capture_output=True, encoding='utf-8')
        if done.returncode:
            print(method, 'failed:', done.stderr[-600:])
            continue
        results[method] = json.loads(done.stdout)
        print(f'{method}: {time.time() - t:.0f} s', flush=True)
    os.unlink(fh.name)
    base = results['difflib']
    summary = {'when': time.strftime('%Y-%m-%d %H:%M'), 'tree': law.git('rev-parse', 'HEAD').strip()[:12],
               'cases': [f'{d} {p}' for d, p in cases], 'methods': {}}
    for method, res in results.items():
        per = {}
        for key, r in res.items():
            per[key] = {'words_s': r['words_s'], 'blame_s': r['blame_s'], **compare(base[key], r)}
        slow_keys = [f'{d} {p}' for d, p in SLOW if f'{d} {p}' in per]
        summary['methods'][method] = {
            'words_s_slow': round(sum(per[k]['words_s'] for k in slow_keys), 1),
            'blame_s_slow': round(sum(per[k]['blame_s'] for k in slow_keys), 1),
            'words_s_sample': round(sum(v['words_s'] for k, v in per.items() if k not in slow_keys), 1),
            'chars_differ': sum(v['chars_differ'] for v in per.values()),
            'chars': sum(v['chars'] for v in per.values()),
            'lines_differ': sum(v['lines_differ'] for v in per.values()),
            'lines': sum(v['lines'] for v in per.values()),
            'files_differ': sum(1 for v in per.values() if v['chars_differ'] or v['lines_differ']),
            'per_case': per,
        }
    out_file.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n',
                                                   encoding='utf-8', newline='\n')
    print(f"{'method':<15}{'words, slow':>12}{'blame, slow':>12}{'words, sample':>14}{'chars differ':>16}{'lines differ':>14}{'files':>7}")
    for m, s in summary['methods'].items():
        print(f"{m:<15}{s['words_s_slow']:>11.1f}s{s['blame_s_slow']:>11.1f}s{s['words_s_sample']:>13.1f}s"
              f"{s['chars_differ']:>9}/{s['chars']:<7}{s['lines_differ']:>6}/{s['lines']:<7}{s['files_differ']:>4}/{len(cases)}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
