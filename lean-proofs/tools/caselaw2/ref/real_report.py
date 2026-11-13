#!/usr/bin/env python3
"""real_report.py - disagreement rates on the real data, per output file and rule, plus a stratified sample for
triage (DESIGN D4).

  python real_report.py RUN_DIR [--sample 100] [--seed 1]

RUN_DIR holds lean/ and ref/ (run_lean.sh and precedent_ref.py outputs on caselaw-lean-2/data). Writes
RUN_DIR/rates.tsv (file, bucket, rule, disagreeing keys, compared keys of that file, rate) and RUN_DIR/sample.tsv
(the sample: at least one row per (file, bucket, rule) class, the rest in proportion to class size, with an empty
'triage' column to fill in: a = Lean wrong, b = reference wrong, c = doctrine ambiguous, d = data).
"""
import argparse
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diff as dmod  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('run')
    ap.add_argument('--sample', type=int, default=100)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    D, missing = dmod.compare(os.path.join(a.run, 'lean'), os.path.join(a.run, 'ref'), dmod.load_map(None), ex=0)
    classes = defaultdict(list)
    for r in D.rows:
        classes[(r[0], r[1], r[2])].append(r)
    with open(os.path.join(a.run, 'rates.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('file\tbucket\trule\tdisagreeing_keys\tcompared_keys\trate\n')
        for fn in ('status', 'findings', 'certs', 'splits'):
            n = D.compared[fn]
            f.write('%s\tALL\tALL\t%d\t%d\t%.6f\n' % (fn, D.bad_keys[fn], n, D.bad_keys[fn] / n if n else 0))
        for (fn, b, rule), rs in sorted(classes.items(), key=lambda kv: -len(kv[1])):
            keys = {r[3].split('@')[0] for r in rs}
            n = D.compared[fn]
            f.write('%s\t%s\t%s\t%d\t%d\t%.6f\n' % (fn, b, rule, len(keys), n, len(keys) / n if n else 0))
    R = random.Random(a.seed)
    total = sum(len(v) for v in classes.values())
    sample = []
    for k, rs in sorted(classes.items()):
        quota = max(1, round(a.sample * len(rs) / total)) if total else 0
        sample += R.sample(rs, min(quota, len(rs)))
    with open(os.path.join(a.run, 'sample.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('file\tbucket\trule\tkey\tlean\tref\ttriage\tnote\n')
        for r in sample:
            f.write('\t'.join(str(x) for x in r) + '\t\t\n')
    print('%d disagreement rows in %d classes; %d sampled; missing: %s' % (total, len(classes), len(sample),
                                                                         ','.join(missing) or '-'))
    for fn in ('status', 'findings', 'certs', 'splits'):
        print('  %-9s %d of %d keys disagree' % (fn, D.bad_keys[fn], D.compared[fn]))


if __name__ == '__main__':
    main()
