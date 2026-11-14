#!/usr/bin/env python3
"""identity_verdicts11.py - round 11 (ref11): the reference's identityTie condition (Engine.check_identity, DESIGN11
§5.2, D11-8) on a builder's identity delta over real data, without a full run: streams decisions2 / cert_text /
window_sha of the base stage (+ the delta's cert_text / window_sha) for the nodes of the lines only, then calls the
reference's own check_identity on a small Data stand-in. Only the identity condition is checked (not the row's
round-10 verdict or power).

  python identity_verdicts11.py --base round10/stage/v10d --history DELTA/history_delta.tsv [--history ...]
         --ident DIR (history_identity_delta.tsv, cert_text_delta.tsv, window_sha_delta.tsv, precheck.tsv) --out TSV
"""
import argparse
import hashlib
import os
import sys
from collections import Counter, defaultdict

REF = os.environ.get('CASELAW2_REF') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', 'global-law-lean', 'lean-proofs',
    'tools', 'caselaw2', 'ref')
sys.path.insert(0, REF)
import precedent_ref as pr  # noqa: E402


class MiniData:
    def __init__(self):
        self.sha, self.date, self.court = {}, {}, {}
        self.cert_text = defaultdict(list)

    def has(self, n):
        return n in self.court and self.court[n] >= 0


class MiniEngine(pr.Engine):
    def __init__(self, D):          # noqa: the reference Engine's state is not needed by check_identity
        self.D = D


def rows(path):
    with open(path, encoding='utf-8', newline='') as f:
        for line in f:
            yield line.rstrip('\n').rstrip('\r').split('\t')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--history', action='append', required=True)
    ap.add_argument('--ident', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    hist = {}
    for h in a.history:
        for p in rows(h):
            if len(p) == 13:
                hist[p[0]] = (int(p[2]), int(p[1]))          # by, target
    lines, bad, dup, unknown = {}, 0, 0, 0
    for p in rows(os.path.join(a.ident, 'history_identity_delta.tsv')):
        if len(p) != 7 or p[1] not in pr.IDENTITY_FORMS or not all(pr._NAT_RX.match(p[c]) for c in (3, 4, 5, 6)):
            bad += 1
        elif p[0] not in hist:
            unknown += 1
        elif p[0] in lines:
            dup += 1
        else:
            lines[p[0]] = (p[1], p[2], int(p[3]), int(p[4]), int(p[5]), int(p[6]))
    nodes = {n for i in lines for n in hist[i]}
    D = MiniData()
    for p in rows(os.path.join(a.base, 'decisions2.tsv')):
        n = int(p[0]) if p[0].isdigit() else -1
        if n in nodes:
            D.court[n], D.date[n], D.sha[n] = int(p[1]), int(p[2]), p[7]
    shas = {D.sha[n] for n in nodes if n in D.sha}
    wsha = defaultdict(set)
    for fn in (os.path.join(a.base, 'window_sha.tsv'), os.path.join(a.ident, 'window_sha_delta.tsv')):
        for p in rows(fn):
            if len(p) == 5 and p[0] in shas:
                wsha[(p[0], int(p[1]), int(p[2]))].add(p[3])
    for fn in (os.path.join(a.base, 'cert_text.tsv'), os.path.join(a.ident, 'cert_text_delta.tsv')):
        for p in rows(fn):
            if len(p) == 4 and p[0] in shas:
                s0, e0 = int(p[1]), int(p[2])
                hs = wsha.get((p[0], s0, e0))
                hok = bool(hs) and hashlib.sha1(p[3].encode('utf-8')).hexdigest() in hs
                D.cert_text[p[0]].append((s0, e0, p[3], hok))
    E = MiniEngine(D)
    pre = {}
    pc = os.path.join(a.ident, 'precheck.tsv')
    if os.path.exists(pc):
        pre = {p[0]: p[1] for p in rows(pc) if len(p) >= 2}
    res, tally = [], Counter()
    for i, m in sorted(lines.items()):
        by, tg = hist[i]
        v = E.check_identity({'id': i, 'by': by, 'target': tg}, m)
        b = pre.get(i, '?')
        agree = (v == 'ok') == (m[0] in b.split(','))
        tally[(m[0], v, 'agree' if agree else 'DIFFER')] += 1
        res.append([i, m[0], m[1], v, b, 'agree' if agree else 'DIFFER'])
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for r in res:
            f.write('\t'.join(r) + '\n')
    print('lines kept %d, bad %d, unknown id %d, dup %d' % (len(lines), bad, unknown, dup))
    for k, n in sorted(tally.items()):
        print('  %-8s %-12s %-7s %d' % (k + (n,)))


if __name__ == '__main__':
    main()
