#!/usr/bin/env python3
"""regress.py - the differential-testing regression set (DESIGN D4): every universe under
caselaw-lean-2/fixtures/regress/<name>/{data,edges} is a counterexample that once made the Lean runner and the
reference disagree; after triage and fixes both must agree on it (canonical diff.py, zero disagreements).

  python regress.py                 # run all, print one line each, exit 1 on any disagreement
  python regress.py --add DIR NAME  # copy a universe's data/ and edges/ into the set
  python regress.py --seeds 3,12 --prefix gen   # generate universes with gen.py's current generator and add them
        [--legacy]                  # ... as generated before the five-limits layer (old counterexample seeds)
  python regress.py --ref-only      # run only the reference on every universe (no Lean): exit 1 on an exception
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen  # noqa: E402
import diff as dmod  # noqa: E402

REG = os.path.join(gen.WORK, 'fixtures', 'regress')


def add(src, name):
    dst = os.path.join(REG, name)
    shutil.rmtree(dst, ignore_errors=True)
    for sub in ('data', 'edges'):
        shutil.copytree(os.path.join(src, sub), os.path.join(dst, sub))
    return dst


def run_one(d):
    out = os.path.join(d, 'out')
    shutil.rmtree(out, ignore_errors=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'precedent_ref.py'), 'run', '--data', os.path.join(d, 'data'),
                    '--edges', os.path.join(d, 'edges'), '--out', os.path.join(out, 'ref')], check=True,
                   stderr=subprocess.DEVNULL)
    gen.run_lean(out_root(d))
    D, missing = dmod.compare(os.path.join(out, 'lean'), os.path.join(out, 'ref'), dmod.load_map(None))
    return D, missing


def out_root(d):
    """gen.run_lean writes <root>/lean from <root>/data: stage a root under out/ pointing at the fixture."""
    root = os.path.join(d, 'out')
    for sub in ('data', 'edges'):
        p = os.path.join(root, sub)
        if not os.path.exists(p):
            shutil.copytree(os.path.join(d, sub), p)
    return root


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--add', nargs=2, metavar=('DIR', 'NAME'))
    ap.add_argument('--seeds')
    ap.add_argument('--prefix', default='gen')
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--legacy', action='store_true', help='with --seeds: the pre-layer generator (gen.py --legacy)')
    ap.add_argument('--no-r5', action='store_true',
                    help='with --seeds: without the round-5 layer (a counterexample seed of a sweep before round 5)')
    ap.add_argument('--ref-only', action='store_true', help='run the reference alone (no Lean, no diff)')
    a = ap.parse_args()
    os.makedirs(REG, exist_ok=True)
    if a.add:
        print(add(*a.add))
        return
    if a.seeds:
        for s in a.seeds.split(','):
            d = os.path.join(REG, '%s-%s' % (a.prefix, s))
            shutil.rmtree(d, ignore_errors=True)
            gen.generate(int(s), d, a.n, a.legacy, r5=not a.no_r5)
        return
    if a.ref_only:
        bad = 0
        names = sorted(n for n in os.listdir(REG) if os.path.isdir(os.path.join(REG, n, 'data')))
        for n in names:
            d = os.path.join(REG, n)
            p = subprocess.run([sys.executable, os.path.join(HERE, 'precedent_ref.py'), 'run', '--data',
                                os.path.join(d, 'data'), '--edges', os.path.join(d, 'edges'), '--out',
                                os.path.join(d, 'out', 'ref')], capture_output=True, text=True)
            bad += p.returncode != 0
            print('%-16s %s' % (n, 'ok' if p.returncode == 0 else 'EXCEPTION ' + p.stderr[-800:]))
        print('%d universes, %d failing (reference only)' % (len(names), bad))
        sys.exit(1 if bad else 0)
    gen.build_lean()
    bad = 0
    names = sorted(n for n in os.listdir(REG) if os.path.isdir(os.path.join(REG, n, 'data')))
    for n in names:
        D, missing = run_one(os.path.join(REG, n))
        k = sum(D.bad_keys.values())
        bad += k > 0 or bool(missing)
        print('%-16s %s' % (n, 'ok' if not k and not missing else '%d disagreeing keys %s' % (k, missing)))
    print('%d universes, %d disagreeing' % (len(names), bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
