#!/usr/bin/env python3
"""check_regress8.py - round 8 (copy of round 7's check_a.py): the earlier rounds' universes, no round-8 table.
Stored outputs: DIR/<u>/ref = the round-7 reference's, DIR/<u>/lean = the round-7 Lean runner's (difftest7 run 3).

For every universe DIR/<u> (data/, edges/, lean/ = the stored Lean output of an earlier differential run, ref/ = the
stored output of the round-6 reference), run the CURRENT reference into OUT/<root>/<u>/ and
  1. compare its bytes with the stored reference output (ref_stats.tsv without seconds / peak_mb);
  2. compare it canonically with the stored Lean output (diff.py, as drt.py does).
A universe that has joined.tsv or history_claim.tsv, or a doctrine class line, is reported (it should not occur).

  CASELAW2_REF=<ref dir> python3 check_a.py --root DIR [--root DIR ...] --out OUT [--jobs 20]
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

FILES = ('status', 'findings', 'certs', 'splits', 'conflicts', 'lines', 'horty', 'classes', 'summary')


def strip(name, b):
    if name != 'ref_stats.tsv':
        return b
    return b'\n'.join(l for l in b.split(b'\n') if not l.startswith((b'seconds\t', b'peak_mb\t')))


def round7_input(data):
    """(round 8) a round-8 input: history_bridge.tsv, or an anchorWide claim line"""
    if os.path.exists(os.path.join(data, 'history_bridge.tsv')):
        return True
    p = os.path.join(data, 'history_claim.tsv')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            return b'anchorWide' in f.read()
    return False


def one(job):
    u, out = job
    data = os.path.join(u, 'data')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.run([sys.executable, os.path.join(REF, 'precedent_ref.py'), 'run', '--data', data, '--edges',
                        os.path.join(u, 'edges'), '--out', out], capture_output=True, text=True)
    if p.returncode != 0:
        return u, 'REF FAILED ' + p.stderr[-300:], None, None, None, []
    # 1. bytes against the stored reference output
    old = os.path.join(u, 'ref')
    bytes_res = 'no stored ref'
    if os.path.isdir(old):
        files = sorted(set(os.listdir(old)) | set(os.listdir(out)))
        bad = [f for f in files if not (os.path.exists(os.path.join(old, f)) and os.path.exists(os.path.join(out, f))
                                        and strip(f, open(os.path.join(old, f), 'rb').read())
                                        == strip(f, open(os.path.join(out, f), 'rb').read()))]
        bytes_res = 'same' if not bad else 'DIFFERENT ' + ','.join(bad)
    # 2. canonical diff against the stored Lean output
    lean = os.path.join(u, 'lean')
    if not os.path.exists(os.path.join(lean, 'certs.tsv')):
        return u, bytes_res, None, None, None, ['no stored lean output']
    D, missing = dmod.compare(lean, out, dmod.load_map(None))
    return u, bytes_res, dict(D.compared), dict(D.bad_keys), [r for r in D.rows], missing + (
        ['ROUND-8 INPUT PRESENT'] if round7_input(data) else [])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', action='append', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=20)
    a = ap.parse_args()
    jobs = []
    for root in a.root:
        tag = os.path.basename(os.path.normpath(root))
        for x in sorted(os.listdir(root)):
            if os.path.isdir(os.path.join(root, x, 'data')):
                jobs.append((os.path.join(root, x), os.path.join(a.out, tag, x)))
    comp, bad, nbytes, ndis, rows = Counter(), Counter(), Counter(), 0, []
    with Pool(a.jobs) as pool:
        for u, br, c, b, rs, missing in pool.imap(one, jobs):
            nbytes[br.split(' ')[0]] += 1
            if br != 'same':
                print('%s: bytes %s' % (u, br), flush=True)
            if c is None:
                print('%s: %s' % (u, missing), flush=True)
                ndis += 1
                continue
            comp.update(c)
            bad.update(b)
            if rs or missing:
                ndis += 1
                print('%s: %d disagreeing rows %s' % (u, len(rs), missing or ''), flush=True)
                rows += [(os.path.basename(u),) + tuple(r) for r in rs]
    with open(os.path.join(a.out, 'diff_rows.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('\n%d universes; bytes against the stored reference output: %s' % (
        len(jobs), ', '.join('%s %d' % kv for kv in sorted(nbytes.items()))))
    print('canonical diff against the stored Lean output: %d universes with a disagreement' % ndis)
    for fn in FILES:
        if comp[fn]:
            print('  %-9s %d of %d keys disagree' % (fn, bad[fn], comp[fn]))
    sys.exit(1 if ndis or set(nbytes) - {'same'} else 0)


if __name__ == '__main__':
    main()
