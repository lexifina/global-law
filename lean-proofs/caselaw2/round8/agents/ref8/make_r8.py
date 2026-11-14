#!/usr/bin/env python3
"""make_r8.py - round-8 universes for bridge evidence (round8/DESIGN8.md §4) and the claim `anchorWide` (§5), for the
differential test of the round-8 Lean runner against the Python reference.

A universe is a universe of tools/caselaw2/ref/gen.py with a round-8 overlay appended (round 7's make_r7.py supplies
the text / window / decision helpers): new decisions with real texts, history rows `h8:<by>:<target>:<kind>` with
lines in `history_bridge.tsv` (a quote of a third decision W citing X, a cue of the row's kind, then O) and history
rows with anchor lines and `anchorWide` claims, malformed and unknown lines, lines on rows of the base universe.
Nothing of the base universe is changed except by appending rows. `expect.tsv` (beside data/, never read by an engine)
records per row id: table, case, flavour, the reason DESIGN8 gives it (reference vocabulary; `?` where the design is
silent or the base universe decides), target, by, `?`. `expect_counts.tsv`: the counters the lines must give.

  python make_r8.py gen    --seed 80000 --rounds 8 --out DIR [--probe] [--fuzz K] [--n 60]
        DIR/u<seed> (main cases), p<seed> (--probe: the readings of REF_QUESTIONS8.md), f<seed> (--fuzz K: the main
        cases, then K byte-level mutations of history_bridge.tsv and history_claim.tsv; expectations become `?`)
  python make_r8.py check  DIR [--ref PATH]   the reference on every universe against expect.tsv / expect_counts.tsv
  python make_r8.py empty  DIR [--ref PATH] [--pre PATH]   with history_bridge.tsv removed (also: present but empty /
        blank) and the anchorWide claim lines dropped, the current reference and the pre-round-8 copy write the same
        bytes
  python make_r8.py report DIR...             attribute each universe's diff.tsv rows to the cases of expect.tsv
"""
import argparse
import os
import random
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
R7 = os.environ.get('MAKE_R7_DIR') or os.path.normpath(os.path.join(HERE, '..', '..', '..', 'round7', 'agents', 'ref'))
sys.path.insert(0, R7)
import make_r7 as m7  # noqa: E402  (imports gen.py from CASELAW2_REF)
from make_r7 import gen, draw, evidence, rows_of, lower  # noqa: E402

REF = m7.REF
PRE_REF = os.path.normpath(os.path.join(HERE, '..', '..', 'pre', 'ref', 'precedent_ref.py'))
CUE = m7.CUE
ANCHOR = CUE['anchor']
DISQ_ANCHOR = CUE['disqualify_anchor']
DISQ_HIST = CUE['disqualify_hist']
HIST = CUE['hist']
ORDER_LINE = m7.ORDER_LINE
BRIDGE_CUE = CUE.get('bridge_cue') or {
    'certDenied': ['cert. denied', 'certiorari denied', 'cert denied'],
    'vacated': ['vacated', 'judgment vacated', 'vacated and remanded'],
    'reversed': ["rev'd", 'reversed'],
    'affirmed': ["aff'd", 'affirmed'],
    'reviewDismissed': ['cert. dismissed', 'certiorari dismissed', 'appeal dismissed']}
BRIDGE_MAX = int(CUE.get('bridge_max_len') or 600)
ANCHOR_WIDE = CUE.get('anchor_wide') or [
    'circuit', '(ca1', '(ca2', '(ca3', '(ca4', '(ca5', '(ca6', '(ca7', '(ca8', '(ca9', '(cadc', '(cafc', 'c.a.',
    'judicial court', 'court of errors', 'case below']
KINDS = sorted(BRIDGE_CUE)
ALL_BRIDGE_CUES = sorted({c for v in BRIDGE_CUE.values() for c in v})
PLAIN_DISP = {
    'certDenied': ['The petition for a writ of certiorari is denied.', 'Certiorari is denied.'],
    'vacated': ['The judgment is vacated, and the case is remanded for further consideration.',
                'We vacate the judgment below.'],
    'reversed': ['The judgment of the Court of Appeals is reversed.', 'We reverse the judgment.'],
    'affirmed': ['The judgment is affirmed.', 'We affirm the judgment below.'],
    'reviewDismissed': ['The writ of certiorari is dismissed as improvidently granted.', 'The appeal is dismissed.'],
    'remanded': ['The case is remanded to the trial court.']}
XPAR = ['(5th Cir. 2015)', '(9th Cir. 2016)', '(Tex. App. 2014)', '(Ohio 2017)', '(D.C. Cir. 2013)', '']
EARLY = ('bridgeMismatch', 'bridgeDate', 'bridgeClause')


def has(s, phrases):
    return m7.has(s, phrases)


def year(d):
    return d // 10000 if d else 2016


class U8(m7.Universe):
    def __init__(self, d, seed, flavour):
        super().__init__(d, seed, flavour)
        self.R = random.Random(seed * 1000003 + 8008)
        self.blines, self.extra_idx = [], []
        self.base_claim = rows_of(self.J('history_claim.tsv'))
        self.base_bridge = os.path.exists(self.J('history_bridge.tsv'))
        self.br_ids = set()            # ids with a kept bridge line (bridge_rows)
        self.aw_unused = set()
        self.oc_rows = []
        if not self.has_idx and seed % 3 != 0:
            self.has_idx = True        # two seeds in three: a cite_index.tsv of the overlay's decisions only

    def dec(self, court, date, cite=None):
        x = self.newdec(court, date)
        if cite:
            self.cites.add(cite)
            x['cite'] = cite
            old = x['T'].parts[0]
            x['T'].parts[0] = '%s, %s.' % (x['name'], cite)
            x['T'].n += len(x['T'].parts[0]) - len(old)
        return x

    def gap(self):
        """A node id with no decisions2 row, below the largest id (Q8-3: an unknown W)."""
        self.next += 1
        return self.next - 1


def scotus_date(R, lo=2013, hi=2022):
    return R.randint(lo, hi) * 10000 + R.randint(1, 12) * 100 + R.randint(1, 28)


def disp_quote(U, kind, oh, how='ok'):
    R = U.R
    if how == 'nocue':
        return draw(U, lambda: R.choice(['The motion for leave is noted.', 'The matter is considered.']),
                    avoid=(HIST.get(kind, ['zzzz']), DISQ_HIST))
    if how == 'disq':
        return draw(U, lambda: '%s the judgment, and the judgment is %s.' % (R.choice(DISQ_HIST).capitalize(), {
            'certDenied': 'denied', 'vacated': 'vacated', 'reversed': 'reversed', 'affirmed': 'affirmed',
            'reviewDismissed': 'dismissed', 'remanded': 'remanded'}[kind]), need=(HIST[kind], DISQ_HIST))
    if oh:
        line = R.choice(ORDER_LINE.get(kind, ['judgment ' + kind]))
        if ' ... ' in line:
            line = line.replace(' ... ', ' %s ' % R.choice(m7.COURTS_BELOW))
        return R.choice([line[0].upper() + line[1:] + '.', line + '.'])
    return draw(U, lambda: R.choice(PLAIN_DISP[kind]), need=(HIST[kind],), avoid=(DISQ_HIST,))


# ---------------------------------------------------------------------------------------------------------------
def bridge_case(U, case, flavour, exp='ok', **o):
    """One history row (O acts on X) with a bridge line from a third decision W. Options: kind, oh (orderHead
    claim + head matter), clause (ok | semi | nocue | cue_before | otherkind | noactor | other_actor | actor_second |
    actor_before | coord | two_cues | upper | curly | nodot | noX), w (ok | gap | big | is_o | before | equal | zero),
    o_zero, x_later, by1, defect (b_off | b_quote | b_empty | b_swapped | b_len | b_nowin | b_badwin | b_hash |
    b_nohash | b_othertext | m_quote | m_sha), part, disp (ok | nocue | disq), xidx / oidx (ok | wrong | none |
    ambig), qlen, dup (a second line: dup | dup_good), anchor (also an anchor line: bad | ok), claims, ocite / zcite
    (prefix probes), lead_zero."""
    R = U.R
    kind = o.get('kind') or R.choice(KINDS)
    oh = o.get('oh', R.random() < 0.6) and kind in ORDER_LINE
    dd = o.get('date') or scotus_date(R)
    dx = gen.add_days(dd, -R.randint(60, 900)) if not o.get('x_later') else gen.add_days(dd, 20)
    lo = R.choice([c for c in (101, 102, 201, 501, 703) if c in U.courts and gen.epoch_at(U.crows, c, dx)] or [101])
    X = U.dec(lo, dx, o.get('xcite'))
    O = U.dec(2906, 0 if o.get('o_zero') else dd, o.get('ocite'))
    Z = U.dec(2906, gen.add_days(dd, R.randint(-400, 400)), o.get('zcite'))     # another order (decoys)
    wmode = o.get('w', 'ok')
    dw = {'before': gen.add_days(dd, -R.randint(1, 300)), 'equal': dd, 'zero': 0}.get(
        wmode, gen.add_days(dd, R.randint(1, 2500)))
    W = O if wmode == 'is_o' else U.dec(R.choice([c for c in (101, 201, 501, 2906) if c in U.courts] or [101]), dw)
    ev = R.choice(['cite', 'name'])
    tev = evidence(U, X, ev)
    # O's own text: docket line, then the disposition quote
    q = o.get('quote') or disp_quote(U, kind, oh, o.get('disp', 'ok'))
    T = O['T']
    T.add(U.filler(R.choice([0, 60, 500])))
    if o.get('anchor'):
        a_sent = ('Certiorari to the United States Court of Appeals. Reported below: %s, %s.' % (X['name'], X['cite'])
                  if o['anchor'] == 'ok' else 'Nothing here names the decision under review.')
        a_span = T.add(a_sent)
        T.add(U.filler(700))
    T.add('No. %d-%d.' % (R.randint(10, 22), R.randint(100, 999)))
    d_span = T.add(q)
    T.add(U.filler(R.choice([0, 40, 300])))
    # W's clause
    cue = o.get('cue') or R.choice(BRIDGE_CUE.get(kind, ['cert. denied']))
    xc, oc, zc = X['cite'], O['cite'], Z['cite']
    xpar = R.choice(XPAR)
    xs = '%s, %s%s' % (X['name'], xc, (' ' + xpar) if xpar else '')
    ys = '(%d)' % year(dd)
    cl = o.get('clause', 'ok')
    if cl == 'ok':
        clause = '%s, %s, %s %s' % (xs, cue, oc, ys)
    elif cl == 'upper':
        clause = '%s, %s, %s %s' % (xs, cue.upper(), oc, ys)
    elif cl == 'semi':
        clause = '%s, %s, %s %s; %s, %s' % (xs, cue, oc, ys, Z['name'], zc)
    elif cl == 'nocue':
        clause = '%s, %s %s' % (xs, oc, ys)
    elif cl == 'cue_before':
        clause = '%s, %s, %s %s' % (cue[0].upper() + cue[1:], xs, oc, ys)
    elif cl == 'otherkind':
        other = [c for k2 in KINDS if k2 != kind for c in BRIDGE_CUE[k2]
                 if not any(c2 in c or c in c2 for c2 in BRIDGE_CUE.get(kind, []))]
        clause = '%s, %s, %s %s' % (xs, R.choice(other), oc, ys)
    elif cl == 'noactor':
        clause = '%s, %s %s' % (xs, cue, ys)
    elif cl == 'other_actor':
        clause = '%s, %s, %s %s' % (xs, cue, zc, ys)
    elif cl == 'actor_second':
        clause = '%s, %s, %s, %s %s' % (xs, cue, zc, oc, ys)
    elif cl == 'actor_before':
        clause = '%s, %s, %s' % (oc, xs, cue)
    elif cl == 'coord':
        # Q8-4: a cue before X's citation whose offset lies between X's compact and normalised positions
        clause = '%s %s, %s, %s %s' % ('- ' * 30, cue, xc, oc, ys)
    elif cl == 'two_cues':
        c2 = BRIDGE_CUE[kind][0]
        clause = '%s, %s, %s %s, %s, %s %s' % (xs, c2, zc, '(5th Cir. 2016)', c2, oc, ys)
    elif cl in ('chain', 'chain_ambig'):
        # D8-9 (step 5b): another citation between X's and the cue of the row's kind
        other = [c for k2 in KINDS if k2 != kind for c in BRIDGE_CUE[k2]
                 if not any(c2 in c or c in c2 for c2 in BRIDGE_CUE.get(kind, []))]
        clause = '%s, %s, %s (5th Cir. 2016), %s, %s %s' % (xs, R.choice(other), zc, cue, oc, ys)
        if cl == 'chain_ambig':
            Z['index'] = 'ambig'
    elif cl == 'xparallel':
        alt = '%d So.3d %d' % (R.randint(1, 99), R.randint(1, 999))
        U.extra_idx.append([alt, X['node']])
        clause = '%s, %s, %s %s, %s, %s %s' % (X['name'], xc, alt, xpar or '(Fla. 2014)', cue, oc, ys)
    elif cl == 'parallel_after':
        clause = '%s, %s, %s, %s %s' % (xs, cue, oc, zc, ys)
    elif cl == 'nonascii_ok':
        # lean8 (01:15): ASCII-only lower / alnum; non-ASCII letters, a dash and digits of another script are dropped
        clause = 'Müller Étude v. Østerß — %s, %s %s' % (xc, cue, oc + ' (٢٠١٦)')
    elif cl == 'kelvin_x':
        # X's citation written with the Kelvin sign U+212A for K: not an ASCII letter, so the compact key differs
        clause = '%s, %s %s, %s, %s %s' % (X['name'], xc.replace('K', 'K'), xpar, cue, oc, ys)
    elif cl == 'arabic_o':
        v, rest = oc.split(' ', 1)
        clause = '%s, %s, %s %s' % (xs, cue, ''.join(chr(0x660 + int(ch)) for ch in v) + ' ' + rest, ys)
    elif cl == 'dotted_i':
        clause = '%s, %s, %s %s' % (xs, cue.upper().replace('I', 'İ'), oc, ys)
    elif cl == 'curly':
        clause = '%s, %s, %s %s' % (xs, "rev’d", oc, ys)
    elif cl == 'nodot':
        clause = '%s, %s, %s %s' % (xs, 'cert denied', oc, ys)
    elif cl == 'noX':
        clause = '%s, %s, %s, %s %s' % (X['name'], zc, cue, oc, ys)
    else:
        raise ValueError(cl)
    bq = R.choice(['See ', '', 'Cf. ']) + clause + '.'
    if o.get('qlen'):
        n = o['qlen']
        pad = (U.filler(n - len(bq) - 1) + ' Further.' * 3)[:n - len(bq) - 1]
        bq = pad + ' ' + bq
        assert len(bq) == n, (len(bq), n)
    WT = W['T']
    WT.add(U.filler(R.choice([0, 80, 900])))
    b_span = WT.add(bq)
    WT.add(U.filler(R.choice([0, 50, 700])))
    by = -1 if o.get('by1') else O['node']
    hid = 'h8:%d:%d:%s' % (by, X['node'], kind)
    part = o.get('part') or ('headmatter' if oh else R.choice(['majority', 'perCuriam']))
    claims = list(o.get('claims', ('orderHead',) if oh else ()))
    row = {'id': hid, 'target': X['node'], 'by': by, 'date': dd, 'kind': kind, 'O': O, 'X': X, 'W': W, 'Z': Z,
           'd': d_span, 'dq': q, 'tev': tev, 'part': part, 'b': b_span, 'bq': bq, 'o': o,
           'a': a_span if o.get('anchor') else None, 'a_sent': a_sent if o.get('anchor') else None}
    U.hrows.append(row)
    for c in claims:
        U.hclines.append('\t'.join([hid, c, 'r8:gen']))
    if o.get('xidx'):
        X['index'] = o['xidx']
    if o.get('oidx'):
        O['index'] = o['oidx']
    if o.get('zidx'):
        Z['index'] = o['zidx']
    if wmode == 'gap':
        row['wnode'] = U.gap()
    elif wmode == 'big':
        row['wnode'] = 10 ** 9
    if exp not in EARLY and exp != '?' and not U.has_idx and not o.get('anchor_only'):
        exp = 'bridgeTarget'          # without cite_index.tsv nothing maps to X (Q8-5)
    if o.get('defect') in ('b_hash', 'b_nohash') and not U.has_wsha:
        exp = 'ok' if U.has_idx else 'bridgeTarget'
    U.expect.append(['history', hid, case, flavour, exp, X['node'], by, '?'])
    U.br_ids.add(hid)
    if R.random() < 0.6:
        C = U.dec(lo, gen.add_days(dd, R.randint(1, 900)))
        U.edges.append([C['node'], X['node']])
    return row


def finish_bridge(U, r):
    O, X, W = r['O'], r['X'], r['W']
    txt, sha = O['text'], O['sha']
    ds, de = r['d']
    assert txt[ds:de] == r['dq']
    o = r['o']
    df = o.get('defect')
    U.window(sha, txt, ds, de)
    dq, c_sha = r['dq'], sha
    if df == 'm_quote':
        dq = dq[:-1] + ('x' if dq[-1] != 'x' else 'y')
    elif df == 'm_sha':
        c_sha = W['sha']
    U.hrows_out.append([r['id'], r['target'], r['by'], r['date'], r['kind'], 'all', c_sha, ds, de, dq, r['tev'],
                        r['part'], 'r8:gen'])
    if r['a']:
        a_s, a_e = r['a']
        U.window(sha, txt, a_s, a_e)
        U.alines.append('\t'.join([r['id'], str(a_s), str(a_e), r['a_sent'], 'headmatter', 'r8:gen']))
    wtxt, wsha = W['text'], W['sha']
    s, e = r['b']
    bq = wtxt[s:e]
    assert bq == r['bq'], (bq, r['bq'])
    wm = {'b_nowin': 'none', 'b_badwin': 'bad', 'b_hash': 'hash', 'b_nohash': 'nohash'}.get(df, 'ok')
    if df == 'b_othertext':
        U.window(X['sha'], wtxt, s, e)
    else:
        U.window(wsha, wtxt, s, e, wm)
    if df == 'b_off':
        s, e = s + 1, e + 1
    elif df == 'b_quote':
        bq = bq[:-1] + ('x' if bq[-1] != 'x' else 'y')
    elif df == 'b_empty':
        e, bq = s, ''
    elif df == 'b_swapped':
        s, e = e, s
    elif df == 'b_len':
        e += 3
    wnode = r.get('wnode', W['node'])
    ss, es = str(s), str(e)
    if o.get('lead_zero'):
        ss, es = '00' + ss, '0' + es
    line = '\t'.join([r['id'], str(wnode), ss, es, bq, 'r8:gen'])
    if o.get('dup') == 'first_bad':
        # Q8-1: the first good line wins, even when it fails and a later line would pass
        U.blines.append('\t'.join([r['id'], str(wnode), str(s + 1), str(e + 1), bq, 'r8:first']))
        U.counts['bridge_duplicates'] += 1
        U.blines.append(line)
    else:
        U.blines.append(line)
        if o.get('dup') == 'dup':
            U.blines.append('\t'.join([r['id'], str(O['node']), '0', '5', 'junk!', 'r8:dup']))
            U.counts['bridge_duplicates'] += 1


# ---------------------------------------------------------------------------------------------------------------
AW_SENT = {
    'wide': ['{name}, {cite} ({ca} {y}), is the decision we review.',
             'The judgment of the circuit in {name}, {cite}, is before us.',
             'Review of the case below, {name}, {cite}, was sought.',
             '{name}, {cite}, was decided by the Supreme Judicial Court of the State.',
             'The Court of Errors and Appeals decided {name}, {cite}.',
             '{name}, {cite} (C.A. {y}), is the decision we review.'],
    'plain': ['Certiorari to the court below. Reported below: {name}, {cite}.',
              'Appeal from the District Court in {name}, {cite}.'],
    'none': ['{name}, {cite}, is the decision we review.', 'We review {name}, {cite}, today.'],
    'disq': ['See also {name}, {cite} ({ca} {y}).'],
    'cal': ['{name}, {cite} (Cal. {y}), is the decision we review.', '{name}, {cite} (Cal.App. {y}), is reviewed.'],
    'noev': ['The decision of the case below is reviewed ({ca} {y}).'],
}
CA = ['CA1', 'CA2', 'CA5', 'CA9', 'CADC', 'CAFC', 'CA7']


def aw_sentence(U, X, how, upper=False):
    R = U.R
    need, avoid = {'wide': ((ANCHOR_WIDE,), (ANCHOR, DISQ_ANCHOR)), 'plain': ((ANCHOR,), (DISQ_ANCHOR,)),
                   'none': ((), (ANCHOR, ANCHOR_WIDE, DISQ_ANCHOR)), 'disq': ((ANCHOR_WIDE, DISQ_ANCHOR), (ANCHOR,)),
                   'cal': ((), (ANCHOR, ANCHOR_WIDE, DISQ_ANCHOR)),
                   'noev': ((ANCHOR_WIDE,), (ANCHOR, DISQ_ANCHOR))}[how]
    mk = lambda: R.choice(AW_SENT[how]).format(name=X['name'], cite=X['cite'], ca=R.choice(CA),
                                               y=R.randint(1980, 2012))
    return draw(U, (lambda: mk().upper()) if upper else mk, need=need, avoid=avoid)


def aw_case(U, case, flavour, exp='ok', **o):
    """A history row with an anchor line (anchor: wide | plain | none | disq | cal | noev, or '' for no anchor line)
    and history claims (claims). Options: kind, scotus (with orderHead and head matter), a_part, upper, bridge (also
    a bridge line: the row is then checked by checkBridge, Q8-2)."""
    R = U.R
    scotus = o.get('scotus', False)
    kind = o.get('kind') or R.choice(['affirmed', 'reversed', 'vacated'])
    claims = list(o.get('claims', ('anchorWide',)))
    if scotus:
        dd = scotus_date(R)
        lo, hi = R.choice([c for c in (101, 102, 201, 501, 703) if c in U.courts] or [101]), 2906
    else:
        dd = R.randint(1960, 2020) * 10000 + R.randint(1, 12) * 100 + R.randint(1, 28)
        lo, hi = R.choice([p for p in [(201, 101), (502, 501), (503, 502), (705, 703)] if p[0] in U.courts
                           and p[1] in U.courts] or [(201, 101)])
    dx = gen.add_days(dd, -R.randint(60, 900))
    if not gen.epoch_at(U.crows, lo, dx):
        lo = 101
    X = U.dec(lo, dx)
    O = U.dec(hi, dd)
    tev = evidence(U, X, R.choice(['cite', 'name']))
    if 'setAside' in claims:
        q = 'The judgment of the Court of Appeals is set aside.'
        kind = 'vacated'
    else:
        q = disp_quote(U, kind, scotus and 'orderHead' in claims)
    T = O['T']
    T.add(U.filler(R.choice([0, 60, 500])))
    how = o.get('anchor', 'wide')
    a_sent = aw_sentence(U, X, how, o.get('upper')) if how else None
    if how:
        a_span = T.add(a_sent)
        T.add(U.filler(R.choice([600, 1200])))
        T.add('No. %d-%d.' % (R.randint(10, 22), R.randint(100, 999)))
    else:
        T.add('No. %d-%d. %s, %s.' % (R.randint(10, 22), R.randint(100, 999), X['name'], X['cite']))
    d_span = T.add(q)
    T.add(U.filler(R.choice([0, 40, 300])))
    hid = 'h8:%d:%d:%s' % (O['node'], X['node'], kind)
    part = 'headmatter' if (scotus and 'orderHead' in claims) else R.choice(['majority', 'perCuriam'])
    row = {'id': hid, 'target': X['node'], 'by': O['node'], 'date': dd, 'kind': kind, 'O': O, 'X': X, 'd': d_span,
           'dq': q, 'tev': tev, 'part': part, 'a': a_span if how else None, 'a_sent': a_sent,
           'a_part': o.get('a_part', R.choice(['headmatter', 'majority', 'perCuriam'])), 'aw': True}
    U.awrows.append(row)
    for c in claims:
        U.hclines.append('\t'.join([hid, c, 'r8:gen']))
    if o.get('dup_claim'):
        U.hclines.append('\t'.join([hid, 'anchorWide', 'r8:dup']))
        U.counts['hclaim_duplicates'] += 1
    if 'anchorWide' in claims and (not how or o.get('bridge')):
        U.aw_unused.add(hid)
    if o.get('bridge'):
        # a bridge line from a third decision W (valid): the row is checked by checkBridge (Q8-2)
        W = U.dec(101 if 101 in U.courts else lo, gen.add_days(dd, R.randint(1, 900)))
        cue = R.choice(BRIDGE_CUE.get(kind, ['cert. denied']))
        bq = '%s, %s, %s, %s (%d).' % (X['name'], X['cite'], cue, O['cite'], year(dd))
        W['T'].add(U.filler(100))
        row['b'] = W['T'].add(bq)
        row['W'], row['bq'] = W, bq
        U.br_ids.add(hid)
        if exp not in EARLY and not U.has_idx:
            exp = 'bridgeTarget'
    U.expect.append(['history', hid, case, flavour, exp, X['node'], O['node'], '?'])
    return row


def finish_aw(U, r):
    O = r['O']
    txt, sha = O['text'], O['sha']
    ds, de = r['d']
    assert txt[ds:de] == r['dq']
    U.window(sha, txt, ds, de)
    U.hrows_out.append([r['id'], r['target'], r['by'], r['date'], r['kind'], 'all', sha, ds, de, r['dq'], r['tev'],
                        r['part'], 'r8:gen'])
    if r['a']:
        a_s, a_e = r['a']
        assert txt[a_s:a_e] == r['a_sent']
        U.window(sha, txt, a_s, a_e)
        U.alines.append('\t'.join([r['id'], str(a_s), str(a_e), r['a_sent'], r['a_part'], 'r8:gen']))
    if r.get('W'):
        W = r['W']
        s, e = r['b']
        U.window(W['sha'], W['text'], s, e)
        U.blines.append('\t'.join([r['id'], str(W['node']), str(s), str(e), r['bq'], 'r8:aw']))


# ---------------------------------------------------------------------------------------------------------------
# oldCircuit (DESIGN8 §6): federal courts appended to courts2.tsv (ids 3901-3908, all dates)
OC_COURTS = [(3901, 'United States Court of Appeals for the Fifth Circuit (r8)', 'A', 5),
             (3902, 'United States Court of Appeals for the Eighth Circuit (r8)', 'A', 8),
             (3903, 'United States District Court for the Northern District of Alabama (r8)', 'T', 11),
             (3904, 'United States Bankruptcy Court for the Middle District of Florida (r8)', 'S', 11),
             (3905, 'United States District Court for the District of Kansas (r8)', 'T', 10),
             (3906, 'United States District Court for the Eastern District of Texas (r8)', 'T', 5),
             (3907, 'United States Court of Appeals for the Eleventh Circuit (r8)', 'A', 11),
             (3908, 'United States Court of Appeals for the Ninth Circuit (r8)', 'A', 9)]
OC_CUT = {(5, 11): 19811001, (8, 10): 19290301}


def oc_courts(U):
    if not getattr(U, 'oc_added', False):
        U.oc_added = True
        for (c, name, tier, circ) in OC_COURTS:
            row = [c, 0, 99999999, name, 0, tier, '-', circ, 0, 'r8', 'S']
            U.crows.append(row)
            U.courts.add(c)
            U.oc_rows.append(row)


def oc_case(U, case, flavour, exp='ok', **o):
    """A history row of a federal court of appeals B (court bc) on a federal trial / bankruptcy decision X (court xc),
    with or without the claim oldCircuit. Options: bc, xc, bdate (B's decisions2 date; 'zero' = 0), kind, claim,
    status ('neg' | 'notneg' | '?')."""
    R = U.R
    oc_courts(U)
    kind = o.get('kind') or R.choice(['reversed', 'vacated'])
    db = o['bdate']
    dx = gen.add_days(db if db else 19700101, -R.randint(60, 700))
    X = U.dec(o['xc'], dx)
    B = U.dec(o['bc'], 0 if o.get('zero') else db)
    tev = evidence(U, X, R.choice(['cite', 'name']))
    q = draw(U, lambda: R.choice(PLAIN_DISP[kind]), need=(HIST[kind],), avoid=(DISQ_HIST,))
    T = B['T']
    T.add(U.filler(R.choice([0, 60, 300])))
    T.add('Appeal from %s, %s.' % (X['name'], X['cite']))
    d_span = T.add(q)
    T.add(U.filler(R.choice([0, 40])))
    hid = 'h8:%d:%d:%s' % (B['node'], X['node'], kind)
    row = {'id': hid, 'target': X['node'], 'by': B['node'], 'date': db, 'kind': kind, 'O': B, 'X': X, 'd': d_span,
           'dq': q, 'tev': tev, 'part': R.choice(['majority', 'perCuriam']), 'a': None}
    U.awrows.append(row)
    if o.get('claim', True):
        U.hclines.append('	'.join([hid, 'oldCircuit', 'r8:gen']))
    U.expect.append(['history', hid, case, flavour, exp, X['node'], B['node'], o.get('status', '?')])
    if R.random() < 0.6:
        C = U.dec(o['xc'], gen.add_days(db or 19800101, R.randint(1, 900)))
        U.edges.append([C['node'], X['node']])


def oc_cases():
    out = []
    for (bc, xc, a, b) in ((3901, 3903, 5, 11), (3901, 3904, 5, 11), (3902, 3905, 8, 10)):
        cut = OC_CUT[(a, b)]
        n = 'ca%d_c%d%s' % (a, b, '_bk' if xc == 3904 else '')
        out += [('oc_%s_ok' % n, dict(bc=bc, xc=xc, bdate=gen.add_days(cut, -400), status='neg')),
                ('oc_%s_daybefore' % n, dict(bc=bc, xc=xc, bdate=gen.add_days(cut, -1), status='neg')),
                ('oc_%s_cutoff' % n, dict(bc=bc, xc=xc, bdate=cut, status='notneg')),
                ('oc_%s_after' % n, dict(bc=bc, xc=xc, bdate=gen.add_days(cut, 300), status='notneg')),
                ('oc_%s_noclaim' % n, dict(bc=bc, xc=xc, bdate=gen.add_days(cut, -400), claim=False,
                                          status='notneg'))]
    out += [('oc_ca5_c10', dict(bc=3901, xc=3905, bdate=19700505, status='notneg')),
            ('oc_ca8_c11', dict(bc=3902, xc=3903, bdate=19250505, status='notneg')),
            ('oc_ca9_c11', dict(bc=3908, xc=3903, bdate=19700505, status='notneg')),
            ('oc_ca5_on_ca11', dict(bc=3901, xc=3907, bdate=19700505, status='notneg')),
            ('oc_ca5_c5_noclaim', dict(bc=3901, xc=3906, bdate=19900505, claim=False, status='neg')),
            ('oc_ca11_c11_claim', dict(bc=3907, xc=3903, bdate=19900505, status='neg')),
            ('oc_affirmed', dict(bc=3901, xc=3903, bdate=19700505, kind='affirmed', status='?')),
            ('oc_bzero', dict(bc=3901, xc=3903, bdate=19700505, zero=True, status='notneg'))]
    return [(n, oc_case, o) for (n, o) in out]


def base_lines(U, flavour):
    """Lines on rows of the base universe, and malformed / unknown lines of both tables."""
    R = U.R
    hb = [p for p in U.base_hist if len(p) == 13]
    R.shuffle(hb)
    for p in hb[:3]:
        # a bridge line on a base row, quoting a made-up window of the acting decision's text (W = by)
        q = 'Reported below as the decision under review, cert. denied.'
        w = q + ' ' + U.filler(30)
        s0 = 5_000_000 + R.randint(0, 1000)
        U.ct.append([p[6], s0, s0 + len(w), w])
        if U.has_wsha:
            U.wsha.append([p[6], s0, s0 + len(w), m7.sha1(w), 'r8'])
        U.blines.append('\t'.join([p[0], p[2] if p[2].isdigit() else '0', str(s0), str(s0 + len(q)), q, 'r8:base']))
        U.br_ids.add(p[0])
        U.expect.append(['history', p[0], 'base_bridge', flavour, '?', p[1], p[2], '?'])
    for p in hb[3:5]:
        U.hclines.append('\t'.join([p[0], 'anchorWide', 'r8:base']))
        U.aw_unused.add(p[0])
        U.expect.append(['history', p[0], 'base_anchorWide', flavour, '?', p[1], p[2], '?'])
    hid = hb[0][0] if hb else 'none'
    w0 = U.decs[0]['node'] if U.decs else 0
    junk_b = [('bridge_bad_rows', '%s\t%d\t5\t9\tabcd' % (hid, w0)),                       # 5 fields
              ('bridge_bad_rows', '%s\t%d\t5\t9\tabcd\tr8\tx' % (hid, w0)),                # 7
              ('bridge_bad_rows', '%s\tx%d\t5\t9\tabcd\tr8' % (hid, w0)),
              ('bridge_bad_rows', '%s\t-%d\t5\t9\tabcd\tr8' % (hid, w0)),
              ('bridge_bad_rows', '%s\t%d\tx\t9\tabcd\tr8' % (hid, w0)),
              ('bridge_bad_rows', '%s\t%d\t5\t-9\tabcd\tr8' % (hid, w0)),
              ('bridge_bad_rows', '%s\t\t5\t9\tabcd\tr8' % hid),
              ('bridge_bad_rows', '%s\t%d\t5\t9.0\tabcd\tr8' % (hid, w0)),
              ('bridge_unknown_ids', 'nope-8\t%d\t5\t9\tabcd\tr8' % w0),
              ('bridge_unknown_ids', '%s\t%d\t5\t9\tabcd\tr8' % (U.base_treat[0][0] if U.base_treat else 'tz', w0))]
    junk_h = [('hclaim_bad_rows', '%s\tanchorwide\tr8' % hid), ('hclaim_bad_rows', '%s\tAnchorWide\tr8' % hid),
              ('hclaim_bad_rows', '%s\tanchorWide' % hid), ('hclaim_bad_rows', '%s\tanchor_wide\tr8' % hid),
              ('hclaim_unknown_ids', 'nope-8\tanchorWide\tr8')]
    for (cnt, l) in R.sample(junk_b, R.randint(4, len(junk_b))):
        U.blines.insert(R.randint(0, len(U.blines)), l)
        U.counts[cnt] += 1
    for (cnt, l) in R.sample(junk_h, R.randint(2, len(junk_h))):
        U.hclines.insert(R.randint(0, len(U.hclines)), l)
        U.counts[cnt] += 1
    if R.random() < 0.5:
        U.blines.insert(R.randint(0, len(U.blines)), '')


def finish(U, flavour):
    R = U.R
    for x in U.decs:
        x['text'] = x['T'].text()
        x['sha'] = m7.sha1(x['text'])
    U.hrows_out = []
    for r in U.hrows:
        finish_bridge(U, r)
    for r in U.awrows:
        finish_aw(U, r)
    base_lines(U, flavour)

    def append(name, rows):
        with open(U.J(name), 'ab') as f:
            for r in rows:
                f.write(('\t'.join(str(v) for v in r) + '\n').encode('utf-8'))

    def write_lines(name, lines):
        with open(U.J(name), 'ab') as f:
            f.write(('\n'.join(lines) + '\n').encode('utf-8') if lines else b'')
    if U.oc_rows:
        append('courts2.tsv', U.oc_rows)
    append('decisions2.tsv', [[x['node'], x['court'], x['date'], x['unit'], x['bench'], x['pub'], x['form'],
                               x['sha'], 'r8'] for x in U.decs])
    append('history.tsv', U.hrows_out)
    append('cert_text.tsv', U.ct)
    if U.has_wsha:
        append('window_sha.tsv', U.wsha)
    if U.has_idx:
        idx = []
        for x in U.decs:
            ix = x['index']
            if ix in ('ok', 'ambig'):
                idx.append([x['cite'], x['node']])
            if ix == 'wrong':
                idx.append([x['cite'], R.choice([y for y in U.decs if y is not x])['node']])
            if ix == 'ambig':
                idx.append([x['cite'].upper().replace(' ', ''), R.choice([y for y in U.decs if y is not x])['node']])
        append('cite_index.tsv', idx + U.extra_idx)
    if U.alines:
        write_lines('history_anchor.tsv', U.alines)
    write_lines('history_claim.tsv', U.hclines)
    with open(U.J('history_bridge.tsv'), 'ab') as f:
        f.write(('\n'.join(U.blines) + '\n').encode('utf-8'))
    U.counts['bridge_rows'] = len(U.br_ids)
    U.counts['hclaim_anchorwide_unused'] = len(U.aw_unused)
    ep = os.path.join(U.d, 'edges', 'edges-00.tsv')
    old = [tuple(int(v) for v in r) for r in (rows_of(ep) or [])]
    gen.write(ep, sorted(set(old) | {tuple(e) for e in U.edges}))
    gen.write(os.path.join(U.d, 'expect.tsv'), U.expect)
    gen.write(os.path.join(U.d, 'expect_counts.tsv'), sorted(U.counts.items()))


# ---------------------------------------------------------------------------------------------------------------
B_ = bridge_case
A_ = aw_case
MAIN = [('br_ok_' + k, B_, dict(kind=k)) for k in KINDS] + [
    ('br_ok', B_, dict()), ('br_ok2', B_, dict()), ('br_ok_plainpart', B_, dict(oh=False)),
    ('br_ok_oh', B_, dict(oh=True, kind='certDenied')),
    ('br_len_max', B_, dict(qlen=BRIDGE_MAX)), ('br_len_over', B_, dict(qlen=BRIDGE_MAX + 1, exp='bridgeMismatch')),
    ('br_off', B_, dict(defect='b_off', exp='bridgeMismatch')),
    ('br_quote', B_, dict(defect='b_quote', exp='bridgeMismatch')),
    ('br_empty', B_, dict(defect='b_empty', exp='bridgeMismatch')),
    ('br_swapped', B_, dict(defect='b_swapped', exp='bridgeMismatch')),
    ('br_len', B_, dict(defect='b_len', exp='bridgeMismatch')),
    ('br_nowin', B_, dict(defect='b_nowin', exp='bridgeMismatch')),
    ('br_badwin', B_, dict(defect='b_badwin', exp='bridgeMismatch')),
    ('br_hash', B_, dict(defect='b_hash', exp='bridgeMismatch')),
    ('br_nohash', B_, dict(defect='b_nohash', exp='bridgeMismatch')),
    ('br_othertext', B_, dict(defect='b_othertext', exp='bridgeMismatch')),
    ('br_wgap', B_, dict(w='gap', exp='bridgeMismatch')),
    ('br_w_before', B_, dict(w='before', exp='bridgeDate')),
    ('br_w_equal', B_, dict(w='equal')),
    ('br_w_zero', B_, dict(w='zero', exp='bridgeDate')),
    ('br_o_zero', B_, dict(o_zero=True, oh=False, exp='bridgeDate')),
    ('br_semi', B_, dict(clause='semi', exp='bridgeClause')),
    ('br_noX', B_, dict(clause='noX', exp='bridgeTarget')),
    ('br_x_wrongidx', B_, dict(xidx='wrong', exp='bridgeTarget')),
    ('br_x_noidx', B_, dict(xidx='none', exp='bridgeTarget')),
    ('br_x_ambig', B_, dict(xidx='ambig', exp='bridgeTarget')),
    ('br_nocue', B_, dict(clause='nocue', exp='bridgeCue')),
    ('br_cue_before', B_, dict(clause='cue_before', exp='bridgeCue')),
    ('br_otherkind', B_, dict(clause='otherkind', exp='bridgeCue')),
    ('br_kind_nolist', B_, dict(kind='remanded', oh=False, cue='remanded', exp='bridgeCue')),
    ('br_chain', B_, dict(clause='chain', exp='bridgeChain')),
    ('br_parallel_after', B_, dict(clause='parallel_after')),
    ('br_noactor', B_, dict(clause='noactor', exp='bridgeActor')),
    ('br_other_actor', B_, dict(clause='other_actor', exp='bridgeActor')),
    ('br_actor_second', B_, dict(clause='actor_second', exp='bridgeActor')),
    ('br_actor_before', B_, dict(clause='actor_before', exp='bridgeActor')),
    ('br_o_wrongidx', B_, dict(oidx='wrong', exp='bridgeActor')),
    ('br_o_noidx', B_, dict(oidx='none', exp='bridgeActor')),
    ('br_o_ambig', B_, dict(oidx='ambig', exp='bridgeActor')),
    ('br_m_part', B_, dict(oh=False, part='dissent', exp='part')),
    ('br_m_head_noclaim', B_, dict(oh=True, kind='certDenied', claims=(), exp='part')),
    ('br_m_nocue', B_, dict(oh=False, disp='nocue', exp='noVerb')),
    ('br_m_disq', B_, dict(oh=False, disp='disq', exp='disqualified')),
    ('br_m_quote', B_, dict(defect='m_quote', exp='quoteMismatch')),
    ('br_m_sha', B_, dict(defect='m_sha', exp='shaMismatch')),
    ('br_m_oh_early', B_, dict(oh=True, kind='certDenied', date=20100315, exp='orderHeadNotAllowed')),
    ('br_x_later', B_, dict(x_later=True, exp='targetLater')),
    ('br_dup', B_, dict(dup='dup')),
    # anchorWide (§5)
    ('aw_ok', A_, dict()), ('aw_ok2', A_, dict()),
    ('aw_noclaim', A_, dict(claims=(), exp='anchorNoCue')),
    ('aw_plain', A_, dict(anchor='plain')), ('aw_plain_noclaim', A_, dict(anchor='plain', claims=())),
    ('aw_none', A_, dict(anchor='none', exp='anchorNoCue')),
    ('aw_disq', A_, dict(anchor='disq', exp='anchorDisqualified')),
    ('aw_cal', A_, dict(anchor='cal', exp='anchorNoCue')),
    ('aw_upper', A_, dict(upper=True)),
    ('aw_noev', A_, dict(anchor='noev', exp='anchorUnresolved')),
    ('aw_apart', A_, dict(a_part='dissent', exp='anchorPart')),
    ('aw_noanchor', A_, dict(anchor='')),
    ('aw_oh', A_, dict(scotus=True, kind='certDenied', claims=('anchorWide', 'orderHead'))),
    ('aw_sa', A_, dict(claims=('anchorWide', 'setAside'))),
    ('aw_dup', A_, dict(dup_claim=True)),
    ('aw_with_bridge', A_, dict(anchor='none', bridge=True)),
]
PROBE = [
    ('pr_coord', B_, dict(kind='reversed', cue='reversed', clause='coord', exp='bridgeCue')),        # Q8-4
    ('pr_prefix_other', B_, dict(kind='certDenied', ocite='777 U.S. 1001', zcite='777 U.S. 100')),   # Q8-6
    ('pr_prefix_o_short', B_, dict(kind='certDenied', ocite='778 U.S. 100', zcite='778 U.S. 1001',
                                   clause='other_actor', exp='bridgeActor')),                         # Q8-6
    ('pr_two_cues', B_, dict(kind='affirmed', clause='two_cues', exp='bridgeActor')),                # Q8-7
    ('pr_upper', B_, dict(clause='upper')),
    ('pr_nonascii_ok', B_, dict(clause='nonascii_ok')),                                              # ASCII-only
    ('pr_kelvin_x', B_, dict(clause='kelvin_x', xcite='%d Kan. %d' % (7, 345), exp='bridgeTarget')),
    ('pr_arabic_o', B_, dict(clause='arabic_o', exp='bridgeActor')),
    ('pr_dotted_i', B_, dict(kind='certDenied', cue='certiorari denied', clause='dotted_i', exp='bridgeCue')),
    ('pr_chain_ambig', B_, dict(clause='chain_ambig')),                                              # Q8-16
    ('pr_actor_after_ambig', B_, dict(clause='actor_second', zidx='ambig')),                         # Q8-16
    ('pr_chain_xparallel', B_, dict(clause='xparallel', exp='bridgeChain')),                         # Q8-13
    ('pr_curly', B_, dict(kind='reversed', clause='curly', exp='bridgeCue')),
    ('pr_nodot', B_, dict(kind='certDenied', clause='nodot')),
    ('pr_anchor_bad', B_, dict(anchor='bad')),                                                        # Q8-2
    ('pr_anchor_ok', B_, dict(anchor='ok')),
    ('pr_w_is_o', B_, dict(w='is_o', exp='?')),
    ('pr_w_big', B_, dict(w='big', exp='bridgeMismatch')),                                            # Q8-3
    ('pr_by1', B_, dict(by1=True, exp='bridgeDate')),                                                # Q8-8
    ('pr_first_bad', B_, dict(dup='first_bad', exp='bridgeMismatch')),                                # Q8-1
    ('pr_lead_zero', B_, dict(lead_zero=True)),                                                      # Q8-1
    ('pr_len_max', B_, dict(qlen=BRIDGE_MAX)), ('pr_len_over', B_, dict(qlen=BRIDGE_MAX + 1, exp='bridgeMismatch')),
    ('pr_aw_bridge', A_, dict(anchor='wide', bridge=True)),                                         # Q8-2/Q8-11
    ('pr_aw_upper', A_, dict(upper=True)),
    ('br_ok', B_, dict()), ('aw_ok', A_, dict()),
]


def make(seed, d, n, flavour, fuzz=0):
    shutil.rmtree(d, ignore_errors=True)
    gen.generate(seed, d, n, r5=True)
    U = U8(d, seed, flavour)
    U.awrows = []
    cases = PROBE if flavour == 'probe' else MAIN
    for name, fn, o in cases:
        fn(U, name, flavour, **o)
    if flavour != 'probe':
        for name, fn, o in oc_cases():
            fn(U, name, flavour, **o)
        # a claim line on a treatments id: unknown (DESIGN8 §6), counted
        if U.base_treat:
            U.hclines.append('	'.join([U.base_treat[0][0], 'oldCircuit', 'r8:treat']))
            U.counts['hclaim_unknown_ids'] += 1
        for i in range(6):
            bridge_case(U, 'br_random', flavour)
    finish(U, flavour)
    if fuzz:
        R = random.Random(seed * 1000003 + 8009)
        log = m7.mutate(U.J('history_bridge.tsv'), R, fuzz, 6, (1, 2, 3)) + m7.mutate(
            U.J('history_claim.tsv'), R, max(1, fuzz // 2), 3, ())
        gen.write(os.path.join(d, 'mutations.txt'), log)
        gen.write(os.path.join(d, 'expect.tsv'), [r[:3] + ['fuzz', '?'] + r[5:7] + ['?'] for r in U.expect])
        gen.write(os.path.join(d, 'expect_counts.tsv'), [])
    return len(U.hrows), len(U.awrows), len(U.blines), len(U.hclines)


# ---------------------------------------------------------------------------------------------------------------
def strip_r8(src, dst):
    """A copy of data dir src without history_bridge.tsv and without the anchorWide claim lines."""
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    if os.path.exists(os.path.join(dst, 'history_bridge.tsv')):
        os.remove(os.path.join(dst, 'history_bridge.tsv'))
    p = os.path.join(dst, 'history_claim.tsv')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            lines = f.read().split(b'\n')
        with open(p, 'wb') as f:
            f.write(b'\n'.join(l for l in lines if not any(x in l.lower() for x in (b'anchorwide', b'oldcircuit'))))


def cmd_empty(root, ref, pre):
    """Round 8 off: the current reference writes what the pre-round-8 copy writes (history_bridge.tsv absent,
    empty, blank; no anchorWide claim). The pre copy runs from a scratch tree with the current cue table."""
    bad = 0
    tmp = tempfile.mkdtemp(prefix='r8pre_')
    shutil.copytree(os.path.dirname(pre), os.path.join(tmp, 'ref'))
    shutil.copytree(os.path.join(REF, '..', 'cues'), os.path.join(tmp, 'cues'))
    pre = os.path.join(tmp, 'ref', os.path.basename(pre))
    strip = lambda x: b'\n'.join(l for l in x.split(b'\n') if not l.startswith((b'seconds', b'peak_mb')))
    us = m7.universes(root)
    for d in us:
        outs = []
        for mode in ('absent', 'empty', 'blank'):
            data = os.path.join(d, 'data_' + mode)
            strip_r8(os.path.join(d, 'data'), data)
            if mode != 'absent':
                with open(os.path.join(data, 'history_bridge.tsv'), 'wb') as fh:
                    fh.write(b'' if mode == 'empty' else b'\n\r\n\n')
            out = os.path.join(d, 'ref_' + mode)
            m7.run_ref(ref, d, out, data)
            outs.append(out)
        out = os.path.join(d, 'ref_pre')
        m7.run_ref(pre, d, out, os.path.join(d, 'data_absent'))
        outs.append(out)
        for o in outs[1:]:
            for fn in sorted(set(os.listdir(outs[0])) | set(os.listdir(o))):
                a = open(os.path.join(outs[0], fn), 'rb').read() if os.path.exists(os.path.join(outs[0], fn)) else None
                b = open(os.path.join(o, fn), 'rb').read() if os.path.exists(os.path.join(o, fn)) else None
                if fn == 'ref_stats.tsv' and a is not None and b is not None:
                    a, b = strip(a), strip(b)
                if a != b:
                    bad += 1
                    print('%s: %s differs (%s)' % (os.path.basename(d), fn, os.path.basename(o)))
        for o in outs:
            shutil.rmtree(o, ignore_errors=True)
        for mode in ('absent', 'empty', 'blank'):
            shutil.rmtree(os.path.join(d, 'data_' + mode), ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print('%d universes, %d differing files' % (len(us), bad))
    return 1 if bad else 0


def cmd_check(root, ref):
    """make_r7.py check, plus the status expectation `neg` (the target has a negative, non-partial status row)."""
    rc = m7.cmd_check(root, ref)
    bad = tot = 0
    for d in m7.universes(root):
        ex = [r for r in rows_of(os.path.join(d, 'expect.tsv')) if r[7] == 'neg']
        if not ex:
            continue
        out = os.path.join(d, 'ref_check_neg')
        m7.run_ref(ref, d, out)
        st = set()
        for p in rows_of(os.path.join(out, 'status.tsv')) or []:
            if p[5] == 'negative' and not p[6].endswith(':partial'):
                st.add(p[0])
        for r in ex:
            tot += 1
            if r[5] not in st:
                bad += 1
                print('%s  %s  case %s  target %s not negative' % (os.path.basename(d), r[1], r[2], r[5]))
        shutil.rmtree(out, ignore_errors=True)
    print('%d negative-status expectations, %d differ' % (tot, bad))
    return 1 if (rc or bad) else 0


def cmd_report(roots):
    """As make_r7.py report (rows are attributed by id through expect.tsv first, so h8: ids need nothing more)."""
    m7.cmd_report(roots)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gen')
    g.add_argument('--seed', type=int, default=80000)
    g.add_argument('--rounds', type=int, default=1)
    g.add_argument('--n', type=int, default=60)
    g.add_argument('--out', required=True)
    g.add_argument('--probe', action='store_true')
    g.add_argument('--fuzz', type=int, default=0, metavar='K')
    c = sub.add_parser('check')
    c.add_argument('dir')
    c.add_argument('--ref', default=os.path.join(REF, 'precedent_ref.py'))
    e = sub.add_parser('empty')
    e.add_argument('dir')
    e.add_argument('--ref', default=os.path.join(REF, 'precedent_ref.py'))
    e.add_argument('--pre', default=PRE_REF)
    r = sub.add_parser('report')
    r.add_argument('dirs', nargs='+')
    a = ap.parse_args()
    if a.cmd == 'gen':
        os.makedirs(a.out, exist_ok=True)
        fl = 'probe' if a.probe else ('fuzz' if a.fuzz else 'main')
        for s in range(a.seed, a.seed + a.rounds):
            d = os.path.join(a.out, '%s%d' % ({'probe': 'q', 'fuzz': 'g', 'main': 'v'}[fl], s))
            h, w, b, c = make(s, d, a.n, fl, a.fuzz)
            print('%s: %d bridge rows, %d anchorWide rows, %d bridge lines, %d claim lines' % (d, h, w, b, c))
    elif a.cmd == 'check':
        sys.exit(cmd_check(a.dir, a.ref))
    elif a.cmd == 'empty':
        sys.exit(cmd_empty(a.dir, a.ref, a.pre))
    else:
        cmd_report(a.dirs)


if __name__ == '__main__':
    main()
