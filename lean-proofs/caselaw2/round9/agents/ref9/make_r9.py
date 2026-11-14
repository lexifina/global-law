#!/usr/bin/env python3
"""make_r9.py - round-9 universes for part zones (round9/DESIGN9.md §4), for the differential test of the round-9 Lean
runner against the Python reference.

A universe is a round-7 universe (make_r7.py: gen.py base + joined / doctrine / orderHead / setAside cases) with the
round-8 overlay of make_r8.py (bridge, anchorWide, oldCircuit cases) on top, then a `part_zone.tsv` built from the
rows' own quotes: for every acting node (`by`) of a treatments or history row, a node flavour (zones around the
quotes, an exact zone, a zone of another part, a zone boundary inside a quote, touching zones, zones elsewhere only,
overlapping zones, a duplicate line, z_start = z_end, z_start > z_end, an unknown part, bad lines that leave the node
alone, no line at all), plus lines on nodes that are only targets, on unknown nodes, and bad lines.

`expect.tsv` (beside data/, never read by an engine): table, id, case (<zone flavour>:<round-7/8 case>), flavour,
the verdict DESIGN9 §4 gives the row (reference vocabulary), target, text owner, `-`. The verdict is the round-8 verdict of
the reference with no part_zone.tsv (the regressions show that is the round-8 output) with the zone rule applied by
this file's own implementation of §4 under the readings of REF_QUESTIONS9.md. `expect_counts.tsv`: the zone
counters.

  python make_r9.py gen    --seed 90000 --rounds 8 --out DIR [--probe] [--fuzz K] [--n 60]
        DIR/z<seed> (main), y<seed> (--probe: round-7/8 probe overlays), x<seed> (--fuzz K: K byte-level mutations of
        part_zone.tsv; expectations become `?`)
  python make_r9.py check  DIR [--ref PATH]          the reference against expect.tsv / expect_counts.tsv
  python make_r9.py empty  DIR [--ref PATH] [--pre PATH]
        part_zone.tsv absent / empty / blank: the current reference and the pre-round-9 copy write the same bytes;
        only lines on unknown nodes or bad lines: every file but ref_stats.tsv the same
  python make_r9.py report DIR...                    attribute each universe's diff.tsv rows to the cases
"""
import argparse
import os
import random
import shutil
import sys
import tempfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R8 = os.environ.get('MAKE_R8_DIR') or os.path.normpath(os.path.join(HERE, '..', '..', '..', 'round8', 'agents', 'ref8'))
if not os.environ.get('MAKE_R7_DIR'):
    os.environ['MAKE_R7_DIR'] = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'round7', 'agents', 'ref'))
sys.path.insert(0, R8)
import make_r8 as m8  # noqa: E402
m7 = m8.m7
gen = m7.gen
rows_of = m7.rows_of
REF = m7.REF
sys.path.insert(0, REF)
import precedent_ref as pr  # noqa: E402

PRE_REF = os.path.normpath(os.path.join(HERE, '..', '..', 'pre', 'ref', 'precedent_ref.py'))
PARTS = ('majority', 'plurality', 'perCuriam', 'concurrence', 'dissent', 'headmatter', 'other')
BAD_PARTS = ('Majority', 'per curiam', 'majority ', '', 'dissenting', 'MAJORITY', 'perCuriam​', 'opinion')
NODE_FLAVOURS = [('good', 46), ('missing', 9), ('overlap', 6), ('dup', 4), ('eq', 4), ('gt', 3), ('badpart', 5),
                 ('elsewhere', 6), ('badline_keep', 7), ('zeros', 4), ('touch_all', 6)]
CLUSTER_MUT = [('inside', 40), ('exact', 15), ('otherpart', 12), ('straddle', 8), ('shift', 5), ('short', 5),
               ('touch_split', 8), ('none', 7)]
BAD_LINES = ['four', 'six', 'node_x', 'neg', 'dec', 'arabic', 'empty_num', 'plus', 'space', 'fullwidth']


def wpick(R, table):
    t = sum(w for _, w in table)
    x = R.uniform(0, t)
    for k, w in table:
        x -= w
        if x <= 0:
            return k
    return table[-1][0]


# ---------------------------------------------------------------------------------------------------------------
# round-9 cases (DESIGN9 §5 joinedFar, §7 implicitReject), built in the make_r7 stage (their rows are finished by
# make_r7.finish_treat); expectations in DESIGN9's words, checked against the reference at generation time
GAPMAX = m7.GAP
FARMAX = int(m7.CUE.get('joined_far_max') or 1200)
IMPLICIT = m7.CUE.get('implicit_reject') or [
    'cannot agree', 'do not agree', 'unpersuaded', 'not convinced', 'wrongly decided', 'incorrectly decided',
    'erroneously decided', 'unsound', 'erroneous', 'incorrect', 'mistaken', 'undermined', 'eroded', 'discredited',
    'called into question', 'contrary to', 'depart from', 'departs from']
NEG = ['overruled', 'disapproved', 'recededFrom', 'abrogated']
SOFT = ['limited', 'questioned', 'criticized', 'declinedToFollow']


def _gap_piece(U, row):
    """The index of the filler piece between the joined quote and the main quote of a make_r7 antecedent row."""
    T = row['owner']['T']
    e = row['lines'][0][1][1]
    k = 0
    for i, p in enumerate(T.parts):
        if k == e + 1:
            return i
        k += len(p) + 1
    raise RuntimeError('no gap piece')


def far_case(U, case, flavour, exp='ok', gap=700, claim='joinedFar', win='ok', gapmod=None, **o):
    """A make_r7 antecedent row with a gap of `gap` characters; claim joinedFar (or none: claim='-'); win: the extra
    window covering [j_end, start) (ok | none | bad | hash); gapmod: what the gap holds (para | para_first |
    para_last | cr | key_other | key_target | key_ambig | key_straddle | key_after)."""
    R = U.R
    kind = o.pop('kind', None) or R.choice(NEG)
    Z, msent = None, o.pop('msent', None)
    if gapmod in ('key_other', 'key_ambig', 'key_straddle', 'key_after'):
        Z = U.newdec(R.choice([c for c in (101, 201, 501) if c in U.courts] or [101]), 0)
    if gapmod == 'key_straddle':
        head, tail = Z['cite'].rsplit(' ', 1)
        msent = '%s; %s' % (tail, m7.main_sentence(U, kind))
    elif gapmod == 'key_after':
        msent = '%s See %s, %s.' % (m7.main_sentence(U, kind), Z['name'], Z['cite'])
    if gapmod in ('key_other', 'key_straddle', 'key_ambig') and not U.has_idx:
        exp = 'ok'
    if win == 'hash' and not U.has_wsha:
        exp = 'ok'
    row = m7.treat_case(U, case, flavour, rel='antecedent', exp=exp, gap=gap, claim=claim, kind=kind, msent=msent,
                        j='ok', **o)
    T = row['owner']['T']
    i = _gap_piece(U, row)
    L = len(T.parts[i])
    p = T.parts[i]
    if gapmod in ('para', 'cr', 'para_first', 'para_last'):
        k = {'para_first': 0, 'para_last': L - 1}.get(gapmod, R.randint(1, L - 2))
        p = p[:k] + ('\r' if gapmod == 'cr' else '\n') + p[k + 1:]
    elif gapmod in ('key_other', 'key_target', 'key_ambig'):
        X = row['X'] if gapmod == 'key_target' else Z
        c = 'See %s, %s.' % (X['name'], X['cite'])
        a = R.randint(1, max(1, L - len(c) - 3))
        p = U.filler(a) + ' ' + c + ' ' + U.filler(L - a - len(c) - 2)
    elif gapmod == 'key_straddle':
        p = U.filler(L - len(head) - 1) + ' ' + head
    assert len(p) == L, (gapmod, len(p), L)
    T.parts[i] = p
    row['far'] = (win, Z if gapmod == 'key_ambig' else None)
    U.r9far.append(row)
    return row


def far_post(U):
    """After make_r7.finish: the extra windows covering each far row's gap, and the second index line of an
    ambiguous key."""
    R = U.R
    ct, ws, idx = [], [], []
    for row in U.r9far:
        win, Zamb = row['far']
        txt, sha = row['owner']['text'], row['owner']['sha']
        e, st = row['lines'][0][1][1], row['m'][0]
        if win != 'none':
            s0, e0 = max(0, e - R.randint(0, 60)), min(len(txt), st + R.randint(0, 60))
            w = txt[s0:e0]
            ct.append([sha, s0, e0, w[:-1] if win == 'bad' else w])
            if U.has_wsha and win != 'nohash':
                ws.append([sha, s0, e0, m7.sha1(w + 'x') if win == 'hash' else m7.sha1(w), 'r9'])
        if Zamb is not None and U.has_idx:
            idx.append([Zamb['cite'].upper(), row['X']['node']])
    for name, rows in (('cert_text.tsv', ct), ('window_sha.tsv', ws), ('cite_index.tsv', idx)):
        if rows:
            with open(U.J(name), 'ab') as f:
                for r in rows:
                    f.write(('\t'.join(str(v) for v in r) + '\n').encode('utf-8'))


IMP_T = ['On {name}, {cite}: {cue}.', 'As for {name}, {cite}, the answer is {cue}.',
         'The holding of {name}, {cite}, is {cue} here.']


def implicit_case(U, case, flavour, exp='ok', how='implicit', kind=None, claim='implicitReject', part=None,
                  pair='review', status='notneg'):
    """A one-quote treatments row (no joined line) whose main quote names the target and holds an implicit_reject
    cue and no plain cue of its kind (how=implicit), a plain cue (plain), or neither (none)."""
    R = U.R
    kind = kind or R.choice(SOFT)
    dx, dd = U.dates()
    lo, hi = U.pick_pair(pair, dx, dd)
    X = U.newdec(lo, dx)
    Dd = U.newdec(hi, dd)
    tev = m7.evidence(U, X, R.choice(['cite', 'name']))
    plain = m7.TREAT.get(kind, [])
    avoid_d = m7.DISQ_TREAT if kind in NEG else []
    if how == 'implicit':
        ms = m7.draw(U, lambda: R.choice(IMP_T).format(name=X['name'], cite=X['cite'], cue=R.choice(IMPLICIT)),
                     need=(IMPLICIT,), avoid=(plain, avoid_d))
    elif how == 'plain':
        ms = m7.draw(U, lambda: R.choice(IMP_T).format(name=X['name'], cite=X['cite'], cue=R.choice(plain)),
                     need=(plain,), avoid=(avoid_d,))
    else:
        ms = m7.draw(U, lambda: R.choice(IMP_T).format(name=X['name'], cite=X['cite'], cue='as stated'),
                     avoid=(plain, IMPLICIT, avoid_d))
    T = Dd['T']
    T.add(U.filler(R.choice([0, 40, 300])))
    m = T.add(ms)
    T.add(U.filler(R.choice([0, 80])))
    tid = 't9:%d:%d:%d' % (Dd['node'], X['node'], m[0])
    row = {'id': tid, 'by': Dd['node'], 'target': X['node'], 'date': dd, 'kind': kind, 'scope': 'all',
           'temporal': 'unknown', 'explicit': 1, 'owner': Dd, 'm': m, 'mq': ms, 'tev': tev,
           'part': part or R.choice(['majority', 'majority', 'perCuriam']), 'X': X, 'D': Dd, 'defect': None,
           'lines': [], 'rel_override': None}
    U.trows.append(row)
    if claim != '-':
        U.klines.append([tid, claim, '-', '-', 'r9:gen'])
    U.expect.append(['treatments', tid, case, flavour, exp, X['node'], Dd['node'], status])


def implicit_joined(U, case, flavour, exp='ok', main='plain', kind='questioned'):
    """A soft row with the claim and a joined antecedent line: the main quote has an anaphor and a plain cue of the
    kind (main=plain) or an anaphor and only an implicit cue (main=implicit; the relation's cue test is the plain
    list, Q9-17)."""
    R = U.R
    plain = m7.TREAT.get(kind, [])
    cues = plain if main == 'plain' else IMPLICIT
    ms = m7.draw(U, lambda: '%s %s.' % (R.choice(m7.ANAPHOR).capitalize(), R.choice(cues)),
                 need=(m7.ANAPHOR, cues), avoid=((m7.DISQ_TREAT,) + (() if main == 'plain' else (plain,))))
    m7.treat_case(U, case, flavour, rel='antecedent', exp=exp, kind=kind, msent=ms, claim='implicitReject', j='ok',
                  status='notneg')


def implicit_witness(U, case, flavour):
    """The claim on a base witness row with no class line (its kind changes status): implicitBadKind."""
    taken = {r[0] for r in (U.base_class or [])} | {k[0] for k in U.klines}
    for w in U.base_wit:
        if w[0] not in taken:
            U.klines.append([w[0], 'implicitReject', '-', '-', 'r9:gen'])
            U.expect.append(['treatments', w[0], case, flavour, 'implicitBadKind|badRow', '?', '?', '-'])
            return


F_ = far_case
I_ = implicit_case
# (no joinedFarPara case: a window is one TSV field, so it cannot hold a LF; the cert_text windows of the corpus
# are normalised, tab / newline -> space (r6lib.norm). REF_QUESTIONS9.md Q9-13.)
R9_MAIN = [
    ('far_ok_301', F_, dict(gap=GAPMAX + 1)), ('far_ok_700', F_, dict(gap=700)), ('far_ok_max', F_, dict(gap=FARMAX)),
    ('far_ok_followed', F_, dict(gap=650, kind='followed')),
    ('far_over', F_, dict(gap=FARMAX + 1, exp='joinedFarGap')),
    ('far_noclaim', F_, dict(gap=700, claim='-', exp='joinedRelation')),
    ('far_noclaim_301', F_, dict(gap=GAPMAX + 1, claim='-', exp='joinedRelation')),
    ('far_nowin', F_, dict(gap=800, win='none', exp='joinedFarWindow')),
    ('far_badwin', F_, dict(gap=800, win='bad', exp='joinedFarWindow')),
    ('far_hashwin', F_, dict(gap=800, win='hash', exp='joinedFarWindow')),
    ('far_key_other', F_, dict(gap=700, gapmod='key_other', exp='joinedFarKey')),
    ('far_key_target', F_, dict(gap=700, gapmod='key_target')),
    ('far_key_ambig', F_, dict(gap=700, gapmod='key_ambig')),
    ('far_key_after', F_, dict(gap=700, gapmod='key_after')),
    ('far_noana', F_, dict(gap=700, main='noana', exp='joinedRelation')),
    ('far_nocue', F_, dict(gap=700, main='nocue', exp='joinedRelation')),
    ('far_jpart', F_, dict(gap=700, j_part='dissent', exp='joinedPart')),
    ('far_noauth', F_, dict(gap=700, pair='noauth')),
    ('imp_ok_dtf', I_, dict(kind='declinedToFollow')), ('imp_ok_q', I_, dict(kind='questioned')),
    ('imp_noclaim_dtf', I_, dict(kind='declinedToFollow', claim='-', exp='noVerb')),
    ('imp_noclaim_q', I_, dict(kind='questioned', claim='-', exp='noVerb')),
    ('imp_plain', I_, dict(how='plain')), ('imp_plain_noclaim', I_, dict(how='plain', claim='-')),
    ('imp_none', I_, dict(how='none', exp='noVerb')),
    ('imp_bad_overruled', I_, dict(kind='overruled', exp='implicitBadKind')),
    ('imp_bad_disapproved', I_, dict(kind='disapproved', how='plain', exp='implicitBadKind')),
    ('imp_part', I_, dict(part='dissent', exp='part')),
    ('imp_noauth', I_, dict(pair='noauth')),
    ('imp_joined_plain', implicit_joined, dict(main='plain')),
]
R9_PROBE = [
    ('pr_far_cr', F_, dict(gap=700, gapmod='cr')),                                          # Q9-13
    ('pr_far_key_straddle', F_, dict(gap=700, gapmod='key_straddle', exp='joinedFarKey')),  # Q9-14
    ('pr_far_max', F_, dict(gap=FARMAX)), ('pr_far_over', F_, dict(gap=FARMAX + 1, exp='joinedFarGap')),
    ('pr_imp_limited', I_, dict(kind='limited')), ('pr_imp_criticized', I_, dict(kind='criticized')),   # Q9-16
    ('pr_imp_followed', I_, dict(kind='followed', exp='implicitBadKind')),                               # Q9-16
    ('pr_imp_superseded', I_, dict(kind='supersededByEnactment', exp='implicitBadKind')),                # Q9-16
    ('pr_imp_distinguished', I_, dict(kind='distinguished', exp='implicitBadKind')),                     # Q9-16
    ('pr_imp_joined_implicit', implicit_joined, dict(main='implicit', exp='joinedRelation')),            # Q9-17
    ('pr_imp_witness', implicit_witness, dict()),                                                        # Q9-18
    ('far_ok_700', F_, dict(gap=700)), ('imp_ok_dtf', I_, dict(kind='declinedToFollow')),
]


# DESIGN9 §8 (D9-9): judge-form anchor sentences, for make_r8.aw_case (anchor='judge:<string>')
JUDGE_T = ['{name}, {cite}, was heard by the {j}.', 'The {j} decided {name}, {cite}.',
           'We review the ruling of the {j} in {name}, {cite}.']
_aw_sentence = m8.aw_sentence


def aw_sentence9(U, X, how, upper=False):
    if not how.startswith('judge:'):
        return _aw_sentence(U, X, how, upper)
    R = U.R
    j = how.split(':', 1)[1]
    mk = lambda: R.choice(JUDGE_T).format(name=X['name'], cite=X['cite'], j=j)
    s = m7.draw(U, mk, need=([j],), avoid=(m8.ANCHOR, m8.ANCHOR_WIDE, m8.DISQ_ANCHOR))
    return s.upper() if upper else s


m8.aw_sentence = aw_sentence9
A8 = m8.aw_case
R9_AW = [
    ('aw9_district', A8, dict(anchor='judge:district judge')),
    ('aw9_magistrate', A8, dict(anchor='judge:magistrate judge')),
    ('aw9_trial', A8, dict(anchor='judge:trial judge')),
    ('aw9_upper', A8, dict(anchor='judge:district judge', upper=True)),
    ('aw9_noclaim', A8, dict(anchor='judge:district judge', claims=(), exp='anchorNoCue')),
    ('aw9_judge_only', A8, dict(anchor='judge:judge of the court', exp='anchorNoCue')),
]


def make_r7_stage(seed, d, n, fl7):
    """make_r7.make (r5 on) with the round-9 cases added before make_r7.finish, then far_post."""
    shutil.rmtree(d, ignore_errors=True)
    gen.generate(seed, d, n, r5=True)
    U = m7.Universe(d, seed, fl7)
    U.r9far = []
    if not U.has_idx and seed % 3 != 0:
        U.has_idx = True
    for name, fn, o in (m7.PROBE if fl7 == 'probe' else m7.MAIN):
        fn(U, name, fl7, **o)
    if fl7 == 'probe':
        m7.probe_extra(U, fl7)
    else:
        m7.witness_joined(U, fl7)
        for i in range(6):
            m7.treat_case(U, 'ant_random', fl7, pair=U.R.choice(['review'] * 4 + ['noauth']))
        for i in range(3):
            m7.treat_case(U, 'doc_random', fl7, rel='doctrine', status='notneg')
    for name, fn, o in (R9_PROBE if fl7 == 'probe' else R9_MAIN):
        fn(U, name, fl7, **dict(o))
    m7.finish(U, fl7)
    far_post(U)


def check_r9_cases(d, v8):
    """The round-9 cases' expectations (expect7.tsv / expect8.tsv rows of R9 cases) against the reference without
    zones."""
    names = {c[0] for c in R9_MAIN + R9_PROBE + R9_AW}
    bad = tot = 0
    out = []
    for r in (rows_of(os.path.join(d, 'expect7.tsv')) or []) + (rows_of(os.path.join(d, 'expect8.tsv')) or []):
        if r[2] not in names or r[4] == '?':
            continue
        tot += 1
        g = v8.get((r[0].replace('.tsv', ''), r[1]), '-')
        if g not in r[4].split('|'):
            bad += 1
            out.append('%s  %s  case %s  expected %s  got %s' % (os.path.basename(d), r[1], r[2], r[4], g))
    return tot, bad, out


def build_base(seed, d, n, flavour):
    """make_r7 universe (+ the round-9 cases), then the make_r8 overlay (cases of the same flavour), as
    make_r8.make without its own gen.generate."""
    fl7 = 'probe' if flavour == 'probe' else 'main'
    make_r7_stage(seed, d, n, fl7)
    os.replace(os.path.join(d, 'expect.tsv'), os.path.join(d, 'expect7.tsv'))
    U = m8.U8(d, seed, fl7)
    U.awrows = []
    cases = m8.PROBE if flavour == 'probe' else m8.MAIN
    for name, fn, o in cases:
        fn(U, name, fl7, **o)
    for name, fn, o in R9_AW:
        fn(U, name, fl7, **o)
    if flavour != 'probe':
        for name, fn, o in m8.oc_cases():
            fn(U, name, fl7, **o)
        for i in range(6):
            m8.bridge_case(U, 'br_random', fl7)
    m8.finish(U, fl7)
    os.replace(os.path.join(d, 'expect.tsv'), os.path.join(d, 'expect8.tsv'))
    case_of = {}
    for fn in ('expect7.tsv', 'expect8.tsv'):
        for r in rows_of(os.path.join(d, fn)) or []:
            if len(r) > 2:
                case_of[(r[0].replace('.tsv', ''), r[1])] = r[2]
                if fn == 'expect7.tsv' and len(r) > 7 and r[7] == 'notneg':
                    case_of[('notneg', r[1])] = True      # a round-9 / round-7 never-negative target
    return case_of


def round8_verdicts(d):
    """The reference with no part_zone.tsv: per (table, id) the round-8 certificate verdict and certs.tsv's verdict,
    and the row list (table, id, by, target, spans) with the joined lines the reference keeps."""
    pr.BAD_ROWS.clear()
    D = pr.Data(os.path.join(d, 'data'))
    assert not D.zone_any
    A = pr.Engine(D)
    A.admit()
    rows = []

    def gate(table, r):
        # D9-4 (2): past the Lean's date-order and power checks (powercheck.py measured them on round-8 outputs)
        b, t = r['by'], r['target']
        if table == 'history':
            return A.same_case_power(b, t, D.hclaim.get(r['id'])) != 'no'
        if (D.date[b] < D.date[t]) if r['id'] in D.witness else (0 < D.date[b] < D.date[t]):
            return False
        return r['kind'] not in pr.NEG_TREAT or A.can_change(b, t, A._scope_dom(r['scope']))[0] != 'no'
    for r in D.treatments:
        c = r['cert']
        spans = [(c.start, c.end, c.part)] + [(l[1], l[2], l[4]) for l in D.joined.get(r['id'], ())]
        w = D.witness.get(r['id'])
        rows.append(('treatments', r['id'], w[0] if w else r['by'], r['target'], spans, 'witness' if w else '',
                     gate('treatments', r)))
    for r in D.history:
        c = r['cert']
        own = D.sha.get(r['target']) == c.sha
        rows.append(('history', r['id'], r['target'] if own else r['by'], r['target'], [(c.start, c.end, c.part)],
                     'owntext' if own else '', gate('history', r)))
    r8 = {(f.replace('.tsv', ''), i): v for (f, i), v in A.cert_ok.items()}
    v8 = {(f.replace('.tsv', ''), i): A.cert_verdict(f, i) for (f, i) in A.cert_ok}
    nodes = set(D.sha) | {i for i in range(len(D.court)) if D.has(i)}
    global RTEXT
    RTEXT = set()          # recognised-claim witness rows whose recognised text checks pass (zone-checked, counted)
    for r in D.treatments:
        w = D.witness.get(r['id'])
        k = D.klass.get(r['id']) if D.r5 else None
        if (w and k and k[0] == 'recognised' and D.has(r['by']) and D.has(r['target'])
                and A.cert_ok.get(('treatments.tsv', r['id'])) != 'badRow' and A._recog_text(r, w[0], w[1])):
            RTEXT.add(r['id'])
    return rows, r8, v8, D, nodes


def clusters(spans):
    """Merge [s, e) spans (s < e) that overlap (strictly) into clusters [(lo, hi, [spans])], sorted."""
    out = []
    for s in sorted(spans):
        if out and s[0] < out[-1][1]:
            out[-1][1] = max(out[-1][1], s[1])
            out[-1][2].append(s)
        else:
            out.append([s[0], s[1], [s]])
    return out


def node_lines(R, node, spans, fl):
    """-> list of (fields tuple of 5 strings, what) for one acting node: what = good | poison | bad (bad line)."""
    cl = clusters([s for s in spans if 0 <= s[0] < s[1]])
    L = []

    def zone(a, b, p, src='calpart9'):
        L.append(((str(node), str(a), str(b), p, src), 'good'))
    if fl == 'missing' or not cl:
        return L
    if fl == 'elsewhere':
        top = max(c[1] for c in cl)
        zone(top + R.randint(1, 50), top + R.randint(60, 900), R.choice(PARTS))
        if cl[0][0] >= 2:
            zone(0, R.randint(1, cl[0][0]), R.choice(PARTS))
        return L
    # zones per cluster, padded by at most half of each gap so neighbours never overlap
    for k, (lo, hi, sp) in enumerate(cl):
        prev_hi = cl[k - 1][1] if k else 0
        next_lo = cl[k + 1][0] if k + 1 < len(cl) else hi + 1000
        pl = R.randint(0, (lo - prev_hi) // 2)
        ph = R.randint(0, (next_lo - hi) // 2)       # the next cluster pads left by at most the other half
        part = sp[0][2] if sp[0][2] in PARTS else R.choice(PARTS)
        a, b = lo - pl, hi + ph
        mut = 'touch_split' if fl == 'touch_all' else wpick(R, CLUSTER_MUT)
        if fl in ('overlap', 'dup', 'eq', 'gt', 'badpart', 'badline_keep', 'zeros'):
            mut = R.choice(['inside', 'exact', 'otherpart'])
        if mut == 'inside':
            zone(a, b, part)
        elif mut == 'exact':
            zone(lo, hi, part)
        elif mut == 'otherpart':
            zone(a, b, R.choice([p for p in PARTS if p != part]))
        elif mut == 'straddle':
            s0 = max(sp, key=lambda s: s[1] - s[0])
            if s0[1] - s0[0] >= 2:
                cut = R.randint(s0[0] + 1, s0[1] - 1)
                zone(a, cut, part)
                zone(cut, b, part)
            else:
                zone(a, b, part)
        elif mut == 'shift':
            if lo + 1 < b:
                zone(lo + 1, b, part)
        elif mut == 'short':
            if a < hi - 1:
                zone(a, hi - 1, part)
        elif mut == 'touch_split':
            # a boundary exactly at the cluster's start (and its end): the quote lies wholly in the middle zone
            if a < lo:
                zone(a, lo, R.choice(PARTS))
            zone(lo, hi, part)
            if hi < b:
                zone(hi, b, R.choice(PARTS))
        # 'none': no zone for this cluster
    if fl == 'overlap' and L:
        f = R.choice(L)[0]
        a, b = int(f[1]), int(f[2])
        x = R.randint(a, b - 1)
        zone(max(0, x - R.randint(0, 20)), x + R.randint(1, 30), R.choice(PARTS))
    elif fl == 'dup' and L:
        L.append(R.choice(L))
    elif fl == 'eq':
        x = R.randint(0, 5000)
        L.append(((str(node), str(x), str(x), R.choice(PARTS), 'eq'), 'poison'))
    elif fl == 'gt':
        x = R.randint(1, 5000)
        L.append(((str(node), str(x), str(R.randint(0, x - 1)), R.choice(PARTS), 'gt'), 'poison'))
    elif fl == 'badpart':
        top = max(c[1] for c in cl)
        L.append(((str(node), str(top + 5), str(top + 50), R.choice(BAD_PARTS), 'bp'), 'poison'))
    elif fl == 'badline_keep':
        for _ in range(R.randint(1, 3)):
            L.append((bad_line(R, node), 'bad'))
    elif fl == 'zeros':
        L = [((f[0] if R.random() < 0.5 else '0' + f[0], '00' + f[1], '0' + f[2], f[3], f[4]), w) for f, w in L]
    return L


def bad_line(R, node):
    k = R.choice(BAD_LINES)
    a, b = R.randint(0, 3000), R.randint(3001, 6000)
    base = [str(node), str(a), str(b), R.choice(PARTS), 'bad']
    if k == 'four':
        return tuple(base[:4])
    if k == 'six':
        return tuple(base + ['x'])
    if k == 'node_x':
        base[0] = 'n%d' % node
    elif k == 'neg':
        base[1] = '-1'
    elif k == 'dec':
        base[2] = '%d.0' % b
    elif k == 'arabic':
        base[1] = '٣'
    elif k == 'empty_num':
        base[2] = ''
    elif k == 'plus':
        base[1] = '+%d' % a
    elif k == 'space':
        base[2] = ' %d' % b
    elif k == 'fullwidth':
        base[1] = '１２'
    return tuple(base)


def model(lines):
    """DESIGN9 §4 loading, this file's own implementation: -> (zones {node: [(a, b, part)]}, bad_nodes, bad_rows,
    kept lines). Not the reference's code."""
    import re
    nat = re.compile(r'^[0-9]+$')
    per, poisoned, bad = defaultdict(list), set(), 0
    for f in lines:
        if len(f) != 5 or not (nat.match(f[0]) and nat.match(f[1]) and nat.match(f[2])):
            bad += 1
            continue
        n, a, b = int(f[0]), int(f[1]), int(f[2])
        if a >= b or f[3] not in PARTS:
            poisoned.add(n)
            continue
        per[n].append((a, b, f[3]))
    for n, zs in per.items():
        for i in range(len(zs)):
            for j in range(i + 1, len(zs)):
                if zs[i][0] < zs[j][1] and zs[j][0] < zs[i][1]:
                    poisoned.add(n)
    zones = {n: zs for n, zs in per.items() if n not in poisoned}
    return zones, len(poisoned), bad, sum(len(z) for z in zones.values())


def zone_ok(zones, by, spans):
    z = zones.get(by)
    if not z:
        return None
    return all(any(a <= s and e <= b and p == q for (a, b, p) in z) for (s, e, q) in spans)


def overlay(d, seed, case_of, fuzz=0):
    R = random.Random(seed * 1000003 + 9009)
    rows, r8, v8, D, known = round8_verdicts(d)
    tot, bad, out = check_r9_cases(d, v8)
    gen.write(os.path.join(d, 'r9cases_check.tsv'), [[tot, bad]] + [[x] for x in out])
    for x in out:
        print(x, flush=True)
    by_node = defaultdict(list)
    for (t, i, by, tg, spans, odd, g) in rows:
        if by >= 0:
            by_node[by] += spans
    nfl = {}
    entries = []
    for node in sorted(by_node):
        fl = wpick(R, NODE_FLAVOURS)
        nfl[node] = fl
        entries += node_lines(R, node, by_node[node], fl)
    # nodes that are only targets: zones that would fail any quote (the zones of a target are not consulted)
    targets = sorted({tg for (t, i, by, tg, spans, odd, g) in rows if tg >= 0} - set(by_node))
    for node in R.sample(targets, min(len(targets), 6)):
        entries.append(((str(node), '0', '1', 'dissent', 'target_only'), 'good'))
        nfl[node] = 'target_only'
    # unknown nodes (no decisions2 row): harmless
    top = max(known) if known else 0
    for k in range(R.randint(1, 3)):
        entries.append(((str(top + 1000 + k), '0', str(R.randint(1, 9999)), R.choice(PARTS), 'unknown'), 'good'))
    entries.append(((str(top + 2000), '50', '10', 'majority', 'unknown_bad'), 'poison'))
    for _ in range(R.randint(0, 3)):
        entries.append((bad_line(R, R.choice(sorted(by_node) or [1])), 'bad'))
    R.shuffle(entries)
    lines = [f for f, w in entries]
    eol = R.choice([b'\n'] * 6 + [b'\r\n'])
    bom = R.random() < 0.05
    body = eol.join('\t'.join(f).encode('utf-8') for f in lines) + (eol if R.random() < 0.85 else b'')
    with open(os.path.join(d, 'data', 'part_zone.tsv'), 'wb') as fh:
        fh.write((b'\xef\xbb\xbf' if bom else b'') + body)
    zones, bad_nodes, bad_rows, nlines = model(lines)
    # expectations
    expect, cnt = [], Counter()
    seen = Counter((t, i) for (t, i, by, tg, spans, odd, g) in rows)
    for (t, i, by, tg, spans, odd, g) in rows:
        a8, show = r8[(t, i)], v8[(t, i)]
        zr = zone_ok(zones, by, spans)
        recog = show in ('okRecognised', 'okRecognisedUnverifiedBy')
        if recog or (t == 'treatments' and i in RTEXT) or (a8 == 'ok' and g):
            if zr is None:
                cnt['zone_missing_rows'] += 1
            else:
                cnt['zone_checked_rows'] += 1
                if not zr:
                    cnt['zone_failed_rows'] += 1
            exp = 'partZone' if (zr is False and (recog or (a8 == 'ok' and g))) else show
        else:
            exp = show
        if seen[(t, i)] > 1:
            exp = '?'
        case = '%s%s:%s' % (nfl.get(by, 'none'), ('/' + odd) if odd else '', case_of.get((t, i), 'base'))
        what = ('r8ok' if a8 == 'ok' else 'r8fail') + ('' if g else '/nopower')
        expect.append([t, i, case, what + ('/zfail' if zr is False else '/zok' if zr else '/nozone'), exp, tg, by,
                       'notneg' if (t == 'treatments' and case_of.get(('notneg', i))) else '-'])
    cnt['zone_nodes'] = len(zones)
    cnt['zone_lines'] = nlines
    cnt['zone_bad_nodes'] = bad_nodes
    cnt['zone_bad_rows'] = bad_rows
    if fuzz:
        log = m7.mutate(os.path.join(d, 'data', 'part_zone.tsv'), R, fuzz, 5, (0, 1, 2))
        gen.write(os.path.join(d, 'mutations.txt'), log)
        expect = [r[:4] + ['?'] + r[5:] for r in expect]
        cnt = Counter()
    gen.write(os.path.join(d, 'expect.tsv'), expect)
    gen.write(os.path.join(d, 'expect_counts.tsv'), sorted(cnt.items()))
    return len(lines), Counter(nfl.values())


def make(seed, d, n, flavour, fuzz=0):
    shutil.rmtree(d, ignore_errors=True)
    case_of = build_base(seed, d, n, flavour)
    return overlay(d, seed, case_of, fuzz)


# ---------------------------------------------------------------------------------------------------------------
def cmd_check(root, ref):
    """make_r7.py check on the zone expectations, then the round-9 cases (DESIGN9 §5, §7) against the reference
    with part_zone.tsv removed (their expectations are DESIGN9's, independent of the zones)."""
    rc = m7.cmd_check(root, ref)
    tot = bad = 0
    for d in m7.universes(root):
        tmp = tempfile.mkdtemp(prefix='r9c_')
        shutil.copytree(os.path.join(d, 'data'), os.path.join(tmp, 'data'))
        pz = os.path.join(tmp, 'data', 'part_zone.tsv')
        if os.path.exists(pz):
            os.remove(pz)
        for fn in ('expect7.tsv', 'expect8.tsv'):
            shutil.copy(os.path.join(d, fn), os.path.join(tmp, fn))
        v8 = round8_verdicts(tmp)[2]
        t, b, out = check_r9_cases(tmp, v8)
        tot, bad = tot + t, bad + b
        for x in out:
            print(x.replace(os.path.basename(tmp), os.path.basename(d)))
        shutil.rmtree(tmp, ignore_errors=True)
    print('%d round-9 case expectations (DESIGN9 §5, §7), %d differ' % (tot, bad))
    return 1 if (rc or bad) else 0


def cmd_empty(root, ref, pre):
    """Round 9 off: with part_zone.tsv absent / empty / blank and no joinedFar / implicitReject class line, the
    current reference writes what the pre-round-9 copy writes; with zone lines only on unknown nodes, or only bad
    lines, every output file but ref_stats.tsv is the same."""
    bad = 0
    tmp = tempfile.mkdtemp(prefix='r9pre_')
    shutil.copytree(os.path.dirname(pre), os.path.join(tmp, 'ref'))
    shutil.copytree(os.path.join(REF, '..', 'cues'), os.path.join(tmp, 'cues'))
    pre = os.path.join(tmp, 'ref', os.path.basename(pre))
    strip = lambda x: b'\n'.join(l for l in x.split(b'\n') if not l.startswith((b'seconds', b'peak_mb')))
    us = m7.universes(root)
    for d in us:
        outs = []
        modes = ('absent', 'empty', 'blank', 'unknown_only')
        for mode in modes:
            data = os.path.join(d, 'data_' + mode)
            shutil.rmtree(data, ignore_errors=True)
            shutil.copytree(os.path.join(d, 'data'), data)
            pz = os.path.join(data, 'part_zone.tsv')
            if os.path.exists(pz):
                os.remove(pz)
            hp = os.path.join(data, 'history_claim.tsv')        # anchorWide (judge strings, DESIGN9 §8) dropped
            if os.path.exists(hp):
                with open(hp, 'rb') as fh:
                    hl = fh.read().split(b'\n')
                with open(hp, 'wb') as fh:
                    fh.write(b'\n'.join(l for l in hl if b'anchorwide' not in l.lower()))
            kp = os.path.join(data, 'treatment_class.tsv')      # the round-9 claims (DESIGN9 §5, §7) dropped
            if os.path.exists(kp):
                with open(kp, 'rb') as fh:
                    kl = fh.read().split(b'\n')
                with open(kp, 'wb') as fh:
                    fh.write(b'\n'.join(l for l in kl if not (len(l.split(b'\t')) > 1 and l.split(b'\t')[1] in (
                        b'joinedFar', b'implicitReject'))))
            if mode == 'empty':
                open(pz, 'wb').close()
            elif mode == 'blank':
                with open(pz, 'wb') as fh:
                    fh.write(b'\n\r\n\n')
            elif mode == 'unknown_only':
                with open(pz, 'wb') as fh:
                    fh.write(b'99999999\t0\t10\tmajority\tx\n12\tx\t3\tdissent\t\n5\t1\t2\n')
            out = os.path.join(d, 'ref_' + mode)
            m7.run_ref(ref, d, out, data)
            outs.append(out)
        out = os.path.join(d, 'ref_pre')
        m7.run_ref(pre, d, out, os.path.join(d, 'data_absent'))
        outs.append(out)
        for o, mode in zip(outs[1:], modes[1:] + ('pre',)):
            for fn in sorted(set(os.listdir(outs[0])) | set(os.listdir(o))):
                a = open(os.path.join(outs[0], fn), 'rb').read() if os.path.exists(os.path.join(outs[0], fn)) else None
                b = open(os.path.join(o, fn), 'rb').read() if os.path.exists(os.path.join(o, fn)) else None
                if fn == 'ref_stats.tsv' and a is not None and b is not None:
                    a, b = strip(a), strip(b)
                    if mode == 'unknown_only':
                        b = b'\n'.join(l for l in b.split(b'\n') if not l.startswith(b'zone_'))
                if a != b:
                    bad += 1
                    print('%s: %s differs (%s)' % (os.path.basename(d), fn, mode))
        for o in outs:
            shutil.rmtree(o, ignore_errors=True)
        for mode in modes:
            shutil.rmtree(os.path.join(d, 'data_' + mode), ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print('%d universes, %d differing files' % (len(us), bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gen')
    g.add_argument('--seed', type=int, default=90000)
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
            d = os.path.join(a.out, '%s%d' % ({'probe': 'y', 'fuzz': 'x', 'main': 'z'}[fl], s))
            nl, fls = make(s, d, a.n, fl, a.fuzz)
            print('%s: %d zone lines; node flavours %s' % (d, nl, dict(sorted(fls.items()))), flush=True)
    elif a.cmd == 'check':
        sys.exit(cmd_check(a.dir, a.ref))
    elif a.cmd == 'empty':
        sys.exit(cmd_empty(a.dir, a.ref, a.pre))
    else:
        m7.cmd_report(a.dirs)


if __name__ == '__main__':
    main()
