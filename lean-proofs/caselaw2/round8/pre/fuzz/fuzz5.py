#!/usr/bin/env python3
"""fuzz5.py - round 5 of the glue fuzzer (caselaw-lean-2/round5/DESIGN5.md; results in FUZZ.md "Round 5").

  python3 -X utf8 fuzz5.py gen   --n 400 [--seed 5] --dir D     # cases with witness rows and a class table
  python3 -X utf8 fuzz5.py run   --dir D [--jobs 12]            # Lean dumper (2 passes), runner on every variant,
                                                                 # the round-4 runner (FUZZ_LP4), the reference
  python3 -X utf8 fuzz5.py check --dir D                        # the properties; report.json in D
  python3 -X utf8 fuzz5.py all   --n 400 --dir D
  python3 -X utf8 fuzz5.py oracle --n 5000 --dir D              # no Lean: generate, reference, check against the oracle
  python3 -X utf8 fuzz5.py directed --dir D                     # the hand-built cases (minimal reproducers)

A case is a case of fuzz.py (fixtures + 1-4 certificate scenarios) plus:
* 1-3 witness scenarios: decisions X, Y, W, a `treatments.tsv` row "X was overruled by Y" certified on W's text, a
  `treatment_witness.tsv` line and (usually) a `recognised` claim in `treatment_class.tsv`;
* 0-2 operative scenarios: decisions X, Y, an explicit `disapproved` row certified on Y's text and (usually) an
  `operativeWords` claim;
* junk class lines (unknown ids, unknown claim words, duplicates, claims on the wrong kind of row, short and long
  lines), byte-level mutations of the two optional tables, a class file that is empty / absent / blank lines only /
  a BOM only, sometimes a `cite_index.tsv`.
W's and Y's texts are the fuzzer's nasty texts; the names of X and Y sit in the quote, or only in the window, with
NBSP, curly quotes, combining marks, astral characters, zero-width spaces, homoglyphs and full-width digits; the
sentence's spaces become tabs, newlines, CRLF or NBSP at random.

Variants of every case, written at generation, for the metamorphic properties: `vB` (class file removed), `vC`
(class file empty), `vD` (only the lines the oracle keeps), `vE` (`vD` without the claims on the wrong kind of row).

The oracle is written from DESIGN5.md, SCHEMA.md and round3/implicit_schema.md, not from the Lean or the reference;
the phrase lists are read from the single table tools/caselaw2/cues/cue_table.json. Court power is not modelled: it
is taken as designed for the courts the scenarios use (the Supreme Court over itself and over the Fifth Circuit: yes;
a Fifth Circuit panel over the Supreme Court or over an earlier panel: no; the Fifth Circuit en banc over a panel:
yes) and only while the courts and rules tables are the fixtures'; everywhere else the oracle makes no prediction.
"""
import argparse
import hashlib
import json
import os
import random
import shutil
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fuzz as F  # noqa: E402

CUE = json.load(open(os.path.join(F.LP, 'tools', 'caselaw2', 'cues', 'cue_table.json'), encoding='utf-8'))
NEG = ('overruled', 'disapproved', 'recededFrom', 'abrogated')
TKINDS = NEG + ('supersededByEnactment', 'limited', 'questioned', 'criticized', 'distinguished', 'followed',
                'declinedToFollow')
CLAIMS = ('recognised', 'operativeWords')
PARTS = ('majority', 'plurality', 'perCuriam')
CLASSES = ('selfAnnounced', 'operativeWords', 'recognised', 'atRiskWitness')
WIT, CLS, IDX = 'treatment_witness.tsv', 'treatment_class.tsv', 'cite_index.tsv'
RULE_FILES = ('courts2.tsv', 'succession.tsv', 'adoption.tsv', 'system_rules.tsv')
ASOF = 20261112
OUTS = ('certs', 'status', 'status_lines', 'findings', 'splits', 'horty')
LP4 = os.environ.get('FUZZ_LP4', '')


# ------------------------------------------------------------------------------------------------- oracle: strings
def lower(s):
    """ASCII lower-casing only (the checker's; a Kelvin sign is not a k)."""
    return ''.join(chr(ord(c) + 32) if 'A' <= c <= 'Z' else c for c in s)


def is_alnum(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9'


def compact(s):
    return ''.join(c for c in lower(s) if is_alnum(c))


def words(s):
    return ' ' + ''.join(c if is_alnum(c) else ' ' for c in lower(s)) + ' '


def resolves(ev, ctx, target, idx):
    """SCHEMA target_evidence in a context: `cite:` compacted in the compacted context and, with a citation index,
    resolving to the node; `name:` every token of length >= 3 a whole word."""
    if ev.startswith('cite:'):
        c = compact(ev[5:])
        return c != '' and c in compact(ctx) and (idx is None or idx.get(c) == target)
    if ev.startswith('name:'):
        toks = [compact(t) for t in lower(ev[5:]).split(' ')]
        toks = [t for t in toks if len(t) >= 3]
        w = words(ctx)
        return bool(toks) and all(' ' + t + ' ' in w for t in toks)
    return False


def temporal_ok(s):
    return s in ('retroactive', 'pureProspective', 'unknown') or (
        s.startswith('prospectiveFrom:') and F.is_nat(s[16:]))


# ------------------------------------------------------------------------------------------------- oracle: tables
class Oracle:
    pass


def oracle_class(data, treat_ids):
    """DESIGN5 section 1. -> (claims {id: (claim, field_limit, doctrine, src)} in file order, bad, dup, extra,
    extra_ids, rows5, loader_bad).
    bad: lines that are not UTF-8, have fewer than 5 fields, an unknown claim word or an id that is no treatments
    row. dup: a later line for an id already taken (the first wins; whether it is counted is not said). extra: a
    line with more than 5 fields (DESIGN5 says only "fewer than 5"; SCHEMA files have exactly their columns, FB-L1:
    taken as rejected); extra_ids: the ids such a line would claim if its first 5 fields were read. rows5: every
    5-field line (what a loader keeps); loader_bad: the lines it cannot keep."""
    acc, bad, dup, extra, extra_ids, rows5, lbad = {}, 0, 0, 0, set(), [], 0
    len_acc, len_bad = set(), 0          # the other reading: the first 5 fields of a longer line are read
    for _, l in F.oracle_lines(data):
        f = l.split('\t') if l is not None else None
        if f is not None and len(f) >= 5 and f[1] in CLAIMS and f[0] in treat_ids:
            len_acc.add(f[0])
        else:
            len_bad += 1
        if f is None or len(f) < 5:
            bad += 1
            lbad += 1
            continue
        if len(f) > 5:
            extra += 1
            lbad += 1
            if f[1] in CLAIMS and f[0] in treat_ids:
                extra_ids.add(f[0])
            continue
        rows5.append(f)
        if f[1] not in CLAIMS or f[0] not in treat_ids:
            bad += 1
        elif f[0] in acc:
            dup += 1
        else:
            acc[f[0]] = (f[1], f[2], f[3], f[4])
    return acc, bad, dup, extra, extra_ids, rows5, lbad, (len(len_acc), len_bad)


def load_oracle(d):
    O = Oracle()
    O.raw = {}
    for n in F.FILES + [WIT, CLS, IDX]:
        p = os.path.join(d, n)
        O.raw[n] = open(p, 'rb').read() if os.path.isfile(p) else None
    O.T = {n: F.oracle_file(n, O.raw[n] or b'') for n in F.FILES}
    O.dec = {int(r[0]): r for r in O.T['decisions2.tsv'][0]}
    O.treat = O.T['treatments.tsv'][0]
    ids = Counter(r[0] for r in O.treat)
    O.treat_ids = set(ids)
    O.dup_ids = {i for i, c in ids.items() if c > 1}
    # witness lines: 4 fields, the node a SCHEMA integer; a later line for an id replaces an earlier one (the
    # design does not say; both engines do this)
    O.wit_rows, O.wit_bad, O.wit = None, 0, {}
    if O.raw[WIT] is not None:
        O.wit_rows = []
        for _, l in F.oracle_lines(O.raw[WIT]):
            f = l.split('\t') if l is not None else None
            if f is None or len(f) != 4 or not F.is_nat(f[1]):
                O.wit_bad += 1
                continue
            O.wit_rows.append([f[0], str(int(f[1])), f[2], f[3]])
            O.wit[f[0]] = (int(f[1]), f[2])
    O.r5 = O.raw[CLS] is not None
    O.claims, O.cbad, O.cdup, O.cextra, O.extra_ids, O.rows5, O.lbad, O.lenient = {}, 0, 0, 0, set(), [], 0, (0, 0)
    if O.r5:
        O.claims, O.cbad, O.cdup, O.cextra, O.extra_ids, O.rows5, O.lbad, O.lenient = \
            oracle_class(O.raw[CLS], O.treat_ids)
    # the citation index: compacted citation -> node; a key given two nodes resolves to nothing
    O.idx = None
    if O.raw[IDX] is not None:
        m, amb = {}, set()
        for _, l in F.oracle_lines(O.raw[IDX]):
            f = l.split('\t') if l is not None else None
            if f is None or len(f) != 2 or not F.is_nat(f[1]):
                continue
            k = compact(f[0])
            if k in m and m[k] != int(f[1]):
                amb.add(k)
            m.setdefault(k, int(f[1]))
        O.idx = {k: v for k, v in m.items() if k not in amb}
    O.wins = defaultdict(list)
    for r in O.T['cert_text.tsv'][0] + O.T['holdings_cert_text.tsv'][0]:
        O.wins[r[0]].insert(0, (int(r[1]), int(r[2]), r[3]))
    # the courts and rules are the fixtures': only then is power taken as designed
    O.pristine = all(O.T[n][1] == 0 and O.T[n][0] == [[str(x) for x in r] for r in F.read_fixture(n)]
                     for n in RULE_FILES)
    return O


def effective(rid, O):
    """DESIGN5 section 1: a `recognised` claim counts only on a witness row, an `operativeWords` claim only on a
    row that is not one."""
    c = O.claims.get(rid)
    if c is None:
        return None
    if c[0] == 'recognised':
        return 'recognised' if rid in O.wit else None
    return 'operativeWords' if rid not in O.wit else None


# ------------------------------------------------------------------------------------------------- oracle: checks
def power(bn, xn, O):
    """Has decision bn's court power to overrule decision xn? True / False as designed for the scenario courts,
    None = no prediction."""
    if not O.pristine or bn not in O.dec or xn not in O.dec:
        return None
    b, x = O.dec[bn], O.dec[xn]
    if (b[5], b[6], x[5], x[6]) != ('published', 'full', 'published', 'full') or b[3] != '0' or x[3] != '0':
        return None
    if b[1] == '2906' and b[4] == 'wholeCourt' and x[1] in ('2906', '346'):
        return True
    if b[1] == '346' and x[1] == '2906':
        return False
    if b[1] == '346' and x[1] == '346' and b[4] in ('enBanc', 'panel') and x[4] == 'panel':
        return b[4] == 'enBanc'
    return None


def power_scope(bn, xn, scope, O):
    if scope.startswith('issues:') and scope != 'issues:con.counsel':
        return None
    return power(bn, xn, O)


def text_reason(r, node, mode, O):
    """The text checks of a treatments row whose certificate is from decision `node`'s text, in the order of the
    design: shaUnknown, noWindow, quoteMismatch, noCue, disqualified, targetUnresolved, partNotMajority.
    mode: 'plain' (round 4), 'recog' (DESIGN5 2.2), 'operative' (3.2). -> the first failing reason, or None."""
    kind, sha, a, b, q, ev, part = r[4], r[8], int(r[9]), int(r[10]), r[11], r[12], r[13]
    if O.dec[node][7] != sha:
        return 'shaUnknown'
    wf = [w for w in O.wins.get(sha, []) if w[0] <= a and b <= w[1] and len(w[2]) == w[1] - w[0]]
    if not wf:
        return 'noWindow'
    nq = F.norm(q)
    if not (a < b and q != '' and any(F.norm(w[2])[a - w[0]:a - w[0] + (b - a)] == nq for w in wf)):
        return 'quoteMismatch'
    ql = lower(nq)
    cues = {'plain': CUE['treat'].get(kind, []), 'recog': CUE['recognised'], 'operative': CUE['operative']}[mode]
    if not any(c and c in ql for c in cues):
        return 'noCue'
    dis = {'plain': CUE['disqualify_treat'] if kind in NEG else [], 'recog': CUE['disqualify_recognised'],
           'operative': CUE['disqualify_treat'] + CUE['disqualify_operative']}[mode]
    if any(c and c in ql for c in dis):
        return 'disqualified'
    if not resolves(ev, context(r, mode, O), int(r[2]), O.idx):
        return 'targetUnresolved'
    if part not in PARTS:
        return 'partNotMajority'
    return None


def context(r, mode, O):
    """Where a name may be found: round 4, the quote or any well-formed window covering it; round 5 modes, the
    quote itself."""
    sha, a, b, q = r[8], int(r[9]), int(r[10]), r[11]
    if mode != 'plain':
        return F.norm(q)
    wf = [w for w in O.wins.get(sha, []) if w[0] <= a and b <= w[1] and len(w[2]) == w[1] - w[0]]
    return F.norm(q) + ' ' + ' '.join(F.norm(w[2]) for w in wf)


def wit_text(r, W, bev, mode, O):
    """The witness checks that no rule set changes (implicit_schema.md steps 1-5 without standing)."""
    X, Y = int(r[2]), int(r[1])
    if W not in O.dec or r[7] != '0' or r[4] not in NEG:
        return 'witnessBadRow'
    t = text_reason(r, W, mode, O)
    if t:
        return t
    if not resolves(bev, context(r, mode, O), Y, O.idx):
        return 'byUnresolved'
    dx, dy, dw = int(O.dec[X][2]), int(O.dec[Y][2]), int(O.dec[W][2])
    if dx > dy:
        return 'targetLater'
    if dy != 0 and dw != 0 and dw < dy:
        return 'witnessEarlier'
    return None


def wit_tail(r, W, O):
    """Standing, then Y's power: 'ok', 'witnessNoStanding', 'noAuthority', or None (no prediction)."""
    X, Y = int(r[2]), int(r[1])
    pw = power(W, X, O)
    st = True if O.dec[W][1] == O.dec[X][1] else pw
    if st is None:
        return None
    if not st:
        return 'witnessNoStanding'
    return {True: 'ok', False: 'noAuthority', None: None}[power_scope(Y, X, r[5], O)]


def judge(r, O):
    """What DESIGN5 says of one treatments row. -> dict:
    verdict     the certs.tsv string, or None where it depends on court power the oracle does not predict;
    mode        plain | witness | recog | operative | badRow;
    recog_text  (recog only) the rule-independent conditions of the recognised check hold;
    cls         the class (section 5), '-' for a row with none, None when it depends on an unpredicted verdict."""
    rid, kind, explicit = r[0], r[4], r[7]
    if kind not in TKINDS or not temporal_ok(r[6]) or int(r[1]) not in O.dec or int(r[2]) not in O.dec:
        return dict(verdict='badRow', mode='badRow', cls='-')
    X, Y = int(r[2]), int(r[1])
    eff = effective(rid, O)
    out = {}
    if rid in O.wit:
        W, bev = O.wit[rid]
        bt = wit_text(r, W, bev, 'plain', O)
        base = bt or wit_tail(r, W, O)
        out = dict(verdict=base, mode='witness')
        if eff == 'recognised':
            rt = wit_text(r, W, bev, 'recog', O)
            distinct = compact(r[12][5:]) != compact(bev[5:])
            known = W in O.dec and all(int(O.dec[n][2]) != 0 for n in (X, Y, W))
            ok = rt is None and distinct and known
            out = dict(verdict=base, mode='recog', recog_text=ok)
            if ok:
                pw = power(W, X, O)
                tail = wit_tail(r, W, O)
                if pw is None or tail is None:
                    out['verdict'] = None
                elif pw and tail == 'ok':
                    out['verdict'] = 'okRecognised'
    else:
        mode = 'operative' if eff == 'operativeWords' else 'plain'
        if mode == 'operative' and not (kind == 'disapproved' and explicit == '1'):
            v = 'operativeBadRow'
        else:
            v = text_reason(r, Y, mode, O)
            if v is None:
                if int(O.dec[X][2]) > int(O.dec[Y][2]):
                    v = 'targetLater'
                elif kind in NEG:
                    v = {True: 'ok', False: 'noAuthority', None: None}[power_scope(Y, X, r[5], O)]
                else:
                    v = 'ok'
        out = dict(verdict=v, mode=mode)
    if kind not in NEG:
        out['cls'] = '-'
    elif out['mode'] == 'recog' and out['verdict'] is None:
        out['cls'] = None
    elif out['verdict'] == 'okRecognised':
        out['cls'] = 'recognised'
    elif explicit != '1':
        out['cls'] = 'atRiskWitness'
    else:
        ql = lower(F.norm(r[11]))
        out['cls'] = 'selfAnnounced' if any(c in ql for c in CUE['self_announced']) else 'operativeWords'
    return out


# ------------------------------------------------------------------------------------------------- generation
NBSP = ' '
SEPS = [' '] * 14 + ['\t', '\n', '\r\n', NBSP, '  ', '\r']
XN = ['Marlow v. Dunn', 'Hale v. Ostrander', 'Quimby v. Reyes']
XC = ['310 U.S. 450', '311 U.S. 451', '312 U.S. 452']
YN = ['Pruitt v. Okafor', 'Sato v. Lindqvist', 'Varga v. Mbeki']
YC = ['370 U.S. 330', '371 U.S. 331', '372 U.S. 332']
ON = ['Tolliver v. Finch', 'Abernathy v. Cole', 'Wexford v. Imani']
OC = ['320 U.S. 460', '321 U.S. 461', '322 U.S. 462']
RT = [('overruled', '{X}, overruled by {Y}')] * 6 + [('overruled', '{X} was overruled in {Y}')] * 6 + \
     [('overruled', '{Y}, overruling {X}')] * 6 + [
    ('overruled', '{X} is no longer good law after {Y}'),
    ('abrogated', '{X}, abrogated by {Y}'),
    ('abrogated', '{X} was abrogated in {Y}'),
    ('overruled', 'we have not overruled {X} in {Y}'),
    ('overruled', 'whether {X} was overruled by {Y}'),
    ('disapproved', '{X} was disapproved in {Y}'),
    ('recededFrom', '{X}, receded from in {Y}'),
    ('overruled', 'the dissent says {X} was overruled by {Y}'),
    ('overruled', '{X} WAS OVERRULED BY {Y}'),
    ('overruled', '{X} was over­ruled by {Y}'),
    ('overruled', '{X} was “overruled” by {Y}'),
    ('overruled', '{X} was overruled, it is argued, by {Y}'),
    ('overruled', '{X} has been repudiated by {Y}'),
    ('overruled', '{X} was OVERRULED, not Kept, by {Y}')]
OT = ['{X} is repudiated'] * 3 + ['we reject the doctrine of {X}'] * 3 + ['{X} is no longer good law'] * 2 + [
      '{X} must be regarded as overthrown', 'we reject the argument based on {X}', '{X} cannot stand',
      '{X} is disapproved', '{X} is overruled and is no longer the law', '{X} has no place in our law',
      'the claim in {X} is rejected', '{X}, overruled by later cases, is discarded', '{X} was WRONGLY DECIDED',
      'we depart from {X}', '{X} is no' + NBSP + 'longer good law', 'we disavow {X}; it is abandoned',
      '{X} IS REPUDIATED', 'the rule of {X} is no longer the law']
DECOS = [None] * 14 + ['nbsp', 'combining', 'homoglyph', 'fullwidth', 'curly', 'astral', 'upper', 'zwsp', 'lower']


def spice(rng, s):
    """Every space becomes a random separator (tab, newline, CRLF, lone CR, NBSP, two spaces)."""
    return ''.join(rng.choice(SEPS) if c == ' ' else c for c in s)


def decorate(rng, name, cite):
    d = rng.choice(DECOS)
    if d == 'nbsp':
        name, cite = name.replace(' ', NBSP), cite.replace(' ', NBSP)
    elif d == 'combining':
        name, cite = name[:3] + '́' + name[3:], cite[:1] + '́' + cite[1:]
    elif d == 'homoglyph':
        name = name.replace('a', 'а', 1)                      # Cyrillic a
    elif d == 'fullwidth':
        cite = ''.join(chr(ord(c) + 0xFEE0) if c.isdigit() else c for c in cite)
    elif d == 'curly':
        name = '“' + name + '”'
    elif d == 'astral':
        name, cite = name.replace(' v. ', '\U0001F600v.\U0001D518'), cite + '\U00010348'
    elif d == 'upper':
        name, cite = name.upper(), cite.upper()
    elif d == 'zwsp':
        name, cite = name[:2] + '​' + name[2:], cite[:2] + '​' + cite[2:]
    elif d == 'lower':
        name, cite = name.lower(), cite.lower()
    return name + ', ' + cite, d


def tokens(name):
    return name.replace(' v. ', ' ')


def certify(rng, sentence, before):
    """A nasty decision text around `sentence`; -> (sha, window row, start, end, quote, variant)."""
    pre = F.noise(rng, rng.choice([0, 0, 2, 30, 120, 500])) + before
    suf = F.noise(rng, rng.choice([0, 0, 2, 30, 120, 500]))
    if suf.startswith('\n'):
        suf = ' ' + suf
    raw = pre + sentence + suf
    T = raw.replace('\r\n', '\n')
    sha = hashlib.sha1(raw.encode('utf-8')).hexdigest()
    c0 = len(pre.replace('\r\n', '\n'))
    c1 = c0 + len(sentence.replace('\r\n', '\n'))
    a = rng.choice([c0] * 4 + [max(0, c0 - rng.randint(1, 5))])
    b = rng.choice([c1] * 4 + [min(len(T), c1 + rng.randint(1, 5))])
    var = rng.choice(['exact'] * 24 + ['bytes', 'utf16', 'plus1'])
    cleanf = F.clean_reader if rng.random() < 0.2 else F.norm
    s0, e0 = max(0, a - 400), min(len(T), b + 400)
    win = [sha, s0, e0, cleanf(T[s0:e0])]
    quote = cleanf(T[a:b])
    sa, sb = a, b
    if var == 'bytes':
        sa, sb = F.u8(T[:a]), F.u8(T[:b])
    elif var == 'utf16':
        sa, sb = F.u16(T[:a]), F.u16(T[:b])
    elif var == 'plus1':
        sa, sb = a + 1, b + 1
    return sha, win, sa, sb, quote, var


def fake_sha(tag):
    return hashlib.sha1(tag.encode('utf-8')).hexdigest()


def recog_scenario(rng, j, seed):
    X, Y, W = 300 + 10 * j, 301 + 10 * j, 302 + 10 * j
    fam = rng.choice(['S'] * 10 + ['P', 'E', 'E', 'L', 'N', 'N', 'D0', 'WE', 'TL', 'EQ', 'EQ'])
    dx = 19300101 + rng.randint(0, 20) * 10000
    dy = dx + rng.randint(1, 20) * 10000
    dw = dy + rng.randint(1, 20) * 10000
    cx = cy = cw = (2906, 'wholeCourt')
    if fam == 'P':                                   # W: a panel of X's court: standing, no power
        cx, cy, cw = (346, 'panel'), (346, 'enBanc'), (346, 'panel')
    elif fam == 'E':                                 # W: X's court en banc: power
        cx, cy, cw = (346, 'panel'), (346, 'enBanc'), (346, 'enBanc')
    elif fam == 'L':                                 # W: a lower court: no standing
        cw = (346, 'panel')
    elif fam == 'N':                                 # Y: a lower court: no power over X
        cy = (346, 'panel')
    elif fam == 'D0':                                # W's date unknown
        dw = 0
    elif fam == 'WE':                                # W earlier than Y
        dw = dy - 10000
    elif fam == 'TL':                                # X later than Y
        dx = dy + 10000
    elif fam == 'EQ':                                # W on Y's day: no unknown interval
        dw = dy
    kind, tpl = rng.choice(RT)
    xs, dxo = decorate(rng, XN[j], XC[j])
    ys, dyo = decorate(rng, YN[j], YC[j])
    place = rng.choice(['in'] * 8 + ['y_out', 'x_out', 'y_absent', 'x_absent'])
    before = ''
    if place == 'y_out':
        before, ys = 'See ' + ys + '. ', 'a later case'
    elif place == 'x_out':
        before, xs = 'See ' + xs + '. ', 'the earlier case'
    elif place == 'y_absent':
        ys = 'a later case'
    elif place == 'x_absent':
        xs = 'the earlier case'
    sentence = spice(rng, tpl.replace('{X}', xs).replace('{Y}', ys))
    sha, win, sa, sb, quote, var = certify(rng, sentence, before)
    tev = rng.choice(['cite:' + XC[j]] * 12 + ['name:' + tokens(XN[j])] * 12 +
                     ['cite:', 'name:v.', 'bogus:' + XC[j], XC[j], 'name:' + XN[j], 'cite:' + compact(XC[j])])
    bev = rng.choice(['cite:' + YC[j]] * 12 + ['name:' + tokens(YN[j])] * 12 +
                     ['cite:', 'name:v.', 'name:' + YN[j], tev, 'cite:' + XC[j].lower(), 'name:' + tokens(XN[j]).upper()])
    explicit = rng.choice(['0'] * 30 + ['1'])
    if rng.random() < 0.03:
        kind = rng.choice(['limited', 'overruledX', 'followed', ''])
    scope = rng.choice(['all'] * 9 + ['partialUnknown', 'issues:con.counsel', 'otherGrounds'])
    temporal = rng.choice(['retroactive'] * 10 + ['unknown', 'pureProspective', 'prospectiveFrom:19990101', 'sometime'])
    part = rng.choice(['majority'] * 24 + ['plurality', 'perCuriam', 'dissent', 'concurrence', 'Majority', ''])
    rid = 'tw:%d:%d:%d:%d' % (Y, X, sa, W)
    decs = [[X, cx[0], dx, 0, cx[1], 'published', 'full', fake_sha('x%d.%d' % (seed, j)), 'fuzz5'],
            [Y, cy[0], dy, 0, cy[1], 'published', 'full', fake_sha('y%d.%d' % (seed, j)), 'fuzz5'],
            [W, cw[0], dw, 0, cw[1], 'published', 'full', sha, 'fuzz5']]
    treat = [rid, Y, X, dy, kind, scope, temporal, explicit, sha, sa, sb, quote, tev, part, 'fuzz5', '0.75']
    wn = rng.choice([W] * 60 + [999, Y])
    wit = [rid, wn, bev, 'fuzz5'] if rng.random() < 0.95 else None
    claim = rng.choice(['recognised'] * 24 + [None, None, 'operativeWords', 'Recognised', 'recognized', 'recognised ', ''])
    disp = ['-', '-', '-', 'in the field of public education', '', 'as' + NBSP + 'respects “rates”', '-\r-',
            'the separate-but-equal doctrine \U0001F600']
    cls = [rid, claim, rng.choice(disp), rng.choice(disp), 'fuzz5'] if claim is not None else None
    cites = [[XC[j], X], [YC[j], Y]]
    meta = dict(kind='recog', id=rid, fam=fam, tpl=tpl, place=place, deco=[dxo, dyo], var=var, X=X, Y=Y, W=W)
    return dict(decs=decs, win=win, treat=treat, wit=wit, cls=cls, cites=cites, meta=meta)


def oper_scenario(rng, j, seed):
    X, Y = 400 + 10 * j, 401 + 10 * j
    fam = rng.choice(['S'] * 9 + ['N', 'TL', 'P'])
    dx = 19300101 + rng.randint(0, 20) * 10000
    dy = dx + rng.randint(1, 20) * 10000
    cx = cy = (2906, 'wholeCourt')
    if fam == 'N':
        cy = (346, 'panel')
    elif fam == 'TL':
        dx = dy + 10000
    elif fam == 'P':
        cx, cy = (346, 'panel'), (346, 'panel')
    tpl = rng.choice(OT)
    xs, dxo = decorate(rng, ON[j], OC[j])
    place = rng.choice(['in'] * 8 + ['x_out', 'x_absent'])
    before = ''
    if place == 'x_out':
        before, xs = 'See ' + xs + '. ', 'that case'
    elif place == 'x_absent':
        xs = 'that case'
    sentence = spice(rng, tpl.replace('{X}', xs))
    sha, win, sa, sb, quote, var = certify(rng, sentence, before)
    tev = rng.choice(['cite:' + OC[j]] * 10 + ['name:' + tokens(ON[j])] * 10 + ['cite:', 'name:v.', OC[j]])
    kind = rng.choice(['disapproved'] * 24 + ['overruled', 'abrogated', 'limited'])
    explicit = rng.choice(['1'] * 30 + ['0'])
    scope = rng.choice(['all'] * 9 + ['partialUnknown', 'issues:con.counsel'])
    temporal = rng.choice(['retroactive'] * 10 + ['unknown', 'pureProspective'])
    part = rng.choice(['majority'] * 24 + ['plurality', 'dissent', 'unknown'])
    rid = 'to:%d:%d:%d' % (Y, X, sa)
    decs = [[X, cx[0], dx, 0, cx[1], 'published', 'full', fake_sha('ox%d.%d' % (seed, j)), 'fuzz5'],
            [Y, cy[0], dy, 0, cy[1], 'published', 'full', sha, 'fuzz5']]
    treat = [rid, Y, X, dy, kind, scope, temporal, explicit, sha, sa, sb, quote, tev, part, 'fuzz5', '0.75']
    claim = rng.choice(['operativeWords'] * 20 + [None, 'recognised', 'OperativeWords', 'operative'])
    cls = [rid, claim, rng.choice(['-', '-', 'in the field of education', '']), rng.choice(['-', 'the X doctrine']),
           'fuzz5'] if claim is not None else None
    meta = dict(kind='oper', id=rid, fam=fam, tpl=tpl, place=place, deco=[dxo], var=var, X=X, Y=Y)
    return dict(decs=decs, win=win, treat=treat, wit=None, cls=cls, cites=[[OC[j], X]], meta=meta)


def junk_class(rng, tabs):
    """One junk class line: (what, fields)."""
    ids = [str(r[0]) for r in tabs['treatments.tsv']]
    what = rng.choice(['unknown_id', 'fixture', 'dup', 'dup', 'short', 'long', 'empty5', 'unknown_claim'])
    if what == 'unknown_id':
        return what, [rng.choice(['nope', '', ids[0] + ' ', ids[-1].upper(), 'treatment:1', ' ' + ids[0]]),
                      rng.choice(CLAIMS), '-', '-', 'junk']
    if what == 'fixture':                      # any row: the wrong kind of row for the claim, or an effective claim
        return what, [rng.choice(ids), rng.choice(CLAIMS), '-', '-', 'junk']
    if what == 'dup' and tabs[CLS]:
        f = [str(x) for x in rng.choice(tabs[CLS])]
        return what, [f[0], rng.choice(CLAIMS), 'again', '-', 'junk']
    if what == 'short':
        return what, [rng.choice(ids), rng.choice(CLAIMS), '-', '-']
    if what == 'long':
        return what, [rng.choice(ids), rng.choice(CLAIMS), '-', '-', 'junk', 'extra']
    if what == 'empty5':
        return what, ['', '', '', '', '']
    return 'unknown_claim', [rng.choice(ids), rng.choice(['overruled', 'recognised\r', 'RECOGNISED', 'operativewords',
                                                         'recognised,operativeWords', '-', 'operative Words']),
                             '-', '-', 'junk']


def link(src, dst):
    try:
        os.link(src, dst)
    except OSError:
        shutil.copyfile(src, dst)


def write_variants(d):
    """vB (no class file), vC (empty), vD (only the lines the oracle keeps), vE (vD without the claims on the wrong
    kind of row). Only for a case whose class file is a regular file."""
    if not os.path.isfile(os.path.join(d, CLS)):
        return
    O = load_oracle(d)
    keep = ['\t'.join((i,) + c) + '\n' for i, c in O.claims.items()]
    eff = ['\t'.join((i,) + c) + '\n' for i, c in O.claims.items() if effective(i, O)]
    names = [n for n in os.listdir(d) if n.endswith('.tsv') and os.path.isfile(os.path.join(d, n))]
    for v, content in (('vB', None), ('vC', b''), ('vD', ''.join(keep).encode('utf-8')),
                       ('vE', ''.join(eff).encode('utf-8'))):
        vd = os.path.join(d, v)
        os.makedirs(vd, exist_ok=True)
        for n in names:
            if n != CLS:
                link(os.path.join(d, n), os.path.join(vd, n))
            elif content is not None:
                with open(os.path.join(vd, n), 'wb') as f:
                    f.write(content)


def gen_case5(seed, d):
    rng = random.Random(seed)
    tabs, vars_ = F.base_tabs(rng)
    r5 = random.Random(seed * 7919 + 5)
    tabs[WIT], tabs[CLS] = [], []
    cites = [['316 U.S. 455', 0], ['478 U.S. 186', 2], ['245 Ga. 1', 13], ['530 F.2d 100', 20]]
    meta = []
    scen = [recog_scenario(r5, j, seed) for j in range(r5.randint(1, 3))] + \
           [oper_scenario(r5, j, seed) for j in range(r5.randint(0, 2))]
    for sc in scen:
        tabs['decisions2.tsv'].extend(sc['decs'])
        tabs['cert_text.tsv'].append(sc['win'])
        tabs['treatments.tsv'].append(sc['treat'])
        if sc['wit']:
            tabs[WIT].append(sc['wit'])
        if sc['cls']:
            tabs[CLS].append(sc['cls'])
        cites.extend(sc['cites'])
        meta.append(sc['meta'])
    junk = []
    for _ in range(r5.choice([0, 0, 1, 1, 2, 3, 4])):
        what, f = junk_class(r5, tabs)
        junk.append(what)
        tabs[CLS].insert(r5.randint(0, len(tabs[CLS])), f)
    ops = []
    fops = defaultdict(set)
    for _ in range(rng.choice([0, 0, 0, 0, 1, 1, 2, 3])):                    # any SCHEMA file, as fuzz.py
        n = rng.choice(F.FILES)
        if rng.random() < 0.15:
            op = rng.choice(F.FILE_OPS)
            fops[n].add(op)
            ops.append((n, op))
        else:
            ops.append((n, F.mutate_lines(rng, tabs[n], n)))
    for _ in range(r5.choice([0, 0, 0, 1, 1, 2, 3])):                        # aimed at the round-5 inputs
        n = r5.choice([CLS] * 5 + [WIT] * 2 + ['treatments.tsv', 'decisions2.tsv', 'cert_text.tsv'])
        if r5.random() < 0.2:
            op = r5.choice(F.FILE_OPS)
            fops[n].add(op)
            ops.append((n, op))
        else:
            ops.append((n, F.mutate_lines(r5, tabs[n], n)))
    cmode = r5.choice(['normal'] * 24 + ['empty', 'empty', 'absent', 'absent', 'blank', 'bomonly'])
    wmode = r5.choice(['normal'] * 24 + ['absent', 'empty'])
    imode = r5.choice(['absent'] * 6 + ['good', 'good', 'wrong', 'ambiguous'])
    os.makedirs(d, exist_ok=True)
    for n in F.FILES:
        with open(os.path.join(d, n), 'wb') as f:
            f.write(F.render(tabs[n], rng, fops[n]))
    if wmode != 'absent':
        with open(os.path.join(d, WIT), 'wb') as f:
            f.write(F.render(tabs[WIT], r5, fops[WIT]) if wmode == 'normal' else b'')
    if cmode != 'absent':
        with open(os.path.join(d, CLS), 'wb') as f:
            f.write({'normal': F.render(tabs[CLS], r5, fops[CLS]), 'empty': b'', 'blank': b'\n\r\n\r\r\n\n',
                     'bomonly': b'\xef\xbb\xbf'}[cmode])
    if imode != 'absent':
        if imode == 'wrong':
            cites[-1] = [cites[-1][0], 3]
        elif imode == 'ambiguous':
            cites.append([cites[-1][0].lower().replace(' ', ''), 3])
        with open(os.path.join(d, IDX), 'wb') as f:
            f.write(''.join('%s\t%s\n' % (c, n) for c, n in cites).encode('utf-8'))
    with open(os.path.join(d, 'case.json'), 'w', encoding='utf-8') as f:
        json.dump({'seed': seed, 'variants': vars_, 'ops': ops,
                   'r5': {'class': cmode, 'witness': wmode, 'index': imode, 'scen': meta, 'junk': junk}}, f)
    write_variants(d)


# ------------------------------------------------------------------------------------------------- directed cases
def directed(root):
    """Hand-built cases, one question each (the minimal reproducers of FUZZ_BUGS.md come from here). Each is the
    fixtures plus one clean witness scenario (Supreme Court X 1940, Y 1950, W 1960; W's text is one sentence) or
    one clean operative scenario, with one thing changed."""
    def base():
        return {n: [[str(x) for x in r] for r in F.read_fixture(n)] for n in F.FILES}

    def put(name, tabs, extra):
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        for n in F.FILES:
            with open(os.path.join(d, n), 'wb') as f:
                f.write(''.join('\t'.join(str(x) for x in r) + '\n' for r in tabs[n]).encode('utf-8'))
        for n, data in extra.items():
            if data == 'DIR':
                os.makedirs(os.path.join(d, n), exist_ok=True)
            elif data is not None:
                with open(os.path.join(d, n), 'wb') as f:
                    f.write(data)
        with open(os.path.join(d, 'case.json'), 'w', encoding='utf-8') as f:
            json.dump({'seed': name, 'variants': [], 'ops': [], 'r5': {'class': 'directed', 'witness': 'directed',
                                                                    'index': 'absent', 'scen': [], 'junk': []}}, f)
        write_variants(d)

    def wscen(tabs, sentence='Marlow v. Dunn, 310 U.S. 450, was overruled in Pruitt v. Okafor, 370 U.S. 330',
              ycourt=(2906, 'wholeCourt'), wcourt=(2906, 'wholeCourt'), lead='The Court. '):
        text = lead + sentence + '. Affirmed.'
        sha = hashlib.sha1(text.encode('utf-8')).hexdigest()
        a = len(lead)
        b = a + len(sentence)
        tabs['decisions2.tsv'] += [[300, 2906, 19400101, 0, 'wholeCourt', 'published', 'full', fake_sha('dx'), 'd'],
                                   [301, ycourt[0], 19500101, 0, ycourt[1], 'published', 'full', fake_sha('dy'), 'd'],
                                   [302, wcourt[0], 19600101, 0, wcourt[1], 'published', 'full', sha, 'd']]
        tabs['cert_text.tsv'].append([sha, 0, len(text), text])
        tabs['treatments.tsv'].append(['tw:301:300', 301, 300, 19500101, 'overruled', 'all', 'retroactive', 0, sha,
                                       a, b, sentence, 'cite:310 U.S. 450', 'majority', 'd', '0.75'])
        return b'tw:301:300\t302\tcite:370 U.S. 330\td\n'

    def oscen(tabs, sentence='Tolliver v. Finch, 320 U.S. 460, is repudiated', kind='disapproved'):
        text = 'The Court. ' + sentence + '. Reversed.'
        sha = hashlib.sha1(text.encode('utf-8')).hexdigest()
        a = len('The Court. ')
        tabs['decisions2.tsv'] += [[400, 2906, 19400101, 0, 'wholeCourt', 'published', 'full', fake_sha('ox'), 'd'],
                                   [401, 2906, 19500101, 0, 'wholeCourt', 'published', 'full', sha, 'd']]
        tabs['cert_text.tsv'].append([sha, 0, len(text), text])
        tabs['treatments.tsv'].append(['to:401:400', 401, 400, 19500101, kind, 'all', 'retroactive', 1, sha,
                                       a, a + len(sentence), sentence, 'cite:320 U.S. 460', 'majority', 'd', '0.75'])

    R = b'tw:301:300\trecognised\t-\t-\td\n'
    OW = b'to:401:400\toperativeWords\t-\t-\td\n'
    t = base(); w = wscen(t); put('d01_recognised', t, {WIT: w, CLS: R})
    t = base(); w = wscen(t); put('d02_class_absent', t, {WIT: w})
    t = base(); w = wscen(t); put('d03_class_empty', t, {WIT: w, CLS: b''})
    t = base(); w = wscen(t); put('d04_six_fields', t, {WIT: w, CLS: R[:-1] + b'\textra\n'})
    t = base(); w = wscen(t); put('d05_duplicate_first_wins', t, {WIT: w, CLS: b'tw:301:300\toperativeWords\t-\t-\td\n' + R})
    t = base(); w = wscen(t); put('d06_duplicate_same', t, {WIT: w, CLS: R + R})
    t = base(); w = wscen(t, ycourt=(346, 'panel')); put('d07_y_no_power', t, {WIT: w, CLS: R})
    t = base(); w = wscen(t, ycourt=(346, 'panel')); put('d08_y_no_power_no_claim', t, {WIT: w, CLS: b''})
    t = base(); w = wscen(t); put('d09_class_is_directory', t, {WIT: w, CLS: 'DIR'})
    t = base(); w = wscen(t); put('d10_witness_is_directory', t, {WIT: 'DIR', CLS: R})
    t = base(); w = wscen(t); put('d11_empty_display_fields', t, {WIT: w, CLS: b'tw:301:300\trecognised\t\t\td\n'})
    t = base(); w = wscen(t, sentence='Marlow v. Dunn, 310 U.S. 450, was not' + NBSP + 'overruled in Pruitt v. Okafor, 370 U.S. 330')
    put('d12_nbsp_in_disqualifier', t, {WIT: w, CLS: R})
    t = base(); w = wscen(t, sentence='That case was overruled in Pruitt v. Okafor, 370 U.S. 330',
                          lead='See Marlow v. Dunn, 310 U.S. 450. ')
    put('d13_x_only_in_window', t, {WIT: w, CLS: R})
    t = base(); oscen(t); put('d14_operative_whole', t, {CLS: OW})
    t = base(); oscen(t, sentence='we reject the doctrine of Tolliver v. Finch, 320 U.S. 460'); put('d15_operative_demoted', t, {CLS: OW})
    t = base(); oscen(t, kind='overruled'); put('d16_operative_bad_row', t, {CLS: OW})
    t = base(); oscen(t); put('d17_recognised_claim_on_explicit_row', t, {CLS: b'to:401:400\trecognised\t-\t-\td\n'})
    t = base(); w = wscen(t); put('d18_operative_claim_on_witness_row', t, {WIT: w, CLS: b'tw:301:300\toperativeWords\t-\t-\td\n'})
    t = base(); w = wscen(t); put('d19_bom_crlf', t, {WIT: w, CLS: b'\xef\xbb\xbf' + R[:-1] + b'\r\n'})
    t = base(); w = wscen(t); put('d20_trailing_tab', t, {WIT: w, CLS: R[:-1] + b'\t\n'})
    t = base(); w = wscen(t); put('d21_claim_fixture_row_operative', t, {WIT: w, CLS: b'1\toperativeWords\t-\t-\td\n'})
    t = base(); w = wscen(t, wcourt=(346, 'panel')); put('d22_w_lower_court', t, {WIT: w, CLS: R})


# ------------------------------------------------------------------------------------------------- running
def cmd_run(root, jobs, lean=True):
    dirs = F.case_dirs(root)
    chunks = [c for c in (dirs[i::jobs] for i in range(jobs)) if c]
    with ProcessPoolExecutor(jobs) as ex:
        list(ex.map(F.run_ref, dirs, chunksize=16))
        if not lean:
            return
        errs = list(ex.map(F.run_dump, chunks))
        errs += list(ex.map(F.run_dump, [[os.path.join(x, 'lean') for x in c] for c in chunks]))
        # the runner on the case and its variants; the round-4 runner on the case without its class file
        alld = [x for d in dirs for x in [d] + [os.path.join(d, v) for v in ('vB', 'vC', 'vD', 'vE')
                                                 if os.path.isdir(os.path.join(d, v))]]
        list(ex.map(F.run_runner_batch, [(k, alld[k::jobs], root) for k in range(jobs) if alld[k::jobs]]))
        if LP4:
            r4 = [os.path.join(d, 'vB') if os.path.isdir(os.path.join(d, 'vB')) else d for d in dirs
                  if not os.path.exists(os.path.join(d, CLS)) or os.path.isdir(os.path.join(d, 'vB'))]
            list(ex.map(F.run_runner_batch, [(k, r4[k::jobs], root, LP4, 'runner4') for k in range(jobs) if r4[k::jobs]]))
    with open(os.path.join(root, 'dump_stderr.txt'), 'w', encoding='utf-8') as f:
        for rc, e in errs:
            f.write('rc=%d\n%s\n' % (rc, e))


# ------------------------------------------------------------------------------------------------- checking
def rd(d, name, sub='runner'):
    p = os.path.join(d, sub, name + '-00.tsv')
    return open(p, 'rb').read() if os.path.exists(p) else None


def rows_of(b):
    return [l.split('\t') for l in b.decode('utf-8', 'replace').split('\n')[:-1]] if b is not None else None


def summary(d, sub='runner'):
    out = {}
    for f in rows_of(rd(d, 'summary', sub)) or []:
        if f[0] not in ('load_ms', 'run_ms'):
            out['\t'.join(f[:-1])] = f[-1]
    return out


def rc_ok(d, sub='runner'):
    p = os.path.join(d, sub + '.json')
    if not os.path.exists(p):
        return False
    j = json.load(open(p, encoding='utf-8'))
    return j['rc'] == 0 and not j.get('stderr')


def step(rows, node):
    """The status of a whole decision as intervals: [(from, to, status, witness_row, actor, oclass)]."""
    return sorted((int(r[3]), int(r[4]), r[5], r[8], r[9], r[11] if len(r) > 11 else None)
                  for r in rows if r[0] == str(node) and r[1] == '-' and r[2] == '-')


def at(st, t):
    return next((x for x in st if x[0] <= t <= x[1]), None)


def check_case5(arg):
    d, lean = arg
    fails, stats = [], Counter()
    cj = json.load(open(os.path.join(d, 'case.json'), encoding='utf-8'))
    O = load_oracle(d)
    r5 = O.r5
    stats['cases.class_' + cj['r5']['class']] += 1
    J = {}
    for r in O.treat:
        if r[0] in O.dup_ids:
            stats['rows.duplicate_id_skipped'] += 1
            continue
        j = judge(r, O)
        if not r5:                                  # no class table: no class, and a claim cannot exist
            j['cls'] = '-'
        J[r[0]] = j
        stats['oracle.%s.%s' % (j['mode'], j['verdict'])] += 1
        if j.get('recog_text'):
            stats['oracle.recog_text_ok'] += 1
    stats['class_lines.kept'] += len(O.claims)
    stats['class_lines.bad'] += O.cbad
    stats['class_lines.duplicate'] += O.cdup
    stats['class_lines.more_than_5_fields'] += O.cextra
    stats['class_lines.wrong_kind_of_row'] += sum(1 for i in O.claims if not effective(i, O))
    # ---------------------------------------------------------------- the reference against the oracle
    ref = json.load(open(os.path.join(d, 'ref.json'), encoding='utf-8')) if os.path.exists(
        os.path.join(d, 'ref.json')) else None
    R5 = (ref or {}).get('r5')
    if ref is not None and 'crash' in ref:
        fails.append(('REF.crash', ref['crash'][-300:]))
    elif ref is not None and r5 and R5 is None:
        fails.append(('REF.no_round5', 'the reference did not report round-5 mode'))
    elif R5 is not None:
        stats['ref.cases'] += 1
        if R5['class_bad'] != O.cbad + O.cextra:
            tag = '.DA-extra' if O.cextra and R5['class_bad'] == O.lenient[1] else \
                  '.DA-dup' if O.cdup and R5['class_bad'] == O.cbad + O.cextra + O.cdup else ''
            fails.append(('REF.class_bad_rows' + tag, 'ref %d oracle %d bad + %d long (+ %d dup)' % (
                R5['class_bad'], O.cbad, O.cextra, O.cdup)))
        if R5['class_rows'] != len(O.claims):
            fails.append(('REF.class_rows' + ('.DA-extra' if O.extra_ids and R5['class_rows'] == O.lenient[0] else ''),
                          'ref %d oracle %d' % (R5['class_rows'], len(O.claims))))
        for rid, j in J.items():
            if rid in O.extra_ids and rid not in O.claims:
                continue                                   # the reference reads a 6-field line as a claim
            if j['verdict'] is not None and j['mode'] in ('recog', 'witness'):
                rec = rid in R5['recog']
                if rec != (j['verdict'] == 'okRecognised'):
                    fails.append(('REF.recognised', '%s ref %s oracle %s' % (rid, R5['recog'].get(rid), j['verdict'])))
            if j['cls'] not in (None, '-') and j['verdict'] != 'badRow' and R5['classes'].get(rid) != j['cls']:
                fails.append(('REF.class', '%s ref %s oracle %s' % (rid, R5['classes'].get(rid), j['cls'])))
            if j['mode'] == 'operative' and j['verdict'] is not None:
                rv = ref['certs'].get('treatments|' + rid)
                if (rv == 'ok') != (j['verdict'] in ('ok', 'noAuthority', 'targetLater')) or \
                        (rv == 'operativeBadRow') != (j['verdict'] == 'operativeBadRow'):
                    fails.append(('REF.operative', '%s ref %s oracle %s' % (rid, rv, j['verdict'])))
    if not lean:
        return fails, stats
    # ---------------------------------------------------------------- Lean: P1-P5 of fuzz.py on the case itself
    f0, s0 = F.check_case(d)
    fails += f0
    stats.update(s0)
    if not rc_ok(d):
        return fails, stats
    # the two optional tables as the loaders read them (P2), and their round trip (P3)
    ld = os.path.join(d, 'lean')
    probs = {r[0]: int(r[2]) for r in F.read_tsv_rows(os.path.join(ld, 'problems.tsv'))}
    for n, want, bad in ((WIT, O.wit_rows, O.wit_bad), (CLS, O.rows5 if r5 else None, O.lbad)):
        got = F.read_tsv_rows(os.path.join(ld, n))
        if got != want:
            fails.append(('P2.lean_rows5', '%s lean %r oracle %r' % (n, got and len(got), want and len(want))))
        if want is not None and probs.get(n, 0) != bad:
            fails.append(('P2.lean_bad5', '%s lean %d oracle %d' % (n, probs.get(n, 0), bad)))
        if got != F.read_tsv_rows(os.path.join(ld, 'lean', n)):
            fails.append(('P3.roundtrip5', n))
    A = {n: rd(d, n) for n in OUTS + ('classes',)}
    SA = summary(d)
    certs = {r[1]: (r[2], r[3]) for r in rows_of(A['certs']) if r[0] == 'treatment' and r[1] not in O.dup_ids}
    width = {'status': 11, 'status_lines': 12, 'findings': 7}
    # ---------------------------------------------------------------- R1: no class file = round 4
    bdir = os.path.join(d, 'vB') if r5 else d
    if os.path.isdir(bdir) and rc_ok(bdir):
        B = {n: rd(bdir, n) for n in OUTS + ('classes',)}
        SB = summary(bdir)
        stats['R1.cases'] += 1
        if B['classes'] is not None or any(k.startswith(('class_', 'recognised_', 'operative_')) for k in SB):
            fails.append(('R1.absent_shape', 'classes file or class counters without a class table'))
        for n, w in width.items():
            if any(len(r) != w for r in rows_of(B[n])):
                fails.append(('R1.absent_shape', '%s is not %d columns wide' % (n, w)))
        if LP4:
            if not rc_ok(bdir, 'runner4'):
                fails.append(('R1.round4_runner', 'the round-4 runner failed'))
            else:
                stats['R1.round4_compared'] += 1
                for n in OUTS:
                    if rd(bdir, n, 'runner4') != B[n]:
                        fails.append(('R1.absent_vs_round4', n))
                if summary(bdir, 'runner4') != SB:
                    fails.append(('R1.absent_vs_round4', 'summary'))
    elif r5:
        fails.append(('P1.runner_variant', 'vB'))
        return fails, stats
    if not r5:
        return fails, stats
    # ---------------------------------------------------------------- R2: an empty class file adds only the extras
    cdir = os.path.join(d, 'vC')
    if rc_ok(cdir):
        stats['R2.cases'] += 1
        C = {n: rd(cdir, n) for n in OUTS + ('classes',)}
        SC = summary(cdir)
        for n in OUTS:
            if n in width:
                rb, rc_ = rows_of(B[n]), rows_of(C[n])
                if [r[:-1] for r in rc_] != rb or any(len(r) != width[n] + 1 for r in rc_):
                    fails.append(('R2.empty_vs_absent', n))
                if any(r[-1] not in ('-',) + CLASSES[:2] for r in rc_):
                    fails.append(('R2.empty_oclass', '%s has an oclass no explicit row can give' % n))
            elif C[n] != B[n]:
                fails.append(('R2.empty_vs_absent', n))
        extra = {k: v for k, v in SC.items() if k not in SB}
        if {k: v for k, v in SC.items() if k in SB} != SB or extra != {
                'class_rows': '0', 'class_bad_rows': '0', 'recognised_rows': '0', 'operative_rows': '0'}:
            fails.append(('R2.empty_summary', str(extra)))
        # classes.tsv with no claim: every status-changing row that parses, its class from the row alone
        cc = {r[1]: r[2] for r in rows_of(C['certs']) if r[0] == 'treatment'}
        want = []
        for r in O.treat:
            if r[0] in J and J[r[0]]['verdict'] != 'badRow' and r[4] in NEG:
                c = 'atRiskWitness' if r[7] != '1' else 'selfAnnounced' if any(
                    x in lower(F.norm(r[11])) for x in CUE['self_announced']) else 'operativeWords'
                want.append([r[0], c, '-', str(cc.get(r[0])), '-', '-', str(O.wit[r[0]][0]) if r[0] in O.wit else '-'])
        want.sort()
        got = sorted(rows_of(C['classes']) or [])
        if got != want and not O.dup_ids:
            fails.append(('R2.empty_classes', 'lean %r oracle %r' % (
                next((g for g in got if g not in want), None), next((w_ for w_ in want if w_ not in got), None))))
    else:
        fails.append(('P1.runner_variant', 'vC'))
    # ---------------------------------------------------------------- R3: ignored lines change nothing, and are counted
    if SA.get('class_rows') != str(len(O.claims)):
        fails.append(('R3.class_rows', 'lean %s oracle %d' % (SA.get('class_rows'), len(O.claims))))
    lb = int(SA.get('class_bad_rows', -1))
    if lb != O.cbad + O.cextra:
        tag = '.DA-dup' if O.cdup and lb == O.cbad + O.cextra + O.cdup else \
              '.DA-extra' if O.cextra and lb == O.lenient[1] else ''
        fails.append(('R3.class_bad_rows' + tag, 'lean %d oracle %d bad + %d long (+ %d dup)' % (
            lb, O.cbad, O.cextra, O.cdup)))
    ddir, edir = os.path.join(d, 'vD'), os.path.join(d, 'vE')
    if rc_ok(ddir) and rc_ok(edir):
        stats['R3.cases'] += 1
        Dv = {n: rd(ddir, n) for n in OUTS + ('classes',)}
        SD = summary(ddir)
        for n in OUTS + ('classes',):
            if Dv[n] != A[n]:
                fails.append(('R3.ignored_line_changes_output', n))
        drop = ('class_bad_rows', 'bad_rows\t' + CLS)
        if {k: v for k, v in SD.items() if k not in drop} != {k: v for k, v in SA.items() if k not in drop} or \
                SD.get('class_bad_rows') != '0':
            fails.append(('R3.ignored_line_changes_output', 'summary'))
        # R4: a claim on the wrong kind of row changes nothing but the claim shown for that row
        Ev = {n: rd(edir, n) for n in OUTS + ('classes',)}
        SE = summary(edir)
        gone = {i for i in O.claims if not effective(i, O)}
        stats['R4.claims_removed'] += len(gone)
        for n in OUTS:
            if Ev[n] != Dv[n]:
                fails.append(('R4.wrong_kind_claim_changes_output', n))
        mask = lambda rs: [r[:2] + ['*'] + r[3:4] + ['*', '*'] + r[6:] if r[0] in gone else r for r in rs or []]
        if mask(rows_of(Ev['classes'])) != mask(rows_of(Dv['classes'])):
            fails.append(('R4.wrong_kind_claim_changes_output', 'classes'))
        if {k: v for k, v in SE.items() if k != 'class_rows'} != {k: v for k, v in SD.items() if k != 'class_rows'}:
            fails.append(('R4.wrong_kind_claim_changes_output', 'summary'))
    else:
        fails.append(('P1.runner_variant', 'vD/vE'))
    # ---------------------------------------------------------------- R5: the verdicts
    bc = {r[1]: (r[2], r[3]) for r in rows_of(B['certs']) if r[0] == 'treatment'}
    for rid, j in J.items():
        lv = certs.get(rid)
        if lv is None:
            fails.append(('R5.no_cert_line', rid))
            continue
        ext = '.DA-extra' if rid in O.extra_ids and rid not in O.claims else ''
        stats['lean.%s.%s' % (j['mode'], lv[0])] += 1
        if j['verdict'] is not None and lv[0] != j['verdict']:
            fails.append(('R5.verdict.%s%s' % (j['mode'], ext), '%s lean %s oracle %s' % (rid, lv[0], j['verdict'])))
        if lv[0].startswith('okRecognised') and not j.get('recog_text'):
            fails.append(('R5.recognised_unsound' + ext, '%s lean %s; oracle: mode %s' % (rid, lv[0], j['mode'])))
        # no effective claim: the row is checked as in round 4; a failed recognised claim falls back to round 4
        for col in (0, 1):
            if (j['mode'] in ('plain', 'witness', 'badRow') or
                    (j['mode'] == 'recog' and not lv[col].startswith('okRecognised'))) and lv[col] != bc.get(rid, (None, None))[col]:
                fails.append(('R5.not_round4_verdict' + ext, '%s col %d: with the class table %s, without %s' % (
                    rid, col, lv[col], bc.get(rid, (None, None))[col])))
    # ---------------------------------------------------------------- R6: classes.tsv, the counters
    cl = {r[0]: r for r in rows_of(A['classes']) or []}
    want_ids = {rid for rid, j in J.items() if j['verdict'] != 'badRow' and j['cls'] != '-'}
    if set(cl) != want_ids and not O.dup_ids:
        fails.append(('R6.classes_rows', 'only lean %s only oracle %s' % (sorted(set(cl) - want_ids)[:3],
                                                                         sorted(want_ids - set(cl))[:3])))
    for rid in want_ids & set(cl):
        r, j = cl[rid], J[rid]
        c = O.claims.get(rid)
        if len(r) != 7:
            fails.append(('R6.classes_shape', rid))
            continue
        if j['cls'] is not None and r[1] != j['cls']:
            fails.append(('R6.class', '%s lean %s oracle %s (verdict %s)' % (rid, r[1], j['cls'], r[3])))
        if (r[1] == 'recognised') != r[3].startswith('okRecognised'):
            fails.append(('R6.class_vs_verdict', '%s class %s verdict %s' % (rid, r[1], r[3])))
        if r[2] != (c[0] if c else '-') or r[3] != certs.get(rid, ('?',))[0] or \
                r[6] != (str(O.wit[rid][0]) if rid in O.wit else '-'):
            fails.append(('R6.classes_fields', '%s %r' % (rid, r)))
        fl, doc = (c[1], c[2]) if c else ('-', '-')
        if (r[4], r[5]) != (fl, doc):
            tag = '.DA-empty-display' if (r[4], r[5]) == (fl or '-', doc or '-') else ''
            fails.append(('R6.classes_display' + tag, '%s lean %r oracle %r' % (rid, r[4:6], [fl, doc])))
    nrec = sum(1 for r in cl.values() if len(r) > 1 and r[1] == 'recognised')
    if SA.get('recognised_rows') != str(nrec):
        fails.append(('R6.recognised_rows', 'summary %s, classes.tsv %d' % (SA.get('recognised_rows'), nrec)))
    nver = sum(1 for v in certs.values() if v[0].startswith('okRecognised'))
    if SA.get('recognised_rows') != str(nver):
        fails.append(('R6.recognised_rows_vs_certs', 'summary %s, certs %d' % (SA.get('recognised_rows'), nver)))
    nop = sum(1 for rid, j in J.items() if j['mode'] == 'operative' and certs.get(rid, ('',))[0] in ('ok', 'okUnverifiedBy'))
    if SA.get('operative_rows') != str(nop):
        fails.append(('R6.operative_rows', 'summary %s, admitted operative rows %d' % (SA.get('operative_rows'), nop)))
    for n in width:
        for r in rows_of(A[n]):
            if len(r) != width[n] + 1 or r[-1] not in ('-',) + CLASSES:
                fails.append(('R6.oclass_shape', '%s %r' % (n, r[-3:])))
                break
            if n == 'status' and r[5] == 'good' and r[-1] != '-':
                fails.append(('R6.oclass_on_good', '%r' % r))
    # ---------------------------------------------------------------- R7: the timeline of a clean row (2.3, 3.3)
    st = rows_of(A['status'])
    for sc in cj['r5']['scen']:
        rid, X, Y = sc['id'], sc['X'], sc['Y']
        j = J.get(rid)
        r = next((r for r in O.treat if r[0] == rid), None)
        if j is None or r is None or certs.get(rid, ('',))[0] != j['verdict'] or r[5] != 'all' or r[6] != 'retroactive':
            continue
        if sum(1 for q in O.treat if q[2] == str(X)) != 1 or any(q[1] in (str(X), str(Y), str(sc.get('W'))) for q in O.T['history.tsv'][0]) \
                or any(q[1] == str(X) for q in O.T['holdings.tsv'][0]) or any(q[1] == str(X) for q in O.T['supersessions.tsv'][0]):
            continue
        dy = int(O.dec[Y][2])
        neg = 'neg:abrogated' if r[4] == 'abrogated' else 'neg:overruled'
        if j['verdict'] == 'okRecognised':
            dw = int(O.dec[sc['W']][2])
            want = [(dy - 1, 'good', '-')] + ([(dy, 'unknown:recognisedLater', 'recognised'), (dw - 1, 'unknown:recognisedLater', 'recognised')]
                                             if dy < dw else []) + [(dw, neg, 'recognised'), (ASOF, neg, 'recognised')]
            name = 'R7.recognised_timeline'
        elif j['mode'] == 'operative' and j['verdict'] == 'ok':
            whole = any(c in lower(F.norm(r[11])) for c in CUE['operative_whole'])
            s = 'neg:overruled' if whole else 'unknown:partialScope'
            want = [(dy - 1, 'good', '-'), (dy, s, j['cls']), (ASOF, s, j['cls'])]
            name = 'R7.operative_timeline.' + ('whole' if whole else 'demoted')
        else:
            continue
        stats[name] += 1
        sx = step(st, X)
        for t, s, oc in want:
            g = at(sx, t)
            if g is None or (g[2], g[5]) != (s, oc) or (s != 'good' and (g[3], g[4]) != (rid, str(Y))):
                fails.append((name, '%s at %d: lean %r oracle %s %s' % (rid, t, g, s, oc)))
                break
    # ---------------------------------------------------------------- R8: Lean against the reference
    if R5 is not None:
        stats['R8.cases'] += 1
        if str(R5['class_rows']) != SA.get('class_rows'):
            fails.append(('R8.ref.class_rows' + ('.DA-extra' if O.extra_ids else ''),
                          'lean %s ref %d' % (SA.get('class_rows'), R5['class_rows'])))
        if R5['class_bad'] != lb:
            tag = '.DA-dup' if O.cdup and not O.cextra else '.DA-extra' if O.cextra and not O.cdup else \
                  '.DA-dup+extra' if O.cdup and O.cextra else ''
            fails.append(('R8.ref.class_bad_rows' + tag, 'lean %d ref %d' % (lb, R5['class_bad'])))
        for rid, lv in certs.items():
            ext = '.DA-extra' if rid in O.extra_ids and rid not in O.claims else ''
            if lv[0].startswith('okRecognised') != (rid in R5['recog']):
                fails.append(('R8.ref.recognised' + ext, '%s lean %s ref %s' % (rid, lv[0], R5['recog'].get(rid))))
            if rid in cl and len(cl[rid]) > 1 and cl[rid][1] != R5['classes'].get(rid):
                fails.append(('R8.ref.class' + ext, '%s lean %s ref %s (lean verdict %s)' % (
                    rid, cl[rid][1], R5['classes'].get(rid), lv[0])))
        if SA.get('operative_rows') != str(len(R5['oper'])):
            fails.append(('R8.ref.operative_rows', 'lean %s ref %d' % (SA.get('operative_rows'), len(R5['oper']))))
    return fails, stats


def cmd_check(root, lean=True, jobs=8):
    dirs = F.case_dirs(root)
    with ProcessPoolExecutor(jobs) as ex:
        res = list(ex.map(check_case5, [(d, lean) for d in dirs], chunksize=8))
    byprop = defaultdict(list)
    stats = Counter()
    cov = Counter()
    for d, (fails, st) in zip(dirs, res):
        stats.update(st)
        cj = json.load(open(os.path.join(d, 'case.json'), encoding='utf-8'))
        cov.update('op.' + o for _, o in cj['ops'])
        cov.update('op5.%s.%s' % (n, o) for n, o in cj['ops'] if n in (WIT, CLS))
        cov.update('junk.' + x for x in cj['r5']['junk'])
        for sc in cj['r5']['scen']:
            cov['scen.' + sc['kind'] + '.' + sc['fam']] += 1
            cov['place.' + sc['place']] += 1
            cov.update('deco.%s' % x for x in sc['deco'])
        for p, det in fails:
            byprop[p].append((os.path.basename(d), det))
    rep = {'cases': len(dirs), 'stats': dict(sorted(stats.items())), 'coverage': dict(sorted(cov.items())),
           'failures': {p: {'count': len(v), 'cases': len({c for c, _ in v}), 'samples': v[:8]}
                        for p, v in sorted(byprop.items())}}
    with open(os.path.join(root, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: rep[k] for k in ('cases', 'stats')}, ensure_ascii=False))
    for p, v in sorted(byprop.items()):
        print('%-44s %5d in %4d cases  e.g. %s %s' % (p, len(v), len({c for c, _ in v}), v[0][0], v[0][1][:200]))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['gen', 'run', 'check', 'all', 'oracle', 'directed'])
    ap.add_argument('--n', type=int, default=400)
    ap.add_argument('--seed', type=int, default=5)
    ap.add_argument('--dir', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    if a.cmd in ('gen', 'all', 'oracle'):
        shutil.rmtree(a.dir, ignore_errors=True)
        os.makedirs(a.dir)
        with ProcessPoolExecutor(a.jobs) as ex:
            list(ex.map(gen_case5, [a.seed * 1000003 + i for i in range(a.n)],
                        [os.path.join(a.dir, 'c%05d' % i) for i in range(a.n)], chunksize=32))
    if a.cmd == 'directed':
        shutil.rmtree(a.dir, ignore_errors=True)
        os.makedirs(a.dir)
        directed(a.dir)
        root = a.dir
        for n in sorted(os.listdir(root)):                 # the case dirs are found by their `c` prefix
            os.rename(os.path.join(root, n), os.path.join(root, 'c_' + n))
        cmd_run(a.dir, a.jobs)
        cmd_check(a.dir, jobs=a.jobs)
    if a.cmd in ('run', 'all'):
        cmd_run(a.dir, a.jobs)
    if a.cmd == 'oracle':
        cmd_run(a.dir, a.jobs, lean=False)
    if a.cmd in ('check', 'all', 'oracle'):
        cmd_check(a.dir, lean=a.cmd != 'oracle', jobs=a.jobs)


if __name__ == '__main__':
    main()
