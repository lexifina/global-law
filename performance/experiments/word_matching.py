#!/usr/bin/env python3
"""Experiment: once `words` has matched the lines of one version to the next, how should it compare the words of the
lines that changed? Each method below replaces law._tokens, law._credit_words or law._pair_old_line; its answer is
compared with law.py as it was (difflib on words and spaces) and timed. Results go to word_matching.json beside this
script; the write-up is word_matching.md.

  python performance/experiments/word_matching.py                every method, the slow files and a sample
  python performance/experiments/word_matching.py --methods current,law.py --out word_matching_chosen.json

Run it on a clone with the corpora of performance/bench.py checked out. Each method runs in its own process.
"""
from __future__ import annotations

import difflib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import law  # noqa: E402

SLOW = [  # the slowest `words` files of the bench and of line_matching.py
    ('2026-11-04', 'czechia/national/acts/sb/2007/378.md'),
    ('2026-11-04', 'czechia/national/acts/sb/2000/218.md'),
    ('2026-11-04', 'czechia/national/acts/sb/1995/247.md'),
    ('2024-11-15', 'canada/federal/acts/S-15.3/schedule-1.md'),
    ('2026-11-04', 'united-states/federal/usc/title-11/1182.md'),
]
METHODS = ['current', 'ints', 'pair-fast', 'ints+pair-fast', 'glued', 'space-junk', 'trim']
_WORD = re.compile(r'\s+|\S+')
_GLUED = re.compile(r'^\s+|\S+\s*')


def credit_with(matcher):
    """law._credit_words with the opcodes from `matcher(old, new)`; the rest as law.py does it."""
    def credit(old, old_authors, new, law_):
        ops = matcher(old, new)
        out = []
        for i, (op, a0, a1, b0, b1) in enumerate(ops):
            island = (op == 'equal' and 0 < i < len(ops) - 1 and ops[i - 1][0] != 'equal' and ops[i + 1][0] != 'equal'
                      and sum(not t.isspace() for t in new[b0:b1]) < 3)
            out += [law_] * (b1 - b0) if op != 'equal' or island else old_authors[a0:a1]
        return out
    return credit


def plain(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()


def as_ints(a, b):
    """The same comparison on whole numbers standing for the tokens: the same answer, cheaper to hash."""
    ids: dict[str, int] = {}
    ia = [ids.setdefault(t, len(ids)) for t in a]
    ib = [ids.setdefault(t, len(ids)) for t in b]
    return difflib.SequenceMatcher(None, ia, ib, autojunk=False).get_opcodes()


def space_junk(a, b):
    """Spaces may not start a match (difflib's isjunk), so they cannot pin two unrelated words together."""
    return difflib.SequenceMatcher(str.isspace, a, b, autojunk=False).get_opcodes()


def trim(a, b):
    """The words both share at the start and end of the stretch matched first, difflib on the rest."""
    n, lim = 0, min(len(a), len(b))
    while n < lim and a[n] == b[n]:
        n += 1
    m = 0
    while m < lim - n and a[-1 - m] == b[-1 - m]:
        m += 1
    ops = [('equal', 0, n, 0, n)] if n else []
    ops += [(op, a0 + n, a1 + n, b0 + n, b1 + n) for op, a0, a1, b0, b1 in plain(a[n:len(a) - m], b[n:len(b) - m])
            if a1 > a0 or b1 > b0]
    if m:
        ops.append(('equal', len(a) - m, len(a), len(b) - m, len(b)))
    return ops


def pair_slow(old_block, line):
    best, score = None, 0.0
    for j, old in enumerate(old_block):
        s = difflib.SequenceMatcher(None, old, line, autojunk=False).quick_ratio()
        if s > score:
            best, score = j, s
    return best if best is not None and score >= 0.6 else None


def pair_fast(old_block, line):
    """The same choice: the new line is set once (difflib keeps its word counts), and an old line whose upper bound
    (real_quick_ratio) cannot beat the best so far is skipped."""
    m = difflib.SequenceMatcher(None, autojunk=False)
    m.set_seq2(line)
    best, score = None, 0.0
    for j, old in enumerate(old_block):
        m.set_seq1(old)
        if m.real_quick_ratio() <= score:
            continue
        s = m.quick_ratio()
        if s > score:
            best, score = j, s
    return best if best is not None and score >= 0.6 else None


def apply(method: str) -> None:
    if method == 'law.py':
        return
    if method == 'no-move':  # law.py without the credit for text moved and amended in one step
        law.MOVE_CREDIT = False
        return
    law._tokens = _WORD.findall
    law._credit_words = credit_with(plain)
    law._pair_old_line = pair_slow
    if method in ('ints', 'ints+pair-fast'):
        law._credit_words = credit_with(as_ints)
    if method in ('pair-fast', 'ints+pair-fast'):
        law._pair_old_line = pair_fast
    if method == 'glued':
        law._tokens = _GLUED.findall
    if method == 'space-junk':
        law._credit_words = credit_with(space_junk)
    if method == 'trim':
        law._credit_words = credit_with(trim)


def worker(method: str, cases: list[tuple[str, str]]) -> dict:
    apply(method)
    out = {}
    for date, path in cases:
        t = time.time()
        runs = law.words_on(date, path)
        out[f'{date} {path}'] = {'words_s': round(time.time() - t, 2), 'words': [[l, s] for l, s in runs]}
    law.close_readers()
    return out


def compare(base: dict, other: dict) -> dict:
    chars_b = [l for l, s in base['words'] for c in s if not c.isspace()]
    chars_o = [l for l, s in other['words'] for c in s if not c.isspace()]
    assert len(chars_b) == len(chars_o), 'the text itself differs'
    return {'chars': len(chars_b), 'chars_differ': sum(x != y for x, y in zip(chars_b, chars_o))}


def main(argv: list[str]) -> int:
    if argv[:1] == ['--worker']:
        print(json.dumps(worker(argv[1], json.loads(Path(argv[2]).read_text(encoding='utf-8')))))
        return 0
    size = int(argv[argv.index('--sample') + 1]) if '--sample' in argv else 30
    methods = argv[argv.index('--methods') + 1].split(',') if '--methods' in argv else METHODS + ['law.py']
    out_file = Path(__file__).with_name(argv[argv.index('--out') + 1] if '--out' in argv else 'word_matching.json')
    random.seed(5)
    here = [c['path'] for c in law.manifest()['corpora'] if (ROOT / c['path'] / '.git').exists()]
    sample = []
    for corpus in sorted(here)[:14]:
        if corpus in law.behind():
            continue
        ix = law._index(corpus)
        many = sorted(f for f, vs in ix['files'].items() if f.endswith('.md') and len(vs) >= 4)
        sample += [('2026-11-04', f'{corpus}/{f}') for f in random.sample(many, min(max(1, size // 8), len(many)))]
    cases = [c for c in SLOW if (ROOT / '/'.join(c[1].split('/')[:3]) / '.git').exists()]
    cases += [c for c in random.sample(sample, min(size, len(sample))) if c not in cases]
    law.close_readers()
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(cases, f)
    results = {}
    for method in methods:
        t = time.time()
        done = subprocess.run([sys.executable, '-X', 'utf8', __file__, '--worker', method, f.name], cwd=ROOT,
                              capture_output=True, encoding='utf-8')
        if done.returncode:
            print(method, 'failed:', done.stderr[-600:], file=sys.stderr)
            continue
        results[method] = json.loads(done.stdout)
        print(f'{method}: {time.time() - t:.0f} s', file=sys.stderr)
    os.unlink(f.name)
    base = results.get('current') or results[methods[0]]
    slow = {f'{d} {p}' for d, p in SLOW}
    summary = {}
    for method, res in results.items():
        diffs = [compare(base[k], res[k]) for k in base]
        summary[method] = {
            'words_slow_s': round(sum(res[k]['words_s'] for k in res if k in slow), 1),
            'words_sample_s': round(sum(res[k]['words_s'] for k in res if k not in slow), 1),
            'chars': sum(d['chars'] for d in diffs), 'chars_differ': sum(d['chars_differ'] for d in diffs),
            'files_differ': sum(1 for d in diffs if d['chars_differ']),
            'per_file': {k: {'words_s': res[k]['words_s'], **compare(base[k], res[k])} for k in res},
        }
    out_file.write_text(json.dumps({'cases': cases, 'summary': summary}, indent=1), encoding='utf-8', newline='\n')
    print(f"{'method':<16}{'slow files':>12}{'sample':>10}{'chars differ':>20}{'files':>8}")
    for m, s in summary.items():
        print(f"{m:<16}{s['words_slow_s']:>11.1f}s{s['words_sample_s']:>9.1f}s{s['chars_differ']:>10}/{s['chars']:<9}"
              f"{s['files_differ']:>4}/{len(cases)}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
