#!/usr/bin/env python3
"""make_r10.py - round-10 universes for the remand bridge (round10/DESIGN10.md §4 + D10-5 + D10-6), for the
differential test of the round-10 Lean runner against the Python reference.

A universe is a round-9 universe (make_r9.py: make_r7 + make_r8 overlays + part_zone.tsv) with a round-10 overlay:
  - new decisions B (decisions2.tsv rows with their own sha) dated relative to the history row's acting order,
    with a window of B's text in cert_text.tsv (+ window_sha.tsv when the universe has one) holding B's quote and a
    docket span; a window added far out in the target's text (offset >= 8,000,000) holding the target's docket span;
  - occasionally a new cite_index.tsv line for an order (a fresh unique citation; only when the file exists);
  - history_remand.tsv: one designed case per chosen history row (court / date / docket / cue / tie, passing and
    failing, check order, duplicates, lines on rows whose round-9 verdict fails or whose acting court has no power),
    plus an unknown-id line and bad lines; CRLF / BOM / no final newline variants.

`expect.tsv` (beside data/, never read by an engine): table, id, case (rm_<case>:<earlier case>), what, the verdict
(reference vocabulary), target, by, '-'. The verdict = the reference's verdict with no history_remand.tsv (the
regressions show that is the round-9 output) with §4 applied by THIS FILE's own model (`model_line`, written from
DESIGN10 §4 / D10-5 / D10-6, not the reference's code). Rows whose id repeats in history.tsv: '?'.
`expect_counts.tsv`: the five remand counters. `cases10.tsv`: per line, the designed reason and the model's.

  python make_r10.py gen    --seed 100000 --rounds 4 --out DIR [--probe] [--fuzz K] [--n 60]
        DIR/r<seed> (main), q<seed> (--probe: round-9 probe base), f<seed> (--fuzz K: K byte-level mutations of
        history_remand.tsv; expectations `?`)
  python make_r10.py check  DIR [--ref PATH]          the reference against expect.tsv / expect_counts.tsv
  python make_r10.py empty  DIR [--ref PATH] [--pre PATH]
        history_remand.tsv absent / empty / blank: the current reference and the round-9 copy write the same bytes;
        only bad / unknown-id lines: every file but ref_stats.tsv the same
  python make_r10.py report DIR...                   attribute each universe's diff.tsv rows to the cases
"""
import argparse
import datetime
import hashlib
import os
import random
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R9 = os.environ.get('MAKE_R9_DIR') or os.path.normpath(os.path.join(HERE, '..', '..', '..', 'round9', 'agents', 'ref9'))
sys.path.insert(0, R9)
import make_r9 as m9  # noqa: E402
m8, m7, gen, rows_of, REF, pr = m9.m8, m9.m7, m9.gen, m9.rows_of, m9.REF, m9.pr

PRE_REF = os.path.normpath(os.path.join(HERE, '..', '..', 'pre', 'ref', 'precedent_ref.py'))
MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December')
ABBR = {1: ['Jan.'], 2: ['Feb.'], 3: ['Mar.'], 4: ['Apr.'], 8: ['Aug.'], 9: ['Sept.', 'Sep.'], 10: ['Oct.'],
        11: ['Nov.'], 12: ['Dec.']}
FAKE_ABBR = {5: 'May.', 6: 'Jun.', 7: 'Jul.', 9: 'Septr.', 1: 'Janv.'}
QMAX, SPANMAX, DAYS = 600, 200, 1826

# designed case -> weight (main); the designed reason is the case's first token after rm_
CASES = [
    ('pass_cite', 6), ('tie_bdocket', 4), ('pass_date', 6), ('pass_abbr', 5), ('pass_lo', 3), ('pass_hi', 3),
    ('pass_span200', 2), ('pass_q600', 2), ('pass_cr', 2), ('pass_upper', 2), ('pass_order', 2), ('pass_uni', 3),
    ('pass_docket_punct', 2), ('pass_existing_b', 1),
    # D10-7 (c2): the reason-case tie through a span of the order's own text
    ('pass_reason', 6), ('pass_reason300', 1), ('pass_reason_upper', 1),
    ('tie_reason_short', 1), ('tie_reason_nolight', 2), ('tie_reason_bonly', 2), ('tie_reason_oonly', 1),
    ('tie_reason_long', 1), ('tie_reason_nowin', 1), ('tie_reason_empty', 1), ('tie_reason_owrong', 1),
    ('court_other', 3), ('court_nonode', 2), ('court_b_is_order', 1),
    ('date_before', 3), ('date_late', 3), ('date_zero', 2), ('date_badcal', 2),
    ('docket_short', 2), ('docket_nodigit', 2), ('docket_notb', 2), ('docket_nott', 2), ('docket_long', 2),
    ('docket_spanempty', 1), ('docket_nowin', 1), ('docket_hash', 2), ('docket_empty', 1), ('docket_tlong', 1),
    ('cue_nocourt', 2), ('cue_nocue', 2), ('cue_long', 2), ('cue_nowin', 1), ('cue_dspace', 1), ('cue_hash', 1),
    ('cue_empty', 1),
    ('tie_none', 3), ('tie_zero', 2), ('tie_fakeabbr', 2), ('tie_otherdate', 2), ('tie_othercite', 2),
    ('multi_court_cue', 1), ('multi_docket_tie', 1), ('multi_date_docket', 1),
]
BAD_KINDS = ['nine', 'eleven', 'thirteen', 'node_x', 'neg', 'off_dec', 'nonutf8', 'empty_num', 'plus', 'fullwidth',
             'o_x']
OSPANMAX, TIEMIN = 300, 8
REASONS = ['Johnson v. United States', 'Welch v. United States', 'Booker', 'United States v. Davis',
           'Montgomery v. Louisiana', 'Mathis v. United States', 'Descamps v. United States', 'Dean v. US']


def wpick(R, table):
    return m9.wpick(R, table)


# --------------------------------------------------------------------------------------------- the model (own)
def compact(s):
    return re.sub(r'[^0-9a-z]', '', s.translate({c: c + 32 for c in range(65, 91)}))


def lower(s):
    return s.translate({c: c + 32 for c in range(65, 91)})


def norm(s):
    return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')


def ordinal(d):
    if d <= 0:
        return None
    try:
        return datetime.date(d // 10000, d // 100 % 100, d % 100).toordinal()
    except ValueError:
        return None


def forms(d):
    o = ordinal(d)
    if o is None:
        return []
    x = datetime.date.fromordinal(o)
    out = ['%s %d, %d' % (MONTHS[x.month - 1].lower(), x.day, x.year)]
    for a in ABBR.get(x.month, ()):
        out.append('%s %d, %d' % (a.lower(), x.day, x.year))
    return out


class World:
    """The universe's tables as this generator reads them (its own loader)."""

    def __init__(self, data):
        self.data = data
        self.dec = {}
        for p in rows_of(os.path.join(data, 'decisions2.tsv')) or []:
            if len(p) == 9 and all(re.match(r'^[0-9]+$', p[c]) for c in (0, 1, 2, 3)):
                self.dec[int(p[0])] = p
        self.wsha = None
        if os.path.exists(os.path.join(data, 'window_sha.tsv')):
            self.wsha = defaultdict(set)
            for p in rows_of(os.path.join(data, 'window_sha.tsv')) or []:
                if len(p) == 5 and p[1].isdigit() and p[2].isdigit():
                    self.wsha[(p[0], int(p[1]), int(p[2]))].add(p[3])
        self.win = defaultdict(list)
        for fn in ('cert_text.tsv', 'holdings_cert_text.tsv'):
            for p in rows_of(os.path.join(data, fn)) or []:
                if len(p) == 4 and p[1].isdigit() and p[2].isdigit():
                    self.win[p[0]].append((int(p[1]), int(p[2]), p[3]))
        self.cite = None
        if os.path.exists(os.path.join(data, 'cite_index.tsv')):
            m = defaultdict(set)
            for p in rows_of(os.path.join(data, 'cite_index.tsv')) or []:
                if len(p) == 2 and p[1].isdigit() and compact(p[0]):
                    m[compact(p[0])].add(int(p[1]))
            self.cite = {k: next(iter(v)) for k, v in m.items() if len(v) == 1}

    def court(self, n):
        return int(self.dec[n][1]) if n in self.dec else None

    def date(self, n):
        return int(self.dec[n][2]) if n in self.dec else None

    def span(self, n, s, e):
        if e <= s or n not in self.dec:
            return None
        sha = self.dec[n][7]
        for (s0, e0, w) in self.win.get(sha, ()):
            if s0 <= s and e <= e0 and len(w) == e0 - s0:
                if self.wsha is not None and hashlib.sha1(w.encode('utf-8')).hexdigest() not in self.wsha.get(
                        (sha, s0, e0), ()):
                    continue
                return norm(w)[s - s0:e - s0]
        return None


def model_line(Wd, by, target, f):
    """DESIGN10 §4 + D10-5 + D10-6 + D10-7 for one good line f = (b, bs, be, docket, ds, de, ts, te, tie, os, oe)."""
    b, bs, be, docket, ds, de, ts, te, tie, os_, oe = f
    if b not in Wd.dec or target not in Wd.dec or Wd.court(b) != Wd.court(target):
        return 'remandCourt'
    if by not in Wd.dec:
        return 'remandDate'
    o, ob, ot = ordinal(Wd.date(by)), ordinal(Wd.date(b)), ordinal(Wd.date(target))
    if o is None or ob is None or ot is None or not (o <= ob <= o + DAYS and ot < o):
        return 'remandDate'
    dk = compact(docket)
    if len(dk) < 4 or not re.search(r'[0-9]', dk) or de - ds > SPANMAX or te - ts > SPANMAX:
        return 'remandDocket'
    sb, st = Wd.span(b, ds, de), Wd.span(target, ts, te)
    if sb is None or st is None or dk not in compact(sb) or dk not in compact(st):
        return 'remandDocket'
    if be - bs > QMAX:
        return 'remandCue'
    q = Wd.span(b, bs, be)
    if q is None:
        return 'remandCue'
    ql = lower(q)
    if 'supreme court' not in ql or not any(c in ql for c in ('vacat', 'remand', 'in light of',
                                                              'further consideration')):
        return 'remandCue'
    cq = compact(ql)
    if Wd.cite is not None and any(k in cq for k, v in Wd.cite.items() if v == by):
        return 'ok'
    if any(x in ql for x in forms(Wd.date(by))):
        return 'ok'
    ck = compact(tie)                      # (c2), D10-7; tie (b) dropped
    if len(ck) >= TIEMIN and ck in cq and 0 < oe - os_ <= OSPANMAX:
        osp = Wd.span(by, os_, oe)
        if osp is not None and 'in light of' in lower(osp) and ck in compact(osp):
            return 'ok'
    return 'remandTie'


# --------------------------------------------------------------------------------------------- the overlay
def sha_of(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def ymd(o):
    x = datetime.date.fromordinal(o)
    return x.year * 10000 + x.month * 100 + x.day


def printed(d, R, abbr=False):
    o = ordinal(d)
    x = datetime.date.fromordinal(o)
    if abbr and ABBR.get(x.month):
        return '%s %d, %d' % (R.choice(ABBR[x.month]), x.day, x.year)
    return '%s %d, %d' % (MONTHS[x.month - 1], x.day, x.year)


def build_case(U, R, case, row):
    """-> (line fields as strings, designed reason, notes). Adds decisions / windows / cite lines to U."""
    rid, by, tg = row['id'], row['by'], row['target']
    Wd = U.world
    dby = Wd.date(by) if by in Wd.dec else 0
    o = ordinal(dby) if dby else None
    if o is None:
        o = datetime.date(2001, 3, 15).toordinal()
    designed = case.split('_')[0]
    designed = {'pass': 'ok', 'court': 'remandCourt', 'date': 'remandDate', 'docket': 'remandDocket',
                'cue': 'remandCue', 'tie': 'remandTie', 'multi': None}[designed]
    # docket token
    yy, nn = R.randint(0, 99), R.randint(1, 9999)
    dtext = R.choice(['%02d-%d' % (yy, nn), 'No. %02d-%d' % (yy, nn), '%d-CV-%04d' % (1990 + yy % 30, nn),
                      'A-%d' % (1000 + nn), '%02d-%d-cr' % (yy, nn)])
    docket = dtext
    if case == 'pass_docket_punct':
        docket = dtext.replace('-', ' - ').upper()
    elif case == 'docket_short':
        docket, dtext = 'a12', 'Docket a12'
    elif case == 'docket_nodigit':
        docket, dtext = 'abcdef', 'No. abcdef'
    elif case == 'docket_empty':
        docket = ''
    # B's court and date
    court = Wd.court(tg) if tg in Wd.dec else 1
    delta = R.randint(1, DAYS - 1)
    if case == 'pass_lo':
        delta = 0
    elif case in ('pass_hi',):
        delta = DAYS
    elif case in ('date_before', 'multi_date_docket'):
        delta = -R.choice([1, 2, 400])
    elif case == 'date_late':
        delta = DAYS + R.choice([1, 2, 300])
    bdate = ymd(o + delta)
    if case == 'date_zero':
        bdate = 0
    elif case == 'date_badcal':
        bdate = (bdate // 10000) * 10000 + R.choice([231, 230, 1332, 1, 1100, 431])
    if case in ('court_other', 'multi_court_cue'):
        others = sorted({int(p[1]) for p in Wd.dec.values()} - {court})
        court = R.choice(others) if others else court + 1
    # the tie
    tie = ''
    keys = [] if Wd.cite is None else [k for k, v in Wd.cite.items() if v == by]
    cite_texts = [p[0] for p in (rows_of(os.path.join(U.data, 'cite_index.tsv')) or [])
                  if len(p) == 2 and p[1] == str(by) and compact(p[0]) in keys]
    if case == 'pass_cite' or (case.startswith('pass') and case not in ('pass_docket', 'pass_date', 'pass_abbr',
                                                                         'pass_docket_punct') and R.random() < 0.3):
        if not cite_texts and Wd.cite is not None and by in Wd.dec:
            ct = '%d U.S. %d' % (900 + R.randint(0, 99), R.randint(1000, 9999))
            U.cite_add.append((ct, by))
            Wd.cite[compact(ct)] = by
            cite_texts = [ct]
        tie = R.choice(cite_texts) if cite_texts else printed(dby, R) if ordinal(dby) else dtext
    elif case in ('tie_bdocket', 'multi_docket_tie'):
        tie = 'No. ' + dtext                 # B's own docket in B's quote: no tie since D10-7
    elif 'reason' in case:
        tie = ''                             # (c2) only: the reason case is put in the quote below
    elif case in ('pass_date', 'pass_lo', 'pass_hi', 'date_before', 'date_late', 'pass_docket_punct'):
        tie = printed(dby, R) if ordinal(dby) else dtext
    elif case == 'pass_abbr':
        tie = printed(dby, R, abbr=True) if ordinal(dby) else dtext
    elif case == 'tie_zero':
        x = datetime.date.fromordinal(o)
        tie = '%s %02d, %d' % (MONTHS[x.month - 1], x.day, x.year) if x.day < 10 else '%s  %d, %d' % (
            MONTHS[x.month - 1], x.day, x.year)
    elif case == 'tie_fakeabbr':
        x = datetime.date.fromordinal(o)
        tie = '%s %d, %d' % (FAKE_ABBR.get(x.month, MONTHS[x.month - 1][:3]), x.day, x.year)
    elif case == 'tie_otherdate':
        tie = printed(ymd(o + R.choice([1, -1, 365])), R)
    elif case == 'tie_othercite':
        other = [p[0] for p in (rows_of(os.path.join(U.data, 'cite_index.tsv')) or []) if len(p) == 2
                 and p[1] != str(by) and Wd.cite and Wd.cite.get(compact(p[0])) not in (None, by)]
        tie = R.choice(other) if other else '%d F.9th %d' % (R.randint(1, 99), R.randint(1, 999))
    elif case in ('tie_none', 'multi_court_cue'):
        tie = ''
    else:
        tie = R.choice([printed(dby, R) if ordinal(dby) else dtext] + cite_texts[:1])
    # B's quote
    sc = 'Supreme Court'
    if case in ('cue_nocourt', 'multi_court_cue'):
        sc = R.choice(['high court', 'Court', 'Supreme Judicial'])
    elif case == 'cue_dspace':
        sc = 'Supreme  Court'
    elif case == 'pass_cr':
        sc = 'Supreme\rCourt'
    cue = R.choice(['vacated our judgment and remanded', 'vacated the judgment', 'remanded the case',
                    'granted certiorari, vacated', 'for further consideration', 'in light of its decision'])
    if case in ('cue_nocue', 'multi_court_cue'):
        cue = R.choice(['denied certiorari', 'affirmed the judgment', 'considered the matter'])
    if case == 'pass_order':
        quote = 'The case was %s by the %s of the United States' % (cue, sc)
    else:
        quote = 'This case is before us again after the %s of the United States %s' % (sc, cue)
    # D10-7 (c2): the reason case
    rs = ''
    if 'reason' in case:
        rs = R.choice([x for x in REASONS if len(compact(x)) >= TIEMIN])
        if case == 'tie_reason_short':
            rs = R.choice([x for x in REASONS if len(compact(x)) < TIEMIN])
    if tie:
        quote += R.choice([' (%s).', ', see %s.', ' on %s.']) % tie
    elif rs and case != 'tie_reason_oonly':
        quote += R.choice([' for further consideration in light of %s.', ', in light of %s.', ' (%s).']) % (
            rs.upper() if case == 'pass_reason_upper' else rs)
    else:
        quote += '.'
    if case == 'pass_upper':
        quote = quote.upper()
    if case == 'pass_q600':
        quote += ' ' + 'x' * (QMAX - len(quote) - 1) if len(quote) < QMAX else ''
        quote = quote[:QMAX]
    elif case == 'cue_long':
        quote += ' ' + 'y' * max(0, QMAX + 1 - len(quote) - 1)
    # B's docket span
    bd = 'Docket No. ' + dtext if case not in ('docket_notb', 'multi_date_docket') else 'Docket No. 9%s' % R.randint(
        100, 999)
    if case == 'docket_long':
        bd = 'D' * (SPANMAX - len(bd) + 1) + bd
    if case == 'pass_span200':
        bd = 'D' * (SPANMAX - len(bd)) + bd
    pre = R.choice(['IN THE COURT OF APPEALS. ', 'Opinion. ', '', 'Cour d\'appel é§ — ']) if case != 'pass_uni' \
        else 'Ünïcödé — «opinion» ½ '
    mid = R.choice([' Background. ', ' ', ' We now consider. '])
    text = pre + quote + mid + bd + ' The end.'
    qs = len(pre)
    qe = qs + len(quote)
    ds = qe + len(mid)
    de = ds + len(bd)
    # B node
    if case == 'pass_existing_b':
        cand = [n for n in Wd.dec if n not in (by, tg) and Wd.court(n) == court and ordinal(Wd.date(n))
                and 0 <= ordinal(Wd.date(n)) - o <= DAYS]
        B = R.choice(sorted(cand)) if cand else None
    else:
        B = None
    if case == 'court_b_is_order':
        B = by
    if B is not None and B in Wd.dec:
        sha = Wd.dec[B][7]
        base = 9_000_000 + 10_000 * len(U.win_add)
    else:
        B = U.next_node
        U.next_node += 1
        sha = sha_of('remandB:%d:%d' % (U.seed, B))
        base = R.choice([0, 0, 120, 5000])
        if case != 'court_nonode':
            U.dec_add.append([str(B), str(court), str(bdate), '0', 'panel', 'published', 'full', sha, 'gen'])
            Wd.dec[B] = U.dec_add[-1]
    s0 = base
    hashbad = case == 'cue_hash'
    U.add_window(sha, s0, text, hashbad)
    bs, be = s0 + qs, s0 + qe
    bds, bde = s0 + ds, s0 + de
    if case == 'cue_hash':
        U.add_window(sha, s0 + 100_000, bd)       # the docket span in a window of its own (good hash)
        bds, bde = s0 + 100_000, s0 + 100_000 + len(bd)
    if case == 'cue_nowin':
        bs, be = s0 + len(text) + 5, s0 + len(text) + 5 + len(quote)
    elif case == 'cue_empty':
        be = bs
    elif case == 'docket_nowin':
        bds, bde = s0 + len(text) - 3, s0 + len(text) + 10
    elif case == 'docket_spanempty':
        bde = bds
    # the target's docket span (a far window of the target's own text)
    ttext = R.choice(['Docket number ', 'No. ', 'Case ', 'Appeal from ']) + (
        dtext if case not in ('docket_nott',) else '7%d-%d' % (R.randint(10, 99), R.randint(10, 99))) + \
        R.choice(['', ' (argued)', '. Filed.'])
    if case == 'docket_tlong':
        ttext = 'T' * (SPANMAX + 1 - len(ttext)) + ttext
    ts = te = 0
    if tg in Wd.dec:
        tsha = Wd.dec[tg][7]
        t0 = 8_000_000 + 10_000 * len(U.win_add)
        lead = R.choice(['', 'Page header. '])
        U.add_window(tsha, t0, lead + ttext + ' Rest.', case == 'docket_hash')
        ts, te = t0 + len(lead), t0 + len(lead) + len(ttext)
    # D10-7: the order span (a far window of the order's own text) and the tie field
    tie_f, os_, oe = '', 0, 0
    if rs and by in Wd.dec:
        other = R.choice([x for x in REASONS if x != rs and len(compact(x)) >= TIEMIN])
        if case == 'tie_reason_nolight':
            ospan = 'Judgment vacated, and case remanded for further consideration. See %s.' % rs
        elif case == 'tie_reason_bonly':
            ospan = 'Judgment vacated, and case remanded for further consideration in light of %s.' % other
        else:
            ospan = R.choice(['Judgment vacated, and case remanded to the Court of Appeals for further consideration '
                              'in light of %s.', 'In light of %s, judgment vacated.',
                              'Certiorari granted, judgment vacated, remanded in light of %s (2015).']) % (
                rs if case != 'pass_reason_upper' else rs.lower())
        if case == 'tie_reason_long':
            ospan = 'O' * (OSPANMAX + 1 - len(ospan)) + ospan
        elif case == 'pass_reason300':
            ospan = 'O' * (OSPANMAX - len(ospan)) + ospan
        lead = R.choice(['', 'Order list. ', 'Nos. 14-1, 14-2. '])
        o0 = 7_000_000 + 10_000 * len(U.win_add)
        osha = Wd.dec[by][7]
        if case == 'tie_reason_owrong' and tg in Wd.dec:
            osha = Wd.dec[tg][7]              # the span is in the target's text, not the order's
        U.add_window(osha, o0, lead + ospan + ' Other orders.')
        os_, oe = o0 + len(lead), o0 + len(lead) + len(ospan)
        if case == 'tie_reason_nowin':
            os_, oe = o0 + len(lead) + len(ospan) + 30, o0 + len(lead) + len(ospan) + 60
        tie_f = R.choice([rs, rs + ',', ' ' + rs]) if case != 'tie_reason_empty' else ''
        if case == 'tie_reason_empty':
            os_ = oe = 0
    f = [rid, str(B), str(bs), str(be), docket, str(bds), str(bde), str(ts), str(te), tie_f, str(os_), str(oe)]
    return f, designed


class U10:
    def __init__(self, d, seed):
        self.d, self.seed, self.data = d, seed, os.path.join(d, 'data')
        self.world = World(self.data)
        self.next_node = max(self.world.dec) + 1 if self.world.dec else 0
        self.dec_add, self.win_add, self.cite_add = [], [], []

    def add_window(self, sha, s0, text, hashbad=False):
        self.win_add.append((sha, s0, s0 + len(text), text, hashbad))
        if not hashbad or self.world.wsha is None:
            self.world.win[sha].append((s0, s0 + len(text), text))
            if self.world.wsha is not None:
                self.world.wsha[(sha, s0, s0 + len(text))].add(sha_of(text))
        else:
            self.world.win[sha].append((s0, s0 + len(text), text))
            self.world.wsha[(sha, s0, s0 + len(text))].add('0' * 40)

    def flush(self):
        J = lambda n: os.path.join(self.data, n)
        for fn in ('decisions2.tsv', 'cert_text.tsv', 'window_sha.tsv', 'cite_index.tsv'):
            if os.path.exists(J(fn)) and os.path.getsize(J(fn)):
                with open(J(fn), 'rb') as fh:
                    fh.seek(-1, 2)
                    last = fh.read(1)
                if last != b'\n':
                    with open(J(fn), 'ab') as fh:
                        fh.write(b'\n')
        with open(J('decisions2.tsv'), 'ab') as fh:
            for p in self.dec_add:
                fh.write(('\t'.join(p) + '\n').encode('utf-8'))
        with open(J('cert_text.tsv'), 'ab') as fh:
            for (sha, s0, e0, text, hb) in self.win_add:
                fh.write(('%s\t%d\t%d\t%s\n' % (sha, s0, e0, text)).encode('utf-8'))
        if self.world.wsha is not None:
            with open(J('window_sha.tsv'), 'ab') as fh:
                for (sha, s0, e0, text, hb) in self.win_add:
                    fh.write(('%s\t%d\t%d\t%s\tgen\n' % (sha, s0, e0, '0' * 40 if hb else sha_of(text))).encode())
        if self.cite_add and os.path.exists(J('cite_index.tsv')):
            with open(J('cite_index.tsv'), 'ab') as fh:
                for (ct, n) in self.cite_add:
                    fh.write(('%s\t%d\n' % (ct, n)).encode('utf-8'))


def bad_line(R, rid):
    k = R.choice(BAD_KINDS)
    f = [rid, '5', '0', '10', '12-345', '0', '5', '0', '5', 'Johnson v. United States', '0', '20']
    if k == 'nine':
        return '\t'.join(f[:9]).encode()           # the D10-5 format: bad since D10-7
    if k == 'eleven':
        return '\t'.join(f[:11]).encode()
    if k == 'thirteen':
        return '\t'.join(f + ['x']).encode()
    if k == 'node_x':
        f[1] = 'x5'
    elif k == 'neg':
        f[R.choice([2, 5, 7, 10])] = '-3'
    elif k == 'off_dec':
        f[3] = '10.0'
    elif k == 'empty_num':
        f[R.choice([1, 2, 3, 5, 6, 7, 8, 10, 11])] = ''
    elif k == 'plus':
        f[6] = '+5'
    elif k == 'fullwidth':
        f[8] = '５'
    elif k == 'o_x':
        f[11] = '2O'
    elif k == 'nonutf8':
        return '\t'.join(f).encode() + b'\xff\xfe'
    return '\t'.join(f).encode('utf-8')


# ------------------------------------------------------------------ DESIGN10 §6 trialBridge (D10-8, D10-9)
TB_CASES = [('tb_pass', 'ok'), ('tb_pass_vac', 'ok'), ('tb_hi', 'ok'), ('tb_t_upper', 'ok'), ('tb_pass2', 'ok'),
            ('tb_d_notrial', 'trialBridgeD'), ('tb_d_inter', 'trialBridgeD'), ('tb_d_dca', 'trialBridgeD'),
            ('tb_d_nocue', 'trialBridgeD'), ('tb_d_coa', 'trialBridgeD'),
            ('tb_t_reverse', 'trialBridgeT'), ('tb_t_remand', 'trialBridgeT'), ('tb_t_noaffirm', 'trialBridgeT'),
            ('tb_t_long', 'trialBridgeT'), ('tb_t_noline', 'trialBridgeT'), ('tb_t_nowin', 'trialBridgeT'),
            ('tb_t_hash', 'trialBridgeT'), ('tb_t_dupfirstbad', 'trialBridgeT'), ('tb_t_vacate', 'trialBridgeT'),
            ('tb_date_after', 'trialBridgeDate'), ('tb_date_late', 'trialBridgeDate'),
            ('tb_date_same', 'trialBridgeDate'), ('tb_date_zero', 'trialBridgeDate'),
            ('tb_kind_other', None), ('tb_noanchor', None), ('tb_noclaim', None), ('tb_bridge', None),
            ('tb_anchor_nocue', 'anchorNoCue'), ('tb_d_t_order', 'trialBridgeD')]
TRIALS = ['trial court', 'District Court', 'circuit court', 'Superior Court', 'county court', 'Court of Common Pleas',
          'chancery court', 'Probate Court', 'court below']
INTERS = ['court of appeal', 'appellate', 'court of special appeals', 'court of civil appeals',
          'court of criminal appeals', 'commonwealth court', 'district court of appeal']
TB_CUES = {'reversed': ('revers', "rev'd"), 'vacated': ('vacat',)}
TB_NEG = ('reversed', 'reverse', 'vacate', 'set aside', 'remand')


def model_tb(Wd, mq, kind, tl, T, Dn):
    """DESIGN10 §6 + D10-9 (Q10-14..16), this file's own model: trialBridgeD, then T, then Date."""
    ql = lower(norm(mq))
    if (not any(c in ql for c in TB_CUES.get(kind, ())) or not any(n.lower() in ql for n in TRIALS)
            or any(n in ql for n in INTERS)):
        return 'trialBridgeD'
    if tl is None or tl[1] - tl[0] > 600:
        return 'trialBridgeT'
    q = Wd.span(T, tl[0], tl[1])
    if q is None:
        return 'trialBridgeT'
    q = lower(q)
    if 'affirm' not in q or any(x in q for x in TB_NEG):
        return 'trialBridgeT'
    if Dn not in Wd.dec or T not in Wd.dec:
        return 'trialBridgeDate'
    a, b = ordinal(Wd.date(T)), ordinal(Wd.date(Dn))
    if a is None or b is None or not (a < b <= a + DAYS) or Wd.court(T) == Wd.court(Dn):
        return 'trialBridgeDate'
    return 'ok'


def tb_overlay(U, R, D0, A0, n_cases):
    """New decision pairs (T an intermediate decision, D a higher court of the same system dated after it) and a
    history row per case, with anchor / claim / tbridge lines. -> (rows, tb lines, design {id: (case, designed)})"""
    Wd = U.world
    tmpl = []
    for r in D0.history:
        b, t = r['by'], r['target']
        if (b in Wd.dec and t in Wd.dec and Wd.court(b) != Wd.court(t) and ordinal(Wd.date(t))
                and A0.same_case_power(b, t) == 'yes'):
            tmpl.append((b, t))
    if not tmpl:
        ns = sorted(Wd.dec)
        tmpl = [(ns[-1], ns[0])]
    hist, anch, claims, tbl, design, bridges = [], [], [], [], {}, []
    cases = list(TB_CASES)
    R.shuffle(cases)
    for k, (case, designed) in enumerate(cases[:n_cases]):
        bt, tt = R.choice(tmpl)
        rid = 'tb%d_%d' % (U.seed, k)
        kind = 'vacated' if case in ('tb_pass_vac',) else ('affirmed' if case == 'tb_kind_other' else
                                                           R.choice(['reversed', 'reversed', 'vacated']))
        dt = Wd.date(tt) if ordinal(Wd.date(tt)) else 20000101
        ot = ordinal(dt)
        delta = R.randint(1, DAYS - 1)
        if case == 'tb_hi':
            delta = DAYS
        elif case == 'tb_date_after':
            delta = -R.choice([1, 30])
        elif case == 'tb_date_late':
            delta = DAYS + 1
        dd = ymd(ot + delta)
        if case == 'tb_date_zero':
            dd = 0
        T, Dn = U.next_node, U.next_node + 1
        U.next_node += 2
        tsha, dsha = sha_of('tbT:%d:%d' % (U.seed, T)), sha_of('tbD:%d:%d' % (U.seed, Dn))
        trow = list(Wd.dec[tt])
        trow[0], trow[2], trow[7] = str(T), str(dt), tsha
        drow = list(Wd.dec[bt])
        drow[0], drow[2], drow[7] = str(Dn), str(dd), dsha
        if case == 'tb_date_same':
            drow[1] = trow[1]
        U.dec_add += [trow, drow]
        Wd.dec[T], Wd.dec[Dn] = trow, drow
        # T's citation (indexed to T when the universe has a citation index)
        tcite = '%d Rep.%s %d' % (R.randint(100, 999), R.choice(['', '2d', '3d']), R.randint(1, 1999))
        if Wd.cite is not None:
            U.cite_add.append((tcite, T))
            Wd.cite[compact(tcite)] = T
        tname = R.choice(['Smith v. Jones', 'State v. Miller', 'In re Estate of Parker', 'Doe v. Roe Corp.'])
        # T's text: its affirmance line
        tq = R.choice(['The judgment of the trial court is affirmed.', 'AFFIRMED.', 'We affirm.',
                       'Judgment affirmed.'])
        if case == 'tb_t_reverse':
            tq = 'Affirmed in part and reversed in part.'
        elif case == 'tb_t_remand':
            tq = 'Affirmed and remanded for resentencing.'
        elif case == 'tb_t_vacate':
            tq = 'The sentence is vacated; the conviction is affirmed.'
        elif case == 'tb_t_noaffirm':
            tq = 'The appeal is dismissed.'
        elif case == 'tb_t_upper':
            tq = 'JUDGMENT AFFIRMED.'
        elif case == 'tb_t_long':
            tq = 'x' * (600 + 1 - len('We affirm.')) + 'We affirm.'
        tpre = R.choice(['', 'Opinion. ', 'Ünïcödé opinion — '])
        U.add_window(tsha, 0, tpre + tq + ' End of opinion.', case == 'tb_t_hash')
        tl = (len(tpre), len(tpre) + len(tq))
        if case == 'tb_t_nowin':
            tl = (len(tpre) + 200, len(tpre) + 220)
        # D's text: the anchor quote and the judgment line
        trial = R.choice(TRIALS)
        verb = {'reversed': 'reversed', 'vacated': 'vacated', 'affirmed': 'affirmed'}[kind]
        mq = R.choice(['The judgment of the %s is %s.', 'Judgment of the %s %s.']) % (trial, verb)
        if case == 'tb_d_notrial':
            mq = 'The judgment is %s.' % verb
        elif case == 'tb_d_inter':
            mq = 'The decision of the %s is %s and the judgment of the %s is reinstated.' % (
                R.choice(['Court of Appeals', 'Appellate Division', 'Court of Civil Appeals']), verb, trial)
        elif case == 'tb_d_coa':
            mq = 'The judgment of the court of appeal is %s.' % verb
        elif case == 'tb_d_dca':
            mq = 'The decision of the District Court of Appeal is %s.' % verb
        elif case == 'tb_d_nocue':
            mq = 'The judgment of the %s is modified.' % trial
        elif case == 'tb_d_t_order':                   # D fails and T fails: D is the reason (check order)
            mq = 'The judgment is %s.' % verb
            tl = None
        aq = R.choice(['On review of the decision of the Court of Appeals in %s, %s.',
                       'Certiorari to the court of appeals: %s, %s.']) % (tname, tcite)
        if case == 'tb_anchor_nocue':
            aq = 'We now turn to %s, %s.' % (tname, tcite)
        dpre = R.choice(['', 'SUPREME COURT. ', 'Opinion of the Court. '])
        mid = R.choice([' ', ' Facts omitted. '])
        dtext = dpre + aq + mid + mq + ' It is so ordered.'
        a0 = len(dpre)
        m0 = a0 + len(aq) + len(mid)
        U.add_window(dsha, 0, dtext)
        hist.append([rid, str(T), str(Dn), str(dd), kind, 'all', dsha, str(m0), str(m0 + len(mq)), mq,
                     'cite:' + tcite, 'majority', 'gen'])
        if case != 'tb_noanchor':
            anch.append([rid, str(a0), str(a0 + len(aq)), aq, 'majority', 'gen'])
        if case != 'tb_noclaim':
            claims.append([rid, 'trialBridge', 'gen'])
        if case == 'tb_bridge':
            bridges.append([rid, str(Dn), '0', '10', dtext[:10], 'gen'])
        if case == 'tb_t_dupfirstbad':
            tbl.append(('good', [rid, str(tl[0] + 200), str(tl[1] + 220)]))
            tbl.append(('dup', [rid, str(tl[0]), str(tl[1])]))
        elif tl is not None and case != 'tb_t_noline':
            tbl.append(('good', [rid, str(tl[0]), str(tl[1])]))
        design[rid] = (case, designed, mq, kind, T, Dn)
    return hist, anch, claims, tbl, design, bridges


def append_rows(path, rows):
    data = b''
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            data = fh.read()
    with open(path, 'ab') as fh:
        if data and not data.endswith(b'\n'):
            fh.write(b'\n')
        for r in rows:
            fh.write(('\t'.join(r) + '\n').encode('utf-8'))


def tb_bad_line(R, rid):
    k = R.choice(['two', 'four', 'x', 'neg', 'nonutf8', 'empty'])
    f = [rid, '0', '10']
    if k == 'two':
        return '\t'.join(f[:2]).encode()
    if k == 'four':
        return '\t'.join(f + ['x']).encode()
    if k == 'x':
        f[1] = '1x'
    elif k == 'neg':
        f[2] = '-10'
    elif k == 'empty':
        f[2] = ''
    elif k == 'nonutf8':
        return '\t'.join(f).encode() + b'\xc3'
    return '\t'.join(f).encode('utf-8')


def round9_verdicts(d):
    """The reference with no history_remand.tsv and no trialBridge claim: (Data, verdict per (table, id) as
    certs.tsv shows it, the certificate verdict, power gate per history id, the engine)."""
    pr.BAD_ROWS.clear()
    D = pr.Data(os.path.join(d, 'data'))
    assert not D.remand_any and not any('trialBridge' in c for c in D.hclaim.values())
    A = pr.Engine(D)
    A.admit()
    show = {(f.replace('.tsv', ''), i): A.cert_verdict(f, i) for (f, i) in A.cert_ok}
    cert = {(f.replace('.tsv', ''), i): v for (f, i), v in A.cert_ok.items()}
    gate = {r['id']: A.same_case_power(r['by'], r['target'], D.hclaim.get(r['id'])) != 'no' for r in D.history}
    return D, show, cert, gate, A


def drop_claim_lines(path):
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            ls = fh.read().split(b'\n')
        with open(path, 'wb') as fh:
            fh.write(b'\n'.join(l for l in ls if b'\ttrialBridge\t' not in l and not l.endswith(b'\ttrialBridge')))


def overlay(d, seed, case_of, flavour, fuzz=0):
    R = random.Random(seed * 1000003 + 10010)
    D0, show0, cert0, gate0, A0 = round9_verdicts(d)
    hist = D0.history
    seen = Counter(r['id'] for r in hist)
    U = U10(d, seed)
    # rows: mostly round-9 ok with power; some failing verdicts, some without power
    okp = [r for r in hist if cert0[('history', r['id'])] == 'ok' and gate0[r['id']] and seen[r['id']] == 1]
    nop = [r for r in hist if cert0[('history', r['id'])] == 'ok' and not gate0[r['id']] and seen[r['id']] == 1]
    bad = [r for r in hist if cert0[('history', r['id'])] != 'ok' and seen[r['id']] == 1]
    dupid = [r for r in hist if seen[r['id']] > 1]
    R.shuffle(okp)
    R.shuffle(nop)
    R.shuffle(bad)
    plan = []
    n_ok = min(len(okp), 40 if flavour != 'probe' else 56)
    names = [c for c, _ in CASES]
    R.shuffle(names)
    for i, r in enumerate(okp[:n_ok]):
        plan.append((r, names[i % len(names)] if (flavour == 'probe' or i < len(names) // 2) else wpick(R, CASES)))
    for r in nop[:5]:
        plan.append((r, R.choice(['pass_date', 'tie_none', 'court_other', 'cue_nocue', 'pass_reason'])))
    for r in bad[:5]:
        plan.append((r, R.choice(['pass_date', 'date_before', 'pass_cite', 'tie_reason_bonly'])))
    for r in dupid[:1]:
        plan.append((r, R.choice(['pass_date', 'tie_none'])))
    lines, design = [], {}
    for (r, case) in plan:
        f, designed = build_case(U, R, case, r)
        lines.append(('good', f, case))
        design[r['id']] = (case, designed)
    # duplicates: a second line for two planned ids (first wins)
    dup_n = 0
    for (r, case) in plan[:2]:
        f2, _ = build_case(U, R, 'tie_none' if case.startswith('pass') else 'pass_date', r)
        lines.append(('dup', f2, 'dup'))
        dup_n += 1
    # an unknown id, bad lines
    lines.append(('unknown', ['h_no_such_row_%d' % seed, '1', '0', '10', '12-345', '0', '5', '0', '5', '', '0', '0'],
                  'unknown'))
    nbad = R.randint(1, 4)
    for _ in range(nbad):
        lines.append(('bad', bad_line(R, R.choice(plan)[0]['id'] if plan else 'x'), 'bad'))
    # §6 trialBridge rows (new decisions T, D and history rows with anchor / claim / tbridge lines)
    ntb = len(TB_CASES) if flavour == 'probe' else R.randint(12, 20)
    tb_hist, tb_anch, tb_claims, tb_lines, tb_design, tb_bridges = tb_overlay(U, R, D0, A0, ntb)
    U.flush()
    J = lambda n: os.path.join(d, 'data', n)
    append_rows(J('history.tsv'), tb_hist)
    append_rows(J('history_anchor.tsv'), tb_anch)
    append_rows(J('history_claim.tsv'), tb_claims)
    if tb_bridges:
        append_rows(J('history_bridge.tsv'), tb_bridges)
    # history_tbridge.tsv: the tb lines, a line for an ordinary row (no claim: unused), an unknown id, bad lines
    tbo = [x for x in tb_lines]
    if okp:
        tbo.append(('good', [R.choice(okp)['id'], '0', '5']))
    tbo.append(('unknown', ['tb_no_such_row_%d' % seed, '0', '5']))
    ntbad = R.randint(0, 3)
    for _ in range(ntbad):
        tbo.append(('bad', tb_bad_line(R, R.choice(list(tb_design) or ['x']))))
    firsts_t = [x for x in tbo if x[0] != 'dup']
    R.shuffle(firsts_t)
    outt = list(firsts_t)
    for x in [x for x in tbo if x[0] == 'dup']:
        pos = max(i for i, y in enumerate(outt) if y[0] == 'good' and y[1][0] == x[1][0])
        outt.insert(R.randint(pos + 1, len(outt)), x)
    enct = [x[1] if isinstance(x[1], bytes) else '\t'.join(x[1]).encode('utf-8') for x in outt]
    with open(J('history_tbridge.tsv'), 'wb') as fh:
        fh.write(b'\n'.join(enct) + (b'\n' if R.random() < 0.9 else b''))
    # history_remand.tsv: order shuffled, but every dup after its first line
    firsts = [x for x in lines if x[0] != 'dup']
    R.shuffle(firsts)
    out = list(firsts)
    for x in [x for x in lines if x[0] == 'dup']:
        pos = max(i for i, y in enumerate(out) if y[0] == 'good' and y[1][0] == x[1][0])
        out.insert(R.randint(pos + 1, len(out)), x)
    enc = [x[1] if isinstance(x[1], bytes) else '\t'.join(x[1]).encode('utf-8') for x in out]
    eol = R.choice([b'\n'] * 6 + [b'\r\n'])
    bom = R.random() < 0.05
    body = eol.join(enc) + (eol if R.random() < 0.85 else b'')
    with open(J('history_remand.tsv'), 'wb') as fh:
        fh.write((b'\xef\xbb\xbf' if bom else b'') + body)
    # expectations: round-9 verdicts on the overlaid data (no remand table, no trialBridge claim, no tbridge table)
    tmp = d + '_r9tmp'
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(os.path.join(d, 'data'), os.path.join(tmp, 'data'))
    os.remove(os.path.join(tmp, 'data', 'history_remand.tsv'))
    os.remove(os.path.join(tmp, 'data', 'history_tbridge.tsv'))
    drop_claim_lines(os.path.join(tmp, 'data', 'history_claim.tsv'))
    D1, show1, cert1, gate1, _ = round9_verdicts(tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    moved = [k for k in show0 if k in show1 and show0[k] != show1[k]]
    Wd = World(os.path.join(d, 'data'))
    rows_by_id = defaultdict(list)
    for r in D1.history:
        rows_by_id[r['id']].append(r)
    first = {}
    for kind, f, case in out:
        if kind == 'good' and f[0] not in first:
            first[f[0]] = f
    hids = set(rows_by_id)
    tfirst = {}
    for kind, f in outt:
        if kind != 'bad' and f[0] in hids and f[0] not in tfirst:
            tfirst[f[0]] = (int(f[1]), int(f[2]))
    cnt = Counter()
    cnt['remand_dup_rows'] = dup_n
    cnt['remand_bad_rows'] = nbad
    cnt['remand_lines'] = len(first)
    cnt['tbridge_lines'] = len(tfirst)
    cnt['tbridge_dup_rows'] = sum(1 for x in outt if x[0] == 'dup')
    cnt['tbridge_bad_rows'] = ntbad
    expect, cases = [], []
    for (t, i), v in sorted(show1.items()):
        rr = rows_by_id.get(i, []) if t == 'history' else []
        exp, what = v, 'noline'
        if t == 'history' and i in first:
            f = first[i]
            fl = (int(f[1]), int(f[2]), int(f[3]), f[4], int(f[5]), int(f[6]), int(f[7]), int(f[8]), f[9],
                  int(f[10]), int(f[11]))
            res = []
            for r in rr:
                m = model_line(Wd, r['by'], r['target'], fl)
                c9 = cert1[('history', i)]
                if c9 == 'ok' and gate1[i]:
                    cnt['remand_checked_rows'] += 1
                    if m != 'ok':
                        cnt['remand_failed_rows'] += 1
                        res.append(m)
                    else:
                        res.append(v)
                    what = 'checked/' + m
                else:
                    res.append(v)
                    what = ('nopower/' if c9 == 'ok' else 'r9fail/') + m
                case, designed = design.get(i, ('?', None))
                ob, ot = ordinal(Wd.date(r['by']) or 0), ordinal(Wd.date(r['target']) or 0)
                why = 'rowdates' if (m == 'remandDate' and not (ob and ot and ot < ob)) else '-'
                if case in ('docket_hash', 'cue_hash') and Wd.wsha is None:
                    why = 'rowdates'      # (no window_sha.tsv in this universe: no hash test; explained)
                cases.append([i, case, designed or '-', m, what, why])
            exp = res[0] if len(set(res)) == 1 else '?'
        elif t == 'history' and i in tb_design:
            case, designed, mq, kind, T, Dn = tb_design[i]
            c9 = cert1[('history', i)]
            if case in ('tb_kind_other', 'tb_noanchor', 'tb_noclaim', 'tb_bridge'):
                m, what = c9, 'tb_ignored/' + c9
            elif c9 in ('ok', 'noVerb', 'targetLater'):
                m = model_tb(Wd, mq, kind, tfirst.get(i), T, Dn)
                exp = m if m != 'ok' else v
                what = 'tb_checked/' + m
            else:
                m, what = c9, 'tb_r9fail/' + c9
            why = 'rowdates' if (case == 'tb_t_hash' and Wd.wsha is None) else '-'
            cases.append([i, case, designed or '-', m if m != 'ok' else 'ok', what, why])
        if t == 'history' and len(rr) > 1:
            exp = '?'
        dc = design.get(i, tb_design.get(i, ('none',)))[0] if t == 'history' else 'none'
        case = 'rm_%s:%s' % (dc, case_of.get((t, i), 'base'))
        tg = rr[0]['target'] if rr else '-'
        by = rr[0]['by'] if rr else '-'
        expect.append([t, i, case, what, exp, tg, by, '-'])
    if fuzz:
        log = m7.mutate(J('history_remand.tsv'), R, fuzz, 12, (1, 2, 3, 5, 6, 7, 8, 10, 11))
        log += m7.mutate(J('history_tbridge.tsv'), R, max(1, fuzz // 2), 3, (1, 2))
        gen.write(os.path.join(d, 'mutations.txt'), log)
        expect = [r[:4] + ['?'] + r[5:] for r in expect]
        cnt = Counter()
    gen.write(os.path.join(d, 'expect.tsv'), expect)
    gen.write(os.path.join(d, 'expect_counts.tsv'), sorted(cnt.items()))
    gen.write(os.path.join(d, 'cases10.tsv'), cases)
    gen.write(os.path.join(d, 'moved10.tsv'), [[k[0], k[1], show0[k], show1.get(k)] for k in moved])
    return len(out), Counter(x[2] for x in out), moved, cases


def make(seed, d, n, flavour, fuzz=0):
    shutil.rmtree(d, ignore_errors=True)
    case_of = m9.build_base(seed, d, n, 'probe' if flavour == 'probe' else 'main')
    m9.overlay(d, seed, case_of, 0)              # part_zone.tsv (its expect.tsv is replaced below)
    for fn in ('expect.tsv', 'expect_counts.tsv'):
        if os.path.exists(os.path.join(d, fn)):
            os.replace(os.path.join(d, fn), os.path.join(d, fn.replace('.tsv', '9.tsv')))
    return overlay(d, seed, case_of, flavour, fuzz)


# ---------------------------------------------------------------------------------------------------------------
def cmd_check(root, ref):
    """make_r7.py check on the round-10 expectations (certs verdicts + the five counters)."""
    rc = m7.cmd_check(root, ref)
    dis = expl = 0
    for d in m7.universes(root):
        for r in rows_of(os.path.join(d, 'cases10.tsv')) or []:
            if r[2] != '-' and r[2] != r[3]:
                if r[4].startswith(('nopower', 'r9fail')) or (len(r) > 5 and r[5] == 'rowdates'):
                    expl += 1
                else:
                    dis += 1
                    print('%s: %s case %s designed %s model %s' % (os.path.basename(d), r[0], r[1], r[2], r[3]))
        mv = rows_of(os.path.join(d, 'moved10.tsv')) or []
        if mv:
            print('%s: %d rows whose round-9 verdict moved with the overlay data' % (os.path.basename(d), len(mv)))
    print('designed reason != model, explained by the row (its own dates / round-9 verdict / power): %d' % expl)
    print('designed reason != model, unexplained: %d' % dis)
    return rc or (1 if dis else 0)


def cmd_empty(root, ref, pre):
    """Round 10 off: history_remand.tsv absent / empty / blank -> the current reference writes what the round-9
    copy writes; only bad lines and unknown-id lines -> every file but ref_stats.tsv the same."""
    bad = 0
    tmp = tempfile.mkdtemp(prefix='r10pre_')
    shutil.copytree(os.path.dirname(pre), os.path.join(tmp, 'ref'), ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(os.path.join(REF, '..', 'cues'), os.path.join(tmp, 'cues'))
    pre = os.path.join(tmp, 'ref', os.path.basename(pre))
    strip = lambda x: b'\n'.join(l for l in x.split(b'\n') if not l.startswith((b'seconds', b'peak_mb')))
    us = m7.universes(root)
    for d in us:
        outs = []
        modes = ('absent', 'empty', 'blank', 'bad_only')
        for mode in modes:
            data = os.path.join(d, 'data_' + mode)
            shutil.rmtree(data, ignore_errors=True)
            shutil.copytree(os.path.join(d, 'data'), data)
            pz = os.path.join(data, 'history_remand.tsv')
            pt = os.path.join(data, 'history_tbridge.tsv')
            for x in (pz, pt):
                if os.path.exists(x):
                    os.remove(x)
            drop_claim_lines(os.path.join(data, 'history_claim.tsv'))     # §6: no trialBridge claim
            if mode == 'empty':
                open(pz, 'wb').close()
                open(pt, 'wb').close()
            elif mode == 'blank':
                with open(pz, 'wb') as fh:
                    fh.write(b'\n\r\n\n')
                with open(pt, 'wb') as fh:
                    fh.write(b'\r\n\n')
            elif mode == 'bad_only':
                with open(pz, 'wb') as fh:
                    fh.write(b'nosuchid\t1\t0\t10\t12-345\t0\t5\t0\t5\t\t0\t0\nx\t1\t2\n'
                             b'y\tz\t0\t1\t1234\t0\t1\t0\t1\t\t0\t0\n')
                with open(pt, 'wb') as fh:
                    fh.write(b'nosuchid\t0\t5\nx\t1\n')
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
                    if mode == 'bad_only':
                        b = b'\n'.join(l for l in b.split(b'\n') if not l.startswith((b'remand_', b'tbridge_')))
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
    g.add_argument('--seed', type=int, default=100000)
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
            d = os.path.join(a.out, '%s%d' % ({'probe': 'q', 'fuzz': 'f', 'main': 'r'}[fl], s))
            nl, kinds, moved, cases = make(s, d, a.n, fl, a.fuzz)
            res = Counter(c[3] for c in cases)
            print('%s: %d remand lines; model results %s; round-9 verdicts moved by the overlay data: %d' % (
                d, nl, dict(sorted(res.items())), len(moved)), flush=True)
    elif a.cmd == 'check':
        sys.exit(cmd_check(a.dir, a.ref))
    elif a.cmd == 'empty':
        sys.exit(cmd_empty(a.dir, a.ref, a.pre))
    else:
        m7.cmd_report(a.dirs)


if __name__ == '__main__':
    main()
