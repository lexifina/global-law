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


NONE = ('none', '-', '-', '1')


def canon_status(rows, M, lines=False):
    """-> ('lean'|'ref', {(node, holding): Timeline}). lines=True (R2-75, status_lines.tsv): the same rows with a
    last column `line` (Lean column 12, reference column 11); the key is (node, holding, line)."""
    tls = defaultdict(Timeline)
    if rows and rows[0][:6] == ['node', 'issue', 'holding', 'from', 'to', 'status']:
        for p in rows[1:]:
            p = pad(p, 12)
            node, hold, st = p[0], p[2] or '-', p[5]
            key = (node, hold, p[11] or '-') if lines else (node, hold)
            if st == 'good':
                v = ('none', '-', '-', p[7])
            elif st.startswith('neg:'):
                k = st[4:]
                v = ('negative', M['kind'].get(k, k), k, p[7])
            elif st.startswith('unknown:'):
                cls = 'partial' if (st == 'unknown:partialScope' and hold == '-') else 'unknown'
                v = (cls, '-', st[8:], p[7])
            else:
                v = (M['status'].get(st, st), '-', st, p[7])
            tls[key].lean.append((ival(p[3]), ival(p[4], OPEN), v))
        return 'lean', tls
    for p in rows or []:
        p = pad(p, 11)
        node, hold, st, kind = p[0], p[2] or '-', p[5], p[6]
        key = (node, hold, p[10] or '-') if lines else (node, hold)
        to = ival(p[4], OPEN) or OPEN
        if to >= 99991231:
            to = OPEN
        base = kind.split(':')[0]
        if st == 'negative':
            if kind.endswith(':partial'):
                v = ('partial', '-', kind, p[9] or '1')
            else:
                v = ('negative', M['kind'].get(base, base), kind, p[9] or '1')
        elif st == 'unknown':
            # an unknown event that reaches only part of the decision: 'partial' as well (some part is or may be
            # changed), as the Lean writes unknown:partialScope for both
            v = ('partial' if (kind.endswith(':partial') and hold == '-') else 'unknown', '-', kind, p[9] or '1')
        else:
            v = ('none', '-', '-', p[9] or '1')
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
            if va[0] != vb[0]:
                bk = ('status:%s/%s' % (va[0], vb[0]), rule)
            elif va[0] == 'negative' and va[1] != vb[1]:
                bk = ('kind', '%s/%s' % (va[1], vb[1]))
            elif va[0] != 'none' and va[3] != vb[3]:
                bk = ('firm', rule)
            else:
                continue
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
def canon_findings(rows, M):
    """-> {canonical key: firm-set}, {uncompared kind: count}"""
    out = defaultdict(set)
    unc = defaultdict(int)
    if not rows:
        return out, unc
    lean = rows[0][:3] == ['finding', 'citing', 'cited']
    cites, pairs, risk = set(M['cites_findings']), set(M['pair_findings']), M['atRisk']
    for p in (rows[1:] if lean else rows):
        if lean:
            p = pad(p, 7)
            kind, i, j, detail, firm = p[0], p[1], p[2], p[4], p[5] or '1'
        else:
            p = pad(p, 5)
            kind, i, j, detail, firm = p[0], p[1], p[2], p[3], p[4] or '1'
        if kind in cites:
            if lean:
                # citesNotCitable also fires on a notCitable force (an unpublished rule), with the status as detail;
                # only the depublished status is a citation-to-negative-status finding
                if not detail.startswith('neg:') or (kind == 'citesNotCitable' and detail != 'neg:depublished'):
                    unc['lean:%s:force' % kind] += 1
                    continue
                k = detail[4:]
            else:
                k = detail.split(':')[0]
            out[('cites', i, j, M['kind'].get(k, k))].add(firm)
        elif kind in pairs:
            out[(kind, i, j)].add(firm)
        elif kind == 'atRisk':
            fam = detail.split(':')[0]
            if fam in risk:
                if lean and fam == 'inferredRejection':
                    i, j = j, i               # Lean writes (target, treating); canonical (source, subject)
                if fam == 'inferredSupersession':
                    i, j = 'lc', i            # Lean writes (target, 0)
                elif fam == 'possiblySuperseded':
                    i = 'lc'                  # the ref writes (lc:<id>, target)
                out[('atRisk:' + risk[fam], i, j)].add(firm)
            else:
                unc['%s:atRisk:%s' % ('lean' if lean else 'ref', fam)] += 1
        else:
            unc['%s:%s' % ('lean' if lean else 'ref', kind)] += 1
    return out, unc


def diff_findings(A, B, D):
    for key in sorted(set(A) | set(B), key=lambda k: tuple(str(x) for x in k)):
        D.compared['findings'] += 1
        k = ' '.join(str(x) for x in key)
        rule = key[0] if key[0] != 'cites' else 'cites:' + key[3]
        a, b = A.get(key), B.get(key)
        if a is None:
            D.add('findings', 'onlyB', rule, k, '', ','.join(sorted(b)))
        elif b is None:
            D.add('findings', 'onlyA', rule, k, ','.join(sorted(a)), '')
        elif ('1' in a) != ('1' in b):
            D.add('findings', 'firm', rule, k, ','.join(sorted(a)), ','.join(sorted(b)))
        else:
            continue
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
        pa, pb = a[1] == 'ok', b[1] == 'ok'
        if pa != pb or 'missing' in (a[1], b[1]):
            D.add('certs', 'okMismatch:%s/%s' % (a[1], b[1]), key[0], k, a[0], b[0])
            D.bad_keys['certs'] += 1
        elif a[1] != b[1]:
            D.info['certs reasonOnly %s/%s' % (a[1], b[1])] += 1


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
    sa, sb = read(os.path.join(a_dir, 'status.tsv')), read(os.path.join(b_dir, 'status.tsv'))
    if sa is not None and sb is not None:
        diff_status(canon_status(sa, M)[1], canon_status(sb, M)[1], asof, D)
    fa, fb = read(os.path.join(a_dir, 'findings.tsv')), read(os.path.join(b_dir, 'findings.tsv'))
    if fa is not None and fb is not None:
        (ca, ua), (cb, ub) = canon_findings(fa, M), canon_findings(fb, M)
        diff_findings(ca, cb, D)
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
        diff_status(canon_status(la, M, lines=True)[1], canon_status(lb, M, lines=True)[1], asof, D, 'lines')
    ha, hb = read(os.path.join(a_dir, 'horty.tsv')), read(os.path.join(b_dir, 'horty.tsv'))
    if ha is not None and hb is not None:
        diff_horty(canon_horty(ha), canon_horty(hb), D)
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
    files = ('status', 'findings', 'certs', 'splits', 'conflicts', 'lines', 'horty')
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
