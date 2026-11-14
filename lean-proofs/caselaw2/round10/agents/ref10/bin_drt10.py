#!/usr/bin/env python3
"""bin_drt10.py - round 10 (ref10): the differential of a compiled Lean runner BINARY against the Python reference on
existing universes DIR/<u>/{data,edges} (as round 7's r7_drt_run.py, but the runner is the binary lean10 copies to
~/caselaw2/r10_bin/, called as wsl/r10_run.sh calls it: <bin> DATA EDGES shard nshards OUT NODES asOf, one shard).

  CASELAW2_REF=<ref dir> python3 bin_drt10.py --bin <binary> --root DIR [--root DIR ...] --out OUT [--jobs 8]

Each universe keeps DIR/<u>/ref, DIR/<u>/lean, DIR/<u>/diff.tsv (read by make_r10.py report). OUT gets drt_diff.tsv
(every disagreement row); the summary goes to stdout.
"""
import argparse
import os
import subprocess
import sys
from collections import Counter
from multiprocessing import Pool

REF = os.environ.get('CASELAW2_REF') or os.path.expanduser(
    '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref')
sys.path.insert(0, REF)
import drt  # noqa: E402

BIN = None


def one(d):
    try:
        _, d, nodes = drt.prep((None, d, 60, False))
    except subprocess.CalledProcessError as e:
        return d, 'REF FAILED %s' % e, None
    lean = os.path.join(d, 'lean')
    p = subprocess.run([BIN, os.path.join(d, 'data'), os.path.join(d, 'edges'), '0', '1', lean, str(nodes),
                        '20261112'], capture_output=True, text=True,
                       cwd=os.environ.get('LP_DIR') or os.path.expanduser('~/caselaw2/lean-proofs'))
    if p.returncode != 0 or not all(os.path.exists(os.path.join(lean, f)) for f in ('certs-00.tsv', 'summary-00.tsv')):
        with open(os.path.join(d, 'lean.err'), 'w', encoding='utf-8') as f:
            f.write(p.stdout[-4000:] + '\n' + p.stderr[-4000:])
        return d, 'LEAN FAILED rc=%d' % p.returncode, None
    return d, 'ok', drt.diff_one((None, d))


def main():
    global BIN
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', action='append', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--bin', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    BIN = os.path.abspath(a.bin)
    os.makedirs(a.out, exist_ok=True)
    dirs = []
    for root in a.root:
        dirs += sorted(os.path.join(root, x) for x in os.listdir(root) if os.path.isdir(os.path.join(root, x, 'data')))
    buckets, keys, comp, bad, info = Counter(), {}, Counter(), Counter(), Counter()
    disagreeing, allrows, failed = 0, [], []
    with Pool(a.jobs, initializer=_init, initargs=(BIN,)) as pool:
        for d, st, res in pool.imap_unordered(one, dirs):
            name = os.path.basename(d)
            if res is None:
                failed.append((name, st))
                continue
            seed, d, rows, c, b, inf, missing = res
            comp.update(c); bad.update(b); info.update(inf)
            allrows.extend((name,) + tuple(r[1:]) for r in rows)
            seen = set()
            for r in rows:
                k = (r[1], r[2], r[3])
                if k in seen:
                    continue
                seen.add(k)
                buckets[k] += 1
                keys.setdefault(k, []).append((name, r[4], r[5], r[6]))
            if rows or missing:
                disagreeing += 1
                print('%s: %d disagreeing rows %s' % (name, len(rows), missing or ''), flush=True)
    with open(os.path.join(a.out, 'drt_diff.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for r in sorted(allrows, key=lambda r: tuple(str(x) for x in r)):
            f.write('\t'.join(str(x) for x in r) + '\n')
    for name, st in failed:
        print('%s %s' % (st, name))
    print('\n%d universes, %d with a disagreement, %d failed (binary %s)' % (len(dirs), disagreeing, len(failed), BIN))
    for fn in drt.FILES + tuple(fn for fn in drt.FILES5 if comp[fn]):
        print('  %-9s %d of %d keys disagree' % (fn, bad[fn], comp[fn]))
    print('  class (file, bucket, rule): universes   first example')
    for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]):
        print('  %-9s %-36s %-26s %5d   e.g. %s %s A=%s B=%s' % (k + (v,) + keys[k][0]))
    for k, v in sorted(info.items()):
        print('  info  %-60s %d' % (k, v))
    sys.exit(1 if (disagreeing or failed) else 0)


def _init(b):
    global BIN
    BIN = b


if __name__ == '__main__':
    main()
