#!/usr/bin/env python3
"""drt.py - generated differential testing with the batched, interpreted Lean runner (DESIGN D4).

Windows Application Control may block the compiled runner (caselaw2.exe); `lake env lean --run Run.lean` then costs
~12 s of elaboration per universe. This driver generates universes and runs the reference with gen.py, then runs the
Lean runner over all of them through caselaw-lean-2/runner/RunBatch.lean (the built Run module, imported once per
batch process), merges each universe's output as gen.run_lean does, and diffs canonically with diff.py.

  python drt.py --seed 50000 --rounds 1000 [--n 60] --out DIR [--jobs 16] [--batches 12] [--keep]
  python drt.py --dirs DIR1,DIR2,...  --out DIR     # existing universes (data/, edges/), e.g. the regression set
"""
import argparse
import os
import shutil
import subprocess
import sys
from collections import Counter
from multiprocessing import Pool
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen  # noqa: E402
import diff as dmod  # noqa: E402

# lean-proofs: this file's own checkout (Windows, or the WSL copy made by caselaw-lean-2/wsl/sync.sh)
LP = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
LAKE = 'lake.exe' if os.name == 'nt' else 'lake'
BATCH = os.path.join(gen.WORK, 'runner', 'RunBatch.lean')
FILES = ('status', 'findings', 'certs', 'splits', 'conflicts', 'lines', 'horty')
# the toolchain's own binaries first: Application Control may block the elan proxies in ~/.elan/bin
TC = os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.35.0/bin')
ENV = dict(os.environ, PATH=TC + os.pathsep + os.path.expanduser('~/.elan/bin') + os.pathsep + os.environ.get('PATH', ''))


def fwd(p):
    return p.replace('\\', '/')


def prep(job):
    seed, d, n = job
    if seed is not None:
        gen.generate(seed, d, n)
    shutil.rmtree(os.path.join(d, 'ref'), ignore_errors=True)
    shutil.rmtree(os.path.join(d, 'lean'), ignore_errors=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'precedent_ref.py'), 'run', '--data', os.path.join(d, 'data'),
                    '--edges', os.path.join(d, 'edges'), '--out', os.path.join(d, 'ref')], check=True,
                   stderr=subprocess.DEVNULL)
    with open(os.path.join(d, 'data', 'decisions2.tsv'), encoding='utf-8') as f:
        nodes = 1 + max([int(l.split('\t', 1)[0]) for l in f if l.strip()] or [0])
    os.makedirs(os.path.join(d, 'lean'), exist_ok=True)
    return seed, d, nodes


def merge(d):
    out = os.path.join(d, 'lean')
    for name, head in gen.LEAN_HEADERS.items():
        src = os.path.join(out, '%s-00.tsv' % name)
        with open(src, encoding='utf-8') as a:
            body = a.read()
        with open(os.path.join(out, name + '.tsv'), 'w', encoding='utf-8', newline='\n') as b:
            b.write(head + '\n' + body)
        os.remove(src)
    os.replace(os.path.join(out, 'summary-00.tsv'), os.path.join(out, 'summary.tsv'))


def diff_one(job):
    seed, d = job
    merge(d)
    D, missing = dmod.compare(os.path.join(d, 'lean'), os.path.join(d, 'ref'), dmod.load_map(None))
    with open(os.path.join(d, 'diff.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for r in D.rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    return seed, d, [(seed,) + tuple(r) for r in D.rows], dict(D.compared), dict(D.bad_keys), dict(D.info), missing


def run_batches(items, k, out):
    procs = []
    for b in range(k):
        part = items[b::k]
        if not part:
            continue
        lst = os.path.join(out, 'batch-%02d.tsv' % b)
        with open(lst, 'w', encoding='utf-8', newline='\n') as f:
            for _, d, nodes in part:
                f.write('%s\t%s\t%s\t%d\t20261112\n' % (fwd(os.path.join(d, 'data')), fwd(os.path.join(d, 'edges')),
                                                       fwd(os.path.join(d, 'lean')), nodes))
        log = open(os.path.join(out, 'batch-%02d.log' % b), 'w', encoding='utf-8')
        procs.append(subprocess.Popen([os.path.join(TC, LAKE), 'env', 'lean', fwd(BATCH)], cwd=LP, stdout=log, stderr=subprocess.STDOUT,
                                      env=dict(ENV, CASELAW2_BATCH=fwd(lst))))
    for p in procs:
        p.wait()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--rounds', type=int, default=1)
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--dirs')
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=16)
    ap.add_argument('--batches', type=int, default=12)
    ap.add_argument('--keep', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    subprocess.run([os.path.join(TC, LAKE), 'build', 'LegalProofs.CaseLaw2.Run'], cwd=LP, check=True, stdout=subprocess.DEVNULL, env=ENV)
    if a.dirs:
        jobs = [(None, d, a.n) for d in a.dirs.split(',')]
    else:
        jobs = [(a.seed + r, os.path.join(a.out, 'r%05d' % (a.seed + r)), a.n) for r in range(a.rounds)]
    with Pool(a.jobs) as pool:
        items = pool.map(prep, jobs)
    run_batches(items, a.batches, a.out)
    buckets, keys, comp, bad, info = Counter(), {}, Counter(), Counter(), Counter()
    disagreeing, allrows, failed = 0, [], []
    with Pool(a.jobs) as pool:
        for seed, d, rows, c, b, inf, missing in pool.imap_unordered(diff_one, [(s, d) for s, d, _ in items]):
            comp.update(c); bad.update(b); info.update(inf); allrows.extend(rows)
            if missing:
                failed.append((d, missing))
            seen = set()
            for r in rows:
                k = (r[1], r[2], r[3])
                if k in seen:
                    continue
                seen.add(k)
                buckets[k] += 1
                keys.setdefault(k, []).append((seed if seed is not None else os.path.basename(d), r[4], r[5], r[6]))
            if rows or missing:
                disagreeing += 1
                print('%s: %d disagreeing rows %s' % (seed if seed is not None else d, len(rows), missing or ''),
                      flush=True)
            elif seed is not None and not a.keep:
                shutil.rmtree(d, ignore_errors=True)
    with open(os.path.join(a.out, 'drt_diff.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for r in sorted(allrows, key=lambda r: tuple(str(x) for x in r)):
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('\n%d universes, %d with a disagreement' % (len(items), disagreeing))
    for fn in FILES:
        print('  %-9s %d of %d keys disagree' % (fn, bad[fn], comp[fn]))
    print('  class (file, bucket, rule): rounds   first example')
    for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]):
        print('  %-9s %-36s %-26s %5d   e.g. %s %s A=%s B=%s' % (k + (v,) + keys[k][0]))
    for k, v in sorted(info.items()):
        print('  info  %-60s %d' % (k, v))


if __name__ == '__main__':
    main()
