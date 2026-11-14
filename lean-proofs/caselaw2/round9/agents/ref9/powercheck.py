#!/usr/bin/env python3
"""powercheck.py - which rows does the Lean runner write as noAuthority / targetLater (the verdicts after the text
checks, which the reference decides in the status layer)? For DESIGN9 D9-4 (2): partZone runs only on a row whose
complete round-8 verdict is ok, so the reference must know these rows. Compares, on stored universes (DIR/<u>/data +
DIR/<u>/lean/certs.tsv of an earlier differential run), the Lean's verdict of every row the reference passes with a
predicate of the reference:
  treatments (non-witness): targetLater if both dates are known and date(by) < date(target); else noAuthority if
      can_change(by, target, scope domain) is no;
  treatments (witness): the same with by (the overruling decision Y);
  history: noAuthority if same_case_power(by, target, claims) is no (targetLater is the reference's own verdict).
  python powercheck.py DIR... -> a confusion table (predicate, Lean verdict) per table / witness.
"""
import os
import sys
from collections import Counter

REF = os.environ.get('CASELAW2_REF') or os.path.expanduser('~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref')
sys.path.insert(0, REF)
import precedent_ref as pr  # noqa: E402
MODE = os.environ.get('PMODE', 'scope')


def predict(A, table, r):
    D = A.D
    if table == 'treatments':
        b, t = r['by'], r['target']
        if r['id'] in D.witness:
            if D.date[b] < D.date[t]:
                return 'targetLater'
        elif D.date[b] and D.date[t] and D.date[b] < D.date[t]:
            return 'targetLater'
        a = A.can_change(b, t, A._scope_dom(r['scope']))[0]
        u = A.can_change(b, t, 'unknown')[0]
        if MODE == 'scope':
            return 'noAuthority' if a == 'no' else 'ok'
        return 'noAuthority' if u == 'no' else 'ok'
    if A.same_case_power(r['by'], r['target'], D.hclaim.get(r['id'])) == 'no':
        return 'noAuthority'
    return 'ok'


def main():
    conf = Counter()
    ex = {}
    for root in sys.argv[1:]:
        for u in sorted(os.listdir(root)):
            d = os.path.join(root, u)
            lc = os.path.join(d, 'lean', 'certs.tsv')
            if not os.path.exists(lc):
                continue
            lean = {}
            with open(lc, encoding='utf-8', errors='replace') as f:
                for line in f:
                    p = line.rstrip('\n').split('\t')
                    if len(p) >= 3 and p[0] != 'table':
                        lean[('treatments' if p[0].startswith('treat') else p[0], p[1])] = p[2]
            pr.BAD_ROWS.clear()
            D = pr.Data(os.path.join(d, 'data'))
            A = pr.Engine(D)
            A.admit()
            for table, rows in (('treatments', D.treatments), ('history', D.history)):
                for r in rows:
                    v = A.cert_ok.get((table + '.tsv', r['id']))
                    if v != 'ok':
                        continue
                    w = 'witness' if (table == 'treatments' and r['id'] in D.witness) else ''
                    if table == 'treatments' and r['id'] in A.recog_all:
                        w += '+recog'
                    p = predict(A, table, r)
                    lv = lean.get((table, r['id']), 'missing')
                    if table == 'treatments':
                        w += ':' + ('neg' if r['kind'] in pr.NEG_TREAT else 'nonneg') + ':' + r['kind'] * (os.environ.get('KINDS') == '1')
                    k = (table + ('/' + w if w else ''), p, lv)
                    conf[k] += 1
                    ex.setdefault(k, '%s %s' % (u, r['id']))
    for k, n in sorted(conf.items()):
        print('%-28s predicted %-12s lean %-26s %6d   e.g. %s' % (k + (n, ex[k])))


if __name__ == '__main__':
    main()
