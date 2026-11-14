#!/usr/bin/env python3
"""remand_verdicts10.py - round 10 (ref10): the reference's remand verdicts on real data (Data + admit only, no
status / findings), for a base data dir plus a remand delta folder (history_remand_delta.tsv, cert_text_delta.tsv,
window_sha_delta.tsv, cite_index_delta.tsv as shadow10 writes them), compared with the delta's precheck.tsv when
present (id, class, pass|fail, reason, note).

  CASELAW2_REF=<ref> python3 remand_verdicts10.py --base <data dir> --delta <folder> --work <scratch dir> --out <tsv>

The work dir gets symlinks to every base table, and concatenated copies (base + delta) of the three tables the
delta extends; it is deleted at the end.
"""
import argparse
import os
import shutil
import sys
from collections import Counter

REF = os.environ.get('CASELAW2_REF') or os.path.expanduser(
    '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref')
sys.path.insert(0, REF)
import precedent_ref as pr  # noqa: E402

EXT = {'cert_text.tsv': 'cert_text_delta.tsv', 'window_sha.tsv': 'window_sha_delta.tsv',
       'cite_index.tsv': 'cite_index_delta.tsv'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--delta', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    shutil.rmtree(a.work, ignore_errors=True)
    os.makedirs(a.work)
    for fn in os.listdir(a.base):
        if not fn.endswith('.tsv') or fn == 'history_remand.tsv':
            continue
        src = os.path.realpath(os.path.join(a.base, fn))
        dfile = os.path.join(a.delta, EXT.get(fn, '-'))
        if fn in EXT and os.path.exists(dfile):
            with open(os.path.join(a.work, fn), 'wb') as out:
                for p in (src, dfile):
                    with open(p, 'rb') as fh:
                        data = fh.read()
                    out.write(data)
                    if data and not data.endswith(b'\n'):
                        out.write(b'\n')
        else:
            os.symlink(src, os.path.join(a.work, fn))
    shutil.copy(os.path.join(a.delta, 'history_remand_delta.tsv'), os.path.join(a.work, 'history_remand.tsv'))
    D = pr.Data(a.work, log=lambda *x: print(*x, file=sys.stderr, flush=True))
    A = pr.Engine(D)
    A.admit()
    rows = []
    res = Counter()
    for r in D.history:
        m = D.remand.get(r['id'])
        if m is None:
            continue
        v = A.cert_ok[('history.tsv', r['id'])]
        why = A.check_remand(r, m)
        gate = A.lean_cert_passes('history', r)
        rows.append([r['id'], v, why, 'power' if gate else 'nopower', 'mute' if ('h', r['id']) in A.remand_mute else '-'])
        res[(v if v.startswith('remand') or v == 'ok' else 'r9:' + v)] += 1
    pre = {}
    pp = os.path.join(a.delta, 'precheck.tsv')
    if os.path.exists(pp):
        for line in open(pp, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) >= 4:
                pre[p[0]] = (p[2], p[3])
    agree = Counter()
    for r in rows:
        if r[0] in pre:
            ps, preason = pre[r[0]]
            mine = 'pass' if r[2] == 'ok' else 'fail'
            agree[(mine == ps and (ps == 'pass' or preason == r[2]))] += 1
            r += [ps, preason]
        else:
            r += ['-', '-']
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('id\tverdict\tremand_check\tpower\tmute\tprecheck\tprecheck_reason\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    print('remand lines %d, dup %d, bad %d, unknown ids %d; checked %d, failed %d' % (
        len(D.remand), D.remand_dup, D.remand_bad, D.remand_unknown, A.remand_checked, A.remand_failed))
    print('verdicts of rows with a line: %s' % dict(sorted(res.items())))
    print('remand check (whatever the verdict): %s' % dict(sorted(Counter(r[2] for r in rows).items())))
    if pre:
        print('agreement with precheck.tsv (pass/fail and reason): same %d, different %d; precheck rows without a line: %d'
              % (agree[True], agree[False], len(set(pre) - {r[0] for r in rows})))
    shutil.rmtree(a.work, ignore_errors=True)


if __name__ == '__main__':
    main()
