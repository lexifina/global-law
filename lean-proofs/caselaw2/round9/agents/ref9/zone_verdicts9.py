#!/usr/bin/env python3
"""zone_verdicts9.py - the reference's part-zone verdicts on a staged data dir (Data + Engine.admit only, no status).

  CASELAW2_REF=<ref dir> python3 zone_verdicts9.py --data DIR [--zones FILE] --out PREFIX [--refused FILE]
    --zones: a part_zone.tsv to use instead of DIR's (DIR is linked file by file into PREFIX.data/ first)
    writes PREFIX.tsv (table, id, text owner, round-9 verdict) for every row whose verdict is partZone, and
    PREFIX.txt (counters, verdict counts, and with --refused the comparison with a list of expected refusals:
    a TSV whose first two columns are id and table).
"""
import argparse
import os
import shutil
import sys
import time
from collections import Counter

REF = os.environ.get('CASELAW2_REF') or os.path.expanduser('~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref')
sys.path.insert(0, REF)
import precedent_ref as pr  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--zones')
    ap.add_argument('--out', required=True)
    ap.add_argument('--refused')
    a = ap.parse_args()
    data = a.data
    if a.zones:
        data = a.out + '.data'
        shutil.rmtree(data, ignore_errors=True)
        os.makedirs(data)
        for f in os.listdir(a.data):
            if f.endswith('.tsv') and f != 'part_zone.tsv':
                os.symlink(os.path.realpath(os.path.join(a.data, f)), os.path.join(data, f))
        os.symlink(os.path.realpath(a.zones), os.path.join(data, 'part_zone.tsv'))
    t0 = time.time()
    D = pr.Data(data, lambda *x: print(*x, file=sys.stderr, flush=True))
    A = pr.Engine(D)
    A.admit()
    out = []
    cnt = Counter()
    for (f, i), v in A.cert_ok.items():
        cnt[(f, A.cert_verdict(f, i))] += 1
        if v == 'partZone':
            out.append((f.replace('.tsv', ''), i))
    lines = ['zone_nodes\t%d' % len(D.zones), 'zone_lines\t%d' % D.zone_lines, 'zone_bad_nodes\t%d' % D.zone_bad_nodes,
             'zone_bad_rows\t%d' % D.zone_bad, 'zone_checked_rows\t%d' % A.zone_checked,
             'zone_failed_rows\t%d' % A.zone_failed, 'zone_missing_rows\t%d' % A.zone_missing,
             'seconds\t%.0f' % (time.time() - t0)]
    lines += ['verdict\t%s\t%s\t%d' % (f, v, n) for (f, v), n in sorted(cnt.items())]
    if a.refused:
        exp = set()
        with open(a.refused, encoding='utf-8') as fh:
            for line in fh:
                p = line.rstrip('\n').split('\t')
                if len(p) >= 2:
                    exp.add((p[1].replace('treatment', 'treatments').replace('treatmentss', 'treatments'), p[0]))
        got = set(out)
        lines += ['refused_expected\t%d' % len(exp), 'refused_ref\t%d' % len(got),
                  'both\t%d' % len(exp & got)]
        lines += ['only_expected\t%s\t%s' % k for k in sorted(exp - got)]
        lines += ['only_ref\t%s\t%s' % k for k in sorted(got - exp)]
    with open(a.out + '.tsv', 'w', encoding='utf-8', newline='\n') as fh:
        for (t, i) in sorted(out):
            fh.write('%s\t%s\n' % (t, i))
    with open(a.out + '.txt', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:60]))


if __name__ == '__main__':
    main()
