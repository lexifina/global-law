#!/usr/bin/env python3
"""bridge_verdicts8.py - the reference's certificate verdicts for every history row with a line in history_bridge.tsv
of a staged data dir (round8/stage/<name>), by reason, plus the step each bridge failure stopped at. Only Data +
Engine.admit run (no status, findings, splits).

  CASELAW2_REF=<ref dir> python3 bridge_verdicts8.py <data dir> [--out FILE]   (FILE: id, verdict, kind, w_node)
"""
import argparse
import os
import sys
from collections import Counter

REF = os.environ.get('CASELAW2_REF') or os.path.expanduser(
    '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref')
sys.path.insert(0, REF)
import precedent_ref as P  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('--out')
    a = ap.parse_args()
    D = P.Data(a.data, lambda *x: print(*x, file=sys.stderr, flush=True))
    E = P.Engine(D)
    E.admit()
    kinds = {r['id']: r['kind'] for r in D.history}
    c = Counter()
    ck = Counter()
    rows = []
    for hid, b in sorted(D.bridge.items()):
        v = E.cert_ok.get(('history.tsv', hid))
        c[v] += 1
        ck[(kinds.get(hid), v)] += 1
        rows.append((hid, v, kinds.get(hid), b[0]))
    print('history_bridge.tsv: kept %d, bad %d, unknown ids %d, duplicates %d' % (
        len(D.bridge), D.bridge_bad, D.bridge_unknown, D.bridge_dup))
    print('cue sources: %s' % {k: v for k, v in P.R7_CUE_SOURCE.items() if k.startswith(('bridge', 'anchor'))})
    for v, n in c.most_common():
        print('  %-22s %d' % (v, n))
    print('by kind:')
    for (k, v), n in sorted(ck.items(), key=lambda kv: (str(kv[0][0]), -kv[1])):
        print('  %-16s %-22s %d' % (k, v, n))
    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            for r in rows:
                f.write('\t'.join(str(x) for x in r) + '\n')


if __name__ == '__main__':
    main()
