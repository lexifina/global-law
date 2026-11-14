#!/usr/bin/env python3
"""make_r11.py - round-11 universes for the history claim `anchorTribunal` (round11/DESIGN11.md §5.1, D11-4), for
the differential test of the round-11 Lean runner against the Python reference.

A universe is a round-10 universe (round10/agents/ref10/make_r10.py, unchanged) with a round-11 overlay:
  - per designed case a new decision pair (T = the decision under review, D = the acting decision; courts copied
    from a history pair of the universe with same-case power, or without power for `nopower`), a history row
    (D acts on T), D's text window (the anchor quote naming the tribunal + the disposition quote), an anchor line,
    claim lines (`anchorTribunal`, alone or with `anchorWide` / `trialBridge` / `setAside`, or none);
  - per such row a TWIN row (same D, T, kind, disposition quote; no `anchorTribunal` claim, the other claims kept)
    whose anchor quote (a far window of D's own text) has `district court` where the claimed row names the tribunal;
  - `anchorTribunal` claims on a few rows of the base universe; an unknown-id claim line, a duplicate, bad lines
    (wrong case, 2 / 4 fields, non-UTF-8, a near-miss value);
  - §5.2 (D11-5): history_identity.tsv lines on base rows (designed docket / cite / date cases, passing and failing;
    lines on noAuthority rows, on rows whose round-10 verdict fails, on a repeated id; dup / unknown / bad lines),
    the spans in far windows of D's and T's own text. Model: `model_identity` (own); a row is checked when its
    expected round-10 verdict is ok and same-case power is not `no` (round-10 reference's power function).

Expectations (`expect.tsv`; never read by an engine): the verdict of every certs.tsv row. The base is the ROUND-10
FINAL reference (round11/pre/ref, run as a separate program) on a copy of the data without any `anchorTribunal`
line (`r10`). THIS FILE's own model of §5.1 (`model_cue`, written from DESIGN11 §5.1, not from the reference's code)
then decides each claimed row: anchor line, no bridge line, r10 = anchorNoCue and a cue of the union in the anchor
quote -> the verdict of its twin (r10, the same remaining checks); otherwise r10. Claimed base rows with no twin:
'?' when the model says the claim moves them. `expect_counts.tsv`: the hclaim counters (base values from the
round-10 reference loader + this overlay's own count). `cases11.tsv`: per designed row, design / model / expected.

  python make_r11.py gen    --seed 110000 --rounds 4 --out DIR [--probe] [--fuzz K] [--n 60]
  python make_r11.py check  DIR [--ref PATH]
  python make_r11.py empty  DIR [--ref PATH] [--pre PATH]
        no anchorTribunal line: the current reference and the round-10 copy write the same bytes; only
        unknown-id lines, or claims only on rows with no anchor line: every file but ref_stats.tsv the same
  python make_r11.py report DIR...
"""
import argparse
import datetime
import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R10 = os.environ.get('MAKE_R10_DIR') or os.path.normpath(os.path.join(HERE, '..', '..', '..', 'round10', 'agents',
                                                                     'ref10'))
sys.path.insert(0, R10)
import make_r10 as m10  # noqa: E402
m9, m8, m7, gen, rows_of, REF, pr = m10.m9, m10.m8, m10.m7, m10.gen, m10.rows_of, m10.REF, m10.pr
ordinal, ymd, sha_of, compact, lower, norm = m10.ordinal, m10.ymd, m10.sha_of, m10.compact, m10.lower, m10.norm

PRE_REF = os.path.normpath(os.path.join(HERE, '..', '..', 'pre', 'ref', 'precedent_ref.py'))
DAYS = 1826


# --------------------------------------------------------------------------------------------- the model (own)
def _cue_json():
    p = os.path.join(REF, '..', 'cues', 'cue_table.json')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


CJ = _cue_json()
L_ANCHOR = tuple(CJ['anchor'])
L_WIDE = tuple(CJ.get('anchor_wide', ())) + tuple(CJ.get('anchor_wide9', ()))
L_TRIB = tuple(CJ.get('anchor_tribunal') or ('court of international trade', 'customs court',
                                            'court of federal claims', 'claims court', 'veterans court',
                                            'court of veterans appeals'))
ANY_CUE = L_ANCHOR + L_WIDE + L_TRIB


def model_cue(aq, claims):
    """DESIGN11 §5.1 check 2: the cue list of the row's claims, substring of the normalised lower-cased quote."""
    q = lower(norm(aq))
    cues = L_ANCHOR
    if 'anchorTribunal' in claims:
        cues = L_ANCHOR + L_WIDE + L_TRIB
    elif 'anchorWide' in claims:
        cues = L_ANCHOR + L_WIDE
    return any(c in q for c in cues)


# --------------------------------------------------------------------------------------------- the overlay
# tribunal phrases: (text, kind of phrase). 'trib' = holds a string of anchor_tribunal; 'wide' = holds only an
# anchor_wide / anchor_wide9 string; 'near' = none of the lists (near misses)
TRIBS = [('Court of International Trade', 'trib'), ('U.S. Court of International Trade', 'trib'),
         ('Customs Court', 'trib'), ('United States Customs Court', 'trib'), ('Court of Federal Claims', 'trib'),
         ('United States Court of Federal Claims', 'trib'), ('Claims Court', 'trib'),
         ('Federal Claims Court', 'trib'), ('Veterans Court', 'trib'), ('Court of Veterans Appeals', 'trib'),
         ('U.S. Claims Court', 'trib')]
WIDES = [('Circuit', 'wide'), ('magistrate judge', 'wide'), ('trial judge', 'wide'), ('district judge', 'wide')]
NEARS = [('Court of International  Trade', 'near'), ("Court of Int'l Trade", 'near'),
         ('International Trade Court', 'near'), ('Court of Federal  Claims', 'near'), ("Veterans' Court", 'near'),
         ('Customs Ct.', 'near'), ('CIT', 'near'), ('Court of International Trade', 'near'),
         ('Court of Veterans  Appeals', 'near'), ('Claims  Court', 'near'), ('Court-of-Federal-Claims', 'near'),
         ("Court of Veterans' Appeals", 'near'), ('Board of Veterans Appeals', 'near'), ('tribunal', 'near')]
NAMES = ['Acme Steel Corp. v. United States', 'Hartford Fire Ins. Co. v. United States', 'Doe v. Shinseki',
         'Jones v. Brown', 'Miller Imports v. United States', 'Parker v. Secretary of Veterans Affairs',
         'Nippon Steel Corp. v. United States', 'Ruiz v. McDonough']
TEMPLATES = ['{T} sustained the agency determination in {N}, {C}.',
             'In {N}, {C}, the {T} granted summary judgment for the government.',
             'We review the decision of the {T} in {N}, {C}, de novo.',
             '{N}, {C} ({T} 1998).',
             'The {T} dismissed the complaint. {N}, {C}.']
# designed cases: (name, phrase pool, claims of the claimed row, tail design)
AT_CASES = [
    ('at_pass', 'trib', ('anchorTribunal',), 'ok'), ('at_pass2', 'trib', ('anchorTribunal',), 'ok'),
    ('at_pass_upper', 'trib', ('anchorTribunal',), 'upper'), ('at_pass_lower', 'trib', ('anchorTribunal',), 'lower'),
    ('at_pass_cr', 'trib', ('anchorTribunal',), 'cr'), ('at_pass_uni', 'trib', ('anchorTribunal',), 'uni'),
    ('at_pass_name', 'trib', ('anchorTribunal',), 'name'), ('at_pass_head', 'trib', ('anchorTribunal',), 'head'),
    ('at_both', 'trib', ('anchorTribunal', 'anchorWide'), 'ok'),
    ('at_wide_only_claim', 'trib', ('anchorWide',), 'ok'),            # mutant: the new list without the claim
    ('at_noclaim', 'trib', (), 'ok'),
    ('at_wideq', 'wide', ('anchorTribunal',), 'ok'),                  # union: an anchor_wide string suffices
    ('at_near', 'near', ('anchorTribunal',), 'ok'), ('at_near2', 'near', ('anchorTribunal', 'anchorWide'), 'ok'),
    ('at_disq', 'trib', ('anchorTribunal',), 'disq'), ('at_unres', 'trib', ('anchorTribunal',), 'unres'),
    ('at_unres_name', 'trib', ('anchorTribunal',), 'unres_name'), ('at_part', 'trib', ('anchorTribunal',), 'part'),
    ('at_mismatch', 'trib', ('anchorTribunal',), 'mismatch'), ('at_maincue', 'trib', ('anchorTribunal',), 'maincue'),
    ('at_later', 'trib', ('anchorTribunal',), 'later'), ('at_nopower', 'trib', ('anchorTribunal',), 'nopower'),
    ('at_noanchor', 'trib', ('anchorTribunal',), 'noanchor'), ('at_bridge', 'trib', ('anchorTribunal',), 'bridge'),
    ('at_tb', 'trib', ('anchorTribunal', 'trialBridge'), 'tb'), ('at_tb_fail', 'trib', ('anchorTribunal', 'trialBridge'),
                                                                 'tb_fail'),
    ('at_setaside', 'trib', ('anchorTribunal', 'setAside'), 'setaside'),
    ('at_dupclaim', 'trib', ('anchorTribunal',), 'dupclaim'),
    ('at_vacated', 'trib', ('anchorTribunal',), 'vacated'), ('at_reversed', 'trib', ('anchorTribunal',), 'reversed'),
]
MAINQ = {'affirmed': ['The judgment is affirmed.', 'AFFIRMED.', 'Accordingly, the decision is affirmed.'],
         'reversed': ['The judgment is reversed.', 'REVERSED.'],
         'vacated': ['The judgment is vacated and the case is remanded.', 'VACATED and REMANDED.']}


def styled(text, style):
    if style == 'upper':
        return text.upper()
    if style == 'lower':
        return lower(text)
    return text


def anchor_text(R, tmpl, phrase, name, cite, style, extra=''):
    q = tmpl.replace('{T}', phrase).replace('{N}', name).replace('{C}', cite) + extra
    q = styled(q, style)
    if style == 'cr':
        i = q.find(phrase.split(' ')[0]) if ' ' in phrase else -1
        j = q.find(' ', i) if i >= 0 else -1
        if j > 0:
            q = q[:j] + '\r' + q[j + 1:]
    return q


def at_overlay(U, R, A0, D0, flavour):
    """-> (hist, anch, claims (with 'dup' / 'unknown' marks), tbl, bridges, design {id: dict})."""
    Wd = U.world
    yes, no = [], []
    for r in D0.history:
        b, t = r['by'], r['target']
        if b in Wd.dec and t in Wd.dec and Wd.court(b) != Wd.court(t) and ordinal(Wd.date(t)):
            p = A0.same_case_power(b, t)
            (yes if p == 'yes' else no if p == 'no' else []).append((b, t))
    if not yes:
        ns = sorted(Wd.dec)
        yes = [(ns[-1], ns[0])]
    hist, anch, claims, tbl, bridges, design = [], [], [], [], [], {}
    cases = list(AT_CASES)
    if flavour != 'probe':
        R.shuffle(cases)
        cases = cases[:R.randint(18, len(cases))]
    for k, (case, pool, cl, tail) in enumerate(cases):
        bt, tt = R.choice(no) if (tail == 'nopower' and no) else R.choice(yes)
        rid = 'at%d_%d' % (U.seed, k)
        kind = 'affirmed'
        if tail in ('vacated', 'setaside'):
            kind = 'vacated'
        elif tail in ('reversed', 'tb', 'tb_fail'):
            kind = R.choice(['reversed', 'vacated']) if tail != 'reversed' else 'reversed'
        dt = Wd.date(tt) if ordinal(Wd.date(tt)) else 20000101
        ot = ordinal(dt)
        delta = R.randint(1, DAYS - 1)
        if tail == 'later':
            delta = -R.choice([1, 30, 400])
        dd = ymd(ot + delta)
        T, Dn = U.next_node, U.next_node + 1
        U.next_node += 2
        tsha, dsha = sha_of('atT:%d:%d' % (U.seed, T)), sha_of('atD:%d:%d' % (U.seed, Dn))
        trow = list(Wd.dec[tt])
        trow[0], trow[2], trow[7] = str(T), str(dt), tsha
        drow = list(Wd.dec[bt])
        drow[0], drow[2], drow[7] = str(Dn), str(dd), dsha
        U.dec_add += [trow, drow]
        Wd.dec[T], Wd.dec[Dn] = trow, drow
        tcite = '%d %s %d' % (R.randint(1, 999), R.choice(['F.3d', 'F. Supp. 2d', 'Fed. Cl.', "Ct. Int'l Trade",
                                                            'Vet. App.', 'F.4th']), R.randint(1, 1999))
        if Wd.cite is not None:
            U.cite_add.append((tcite, T))
            Wd.cite[compact(tcite)] = T
        name = R.choice(NAMES)
        phrases = {'trib': TRIBS, 'wide': WIDES, 'near': NEARS}[pool]
        style = tail if tail in ('upper', 'lower', 'cr') else R.choice(['', '', '', 'upper', 'lower'])
        for _ in range(200):
            phrase = R.choice(phrases)[0]
            tmpl = R.choice(TEMPLATES)
            extra = ' See the prior appeal, 12 F.3d 1.' if tail == 'disq' else ''
            acite = tcite if tail != 'unres' else '%d F.2d %d' % (R.randint(1, 999), R.randint(2000, 2999))
            aname = name if tail != 'unres_name' else 'Smith v. Wesson'
            aq = anchor_text(R, tmpl, phrase, aname, acite, style, extra)
            twin = anchor_text(R, tmpl, 'district court', aname, acite, style if style != 'cr' else '', extra)
            ql = lower(norm(aq))
            # the claimed quote holds a cue of its own pool only (generator check; the model decides the verdict)
            if pool == 'trib' and (not any(c in ql for c in L_TRIB) or any(c in ql for c in L_ANCHOR + L_WIDE)):
                continue
            if pool == 'wide' and (not any(c in ql for c in L_WIDE) or any(c in ql for c in L_ANCHOR + L_TRIB)):
                continue
            if pool == 'near' and any(c in ql for c in ANY_CUE):
                continue
            break
        else:
            raise SystemExit('no anchor quote for %s' % case)
        if tail == 'uni':
            aq, twin = 'Ünïcödé — «%s» ½' % aq, 'Ünïcödé — «%s» ½' % twin
        ev = 'cite:' + tcite
        if tail in ('name', 'unres_name'):
            ev = 'name:' + name
        mq = R.choice(MAINQ[kind])
        if tail in ('tb', 'tb_fail'):
            mq = 'The judgment of the %s is %s.' % (R.choice(['trial court', 'District Court', 'circuit court']),
                                                    kind)
        elif tail == 'maincue':
            mq = 'The judgment is modified.'
        elif tail == 'setaside':
            mq = 'The judgment is set aside.'
        dpre = R.choice(['', 'OPINION. ', 'Opinion for the court. '])
        mid = R.choice([' ', ' Facts omitted. '])
        dtext = dpre + aq + mid + mq + ' It is so ordered.'
        a0 = len(dpre)
        m0 = a0 + len(aq) + len(mid)
        U.add_window(dsha, 0, dtext)
        w0 = 5_000_000 + 1000 * k
        tpre = R.choice(['', 'Background. '])
        U.add_window(dsha, w0, tpre + twin + ' Rest of the opinion.')
        part = 'headmatter' if tail == 'head' else 'majority'
        apart = 'dissent' if tail == 'part' else part
        a_s, a_e = a0, a0 + len(aq)
        if tail == 'mismatch':
            a_s, a_e = a0 + 1, a0 + len(aq) + 1
        tw_s, tw_e = w0 + len(tpre), w0 + len(tpre) + len(twin)
        if tail == 'mismatch':
            tw_s, tw_e = tw_s + 1, tw_e + 1
        # T's own text: the affirmance line for trialBridge rows
        if tail in ('tb', 'tb_fail'):
            tq = 'Judgment affirmed.' if tail == 'tb' else 'Affirmed in part and reversed in part.'
            U.add_window(tsha, 0, 'Opinion. ' + tq + ' End.')
            for x in (rid, rid + '_tw'):
                tbl.append([x, str(len('Opinion. ')), str(len('Opinion. ') + len(tq))])
        for x, aqx, s, e, cls in ((rid, aq, a_s, a_e, cl), (rid + '_tw', twin, tw_s, tw_e,
                                                              tuple(c for c in cl if c != 'anchorTribunal'))):
            hist.append([x, str(T), str(Dn), str(dd), kind, 'all', dsha, str(m0), str(m0 + len(mq)), mq, ev,
                         'majority', 'gen'])
            if tail != 'noanchor':
                anch.append([x, str(s), str(e), aqx, apart, 'gen'])
            for c in cls:
                claims.append(('good', [x, c, 'gen']))
            if tail == 'bridge':
                bridges.append([x, str(Dn), '0', '10', dtext[:10], 'gen'])
        if tail == 'dupclaim':
            claims.append(('dup', [rid, 'anchorTribunal', 'gen2']))
        design[rid] = dict(case=case, pool=pool, claims=cl, tail=tail, aq=aq, twin=rid + '_tw',
                           anchor=tail != 'noanchor', bridge=tail == 'bridge')
    return hist, anch, claims, tbl, bridges, design


def claim_bad_line(R, rid):
    k = R.choice(['lower', 'title', 'two', 'four', 'nonutf8', 'near', 'space'])
    if k == 'lower':
        return ('%s\tanchortribunal\tgen' % rid).encode()
    if k == 'title':
        return ('%s\tAnchorTribunal\tgen' % rid).encode()
    if k == 'two':
        return ('%s\tanchorTribunal' % rid).encode()
    if k == 'four':
        return ('%s\tanchorTribunal\tgen\tx' % rid).encode()
    if k == 'nonutf8':
        return ('%s\tanchorTribunal\tgen' % rid).encode() + b'\xff'
    if k == 'near':
        return ('%s\tanchorTribunals\tgen' % rid).encode()
    return ('%s\tanchorTribunal \tgen' % rid).encode()


def append_bytes(path, lines):
    data = b''
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            data = fh.read()
    with open(path, 'ab') as fh:
        if data and not data.endswith(b'\n'):
            fh.write(b'\n')
        for l in lines:
            fh.write(l + b'\n')


def is_at_line(l):
    """a well-formed anchorTribunal claim line (the lines a 'no anchorTribunal' copy drops)"""
    try:
        l.decode('utf-8')
    except UnicodeDecodeError:
        return False                      # a bad line under both rounds: kept, counted by both
    p = l.rstrip(b'\r').split(b'\t')
    return len(p) == 3 and p[1] == b'anchorTribunal'


# ------------------------------------------------------------------ DESIGN11 §5.2 identityTie (D11-5)
SPANMAX = 200
ID_CASES = [('id_docket', 4), ('id_cite', 4), ('id_date', 4), ('id_date_abbr', 2), ('id_upper', 1), ('id_cr', 1),
            ('id_span200', 1), ('id_punct', 1),
            ('id_donly', 2), ('id_tonly', 2), ('id_short', 1), ('id_nodigit', 1), ('id_span201', 1),
            ('id_tspan201', 1), ('id_empty', 1), ('id_nowin', 1), ('id_hash', 1), ('id_date_other', 2),
            ('id_date_7', 1), ('id_date_zero_pad', 1), ('id_date_donly', 1), ('id_date_iso', 1),
            ('id_cite_as_date', 1), ('id_tok_empty', 1), ('id_wrong_node', 1)]


def model_identity(Wd, by, T, f):
    """DESIGN11 §5.2 (this file's own model) for one good line f = (form, token, ds, de, ts, te)."""
    form, token, ds, de, ts, te = f
    if de - ds > SPANMAX or te - ts > SPANMAX or by not in Wd.dec or T not in Wd.dec:
        return 'identityTie'
    dsp, tsp = Wd.span(by, ds, de), Wd.span(T, ts, te)
    if dsp is None or tsp is None:
        return 'identityTie'
    if form in ('docket', 'cite'):
        k = compact(token)
        ok = len(k) >= 4 and any(c.isdigit() for c in k) and k in compact(dsp) and k in compact(tsp)
        return 'ok' if ok else 'identityTie'
    dt = Wd.date(T)
    if not (len(token) == 8 and all('0' <= c <= '9' for c in token)) or not dt or int(token) != dt:
        return 'identityTie'
    fs = m10.forms(dt)
    if not fs or not any(x in lower(dsp) for x in fs) or not any(x in lower(tsp) for x in fs):
        return 'identityTie'
    return 'ok'


def id_build(U, R, case, r):
    """-> line fields (strings). Adds far windows of D's (by) and T's own text holding the spans."""
    Wd = U.world
    by, T = r['by'], r['target']
    dt = Wd.date(T) if T in Wd.dec else 0
    yy, nn = R.randint(0, 99), R.randint(1, 9999)
    dtext = R.choice(['%02d-%d' % (yy, nn), 'No. %02d-%d' % (yy, nn), '%d-CV-%04d' % (1990 + yy % 30, nn),
                      'Civ. A. %d-%04d' % (1980 + yy % 40, nn)])
    cite = '%d %s %d' % (R.randint(1, 999), R.choice(['F.3d', 'F. Supp. 2d', 'So. 2d', 'N.E.2d', 'P.3d']),
                         R.randint(1, 1999))
    form = 'date' if 'date' in case and case != 'id_cite_as_date' else ('cite' if case in ('id_cite',
                                                                                            'id_cite_as_date')
                                                                       else R.choice(['docket', 'docket', 'cite']))
    if form == 'date':
        o = ordinal(dt)
        x = datetime.date.fromordinal(o) if o else datetime.date(2001, 3, 15)
        printed = '%s %d, %d' % (m10.MONTHS[x.month - 1], x.day, x.year)
        if case == 'id_date_abbr' and m10.ABBR.get(x.month):
            printed = '%s %d, %d' % (R.choice(m10.ABBR[x.month]), x.day, x.year)
        if case == 'id_date_zero_pad':
            printed = '%s %02d, %d' % (m10.MONTHS[x.month - 1], x.day, x.year) if x.day < 10 else \
                '%s  %d, %d' % (m10.MONTHS[x.month - 1], x.day, x.year)
        if case == 'id_date_iso':
            printed = '%04d-%02d-%02d' % (x.year, x.month, x.day)
        token = '%08d' % dt if dt else '%04d%02d%02d' % (x.year, x.month, x.day)
        if case == 'id_date_other':
            token = '%04d%02d%02d' % (x.year, x.month, min(28, x.day) if x.day != 28 else 27)
            if token == '%08d' % dt:
                token = '%04d%02d%02d' % (x.year + 1, x.month, min(28, x.day))
        elif case == 'id_date_7':
            token = token[1:]
        dsay, tsay = printed, printed
        if case == 'id_date_donly':
            tsay = 'the decision below'
    else:
        tok = dtext if form == 'docket' else cite
        token = tok
        if case == 'id_punct':
            token = tok.replace(' ', '').replace('.', '').upper()
        elif case == 'id_short':
            token, tok = 'a12', 'a12'
        elif case == 'id_nodigit':
            token, tok = 'abcdef', 'abcdef'
        elif case == 'id_tok_empty':
            token = ''
        elif case == 'id_cite_as_date':
            token = tok                                 # a cite token under form cite: the cite case, plain
        dsay, tsay = tok, tok
        if case == 'id_donly':
            tsay = '%d-%d' % (R.randint(10, 99), R.randint(10000, 99999))
        elif case == 'id_tonly':
            dsay = '%d-%d' % (R.randint(10, 99), R.randint(10000, 99999))
    dspan = R.choice(['Appeal from No. %s.', 'Docket %s, decided below.', 'see %s', '(%s)']) % dsay
    tspan = R.choice(['%s', 'Case %s.', 'Decided %s.', 'Docket No. %s']) % tsay
    if case == 'id_upper':
        dspan, tspan = dspan.upper(), tspan.upper()
    if case == 'id_cr':
        dspan = dspan.replace(' ', '\r', 1)
    if case == 'id_span200':
        dspan, tspan = 'D' * (SPANMAX - len(dspan)) + dspan, 'T' * (SPANMAX - len(tspan)) + tspan
    elif case == 'id_span201':
        dspan = 'D' * (SPANMAX + 1 - len(dspan)) + dspan
    elif case == 'id_tspan201':
        tspan = 'T' * (SPANMAX + 1 - len(tspan)) + tspan
    k = len(U.win_add)
    ds = de = ts = te = 0
    if by in Wd.dec:
        dsha = Wd.dec[by][7]
        d0 = 6_000_000 + 1000 * k
        lead = R.choice(['', 'Opinion. ', 'Ünïcödé — '])
        U.add_window(dsha, d0, lead + dspan + ' Rest.', case == 'id_hash')
        ds, de = d0 + len(lead), d0 + len(lead) + len(dspan)
    if T in Wd.dec:
        tsha = Wd.dec[T][7]
        t0 = 6_500_000 + 1000 * k
        lead = R.choice(['', 'Header. '])
        U.add_window(tsha, t0, lead + tspan + ' Rest.')
        ts, te = t0 + len(lead), t0 + len(lead) + len(tspan)
    if case == 'id_empty':
        de = ds
    elif case == 'id_nowin':
        ts, te = te + 50, te + 60
    elif case == 'id_wrong_node' and T in Wd.dec:
        ds, de = ts, te                                  # T's offsets read in D's text (no such window there)
    return [r['id'], form, token, str(ds), str(de), str(ts), str(te)]


def id_bad_line(R, rid):
    k = R.choice(['six', 'eight', 'form', 'formcase', 'x', 'neg', 'nonutf8', 'empty_num', 'fullwidth'])
    f = [rid, 'docket', '12-345', '0', '10', '0', '10']
    if k == 'six':
        return '\t'.join(f[:6]).encode()
    if k == 'eight':
        return '\t'.join(f + ['x']).encode()
    if k == 'form':
        f[1] = 'citation'
    elif k == 'formcase':
        f[1] = 'Docket'
    elif k == 'x':
        f[R.choice([3, 4, 5, 6])] = '1x'
    elif k == 'neg':
        f[R.choice([3, 4, 5, 6])] = '-1'
    elif k == 'empty_num':
        f[R.choice([3, 4, 5, 6])] = ''
    elif k == 'fullwidth':
        f[4] = '１０'
    elif k == 'nonutf8':
        return '\t'.join(f).encode() + b'\xc3'
    return '\t'.join(f).encode('utf-8')


def id_overlay(U, R, D0, A0, d, exclude, flavour):
    """identity lines on base history rows -> (encoded lines in file order, {id: case}, first {id: fields}, dup n,
    bad n)"""
    old10 = {(r[0], r[1]): r for r in rows_of(os.path.join(d, 'expect10.tsv')) or []}
    seen = Counter(r['id'] for r in D0.history)
    single = [r for r in D0.history if seen[r['id']] == 1 and r['id'] not in exclude]
    okp, nop, bad = [], [], []
    for r in single:
        v = old10.get(('history', r['id']))
        v = v[4] if v else '?'
        if v == 'ok':
            (okp if A0.same_case_power(r['by'], r['target'], D0.hclaim.get(r['id'])) != 'no' else nop).append(r)
        elif v != '?':
            bad.append(r)
    for x in (okp, nop, bad):
        R.shuffle(x)
    names = [c for c, _ in ID_CASES]
    R.shuffle(names)
    plan = []
    n_ok = min(len(okp), 40 if flavour != 'probe' else 60)
    for i, r in enumerate(okp[:n_ok]):
        plan.append((r, names[i % len(names)] if (flavour == 'probe' or i < len(names)) else m9.wpick(R, ID_CASES)))
    for r in nop[:4]:
        plan.append((r, R.choice(['id_docket', 'id_donly', 'id_date'])))
    for r in bad[:5]:
        plan.append((r, R.choice(['id_docket', 'id_date', 'id_tonly'])))
    for r in [r for r in D0.history if seen[r['id']] > 1][:1]:
        plan.append((r, 'id_docket'))
    lines, cases = [], {}
    for (r, case) in plan:
        lines.append(('good', id_build(U, R, case, r)))
        cases[r['id']] = case
    dup_n = 0
    for (r, case) in plan[:2]:
        lines.append(('dup', id_build(U, R, 'id_donly' if case != 'id_donly' else 'id_docket', r)))
        dup_n += 1
    lines.append(('unknown', ['id_no_such_row_%d' % U.seed, 'docket', '12-345', '0', '6', '0', '6']))
    nbad = R.randint(1, 4)
    for _ in range(nbad):
        lines.append(('bad', id_bad_line(R, R.choice(plan)[0]['id'] if plan else 'x')))
    firsts = [x for x in lines if x[0] != 'dup']
    R.shuffle(firsts)
    out = list(firsts)
    for x in [x for x in lines if x[0] == 'dup']:
        pos = max(i for i, y in enumerate(out) if y[0] == 'good' and y[1][0] == x[1][0])
        out.insert(R.randint(pos + 1, len(out)), x)
    first = {}
    for k, f in out:
        if k == 'good' and f[0] not in first:
            first[f[0]] = (f[1], f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]))
    enc = [x[1] if isinstance(x[1], bytes) else '\t'.join(x[1]).encode('utf-8') for x in out]
    return enc, cases, first, dup_n, nbad


def strip_at(src_data, dst_data, keep=None):
    """a copy of a data dir without the well-formed anchorTribunal claim lines (keep(line) -> True keeps one) and
    without history_identity.tsv: the round-10 view of the universe"""
    shutil.rmtree(dst_data, ignore_errors=True)
    shutil.copytree(src_data, dst_data)
    if os.path.exists(os.path.join(dst_data, 'history_identity.tsv')):
        os.remove(os.path.join(dst_data, 'history_identity.tsv'))
    p = os.path.join(dst_data, 'history_claim.tsv')
    if os.path.exists(p):
        with open(p, 'rb') as fh:
            ls = fh.read().split(b'\n')
        with open(p, 'wb') as fh:
            fh.write(b'\n'.join(l for l in ls if not is_at_line(l) or (keep and keep(l))))


_PRE = {}


def pre_paths(pre):
    """the round-10 final reference as a program (a temp copy beside the current cue table) and as a module"""
    if pre in _PRE:
        return _PRE[pre]
    tmp = tempfile.mkdtemp(prefix='r11pre_')
    shutil.copytree(os.path.dirname(pre), os.path.join(tmp, 'ref'),
                    ignore=shutil.ignore_patterns('__pycache__', 'SHA256SUMS'))
    shutil.copytree(os.path.join(REF, '..', 'cues'), os.path.join(tmp, 'cues'))
    path = os.path.join(tmp, 'ref', os.path.basename(pre))
    spec = importlib.util.spec_from_file_location('pre_ref_r10', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _PRE[pre] = (tmp, path, mod)
    return _PRE[pre]


def run_prog(ref, d, out, data):
    shutil.rmtree(out, ignore_errors=True)
    subprocess.run([sys.executable, ref, 'run', '--data', data, '--edges', os.path.join(d, 'edges'), '--out', out],
                   check=True, stderr=subprocess.DEVNULL)


def overlay(d, seed, flavour, fuzz, pre):
    R = random.Random(seed * 1000003 + 11011)
    J = lambda n: os.path.join(d, 'data', n)
    pr.BAD_ROWS.clear()
    D0 = pr.Data(os.path.join(d, 'data'))
    A0 = pr.Engine(D0)
    U = m10.U10(d, seed)
    hist, anch, claims, tbl, bridges, design = at_overlay(U, R, A0, D0, flavour)
    m10.append_rows(J('history.tsv'), hist)
    m10.append_rows(J('history_anchor.tsv'), anch)
    if bridges:
        m10.append_rows(J('history_bridge.tsv'), bridges)
    if tbl:
        m10.append_rows(J('history_tbridge.tsv'), tbl)
    # claims on base rows: rows with an anchor line (some anchorNoCue under round 10) and rows without
    base_ids = sorted({r['id'] for r in D0.history})
    with_anchor = [i for i in base_ids if i in D0.anchor]
    R.shuffle(with_anchor)
    others = [i for i in base_ids if i not in D0.anchor]
    R.shuffle(others)
    base_claimed = with_anchor[:R.randint(2, 6)] + others[:R.randint(1, 3)]
    # §5.2: identity lines on base rows (own random stream, so the §5.1 part of a seed is unchanged)
    R2 = random.Random(seed * 1000003 + 11012)
    id_enc, id_cases, id_first, id_dup, id_bad = id_overlay(U, R2, D0, A0, d, set(base_claimed), flavour)
    U.flush()
    eol = R2.choice([b'\n'] * 6 + [b'\r\n'])
    with open(J('history_identity.tsv'), 'wb') as fh:
        fh.write((b'\xef\xbb\xbf' if R2.random() < 0.05 else b'') + eol.join(id_enc)
                 + (eol if R2.random() < 0.85 else b''))
    lines = [('good', [c[1][0], c[1][1], c[1][2]]) if c[0] == 'good' else c for c in claims]
    lines += [('good', [i, 'anchorTribunal', 'gen']) for i in base_claimed]
    nunk = R.randint(1, 2)
    lines += [('unknown', ['at_no_such_row_%d_%d' % (seed, j), 'anchorTribunal', 'gen']) for j in range(nunk)]
    if base_claimed and R.random() < 0.5:
        lines.append(('dup', [base_claimed[0], 'anchorTribunal', 'gen3']))
    nbad = R.randint(1, 3)
    lines += [('bad', claim_bad_line(R, R.choice(list(design) + base_claimed))) for _ in range(nbad)]
    firsts = [x for x in lines if x[0] != 'dup']
    R.shuffle(firsts)
    out = list(firsts)
    for x in [x for x in lines if x[0] == 'dup']:
        pos = max(i for i, y in enumerate(out) if y[0] == 'good' and y[1][:2] == x[1][:2])
        out.insert(R.randint(pos + 1, len(out)), x)
    append_bytes(J('history_claim.tsv'),
                 [x[1] if isinstance(x[1], bytes) else '\t'.join(x[1]).encode('utf-8') for x in out])
    if fuzz:
        log = m7.mutate(J('history_claim.tsv'), R, fuzz, 3, ())
        log += m7.mutate(J('history_anchor.tsv'), R, max(1, fuzz // 2), 6, (1, 2))
        log += m7.mutate(J('history_identity.tsv'), R, max(1, fuzz // 2), 7, (3, 4, 5, 6))
        gen.write(os.path.join(d, 'mutations11.txt'), log)
    expect(d, design, set(base_claimed), pre, fuzz,
           dup_n=sum(1 for x in out if x[0] == 'dup'), unk_n=nunk,
           ident=(id_cases, id_first, id_dup, id_bad))
    return design


def expect(d, design, base_claimed, pre, fuzz, dup_n, unk_n, ident):
    id_cases, id_first, id_dup, id_bad = ident
    tmpdir, pre_prog, pre_mod = pre_paths(pre)
    data0 = d + '_r10data'
    out0 = d + '_r10out'
    strip_at(os.path.join(d, 'data'), data0)
    run_prog(pre_prog, d, out0, data0)
    r10 = {(r[0].replace('.tsv', ''), r[1]): r[2] for r in rows_of(os.path.join(out0, 'certs.tsv')) or []}
    s10 = {p[0]: p[1] for p in rows_of(os.path.join(out0, 'ref_stats.tsv')) or [] if len(p) >= 2}
    pre_mod.BAD_ROWS.clear()
    D1 = pre_mod.Data(data0)
    A1 = pre_mod.Engine(D1)
    A1.admit()
    Wd = m10.World(os.path.join(d, 'data'))
    shutil.rmtree(data0, ignore_errors=True)
    shutil.rmtree(out0, ignore_errors=True)
    hcount = Counter(r['id'] for r in D1.history)
    hids = set(hcount)
    # the anchorTribunal claims this file wrote (good lines, known ids, first line per id)
    at_ids = {i for i, x in design.items() if 'anchorTribunal' in x['claims']} | base_claimed
    at_ids &= hids
    claims_of = defaultdict(set)
    for i, c in D1.hclaim.items():
        claims_of[i] |= set(c)
    for i in at_ids:
        claims_of[i].add('anchorTribunal')
    old10 = {(r[0], r[1]): r for r in rows_of(os.path.join(d, 'expect10.tsv')) or []}
    rows, cases = [], []
    id_cnt = Counter()
    for (t, i), v in sorted(r10.items()):
        exp, what = v, 'r10'
        if t == 'history' and i in at_ids:
            anc = D1.anchor.get(i)
            if anc is None or i in D1.bridge:
                what = 'unused'
            elif v != 'anchorNoCue':
                what = 'cue_irrelevant'
            elif not model_cue(anc[2], claims_of[i]):
                what = 'nocue'
            elif i in design:
                exp, what = r10.get(('history', design[i]['twin']), '?'), 'twin'
            else:
                exp, what = '?', 'moved_base'
        if t == 'history' and i in id_first and i in hids:
            # §5.2: after the complete round-10 verdict; checked only when ok and the Lean admits (power not no)
            r = next(x for x in D1.history if x['id'] == i)
            m = model_identity(Wd, r['by'], r['target'], id_first[i])
            gate = A1.same_case_power(r['by'], r['target'], D1.hclaim.get(i)) != 'no'
            if exp == 'ok' and gate and hcount[i] == 1:
                id_cnt['identity_checked_rows'] += 1
                if m != 'ok':
                    id_cnt['identity_failed_rows'] += 1
                    exp = m
                what = 'id_checked/' + m
            else:
                what = ('id_nopower/' if exp == 'ok' else 'id_r10fail/') + m
            cases.append([i, id_cases.get(i, '?'), 'identity', '-', '-', what, exp])
        if t == 'history' and hcount[i] > 1:
            exp = '?'
        if fuzz:
            exp = '?'
        if i in design:
            x = design[i]
            case = '%s:%s' % (x['case'], x['tail'])
            cases.append([i, x['case'], x['pool'], '+'.join(x['claims']) or '-', x['tail'], what, exp])
        elif i.endswith('_tw') and i[:-3] in design:
            case = 'twin:%s' % design[i[:-3]]['case']
        else:
            o = old10.get((t, i))
            case = ('at_base:' if i in base_claimed else '') + (id_cases[i] + ':' if i in id_cases else '') + (
                o[2] if o else 'base')
        o = old10.get((t, i))
        tg, by = (o[5], o[6]) if o else ('-', '-')
        rows.append([t, i, case, what, exp, tg, by, '-'])
    gen.write(os.path.join(d, 'expect.tsv'), rows)
    gen.write(os.path.join(d, 'cases11.tsv'), cases)
    if fuzz:
        gen.write(os.path.join(d, 'expect_counts.tsv'), [])
        return
    cnt = []
    for k in ('hclaim_bad_rows',):
        cnt.append((k, int(s10.get(k, 0))))
    kept = set(D1.hclaim) | at_ids
    cnt.append(('hclaim_rows', len(kept)))
    cnt.append(('hclaim_duplicates', int(s10.get('hclaim_duplicates', 0)) + dup_n))
    cnt.append(('hclaim_unknown_ids', int(s10.get('hclaim_unknown_ids', 0)) + unk_n))
    cnt.append(('hclaim_anchortribunal', len(at_ids)))
    cnt.append(('hclaim_anchortribunal_unused', sum(1 for i in at_ids if i not in D1.anchor or i in D1.bridge)))
    cnt.append(('identity_lines', len([i for i in id_first if i in hids])))
    if not any(hcount[i] > 1 for i in id_first if i in hids):     # (a repeated history id: per-row, not modelled)
        cnt.append(('identity_checked_rows', id_cnt['identity_checked_rows']))
        cnt.append(('identity_failed_rows', id_cnt['identity_failed_rows']))
    cnt.append(('identity_dup_rows', id_dup))
    cnt.append(('identity_bad_rows', id_bad))
    gen.write(os.path.join(d, 'expect_counts.tsv'), sorted(cnt))


def make(seed, d, n, flavour, fuzz, pre):
    shutil.rmtree(d, ignore_errors=True)
    fl10 = 'probe' if flavour == 'probe' else 'main'
    case_of = m9.build_base(seed, d, n, fl10)
    m9.overlay(d, seed, case_of, 0)
    for fn in ('expect.tsv', 'expect_counts.tsv'):
        if os.path.exists(os.path.join(d, fn)):
            os.replace(os.path.join(d, fn), os.path.join(d, fn.replace('.tsv', '9.tsv')))
    m10.overlay(d, seed, case_of, fl10, 0)
    for fn in ('expect.tsv', 'expect_counts.tsv'):
        os.replace(os.path.join(d, fn), os.path.join(d, fn.replace('.tsv', '10.tsv')))
    return overlay(d, seed, flavour, fuzz, pre)


# ---------------------------------------------------------------------------------------------------------------
def cmd_check(root, ref):
    rc = m7.cmd_check(root, ref)
    tally = Counter()
    for d in m7.universes(root):
        for r in rows_of(os.path.join(d, 'cases11.tsv')) or []:
            tally[(r[1], r[5], r[6])] += 1
    print('designed case, model path, expected verdict: rows')
    for (c, w, e), n in sorted(tally.items()):
        print('  %-20s %-15s %-22s %d' % (c, w, e, n))
    return rc


def cmd_empty(root, ref, pre):
    """Round 11 off: no anchorTribunal line -> the current reference writes what the round-10 copy writes (bytes);
    only unknown-id anchorTribunal lines, or the claim only on rows with no anchor line -> every file but
    ref_stats.tsv the same."""
    tmpdir, pre_prog, pre_mod = pre_paths(pre)
    bad = 0
    strip = lambda x: b'\n'.join(l for l in x.split(b'\n') if not l.startswith((b'seconds', b'peak_mb')))
    us = m7.universes(root)
    for d in us:
        pr.BAD_ROWS.clear()
        D = pr.Data(os.path.join(d, 'data'))
        noanchor = {i for i in (r['id'] for r in D.history) if i not in D.anchor}
        modes = ('absent', 'id_empty', 'id_blank', 'unknown_only', 'unused_only')
        outs = {}
        for mode in modes:
            data = os.path.join(d, 'data_' + mode)
            if mode == 'absent':
                strip_at(os.path.join(d, 'data'), data)
            elif mode in ('id_empty', 'id_blank'):
                strip_at(os.path.join(d, 'data'), data)
                with open(os.path.join(data, 'history_identity.tsv'), 'wb') as fh:
                    fh.write(b'' if mode == 'id_empty' else b'\n\r\n\n')
            elif mode == 'unknown_only':
                strip_at(os.path.join(d, 'data'), data)
                append_bytes(os.path.join(data, 'history_claim.tsv'),
                             [b'at_nosuch_1\tanchorTribunal\tgen', b'at_nosuch_2\tanchorTribunal\tgen'])
                with open(os.path.join(data, 'history_identity.tsv'), 'wb') as fh:
                    fh.write(b'id_nosuch\tdocket\t12-345\t0\t6\t0\t6\nx\tdocket\t1\t2\nx\tDocket\t12-345\t0\t6\t0\t6\n')
            else:
                strip_at(os.path.join(d, 'data'), data,
                         keep=lambda l: l.split(b'\t')[0].decode('utf-8', 'replace') in noanchor)
            out = os.path.join(d, 'ref_' + mode)
            m7.run_ref(ref, d, out, data)
            outs[mode] = out
        out = os.path.join(d, 'ref_pre')
        run_prog(pre_prog, d, out, os.path.join(d, 'data_absent'))
        outs['pre'] = out
        for mode in modes:
            a_dir, b_dir = outs['pre'], outs[mode]
            for fn in sorted(set(os.listdir(a_dir)) | set(os.listdir(b_dir))):
                pa, pb = os.path.join(a_dir, fn), os.path.join(b_dir, fn)
                a = open(pa, 'rb').read() if os.path.exists(pa) else None
                b = open(pb, 'rb').read() if os.path.exists(pb) else None
                if fn == 'ref_stats.tsv' and a is not None and b is not None:
                    a, b = strip(a), strip(b)
                    if mode in ('unknown_only', 'unused_only'):
                        a = b'\n'.join(l for l in a.split(b'\n') if not l.startswith((b'hclaim_', b'identity_')))
                        b = b'\n'.join(l for l in b.split(b'\n') if not l.startswith((b'hclaim_', b'identity_')))
                if a != b:
                    bad += 1
                    print('%s: %s differs (%s)' % (os.path.basename(d), fn, mode))
        for o in outs.values():
            shutil.rmtree(o, ignore_errors=True)
        for mode in modes:
            shutil.rmtree(os.path.join(d, 'data_' + mode), ignore_errors=True)
    print('%d universes, %d differing files' % (len(us), bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gen')
    g.add_argument('--seed', type=int, default=110000)
    g.add_argument('--rounds', type=int, default=1)
    g.add_argument('--n', type=int, default=60)
    g.add_argument('--out', required=True)
    g.add_argument('--probe', action='store_true')
    g.add_argument('--fuzz', type=int, default=0, metavar='K')
    g.add_argument('--pre', default=PRE_REF)
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
    try:
        if a.cmd == 'gen':
            os.makedirs(a.out, exist_ok=True)
            fl = 'probe' if a.probe else ('fuzz' if a.fuzz else 'main')
            for s in range(a.seed, a.seed + a.rounds):
                d = os.path.join(a.out, '%s%d' % ({'probe': 'q', 'fuzz': 'f', 'main': 'r'}[fl], s))
                design = make(s, d, a.n, fl, a.fuzz, a.pre)
                print('%s: %d designed anchorTribunal rows' % (d, len(design)), flush=True)
        elif a.cmd == 'check':
            sys.exit(cmd_check(a.dir, a.ref))
        elif a.cmd == 'empty':
            sys.exit(cmd_empty(a.dir, a.ref, a.pre))
        else:
            m7.cmd_report(a.dirs)
    finally:
        for (tmp, _, _) in _PRE.values():
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
