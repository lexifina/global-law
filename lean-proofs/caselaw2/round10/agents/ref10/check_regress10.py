#!/usr/bin/env python3
"""check_regress10.py - round 10 (after round 9 check_regress9.py): universes with no round-10 table.

For every universe DIR/<u> (data/, edges/; optionally lean/ = a stored Lean output, ref/ = a stored reference output)
run the CURRENT reference (CASELAW2_REF) and the BASE reference (--base, the round-9 final in round10/pre/ref) into
OUT/<root>/<u>/{cur,base} and compare
  1. bytes cur vs base (ref_stats.tsv without seconds / peak_mb): must be the same (round-10 mode by presence);
  2. bytes cur vs the stored ref/ when present (informational: the stored output of an earlier reference);
  3. canonical diff cur vs the stored lean/ when present (informational: as the earlier rounds).
A universe that has history_remand.tsv is reported (it should not occur here).

  CASELAW2_REF=<ref dir> python3 check_regress10.py --base <base ref dir> --root DIR [--root DIR ...] --out OUT
"""
import argparse
import os
import shutil
import subprocess
import sys
from collections import Counter
from multiprocessing import Pool

REF = os.environ.get('CASELAW2_REF') or os.path.expanduser(
    '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref')
sys.path.insert(0, REF)
import diff as dmod  # noqa: E402

BASE = None


def strip(name, b):
    if name != 'ref_stats.tsv':
        return b
    return b'\n'.join(l for l in b.split(b'\n') if not l.startswith((b'seconds\t', b'peak_mb\t')))


def same_dirs(a, b):
    files = sorted(set(os.listdir(a)) | set(os.listdir(b)))
    bad = [f for f in files if not (os.path.exists(os.path.join(a, f)) and os.path.exists(os.path.join(b, f))
                                    and strip(f, open(os.path.join(a, f), 'rb').read())
                                    == strip(f, open(os.path.join(b, f), 'rb').read()))]
    return 'same' if not bad else 'DIFFERENT ' + ','.join(bad)


def run_ref(ref, u, out):
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    env = dict(os.environ, CASELAW2_REF=ref)
    p = subprocess.run([sys.executable, os.path.join(ref, 'precedent_ref.py'), 'run', '--data', os.path.join(u, 'data'),
                        '--edges', os.path.join(u, 'edges'), '--out', out], capture_output=True, text=True, env=env)
    return p.returncode, p.stderr[-300:]


def one(job):
    u, out, base = job
    cur, bas = os.path.join(out, 'cur'), os.path.join(out, 'base')
    rc, err = run_ref(REF, u, cur)
    if rc != 0:
        return u, 'CUR FAILED ' + err, '-', None
    rc, err = run_ref(base, u, bas)
    if rc != 0:
        return u, 'BASE FAILED ' + err, '-', None
    res = same_dirs(bas, cur)
    stored = same_dirs(os.path.join(u, 'ref'), cur) if os.path.isdir(os.path.join(u, 'ref')) else 'none'
    lean = os.path.join(u, 'lean')
    nlean = None
    if os.path.exists(os.path.join(lean, 'certs.tsv')):
        D, missing = dmod.compare(lean, cur, dmod.load_map(None))
        nlean = len(D.rows) + len(missing)
    if os.path.exists(os.path.join(u, 'data', 'history_remand.tsv')):
        res += ' (ROUND-10 INPUT PRESENT)'
    if res == 'same' and stored in ('same', 'none'):
        shutil.rmtree(out, ignore_errors=True)
    return u, res, stored, nlean


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', action='append', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    jobs = []
    for root in a.root:
        tag = os.path.basename(os.path.normpath(root))
        for x in sorted(os.listdir(root)):
            if os.path.isdir(os.path.join(root, x, 'data')):
                jobs.append((os.path.join(root, x), os.path.join(a.out, tag, x), a.base))
    nres, nstored, nlean_bad = Counter(), Counter(), 0
    with Pool(a.jobs) as pool:
        for u, res, stored, nlean in pool.imap(one, jobs):
            nres[res.split(' ')[0]] += 1
            nstored[stored.split(' ')[0]] += 1
            if res != 'same':
                print('%s: cur vs base %s' % (u, res), flush=True)
            if stored not in ('same', 'none'):
                print('%s: cur vs stored ref %s' % (u, stored), flush=True)
            if nlean:
                nlean_bad += 1
                print('%s: %d canonical disagreements with the stored lean output' % (u, nlean), flush=True)
    print('\n%d universes; cur vs base reference bytes: %s' % (
        len(jobs), ', '.join('%s %d' % kv for kv in sorted(nres.items()))))
    print('cur vs stored ref output bytes: %s' % ', '.join('%s %d' % kv for kv in sorted(nstored.items())))
    print('universes disagreeing canonically with the stored lean output: %d' % nlean_bad)
    sys.exit(1 if set(nres) - {'same'} else 0)


if __name__ == '__main__':
    main()
