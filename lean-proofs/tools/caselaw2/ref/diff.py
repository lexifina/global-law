#!/usr/bin/env python3
"""diff.py - compare the Lean runner's outputs with precedent_ref.py's in one canonical form, and bucket every
disagreement by file, field and rule (DESIGN D4: each disagreement is then triaged as Lean / reference / ambiguous
doctrine / data).

  python diff.py A_OUT B_OUT [--map labels.json] [--tsv diff.tsv] [--examples 3] [--quiet] [--asof 20261112]

Either directory may hold the Lean runner's format (LEAN.md "Output formats"; recognised by its header lines) or the
reference's (REF_NOTES.md); both are read into the canonical form below, so Lean-vs-ref and ref-vs-ref (the mutant
self-test) use the same code. By convention A is the Lean side.

Canonical form (labels.json says how each side's labels map; the map only renames, it never changes a verdict):
  status    For each (node, holding), the status on the diagonal asOf t = conduct u, for every t <= asOf, as a
            canonical class none | negative | partial | unknown (+ the canonical negative kind, + firm). The Lean
            writes only the diagonal (LEAN.md: t = u); the ref writes asOf x conduct pieces, evaluated at (t, t).
            Both are compared as functions at every breakpoint either side uses. A (node, holding) with no rows on
            one side is 'none' there. Buckets: status:<a>/<b> (the verdict), kind (both negative, different kind),
            firm. Rule = the event kind behind the verdict (B side, else A side).
  findings  cites:  (citing, cited, canonical kind of the cited status) from the citation-edge findings;
            pair:   (kind, citing, cited) for citesUnpublishedAsBinding, pluralityTreatedAsBinding,
                    panelDepartsWithoutEnBanc, ignoresBindingInUnit;
            atRisk: ('atRisk:<family>', source, subject) for inferred, possiblySuperseded, soft, claim,
                    contraryBinding, citesLaterNegated and supersededConductUnknown (citing, cited) (labels.json "atRisk"; the detail after the
                    family - treatment kind, holding id, status - is not part of the key).
            Kinds only one side defines (now only Lean inconsistentBindingBase and the Lean's force-based
            citesNotCitable) are counted and listed as 'uncompared', never as disagreements.
  certs     (table, id) -> passed | rejected (labels.json "reason"); ok/rejected mismatches are disagreements,
            differing rejection reasons are reported as 'reasonOnly' (informational).
  splits    (issue, {court1, court2}) of splits existing on the asOf date (units dropped). The Lean's
            split rows vs the ref's splits_asof.tsv (falling back to splits.tsv).
  conflicts ('conflict', issue, court, unit) -> answers, firm: the Lean's splits.tsv 'conflict' rows (court as
            123 or 123/4; unit 0 or none = '-') vs the ref's conflicts_asof.tsv. Missing on one side = onlyA/onlyB;
            same key, different answers or firm = 'answers' / 'firm'.
  lines     status_lines.tsv (DEVIATIONS 75): as status, keyed (node, holding, line), line = orig or an adopter
            court id. A key with no rows on one side is 'none' there. Skipped when either side has no such file.
  horty     horty.tsv (DEVIATIONS 78): (family, cases) -> verdict; buckets onlyA / onlyB / verdict. court and firm
            are not compared. Skipped when either side has no such file.
Round 5 (DESIGN5 §5.1; all of it is skipped when neither side has the round-5 columns or files, so a round-4 pair
of directories is compared exactly as before):
  oclass    the trailing `oclass` column of status.tsv, status_lines.tsv and findings.tsv. Status: compared at
            every breakpoint where both sides state the same non-good class (bucket `oclass`, rule a/b). Findings:
            the set of oclass values of a canonical key present on both sides (bucket `oclass`). A side that has
            the column while the other has not is reported under MISSING FILES (`oclass(status)(B)`, ...).
  status    `unknown:recognisedLater` is its own canonical class `recognisedLater` (Lean) = the reference's
            unknown row of kind `recognisedLater`; any other unknown stays `unknown` / `partial`.
  certs     okRecognised and okRecognisedUnverifiedBy are the canonical verdict `recognised`: a passed
            certificate, but a different verdict from `ok` (recognised on one side only is an okMismatch).
            Verified against unverified is informational.
  classes   classes.tsv: id -> class, claim, verdict (canonical), field_limit, doctrine, witness. Buckets onlyA /
            onlyB / class / claim / verdict / display / witness. One side without the file: MISSING FILES.
  summary   class_rows, class_bad_rows, recognised_rows, operative_rows of the Lean's summary.tsv against the
            reference's ref_stats.tsv (a sharded summary repeats a key: equal values are taken once, differing
            values are summed). Compared when either side has one of the four keys.
  atRisk    the new family recognisedLater (citing, cited) is in labels.json.
Round 6 (round6/history/DESIGN6.md §4; skipped when neither side has an anchor counter):
  certs     the five anchor reasons (anchorMismatch ... anchorPart) are rejections, each its own canonical reason.
  summary   anchor_rows, anchor_unknown_ids, anchor_duplicates, and the bad lines of history_anchor.tsv (the
            Lean's `bad_rows history_anchor.tsv n` line, the reference's anchor_bad_rows); a missing key is 0.
Round 7 (round7/DESIGN7.md §1-3; skipped when neither side has a round-7 counter):
  certs     the eight new reasons (joinedMismatch ... orderHeadNotAllowed) are rejections, each its own canonical
            reason (labels.json).
  summary   joined_unknown_ids, joined_extra, joined_history_ignored, joined_witness_ignored, hclaim_unknown_ids,
            hclaim_duplicates and the bad lines of joined.tsv / history_claim.tsv (the Lean's `bad_rows <file> n`);
            a missing key is 0. joined_rows, hclaim_rows, doctrine_rows only when both sides write them.
Round 8 (round8/DESIGN8.md §4-5; skipped when neither side has a bridge counter):
  certs     the seven bridge reasons (bridgeMismatch ... bridgeChain, bridgeActor) are rejections, each its own canonical reason.
  summary   bridge_unknown_ids, bridge_duplicates and the bad lines of history_bridge.tsv; a missing key is 0.
            bridge_rows and hclaim_anchorwide_unused only when both sides write them.
Round 9 (round9/DESIGN9.md §4; skipped when neither side has a zone counter):
  certs     partZone is a rejection, its own canonical reason.
  summary   zone_bad_nodes, zone_missing_rows and the bad lines of part_zone.tsv; a missing key is 0. zone_nodes,
            zone_lines, zone_checked_rows, zone_failed_rows only when both sides write them.
Round 10 (round10/DESIGN10.md §4, D10-5, D10-6; skipped when neither side has a remand counter):
  certs     remandCourt, remandDate, remandDocket, remandCue, remandTie are rejections, each its own canonical reason.
  summary   remand_lines, remand_checked_rows, remand_failed_rows, remand_dup_rows and the bad lines of
            history_remand.tsv (remand_bad_rows); a missing key is 0.
  (§6, D10-8/9) certs: trialBridgeD, trialBridgeT, trialBridgeDate are rejections; summary: tbridge_lines,
            tbridge_dup_rows, tbridge_bad_rows (`bad_rows history_tbridge.tsv`); a missing key is 0.
Exit status 0 if no disagreements, 1 otherwise.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

OPEN = 99999999
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.join(HERE, 'labels.json')
FILES = ('status', 'findings', 'certs', 'splits', 'conflicts', 'lines', 'horty')
FILES5 = ('classes', 'summary')      # round 5: reported only when compared


def read(path):
    if not os.path.exists(path):
        return None
    out = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            if line:
                out.append(line.split('\t'))
    return out


def ival(s, d=0):
    try:
        return int(s)
    except (ValueError, TypeError):
        return d


def pad(p, n):
    return p + [''] * (n - len(p))


# ============================================================================ status
class Timeline:
    """Status of one (node, holding) on the diagonal t = u."""

    def __init__(self):
        self.lean = []   # (from, to_inclusive, value)
        self.ref = []    # (from, to_exclusive, conduct_from, value)

    def at(self, t):
        if self.lean:
            for (f, to, v) in self.lean:
                if f <= t <= to:
                    return v
            return NONE
        best = None
        for (f, to, c, v) in self.ref:
            if f <= t < to and c <= t and (best is None or c > best[0]):
                best = (c, v)
        return best[1] if best else NONE

    def points(self):
        ps = {0}
        for (f, to, v) in self.lean:
            ps.add(f)
            ps.add(to + 1)
        for (f, to, c, v) in self.ref:
            ps.update((f, to, c))
        return ps


NONE = ('none', '-', '-', '1', None)


def canon_status(rows, M, lines=False, oc=None):
    """-> ('lean'|'ref', {(node, holding): Timeline}). lines=True (R2-75, status_lines.tsv): the same rows with a
    last column `line` (Lean column 12, reference column 11); the key is (node, holding, line).
    Round 5: a value is (class, kind, detail, firm, oclass); oclass is None on a side without the trailing column
    (Lean: the header names it, after `path` or `line`; reference: a row has one more field, after `firm` or
    `line`). `oc` (a list, optional) receives True / False: whether this side has the column (nothing for an empty
    reference file, which cannot tell)."""
    tls = defaultdict(Timeline)
    if rows and rows[0][:6] == ['node', 'issue', 'holding', 'from', 'to', 'status']:
        has = 'oclass' in rows[0]
        ci = rows[0].index('oclass') if has else None
        if oc is not None:
            oc.append(has)
        for p in rows[1:]:
            p = pad(p, 13)
            node, hold, st = p[0], p[2] or '-', p[5]
            key = (node, hold, p[11] or '-') if lines else (node, hold)
            o = (p[ci] or '-') if has else None
            if st == 'good':
                v = ('none', '-', '-', p[7], o)
            elif st.startswith('neg:'):
                k = st[4:]
                v = ('negative', M['kind'].get(k, k), k, p[7], o)
            elif st == 'unknown:recognisedLater':
                v = ('recognisedLater', '-', st[8:], p[7], o)     # round 5: its own class
            elif st.startswith('unknown:'):
                cls = 'partial' if (st == 'unknown:partialScope' and hold == '-') else 'unknown'
                v = (cls, '-', st[8:], p[7], o)
            else:
                v = (M['status'].get(st, st), '-', st, p[7], o)
            tls[key].lean.append((ival(p[3]), ival(p[4], OPEN), v))
        return 'lean', tls
    ci = 11 if lines else 10
    for p in rows or []:
        has = len(p) > ci
        if oc is not None and not oc:
            oc.append(has)
        p = pad(p, 12)
        node, hold, st, kind = p[0], p[2] or '-', p[5], p[6]
        key = (node, hold, p[10] or '-') if lines else (node, hold)
        o = (p[ci] or '-') if has else None
        to = ival(p[4], OPEN) or OPEN
        if to >= 99991231:
            to = OPEN
        base = kind.split(':')[0]
        if st == 'negative':
            if kind.endswith(':partial'):
                v = ('partial', '-', kind, p[9] or '1', o)
            else:
                v = ('negative', M['kind'].get(base, base), kind, p[9] or '1', o)
        elif st == 'unknown' and kind == 'recognisedLater':
            v = ('recognisedLater', '-', kind, p[9] or '1', o)    # round 5: its own class
        elif st == 'unknown':
            # an unknown event that reaches only part of the decision: 'partial' as well (some part is or may be
            # changed), as the Lean writes unknown:partialScope for both
            v = ('partial' if (kind.endswith(':partial') and hold == '-') else 'unknown', '-', kind, p[9] or '1', o)
        else:
            v = ('none', '-', '-', p[9] or '1', o)
        tls[key].ref.append((ival(p[3]), to, ival(p[8]), v))
    return 'ref', tls


def valid_date(t):
    """Question dates are calendar days: a breakpoint such as 19980229 (yyyymmdd + 1, the Lean's day after
    19980228) is read as the next real day, so equivalent breakpoints compare equal."""
    import datetime
    if t <= 0 or t >= 99990000:
        return t
    y, m, d = t // 10000, t // 100 % 100, t % 100
    for _ in range(4):
        try:
            datetime.date(y, m, d)
            return y * 10000 + m * 100 + d
        except ValueError:
            if d > 1:
                y, m, d = (y + (m == 12), m % 12 + 1, 1)
            else:
                return t
    return t


def diff_status(A, B, asof, D, name='status'):
    """name='lines' (R2-75): the same comparison over (node, holding, line) keys of status_lines.tsv."""
    keys = sorted(set(A) | set(B), key=lambda k: (ival(k[0]),) + tuple(k[1:]))
    for key in keys:
        a, b = A.get(key, Timeline()), B.get(key, Timeline())
        ts = sorted({valid_date(t) for t in (a.points() | b.points()) if 0 <= t <= asof} - {0} | {0})
        seen = set()
        D.compared[name] += 1
        bad = False
        for t in ts:
            va, vb = a.at(t), b.at(t)
            rule = (vb[2] if vb[0] != 'none' else va[2]).split(':')[0]
            k = '%s@%d' % ('/'.join(key), t)
            bks = []
            if va[0] != vb[0]:
                bks.append(('status:%s/%s' % (va[0], vb[0]), rule))
            elif va[0] == 'negative' and va[1] != vb[1]:
                bks.append(('kind', '%s/%s' % (va[1], vb[1])))
            elif va[0] != 'none' and va[3] != vb[3]:
                bks.append(('firm', rule))
            # round 5: the oclass tag, wherever both sides carry it and state the same class other than good law
            if va[0] == vb[0] and va[0] != 'none' and va[4] is not None and vb[4] is not None and va[4] != vb[4]:
                bks.append(('oclass', '%s/%s' % (va[4], vb[4])))
            for bk in bks:
                bad = True
                if bk not in seen:
                    seen.add(bk)
                    D.add(name, bk[0], bk[1], k, '%s|%s' % (va[0], va[2]), '%s|%s' % (vb[0], vb[2]))
        if bad:
            D.bad_keys[name] += 1


# ============================================================================ horty (R2-78)
def canon_horty(rows):
    """-> {(family, cases): verdict}; cases = the holding ids sorted as strings. Lean: header family, court,
    verdict, cases, firm; the reference: the same columns without a header. court and firm are not compared."""
    out = {}
    if rows and rows[0][:4] == ['family', 'court', 'verdict', 'cases']:
        rows = rows[1:]
    for p in rows or []:
        p = pad(p, 5)
        out[(p[0], ','.join(sorted(x for x in p[3].split(',') if x)))] = p[2]
    return out


def diff_horty(A, B, D):
    for key in sorted(set(A) | set(B)):
        D.compared['horty'] += 1
        k = '%s %s' % key
        a, b = A.get(key), B.get(key)
        if a is None:
            D.add('horty', 'onlyB', key[0], k, '', b)
        elif b is None:
            D.add('horty', 'onlyA', key[0], k, a, '')
        elif a != b:
            D.add('horty', 'verdict', key[0], k, a, b)
        else:
            continue
        D.bad_keys['horty'] += 1


# ============================================================================ findings
def canon_findings(rows, M, ocs=None):
    """-> {canonical key: firm-set}, {uncompared kind: count}. Round 5: `ocs` (a dict, optional) receives
    {canonical key: set of oclass values} and, under the key None, whether this side has the column (Lean: the
    header names it; reference: a sixth field)."""
    out = defaultdict(set)
    unc = defaultdict(int)
    if not rows:
        return out, unc
    lean = rows[0][:3] == ['finding', 'citing', 'cited']
    has = ('oclass' in rows[0]) if lean else any(len(p) > 5 for p in rows)
    ci = rows[0].index('oclass') if (lean and has) else 5
    if ocs is not None:
        ocs[None] = has
    cites, pairs, risk = set(M['cites_findings']), set(M['pair_findings']), M['atRisk']
    for p in (rows[1:] if lean else rows):
        if lean:
            p = pad(p, 8)
            kind, i, j, detail, firm = p[0], p[1], p[2], p[4], p[5] or '1'
        else:
            p = pad(p, 6)
            kind, i, j, detail, firm = p[0], p[1], p[2], p[3], p[4] or '1'
        key = _finding_key(kind, i, j, detail, lean, cites, pairs, risk, unc, M)
        if key is None:
            continue
        out[key].add(firm)
        if has and ocs is not None:
            ocs.setdefault(key, set()).add(p[ci] or '-')
    return out, unc


def _finding_key(kind, i, j, detail, lean, cites, pairs, risk, unc, M):
    """The canonical key of one finding row, or None when the row is not compared (counted in `unc`)."""
    if kind in cites:
        if lean:
            # citesNotCitable also fires on a notCitable force (an unpublished rule), with the status as detail;
            # only the depublished status is a citation-to-negative-status finding
            if not detail.startswith('neg:') or (kind == 'citesNotCitable' and detail != 'neg:depublished'):
                unc['lean:%s:force' % kind] += 1
                return None
            k = detail[4:]
        else:
            k = detail.split(':')[0]
        return ('cites', i, j, M['kind'].get(k, k))
    if kind in pairs:
        return (kind, i, j)
    if kind == 'atRisk':
        fam = detail.split(':')[0]
        if fam in risk:
            if lean and fam == 'inferredRejection':
                i, j = j, i               # Lean writes (target, treating); canonical (source, subject)
            if fam == 'inferredSupersession':
                i, j = 'lc', i            # Lean writes (target, 0)
            elif fam == 'possiblySuperseded':
                i = 'lc'                  # the ref writes (lc:<id>, target)
            return ('atRisk:' + risk[fam], i, j)
        unc['%s:atRisk:%s' % ('lean' if lean else 'ref', fam)] += 1
        return None
    unc['%s:%s' % ('lean' if lean else 'ref', kind)] += 1
    return None


def diff_findings(A, B, D, oa=None, ob=None):
    """oa, ob (round 5): {key: oclass set} of each side, given only when both sides carry the column."""
    for key in sorted(set(A) | set(B), key=lambda k: tuple(str(x) for x in k)):
        D.compared['findings'] += 1
        k = ' '.join(str(x) for x in key)
        rule = key[0] if key[0] != 'cites' else 'cites:' + key[3]
        a, b = A.get(key), B.get(key)
        bad = True
        if a is None:
            D.add('findings', 'onlyB', rule, k, '', ','.join(sorted(b)))
        elif b is None:
            D.add('findings', 'onlyA', rule, k, ','.join(sorted(a)), '')
        elif ('1' in a) != ('1' in b):
            D.add('findings', 'firm', rule, k, ','.join(sorted(a)), ','.join(sorted(b)))
        else:
            bad = False
        if oa is not None and ob is not None and a is not None and b is not None \
                and oa.get(key, set()) != ob.get(key, set()):
            D.add('findings', 'oclass', rule, k, ','.join(sorted(oa.get(key, ()))), ','.join(sorted(ob.get(key, ()))))
            bad = True
        if bad:
            D.bad_keys['findings'] += 1


# ============================================================================ certs
TABLE = {'treatments.tsv': 'treatment', 'history.tsv': 'history', 'holdings.tsv': 'holding',
         'treatment': 'treatment', 'history': 'history', 'holding': 'holding'}


def canon_certs(rows, M):
    out = {}
    if not rows:
        return out
    if rows[0][:2] == ['table', 'id']:
        rows = rows[1:]
    for p in rows:
        p = pad(p, 3)
        out[(TABLE.get(p[0], p[0]), p[1])] = (p[2], M['reason'].get(p[2], p[2]))
    return out


def diff_certs(A, B, D):
    for key in sorted(set(A) | set(B)):
        D.compared['certs'] += 1
        a, b = A.get(key, ('missing', 'missing')), B.get(key, ('missing', 'missing'))
        k = '%s:%s' % key
        # round 5: `recognised` is a passed certificate too, but not the same verdict as `ok`
        pa, pb = a[1] in PASSED, b[1] in PASSED
        if pa != pb or 'missing' in (a[1], b[1]) or (pa and a[1] != b[1]):
            D.add('certs', 'okMismatch:%s/%s' % (a[1], b[1]), key[0], k, a[0], b[0])
            D.bad_keys['certs'] += 1
        elif a[1] != b[1]:
            D.info['certs reasonOnly %s/%s' % (a[1], b[1])] += 1
        elif a[1] == 'recognised' and a[0] != b[0]:
            D.info['certs recognised %s/%s' % (a[0], b[0])] += 1


PASSED = ('ok', 'recognised')


# ============================================================================ classes (round 5, DESIGN5 §5.1)
def canon_classes(rows, M):
    """-> {id: (class, claim, canonical verdict, field_limit, doctrine, witness, raw verdict)}. Lean: header
    id, class, claim, verdict, field_limit, doctrine, witness; the reference: the same columns, no header."""
    out = {}
    if rows and rows[0][:3] == ['id', 'class', 'claim']:
        rows = rows[1:]
    for p in rows or []:
        p = pad(p, 7)
        out[p[0]] = (p[1], p[2] or '-', M['reason'].get(p[3], p[3]), p[4] or '-', p[5] or '-', p[6] or '-', p[3])
    return out


def diff_classes(A, B, D):
    for key in sorted(set(A) | set(B)):
        D.compared['classes'] += 1
        a, b = A.get(key), B.get(key)
        bad = True
        if a is None:
            D.add('classes', 'onlyB', b[0], key, '', b[0])
        elif b is None:
            D.add('classes', 'onlyA', a[0], key, a[0], '')
        else:
            bad = False
            if a[0] != b[0]:
                D.add('classes', 'class', '%s/%s' % (a[0], b[0]), key, a[0], b[0])
                bad = True
            if a[1] != b[1]:
                D.add('classes', 'claim', '%s/%s' % (a[1], b[1]), key, a[1], b[1])
                bad = True
            va, vb = a[2], b[2]
            if (va in PASSED) != (vb in PASSED) or (va in PASSED and va != vb):
                D.add('classes', 'verdict', '%s/%s' % (va, vb), key, a[6], b[6])
                bad = True
            elif va != vb:
                D.info['classes reasonOnly %s/%s' % (va, vb)] += 1
            if a[3:5] != b[3:5]:
                D.add('classes', 'display', a[0], key, '|'.join(a[3:5]), '|'.join(b[3:5]))
                bad = True
            if a[5] != b[5]:
                D.add('classes', 'witness', a[0], key, a[5], b[5])
                bad = True
        if bad:
            D.bad_keys['classes'] += 1


# ============================================================================ summary (round 5, DESIGN5 §5.1)
SUMMARY_KEYS = ('class_rows', 'class_bad_rows', 'recognised_rows', 'operative_rows')
# round 6 (DESIGN6 §4; round6/history/REF_QUESTIONS.md Q-11): the anchor table's counters. The Lean summary writes
# anchor_rows, anchor_unknown_ids, anchor_duplicates and `bad_rows <tab> history_anchor.tsv <tab> n`; the reference
# writes the first three under the same names and the last as anchor_bad_rows. Compared only when either side has
# one of them (a missing key is then 0), so a pair of directories without an anchor table is compared as before.
# The Lean's anchored_admitted / anchored_rejected are not compared: they count power and date order, which the
# reference decides in the status layer (the status rows are compared).
SUMMARY_KEYS6 = ('anchor_rows', 'anchor_unknown_ids', 'anchor_duplicates', 'anchor_bad_rows')
# round 7 (round7/DESIGN7.md §1 and lead ruling D7-6): the counters of joined.tsv and history_claim.tsv. The names
# below are those of DESIGN7 / D7-6; the Lean's `bad_rows <tab> joined.tsv <tab> n` and `bad_rows <tab>
# history_claim.tsv <tab> n` lines are the reference's joined_bad_rows and hclaim_bad_rows. Compared when either side
# has one of them (a missing key is then 0). SUMMARY_KEYS7_BOTH (the reference's own row counts) are compared only
# when both sides write the key.
SUMMARY_KEYS7 = ('joined_unknown_ids', 'joined_extra', 'joined_history_ignored', 'joined_witness_ignored',
                 'joined_bad_rows', 'hclaim_unknown_ids', 'hclaim_duplicates', 'hclaim_bad_rows')
SUMMARY_KEYS7_BOTH = ('joined_rows', 'hclaim_rows', 'doctrine_rows', 'doctrine_admitted')
# round 8 (round8/DESIGN8.md §4-5; round8/agents/ref8/REF_QUESTIONS8.md Q8-9): the bridge table's counters, compared
# when either side has one (a missing key is then 0); the Lean's `bad_rows <tab> history_bridge[.tsv] <tab> n` line is
# the reference's bridge_bad_rows. SUMMARY_KEYS8_BOTH only when both sides write the key.
SUMMARY_KEYS8 = ('bridge_unknown_ids', 'bridge_duplicates', 'bridge_bad_rows')
SUMMARY_KEYS8_BOTH = ('bridge_rows', 'hclaim_anchorwide_unused')
# round 9 (round9/DESIGN9.md §4; round9/agents/ref9/REF_QUESTIONS9.md Q9-6, Q9-9): the part-zone counters, compared
# when either side has one (a missing key is then 0); the Lean's `bad_rows <tab> part_zone[.tsv] <tab> n` line is the
# reference's zone_bad_rows. SUMMARY_KEYS9_BOTH only when both sides write the key.
SUMMARY_KEYS9 = ('zone_bad_nodes', 'zone_missing_rows', 'zone_bad_rows')
SUMMARY_KEYS9_BOTH = ('zone_nodes', 'zone_lines', 'zone_checked_rows', 'zone_failed_rows')
# round 10 (round10/DESIGN10.md §4, D10-6; round10/agents/ref10/REF_QUESTIONS10.md Q10-9): the remand table's
# counters, compared when either side has one (a missing key is then 0); the Lean's `bad_rows <tab>
# history_remand[.tsv] <tab> n` line is the reference's remand_bad_rows.
SUMMARY_KEYS10 = ('remand_lines', 'remand_checked_rows', 'remand_failed_rows', 'remand_dup_rows', 'remand_bad_rows',
                  'tbridge_lines', 'tbridge_dup_rows', 'tbridge_bad_rows')   # (+ DESIGN10 §6, Q10-17)
# round 11 (round11/DESIGN11.md §5.1; round11/agents/ref11/REF_QUESTIONS11.md Q11-4): the anchorTribunal claim's
# counters, compared when either side has one (a missing key is then 0).
SUMMARY_KEYS11 = ('hclaim_anchortribunal', 'hclaim_anchortribunal_unused',
                  # §5.2 (D11-5): the identity table's counters; the Lean's `bad_rows <tab> history_identity[.tsv]
                  # <tab> n` line is the reference's identity_bad_rows
                  'identity_lines', 'identity_checked_rows', 'identity_failed_rows', 'identity_dup_rows',
                  'identity_bad_rows')
BAD_ROWS_KEY = {'history_anchor.tsv': 'anchor_bad_rows', 'joined.tsv': 'joined_bad_rows',
                'history_claim.tsv': 'hclaim_bad_rows', 'history_bridge.tsv': 'bridge_bad_rows',
                'history_bridge': 'bridge_bad_rows', 'part_zone.tsv': 'zone_bad_rows', 'part_zone': 'zone_bad_rows',
                'history_remand.tsv': 'remand_bad_rows', 'history_remand': 'remand_bad_rows',
                'history_tbridge.tsv': 'tbridge_bad_rows', 'history_tbridge': 'tbridge_bad_rows',
                'history_identity.tsv': 'identity_bad_rows', 'history_identity': 'identity_bad_rows'}


def canon_summary(d):
    """-> {key: value} for the four round-5 counters and the four round-6 ones, from summary.tsv (Lean) or
    ref_stats.tsv (reference); None when the directory has neither file. A sharded Lean summary repeats every key
    once per shard: equal values are taken once, differing values are summed."""
    rows = read(os.path.join(d, 'summary.tsv'))
    if rows is None:
        rows = read(os.path.join(d, 'ref_stats.tsv'))
    if rows is None:
        return None
    vals = defaultdict(list)
    for p in rows:
        if len(p) >= 2 and (p[0] in SUMMARY_KEYS or p[0] in SUMMARY_KEYS6 or p[0] in SUMMARY_KEYS7
                            or p[0] in SUMMARY_KEYS7_BOTH or p[0] in SUMMARY_KEYS8 or p[0] in SUMMARY_KEYS8_BOTH
                            or p[0] in SUMMARY_KEYS9 or p[0] in SUMMARY_KEYS9_BOTH
                            or p[0] in SUMMARY_KEYS10 or p[0] in SUMMARY_KEYS11):
            vals[p[0]].append(ival(p[1], -1))
        elif len(p) >= 3 and p[0] == 'bad_rows' and p[1] in BAD_ROWS_KEY:
            vals[BAD_ROWS_KEY[p[1]]].append(ival(p[2], -1))
    return {k: (v[0] if len(set(v)) == 1 else sum(v)) for k, v in vals.items()}


def diff_summary(A, B, D):
    if any(k in A or k in B for k in SUMMARY_KEYS):
        for key in SUMMARY_KEYS:
            a, b = A.get(key), B.get(key)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, '' if a is None else str(a), '' if b is None else str(b))
                D.bad_keys['summary'] += 1
    if any(k in A or k in B for k in SUMMARY_KEYS6):
        for key in SUMMARY_KEYS6:
            a, b = A.get(key, 0), B.get(key, 0)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, str(a), str(b))
                D.bad_keys['summary'] += 1
    if any(k in A or k in B for k in SUMMARY_KEYS7):
        for key in SUMMARY_KEYS7:
            a, b = A.get(key, 0), B.get(key, 0)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, str(a), str(b))
                D.bad_keys['summary'] += 1
    for key in SUMMARY_KEYS7_BOTH:
        if key in A and key in B:
            D.compared['summary'] += 1
            if A[key] != B[key]:
                D.add('summary', 'count', key, key, str(A[key]), str(B[key]))
                D.bad_keys['summary'] += 1
    if any(k in A or k in B for k in SUMMARY_KEYS8):
        for key in SUMMARY_KEYS8:
            a, b = A.get(key, 0), B.get(key, 0)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, str(a), str(b))
                D.bad_keys['summary'] += 1
    for key in SUMMARY_KEYS8_BOTH:
        if key in A and key in B:
            D.compared['summary'] += 1
            if A[key] != B[key]:
                D.add('summary', 'count', key, key, str(A[key]), str(B[key]))
                D.bad_keys['summary'] += 1
    if any(k in A or k in B for k in SUMMARY_KEYS9):
        for key in SUMMARY_KEYS9:
            a, b = A.get(key, 0), B.get(key, 0)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, str(a), str(b))
                D.bad_keys['summary'] += 1
    for key in SUMMARY_KEYS9_BOTH:
        if key in A and key in B:
            D.compared['summary'] += 1
            if A[key] != B[key]:
                D.add('summary', 'count', key, key, str(A[key]), str(B[key]))
                D.bad_keys['summary'] += 1
    if any(k in A or k in B for k in SUMMARY_KEYS10):
        for key in SUMMARY_KEYS10:
            a, b = A.get(key, 0), B.get(key, 0)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, str(a), str(b))
                D.bad_keys['summary'] += 1
    if any(k in A or k in B for k in SUMMARY_KEYS11):
        for key in SUMMARY_KEYS11:
            a, b = A.get(key, 0), B.get(key, 0)
            D.compared['summary'] += 1
            if a != b:
                D.add('summary', 'count', key, key, str(a), str(b))
                D.bad_keys['summary'] += 1


# ============================================================================ splits
def canon_splits(d):
    rows = read(os.path.join(d, 'splits.tsv'))
    out = set()
    unc = defaultdict(int)
    if rows and rows[0][:2] == ['kind', 'issue']:
        for p in rows[1:]:
            p = pad(p, 10)
            if p[0] == 'conflict':
                continue                     # compared in canon_conflicts
            if p[0] != 'split':
                unc['lean:' + p[0]] += 1
                continue
            c1, c2 = p[2].split('/')[0], p[3].split('/')[0]
            out.add((p[1],) + tuple(sorted((c1, c2))))
        return out, unc
    asof = read(os.path.join(d, 'splits_asof.tsv'))
    for p in (asof if asof is not None else rows or []):
        p = pad(p, 6)
        out.add((p[0],) + tuple(sorted((p[1], p[2]))))
    return out, unc


def diff_splits(A, B, D):
    for key in sorted(A | B):
        D.compared['splits'] += 1
        k = '%s %s|%s' % key
        if key not in A:
            D.add('splits', 'onlyB', key[0], k, '', 'split')
        elif key not in B:
            D.add('splits', 'onlyA', key[0], k, 'split', '')
        else:
            continue
        D.bad_keys['splits'] += 1


# ============================================================================ conflicts
def _unit(u):
    u = (u or '').strip()
    return '-' if u in ('', '-', '0') else u


def canon_conflicts(d):
    """-> {('conflict', issue, court, unit): (answers, firm-set)}; None if this side wrote no conflict output."""
    out = {}
    rows = read(os.path.join(d, 'splits.tsv'))
    if rows and rows[0][:2] == ['kind', 'issue']:          # Lean: conflict rows inside splits.tsv
        for p in rows[1:]:
            p = pad(p, 10)
            if p[0] != 'conflict':
                continue
            court, _, unit = p[2].partition('/')
            key = ('conflict', p[1], court, _unit(unit))
            ans = ','.join(sorted(x for x in p[4].split(',') if x))
            a, f = out.get(key, (ans, set()))
            out[key] = (a, f | {p[9] or '1'})
        return out
    rows = read(os.path.join(d, 'conflicts_asof.tsv'))
    if rows is None:
        return None
    for p in rows:
        p = pad(p, 5)
        key = ('conflict', p[0], p[1], _unit(p[2]))
        ans = ','.join(sorted(x for x in p[3].split(',') if x))
        a, f = out.get(key, (ans, set()))
        out[key] = (a, f | {p[4] or '1'})
    return out


def diff_conflicts(A, B, D):
    for key in sorted(set(A) | set(B)):
        D.compared['conflicts'] += 1
        k = '%s %s/%s' % key[1:]
        a, b = A.get(key), B.get(key)
        if a is None:
            D.add('conflicts', 'onlyB', key[1], k, '', b[0])
        elif b is None:
            D.add('conflicts', 'onlyA', key[1], k, a[0], '')
        elif a[0] != b[0]:
            D.add('conflicts', 'answers', key[1], k, a[0], b[0])
        elif ('1' in a[1]) != ('1' in b[1]):
            D.add('conflicts', 'firm', key[1], k, ','.join(sorted(a[1])), ','.join(sorted(b[1])))
        else:
            continue
        D.bad_keys['conflicts'] += 1


# ============================================================================ driver
class Diff:
    def __init__(self, ex):
        self.buckets = defaultdict(int)
        self.keys = defaultdict(set)
        self.examples = defaultdict(list)
        self.rows = []
        self.ex = ex
        self.compared = defaultdict(int)
        self.bad_keys = defaultdict(int)
        self.info = defaultdict(int)

    def add(self, file, bucket, rule, key, a, b):
        bk = (file, bucket, rule)
        self.buckets[bk] += 1
        self.keys[bk].add(key.split('@')[0])
        if len(self.examples[bk]) < self.ex:
            self.examples[bk].append((key, a, b))
        self.rows.append((file, bucket, rule, key, a, b))


def load_map(path):
    with open(path or DEFAULT_MAP, encoding='utf-8') as f:
        M = json.load(f)
    for k in ('status', 'kind', 'reason', 'atRisk'):
        M.setdefault(k, {})
    M.setdefault('cites_findings', [])
    M.setdefault('pair_findings', [])
    return M


def compare(a_dir, b_dir, M, asof=20261112, ex=3):
    D = Diff(ex)
    missing = []
    for fn in ('status.tsv', 'findings.tsv', 'certs.tsv', 'splits.tsv'):
        for side, d in (('A', a_dir), ('B', b_dir)):
            if not os.path.exists(os.path.join(d, fn)):
                missing.append('%s(%s)' % (fn, side))
    def one_sided(what, ha, hb):
        # round 5: the oclass column on one side only (an empty reference file cannot tell: [] is no evidence)
        if ha and hb and ha[0] != hb[0]:
            missing.append('oclass(%s)(%s)' % (what, 'B' if ha[0] else 'A'))

    sa, sb = read(os.path.join(a_dir, 'status.tsv')), read(os.path.join(b_dir, 'status.tsv'))
    if sa is not None and sb is not None:
        ha, hb = [], []
        diff_status(canon_status(sa, M, oc=ha)[1], canon_status(sb, M, oc=hb)[1], asof, D)
        one_sided('status', ha, hb)
    fa, fb = read(os.path.join(a_dir, 'findings.tsv')), read(os.path.join(b_dir, 'findings.tsv'))
    if fa is not None and fb is not None:
        oa, ob = {}, {}
        (ca, ua), (cb, ub) = canon_findings(fa, M, oa), canon_findings(fb, M, ob)
        both = oa.get(None) and ob.get(None)
        diff_findings(ca, cb, D, oa if both else None, ob if both else None)
        if None in oa and None in ob:
            one_sided('findings', [oa[None]], [ob[None]])
        for k, n in list(ua.items()) + list(ub.items()):
            D.info['findings uncompared ' + k] += n
    ca, cb = read(os.path.join(a_dir, 'certs.tsv')), read(os.path.join(b_dir, 'certs.tsv'))
    if ca is not None and cb is not None:
        diff_certs(canon_certs(ca, M), canon_certs(cb, M), D)
    if os.path.exists(os.path.join(a_dir, 'splits.tsv')) and os.path.exists(os.path.join(b_dir, 'splits.tsv')):
        (xa, ua), (xb, ub) = canon_splits(a_dir), canon_splits(b_dir)
        diff_splits(xa, xb, D)
        for k, n in list(ua.items()) + list(ub.items()):
            D.info['splits uncompared ' + k] += n
    qa, qb = canon_conflicts(a_dir), canon_conflicts(b_dir)
    if qa is not None and qb is not None:
        diff_conflicts(qa, qb, D)
    elif (qa is None) != (qb is None):
        missing.append('conflicts(%s)' % ('A' if qa is None else 'B'))
    # R2-75 / R2-78: the two round-2 files. An output directory written before round 2 has neither: the comparison
    # is then skipped and the file is not reported as missing.
    la, lb = read(os.path.join(a_dir, 'status_lines.tsv')), read(os.path.join(b_dir, 'status_lines.tsv'))
    if la is not None and lb is not None:
        ha, hb = [], []
        diff_status(canon_status(la, M, lines=True, oc=ha)[1], canon_status(lb, M, lines=True, oc=hb)[1], asof, D,
                    'lines')
        one_sided('lines', ha, hb)
    ha, hb = read(os.path.join(a_dir, 'horty.tsv')), read(os.path.join(b_dir, 'horty.tsv'))
    if ha is not None and hb is not None:
        diff_horty(canon_horty(ha), canon_horty(hb), D)
    # round 5 (DESIGN5 §5.1): classes.tsv and the four summary counters. Neither side has them: nothing is
    # compared and nothing is reported (round 4). One side only: reported as missing.
    ka, kb = read(os.path.join(a_dir, 'classes.tsv')), read(os.path.join(b_dir, 'classes.tsv'))
    if ka is not None and kb is not None:
        diff_classes(canon_classes(ka, M), canon_classes(kb, M), D)
    elif (ka is None) != (kb is None):
        missing.append('classes.tsv(%s)' % ('A' if ka is None else 'B'))
    ma, mb = canon_summary(a_dir), canon_summary(b_dir)
    if ma is not None and mb is not None and (ma or mb):
        diff_summary(ma, mb, D)
    return D, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lean')
    ap.add_argument('ref')
    ap.add_argument('--tsv', help='write every disagreement: file, bucket, rule, key, a, b')
    ap.add_argument('--examples', type=int, default=3)
    ap.add_argument('--map', help='label map (default: labels.json next to this script)')
    ap.add_argument('--asof', type=int, default=20261112, help='last question date compared (the Lean asOf)')
    ap.add_argument('--quiet', action='store_true', help='one summary line per file')
    ap.add_argument('--info', action='store_true', help='also print uncompared kinds and reason-only differences')
    a = ap.parse_args()
    M = load_map(a.map)
    D, missing = compare(a.lean, a.ref, M, a.asof, a.examples)
    if a.tsv:
        with open(a.tsv, 'w', encoding='utf-8', newline='\n') as f:
            for r in D.rows:
                f.write('\t'.join(str(x) for x in r) + '\n')
    files = FILES + tuple(fn for fn in FILES5 if D.compared[fn])     # round 5 files only when compared
    if a.quiet:
        print(' | '.join('%s %d/%d' % (fn, D.bad_keys[fn], D.compared[fn]) for fn in files)
              + ('  missing: ' + ','.join(missing) if missing else ''))
    else:
        if missing:
            print('MISSING FILES: ' + ', '.join(missing))
        for fn in files:
            print('%-9s compared %6d keys   disagreeing %d' % (fn, D.compared[fn], D.bad_keys[fn]))
        if D.buckets:
            print('\nfile      bucket                                   rule                         count')
            for (file, bucket, rule), n in sorted(D.buckets.items(), key=lambda kv: (kv[0][0], -kv[1], kv[0])):
                print('%-9s %-40s %-28s %5d' % (file, bucket, rule, len(D.keys[(file, bucket, rule)])))
                for (k, l, r) in D.examples[(file, bucket, rule)]:
                    print('            e.g. %s   A=%s   B=%s' % (k, l, r))
        if a.info and D.info:
            print('\ninformational (not disagreements):')
            for k, n in sorted(D.info.items()):
                print('  %-60s %d' % (k, n))
    sys.exit(1 if D.buckets or missing else 0)


if __name__ == '__main__':
    main()
