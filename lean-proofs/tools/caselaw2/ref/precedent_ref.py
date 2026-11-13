#!/usr/bin/env python3
"""precedent_ref.py - independent Python reference implementation of the US rules of precedent
for caselaw-lean-2 (DESIGN.md "REVISED DESIGN" D4: differential testing against the Lean model).

Written from research/doctrine.md and SCHEMA.md only; no Lean under LegalProofs/CaseLaw2 was read.
Every rule carries the doctrine.md id it implements (F1..F14, E1..E3, H1..H4, S-xx, T1..T4, TM1..TM5,
AB1, HD1..HD6, §8.2, §9.nn). Interpretive choices are listed in REF_NOTES.md (R-numbers below).

Usage
  python precedent_ref.py run   --data DIR [--edges DIR] --out DIR [--no-firm]
  python precedent_ref.py force --data DIR NODE HOLDING|- DST_COURT T U [--unit N]
  python precedent_ref.py status --data DIR NODE HOLDING|- T U
  python precedent_ref.py can   --data DIR BY_NODE TARGET_NODE [ISSUE|-]

Outputs (LEAN.md "Outputs"): status.tsv, findings.tsv, certs.tsv, splits.tsv, splits_asof.tsv, conflicts_asof.tsv,
status_lines.tsv (R2-75: status per line of authority), horty.tsv (R2-78: Horty binding bases) (+ ref_stats.tsv).

Optional inputs read when present (REF_NOTES "Revisions: five limits"): cite_index.tsv (citation -> node, T2),
window_sha.tsv (window hashes, T3), commission.tsv (H4 notations, T4); factors.tsv and factor_cases.tsv (R2-78).
"""
import argparse
import array
import datetime
import glob
import hashlib
import os
import re
import sys
import time
from collections import defaultdict

OPEN = 99999999          # open-ended date (SCHEMA uses 99999999 for "to")
ERIE = 19380425          # E1
FED_CIR_START = 19821001 # F11
EN_BANC_STATUTE = 19480901   # H3b: 28 U.S.C. § 46(c) (Judicial Code of 1948), in force 1 Sept 1948
CA_REVIEW_2016 = 20160701  # S-CA review-granted rule change
TX_PETITION_ERA = 19970901  # S-TX: writ era before 1 Sept 1997, petition era from it (TRAP 56.1(c))

UNK = 'unknown'
# Deliberately broken variants (DESIGN D3) used only to test that differential runs catch such bugs:
# PREF_MUTANT=name[,name] - see MUTANTS. Never set in a real run.
MUTANTS = ('erieBothWays', 'panelOverrulesPanel', 'ignoreUnpublished', 'ignorePartialScope',
           'supersessionRetroactive', 'revivalIgnored', 'certAcceptsDissent', 'temporalIgnored',
           'successionIgnored', 'vacaturIgnored')
HIST_KINDS_ALL = ('affirmed', 'reversed', 'vacated', 'modified', 'remanded', 'certDenied', 'reviewGranted',
                  'reviewDismissed', 'depublished', 'withdrawn', 'substitutedBy', 'rehearingEnBancGranted',
                  'reinstated', 'writRefused', 'other')
MUT = set(x for x in os.environ.get('PREF_MUTANT', '').split(',') if x)
# R2 debug switch (self-tests only, never set in a real run): PREF_UNION_VIEWS=1 makes every effect reach every view,
# so every per-line status is the union status (what splits, conflicts and the treatment findings read in round 1).
UNION_VIEWS = os.environ.get('PREF_UNION_VIEWS', '') == '1'
# §9.10: binding > bindingAbsentConflict > persuasiveStrong > persuasive > citableNoWeight > notCitable > none,
# plus resultOnly (R3: ranked between persuasiveStrong and persuasive) and physicalPrecedent (= persuasive).
FORCE_RANK = {'binding': 8, 'bindingAbsentConflict': 7, 'persuasiveStrong': 6, 'resultOnly': 5,
              'persuasive': 4, 'physicalPrecedent': 4, 'citableNoWeight': 2, 'notCitable': 1, 'none': 0}

TIER_RANK = {'L': 4, 'A': 3, 'B': 2, 'S': 2, 'D': 1, 'T': 0}
FED_LOWER = ('T', 'B', 'D', 'S')

BENCH = ['unknown', 'panel', 'division', 'enBanc', 'limitedEnBanc', 'circulated', 'conflictPanel', 'wholeCourt']
PUB = ['unknown', 'published', 'unpublished', 'table', 'summaryOrder', 'memorandum']
FORM = ['unknown', 'full', 'perCuriam', 'summaryAffirmance', 'equallyDivided', 'certifiedAnswer', 'plurality',
        'memorandum']
BENCH_I = {b: i for i, b in enumerate(BENCH)}
PUB_I = {b: i for i, b in enumerate(PUB)}
FORM_I = {b: i for i, b in enumerate(FORM)}
UNPUB = ('unpublished', 'table', 'summaryOrder', 'memorandum')
EN_BANC_EQUIV = ('enBanc', 'limitedEnBanc', 'conflictPanel', 'wholeCourt')  # F7, F8, S-MI

# T1(b): treatments that change status; T1: "limited/questioned/criticized/distinguished never change status"
NEG_TREAT = ('overruled', 'disapproved', 'recededFrom', 'abrogated')
# fuzz: the values a row may name (SCHEMA); any other value makes the row a badRow, as Lean's TKind/Temporal.ofString?
_TKINDS = ('overruled', 'disapproved', 'recededFrom', 'abrogated', 'supersededByEnactment', 'limited', 'questioned',
           'criticized', 'distinguished', 'followed', 'declinedToFollow')
_HKINDS = HIST_KINDS_ALL


def _temporal_ok(t):
    return t in ('retroactive', 'pureProspective', 'unknown') or (
        t.startswith('prospectiveFrom:') and _NAT_RX.match(t[16:]) is not None)
SOFT_TREAT = ('limited', 'questioned', 'criticized', 'declinedToFollow')
# §5.1 A: same-case events with a status effect
NEG_HIST = ('reversed', 'vacated', 'withdrawn', 'substitutedBy', 'depublished', 'rehearingEnBancGranted',
            'reviewGranted')
LAPSE_KINDS = ('withdrawn', 'vacated', 'substitutedBy', 'depublished', 'rehearingEnBancGranted')  # TM3, T3
CLOSES = {  # restoring same-case events -> which open effects they end (§5.1 A "reinstated restores", S-CA)
    'reinstated': ('withdrawn', 'vacated', 'depublished', 'rehearingEnBancGranted', 'substitutedBy',
                   'enBancGrantVacatesPanel.missing',
                   'reviewGranted', 'reviewGrantedDepublished', 'reversed'),   # §5.1 A: reinstated restores status
    'reviewDismissed': ('reviewGranted', 'reviewGrantedDepublished'),
    'affirmed': ('reviewGranted', 'reviewGrantedDepublished'),
    'modified': ('reviewGranted', 'reviewGrantedDepublished'),
    'reversed': ('reviewGranted', 'reviewGrantedDepublished'),
}
# representative-kind order when several negative effects are active (R17)
KIND_ORDER = ['withdrawn', 'substitutedBy', 'vacated', 'depublished', 'rehearingEnBancGranted', 'reversed',
              'overruled', 'recededFrom', 'disapproved', 'abrogated', 'supersededByEnactment', 'reviewGranted']
KIND_POS = {k: i for i, k in enumerate(KIND_ORDER)}
# R17 (revised, D4 triage (c)): the reported kind is the most severe live effect (a withdrawn opinion is reported as
# withdrawn even if it was overruled earlier); ties by earliest start, then KIND_ORDER
SEVERITY = {'reviewGranted': 0, 'supersededByEnactment': 1, 'abrogated': 2, 'overruled': 3, 'disapproved': 3,
            'recededFrom': 3, 'reversed': 4, 'depublished': 5, 'reviewGrantedDepublished': 5, 'vacated': 6,
            'rehearingEnBancGranted': 6, 'withdrawn': 7, 'substitutedBy': 7}

FIND_OVERRULED = ('overruled', 'disapproved', 'recededFrom', 'abrogated')
FIND_VACATED = ('vacated', 'withdrawn', 'substitutedBy', 'depublished', 'rehearingEnBancGranted',
                'reviewGrantedDepublished')

# Certificate verbs (DESIGN layer 4: "it contains a treatment verb of the asserted kind"); R20.
# R20 (revised, D4 real data (c)): one cue table for both sides (the Lean's Certificate.cues), a quote passes if it
# contains any cue of its kind
# round 4: the table is generated from tools/caselaw2/cues/cue_table.json (gen_cues.py) into this module, the
# reader's copy and the Lean's CueTable.lean
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cue_table import VERBS, DISQUALIFY_TREAT, DISQUALIFY_HIST  # noqa: E402
CERT_PARTS = ('majority', 'plurality', 'perCuriam')
# round 4 (DEVIATIONS 84): the words a panelDepartsWithoutEnBanc finding needs in the certified quote
PANEL_OWN_WORDS = ('overrul', 'disapprov', 'recede from', 'receded from', 'recedes from', 'receding from')
# R33 (c, D4 real data): phrases that show a quote is not the court's own status-changing act (T4): a procedural
# ruling ("point of error ... overruled"), a reported history ("overruled by", "as stated in"), or a refusal to
# overrule; for history, a separate opinion's would-be disposition. Phrases only: word pairs such as
# "objection ... overruled" also fire on genuine overrulings.
# (the phrases are in the generated cue_table module)

# H4 / §3.2 TX (five limits, L4): commission.tsv notation -> the adoption.tsv filter it satisfies. 'opinionApproved'
# and 'adoptedAsOpinionOfCourt' approve the whole opinion, so they read as an adopted opinion; 'other' (a notation
# whose wording was not classified) satisfies no known filter: unknown (D5). A node with no row: 'none'.
NOTATION_FILTER = {'opinionAdopted': 'opinionAdopted', 'opinionApproved': 'opinionAdopted',
                   'adoptedAsOpinionOfCourt': 'opinionAdopted', 'holdingApproved': 'holdingApproved',
                   'judgmentAdopted': 'judgmentAdopted'}
NOTATION_FILTERS = ('opinionAdopted', 'holdingApproved', 'judgmentAdopted', 'none')
# S-TX / F3 (five limits, L5): what a Texas review notation says. n.r.e., denials and dismissals add nothing; a PDR is
# criminal and adds nothing; "writ ref'd" (writ era) and "pet. ref'd" (petition era) promote.
TX_NOADD = re.compile(r"n\.\s?r\.\s?e\b|\bnre\b|no reversible error|\bden(?:ied\b|\.)|\bdism|\bw\.?o\.?j\b")
TX_CRIMINAL = re.compile(r"\bpdr\b|discretionary review")
TX_WRIT_REF = re.compile(r"\bwrit(?:\s+of\s+error)?\s+ref(?:['’]?d\b|used\b|\.)")
TX_PET_REF = re.compile(r"\bpet(?:ition)?(?:\s+for\s+review)?\.?\s+ref(?:['’]?d\b|used\b|\.)")

STATE_CIRCUIT = {  # 28 U.S.C. § 41 geography, used only for E3 stateFollowsCircuit rows (R11)
    'Maine': 1, 'Massachusetts': 1, 'New Hampshire': 1, 'Rhode Island': 1, 'Puerto Rico': 1,
    'Connecticut': 2, 'New York': 2, 'Vermont': 2, 'Delaware': 3, 'New Jersey': 3, 'Pennsylvania': 3,
    'Virgin Islands': 3, 'Maryland': 4, 'North Carolina': 4, 'South Carolina': 4, 'Virginia': 4,
    'West Virginia': 4, 'Louisiana': 5, 'Mississippi': 5, 'Texas': 5, 'Kentucky': 6, 'Michigan': 6, 'Ohio': 6,
    'Tennessee': 6, 'Illinois': 7, 'Indiana': 7, 'Wisconsin': 7, 'Arkansas': 8, 'Iowa': 8, 'Minnesota': 8,
    'Missouri': 8, 'Nebraska': 8, 'North Dakota': 8, 'South Dakota': 8, 'Alaska': 9, 'Arizona': 9,
    'California': 9, 'Hawaii': 9, 'Idaho': 9, 'Montana': 9, 'Nevada': 9, 'Oregon': 9, 'Washington': 9,
    'Guam': 9, 'Northern Mariana Islands': 9, 'Colorado': 10, 'Kansas': 10, 'New Mexico': 10, 'Oklahoma': 10,
    'Utah': 10, 'Wyoming': 10, 'Alabama': 11, 'Florida': 11, 'Georgia': 11, 'District of Columbia': 12,
}
_STATE_RE = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, STATE_CIRCUIT), key=len, reverse=True)) + r')\b')


# ----------------------------------------------------------------------------------------------------------------
# Force algebra (results are (label, rule) pairs; label may be UNK - D5 "no silent defaults")

def upper(r):
    """The highest force an (possibly unknown) result can be: its label, or for an unknown the bound carried as a
    third element (every reading of the unknown attribute is at most that), else None."""
    if r[0] != UNK:
        return r[0]
    return r[2] if len(r) > 2 else None


def lower_of(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if FORCE_RANK[a] <= FORCE_RANK[b] else b


def fmin(a, b):
    """Cap a by b. With an unknown side the result is definite only if the other side is rank 0; otherwise it stays
    unknown, bounded above by the definite side (and the unknown side's own bound)."""
    la, lb = a[0], b[0]
    if la == UNK and lb == UNK:
        ub = lower_of(upper(a), upper(b))
        return (UNK, a[1], ub) if ub is not None else a
    if la == UNK:
        return b if FORCE_RANK[lb] == 0 else (UNK, a[1], lower_of(upper(a), lb))
    if lb == UNK:
        return a if FORCE_RANK[la] == 0 else (UNK, b[1], lower_of(upper(b), la))
    ra, rb = FORCE_RANK[la], FORCE_RANK[lb]
    if rb < ra or (rb == ra and la != lb):
        return b
    return a


def fmax(a, b):
    """Strongest of two routes (holders). Unknown is definite only against a binding route."""
    la, lb = a[0], b[0]
    if la != UNK and FORCE_RANK[la] == 8:
        return a
    if lb != UNK and FORCE_RANK[lb] == 8:
        return b
    if la == UNK:
        return a
    if lb == UNK:
        return b
    return a if FORCE_RANK[la] >= FORCE_RANK[lb] else b


def agree(results, what):
    """D5: evaluate an unknown attribute over its possible values; definite only if every value agrees."""
    labels = {r[0] for r in results}
    if len(labels) == 1:
        return results[0]
    ups = [upper(r) for r in results]
    if None in ups:
        return (UNK, 'ambiguous:' + what)
    return (UNK, 'ambiguous:' + what, max(ups, key=lambda x: FORCE_RANK[x]))


def next_day(d):
    try:
        x = datetime.date(d // 10000, d // 100 % 100, d % 100) + datetime.timedelta(days=1)
        return x.year * 10000 + x.month * 100 + x.day
    except ValueError:
        return d + 1


# fuzz: SCHEMA integers are ASCII digits with an optional '-'. Python's int() also took ' 5', '+5', '1_000', NBSP and
# other scripts' digits ('٣'), and float() took 'nan', '1e5', '-0.5'; the Lean glue (Tsv.nat?/int?/ppm?) does not.
_NAT_RX = re.compile(r'[0-9]+\Z')
_INT_RX = re.compile(r'-?[0-9]+\Z')
_DEC_RX = re.compile(r'(?=[0-9]|\.[0-9])[0-9]*(?:\.[0-9]*)?\Z')


def toint(s, default=0):
    if isinstance(s, str) and _INT_RX.match(s):    # fuzz: strict, as Tsv.int?
        return int(s)
    return default


def tofloat(s, default=0.0):
    if isinstance(s, str) and _DEC_RX.match(s):    # fuzz: strict non-negative decimal, as Tsv.ppm?
        a, _, b = s.partition('.')
        return int(a or '0') + int((b + '000000')[:6]) / 1e6   # fuzz: 6 decimals (Lean keeps parts per million)
    return default


BAD_ROWS = defaultdict(int)   # fuzz: rows rejected per file (the Lean runner reports them as bad_rows)


def read_lines(path):
    """fuzz: the lines of a SCHEMA file as Lean's Tsv.foldLines reads them: split on LF only (open(newline='') also
    split on a lone CR, which is data), trailing CRs dropped, a BOM dropped from line 1, blank lines skipped; a line
    that is not valid UTF-8 comes back as None (open(encoding='utf-8') raised and stopped the whole run)."""
    if not os.path.exists(path):
        return
    with open(path, 'rb') as f:
        for i, raw in enumerate(f):
            raw = raw[:-1] if raw.endswith(b'\n') else raw
            raw = raw.rstrip(b'\r')
            if i == 0 and raw.startswith(b'\xef\xbb\xbf'):
                raw = raw[3:]
            if not raw:
                continue
            try:
                yield raw.decode('utf-8')
            except UnicodeDecodeError:
                yield None


def read_tsv(path, ncols=None, nat=(), int_=(), dec=(), flag=()):
    """Yield rows of a SCHEMA TSV (no header). fuzz: a row is rejected (and counted in BAD_ROWS) unless it has exactly
    `ncols` fields, its `nat` columns are ASCII digits and its `int_` columns '-'? digits, as Lean's loadRows and row
    parsers require. It used to pad short rows with '' (silently reading a 15-field treatment row), keep extra fields
    (a tab inside a quote shifted every later column), and skip '#' and header-looking lines that Lean reads."""
    name = os.path.basename(path)
    for line in read_lines(path):
        p = line.split('\t') if line is not None else None
        if (p is None or (ncols and len(p) != ncols) or any(not _NAT_RX.match(p[c]) for c in nat)
                or any(not _INT_RX.match(p[c]) for c in int_)
                # fuzz FB-L5: a decimal column (confidence, score) must parse, and a flag (explicit) must be 0 or 1
                or any(not _DEC_RX.match(p[c]) for c in dec) or any(p[c] not in ('0', '1') for c in flag)):
            BAD_ROWS[name] += 1
            continue
        yield p


def alnum(s):
    return re.sub(r'[^0-9a-z]', '', ascii_lower(s))    # fuzz: ASCII lowering, as Lean's Cert.compact


def norm_quote(s):
    # fuzz: one for one, as SCHEMA and Lean's Cert.norm (it collapsed CR LF to one space, shifting offsets)
    return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')


_ASCII_LOWER = {c: c + 32 for c in range(65, 91)}


def ascii_lower(s):
    # fuzz: Lean's String.toLower maps A-Z only; str.lower() also maps the Kelvin sign U+212A to 'k' and U+0130 to
    # 'i' + U+0307, so cue, disqualifier and evidence matching differed on such text
    return s.translate(_ASCII_LOWER)


# ----------------------------------------------------------------------------------------------------------------
class Epoch:
    __slots__ = ('court', 'frm', 'to', 'name', 'system', 'tier', 'lrf', 'circuit', 'unit', 'tag')

    def __init__(self, p):
        self.court = toint(p[0])
        self.frm = toint(p[1])
        self.to = toint(p[2], OPEN) or OPEN
        self.name = p[3]
        self.system = toint(p[4])
        self.tier = p[5] if p[5] in TIER_RANK else 'T'
        self.lrf = p[6] or '-'
        self.circuit = toint(p[7])
        self.unit = toint(p[8])
        self.tag = (p[10] or 'L') if len(p) > 10 else 'L'


class Holder:
    """A court that holds a decision's authority at time t (H3 succession, F10/F11 adoption)."""
    __slots__ = ('court', 'tier', 'system', 'circuit', 'unit', 'cap', 'power', 'via')

    def __init__(self, court, tier, system, circuit, unit, cap, power, via):
        self.court, self.tier, self.system, self.circuit = court, tier, system, circuit
        self.unit, self.cap, self.power, self.via = unit, cap, power, via


class Cert:
    __slots__ = ('sha', 'start', 'end', 'quote', 'tev', 'part')

    def __init__(self, p):
        self.sha, self.start, self.end = p[0], toint(p[1], -1), toint(p[2], -1)
        self.quote, self.tev, self.part = p[3], p[4], p[5]


class Data:
    """Every SCHEMA table, decisions held in flat arrays (6.9M rows ≈ 100 MB)."""

    def __init__(self, ddir, log=None):
        self.dir = ddir
        self.log = log or (lambda *a: None)
        t0 = time.time()
        J = lambda n: os.path.join(ddir, n)
        # courts and doctrine tables (tagged rows; Engine filters U for the firm instance)
        self.courts = defaultdict(list)
        self.court_rows = []                  # courts2.tsv rows in file order (conflict destinations, L3)
        for p in read_tsv(J('courts2.tsv'), 11, nat=(0, 1, 2, 4, 7, 8)):   # fuzz: required columns, as Data.lean
            e = Epoch(p)
            self.courts[e.court].append(e)
            self.court_rows.append(e)
        for eps in self.courts.values():
            eps.sort(key=lambda e: e.frm)
        self.succession = [(toint(p[0]), toint(p[1]), toint(p[2]), p[3], p[5] or 'L')
                           for p in read_tsv(J('succession.tsv'), 6, nat=(0, 1, 2))]
        self.adoption = [(toint(p[0]), toint(p[1]), toint(p[2], OPEN), p[3] or 'all', p[4] or 'binding',
                          p[6] or 'L') for p in read_tsv(J('adoption.tsv'), 7, nat=(0, 1, 2))]
        self.sysrules = [(toint(p[0]), p[1], p[2], toint(p[3]), toint(p[4], OPEN) or OPEN, p[6] or 'L')
                         for p in read_tsv(J('system_rules.tsv'), 7, nat=(3, 4), int_=(0,))]
        self.marks = [(toint(p[0]), p[1], p[5] or 'L') for p in read_tsv(J('marks.tsv'), 6, nat=(0,))]
        # issues / holdings
        self.issues = {}
        for p in read_tsv(J('issues.tsv'), 6):
            self.issues[p[0]] = {'label': p[1], 'domain': p[2] or 'unknown', 'usc': p[3], 'question': p[4]}
        self.holdings = {}
        self.holdings_by_node = defaultdict(list)
        for p in read_tsv(J('holdings.tsv'), 14, nat=(1, 7, 8), dec=(13,)):
            h = {'id': p[0], 'node': toint(p[1], -1), 'issue': p[2], 'prop': p[3], 'answer': p[4],
                 'role': p[5], 'cert': Cert(p[6:12]), 'reader': p[12], 'conf': tofloat(p[13])}
            self.holdings[h['id']] = h
            self.holdings_by_node[h['node']].append(h)
        # same-case history and treatments
        self.history = []
        for p in read_tsv(J('history.tsv'), 13, nat=(1, 3, 7, 8), int_=(2,)):
            self.history.append({'id': p[0], 'target': toint(p[1], -1), 'by': toint(p[2], -1),
                                 'date': toint(p[3]), 'kind': p[4], 'scope': p[5] or 'unknown',
                                 'cert': Cert(p[6:12]), 'src': p[12]})
        self.treatments = []
        for p in read_tsv(J('treatments.tsv'), 16, nat=(1, 2, 3, 9, 10), dec=(15,), flag=(7,)):
            self.treatments.append({'id': p[0], 'by': toint(p[1], -1), 'target': toint(p[2], -1),
                                    'date': toint(p[3]), 'kind': p[4], 'scope': p[5] or 'all',
                                    'temporal': p[6] or 'unknown', 'temporal_raw': p[6], 'explicit': toint(p[7]),
                                    'cert': Cert(p[8:14]), 'reader': p[14], 'conf': tofloat(p[15])})
        # round 4: witness rows (round3/implicit_schema.md): treatment id -> (W, by_evidence). File absent: none.
        self.witness = {}
        if os.path.exists(J('treatment_witness.tsv')):
            for p in read_tsv(J('treatment_witness.tsv'), 4, nat=(1,)):
                self.witness[p[0]] = (toint(p[1], -1), p[2])
        # L7 (five limits, T3): optional window hashes. A window is usable only if a row with its (sha, start0, end0)
        # exists and sha1(window as stored) equals it. File absent: every window is usable (hash flag True).
        wsha = None
        if os.path.exists(J('window_sha.tsv')):
            wsha = defaultdict(set)
            for p in read_tsv(J('window_sha.tsv'), 5, nat=(1, 2)):
                wsha[(p[0], toint(p[1]), toint(p[2]))].add(p[3])
        self.cert_text = defaultdict(list)    # sha -> [(start0, end0, window, hashOk)]
        for fn in ('cert_text.tsv', 'holdings_cert_text.tsv'):    # holdings ship their own windows
            for p in read_tsv(J(fn), 4, nat=(1, 2)):
                s0, e0 = toint(p[1]), toint(p[2])
                hok = True
                if wsha is not None:
                    hs = wsha.get((p[0], s0, e0))
                    hok = bool(hs) and hashlib.sha1(p[3].encode('utf-8')).hexdigest() in hs
                self.cert_text[p[0]].append((s0, e0, p[3], hok))
        # L6 (five limits, T2): optional citation index; compact key -> node, None when ambiguous (>= 2 distinct nodes)
        self.cite_index = None
        if os.path.exists(J('cite_index.tsv')):
            m = defaultdict(set)
            for p in read_tsv(J('cite_index.tsv'), 2, nat=(1,)):
                k = alnum(p[0])
                if k:
                    m[k].add(toint(p[1], -1))
            self.cite_index = {k: (next(iter(v)) if len(v) == 1 else None) for k, v in m.items()}
        # L4 (five limits, T4): optional commission / adoption notations (H4); node -> notation (first row wins)
        self.commission = None
        if os.path.exists(J('commission.tsv')):
            self.commission = {}
            for p in read_tsv(J('commission.tsv'), 4, nat=(0,)):
                n = toint(p[0], -1)
                if n not in self.commission:
                    self.commission[n] = p[2]
        # law changes
        self.lawchanges = {}
        for p in read_tsv(J('lawchanges.tsv'), 7, nat=(3, 4, 5)):
            self.lawchanges[p[0]] = {'id': p[0], 'law': p[1], 'usc': p[2], 'enacted': toint(p[3]),
                                     'effective': toint(p[4]), 'retro': toint(p[5]), 'src': p[6]}
        self.supersessions = []
        for p in read_tsv(J('supersessions.tsv'), 8, nat=(1,), dec=(5,), flag=(6,)):
            self.supersessions.append({'id': p[0], 'target': toint(p[1], -1), 'issue': p[2] or '-',
                                       'lc': p[3], 'evidence': p[4], 'score': tofloat(p[5]),
                                       'explicit': toint(p[6]), 'src': p[7]})
        # optional per-decision extras (DESIGN D9: appeal_venue for Golsen, transfer_from for TRAP 41.3)
        self.extra = {}
        for p in read_tsv(J('decisions2_extra.tsv'), 3, nat=(0,)):
            self.extra[toint(p[0], -1)] = {'venue': toint(p[1]) or None, 'transfer_from': toint(p[2]) or None}
        # R2-78 (DEVIATIONS 78): optional Horty inputs. factors.tsv: holding_id, factor id, side (pi | anything else
        # = delta), inReason (1 | anything else = 0). factor_cases.tsv (11 columns): column 0 holding id, column 3
        # family key, column 4 outcome yes|no; a later row for a holding replaces an earlier one, a row with another
        # outcome is ignored.
        self.factors = defaultdict(list)
        for p in read_tsv(J('factors.tsv'), 4):
            self.factors[p[0]].append((p[1], 'pi' if p[2] == 'pi' else 'delta', p[3] == '1'))
        self.factor_cases = {}
        for p in read_tsv(J('factor_cases.tsv'), 11):
            if p[4] in ('yes', 'no'):
                self.factor_cases[p[0]] = (p[3], p[4])
        # which text shas must be kept (only cert owners)
        need = set()
        for h in self.holdings.values():
            need.add(h['node'])
        for r in self.history:
            need.add(r['target'])
            need.add(r['by'])
        for r in self.treatments:
            need.add(r['by'])
            need.add(r['target'])
        for (wn, _) in self.witness.values():
            need.add(wn)
        self._load_decisions(J('decisions2.tsv'), need)
        self.state_name = self._state_names()
        self.log('loaded %s in %.1fs (%d decisions, %d treatments, %d history, %d holdings)' % (
            ddir, time.time() - t0, self.n_present, len(self.treatments), len(self.history), len(self.holdings)))

    def _load_decisions(self, path, need):
        cap = 1 << 16
        court = array.array('q', [-1]) * cap      # fuzz: 'q', not 'i': a date or id over 2**31 raised OverflowError
        date = array.array('q', [0]) * cap
        unit = array.array('q', [0]) * cap
        bench = bytearray(cap)
        pub = bytearray(cap)
        form = bytearray(cap)
        sha = {}
        n = 0
        maxid = -1
        BI, PI, FI = BENCH_I, PUB_I, FORM_I
        # fuzz: node ids at or above the node count are rejected, as Lean's loadDecisions does ("node out of range";
        # the runner gets the count from run_lean.sh); one huge id used to grow these arrays without bound
        limit = int(os.environ.get('CASELAW2_NODES') or (1 << 27))
        Q = (1 << 63) - 1
        for line in read_lines(path):
            p = line.split('\t') if line is not None else None
            # fuzz: exactly 9 SCHEMA columns, ASCII-digit node/court/date/unit (it took 8 columns, isdigit() digits
            # such as '²' that int() then rejected with a crash, and negative courts)
            if (p is None or len(p) != 9 or any(not _NAT_RX.match(p[c]) for c in (0, 1, 2, 3))
                    or int(p[0]) >= limit or any(int(p[c]) > Q for c in (1, 2, 3))):
                BAD_ROWS['decisions2.tsv'] += 1
                continue
            i = int(p[0])
            if i >= cap:
                while i >= cap:
                    cap *= 2
                grow = cap - len(court)
                court.extend(array.array('q', [-1]) * grow)
                date.extend(array.array('q', [0]) * grow)
                unit.extend(array.array('q', [0]) * grow)
                bench.extend(bytes(grow))
                pub.extend(bytes(grow))
                form.extend(bytes(grow))
            court[i] = int(p[1])
            date[i] = int(p[2])
            unit[i] = int(p[3])
            bench[i] = BI.get(p[4], 0)
            pub[i] = PI.get(p[5], 0)
            form[i] = FI.get(p[6], 0)
            if i in need:
                sha[i] = p[7]
            n += 1
            if i > maxid:
                maxid = i
        self.court, self.date, self.unit = court, date, unit
        self.bench, self.pub, self.form, self.sha = bench, pub, form, sha
        self.n_present = n
        self.maxid = maxid

    def has(self, node):
        return 0 <= node < len(self.court) and self.court[node] >= 0

    def _state_names(self):
        """system index -> state name, from the names of that system's courts (for E3 table rows)."""
        out = {}
        votes = defaultdict(lambda: defaultdict(int))
        for c, eps in self.courts.items():
            for e in eps:
                if e.system != 0:
                    for m in _STATE_RE.findall(e.name):
                        votes[e.system][m] += 1
        for s, v in votes.items():
            out[s] = max(v.items(), key=lambda kv: (kv[1], kv[0]))[0]
        return out


# ----------------------------------------------------------------------------------------------------------------
class Engine:
    """One rules instance. firm=True drops every U-tagged doctrine row (DESIGN D2: firm = S/L only)."""

    def __init__(self, D, firm=False):
        self.D = D
        self.firm = firm
        keep = (lambda tag: tag != 'U') if firm else (lambda tag: True)
        self.courts = {}
        for c, eps in D.courts.items():
            k = [e for e in eps if keep(e.tag)]
            if k:
                self.courts[c] = k
        self.succ = defaultdict(list)
        for (old, new, d, kind, tag) in D.succession:
            if keep(tag):
                self.succ[old].append((new, d, kind))
        self.adopt = defaultdict(list)
        self.adopt_pairs = set()
        for (adopter, src, upto, filt, force, tag) in D.adoption:
            if keep(tag):
                self.adopt[src].append((adopter, upto, filt, force))
                self.adopt_pairs.add((adopter, src))
        self.rules = defaultdict(list)
        for (system, rule, val, frm, to, tag) in D.sysrules:
            if keep(tag):
                self.rules[(system, rule)].append((val, frm, to))
        self.iac_courts = defaultdict(set)     # system -> courts with an intermediate (A) epoch
        for c, eps in self.courts.items():
            for e in eps:
                if e.tier == 'A':
                    self.iac_courts[e.system].add(c)
        self.marks = {(n, k) for (n, k, tag) in D.marks if keep(tag)}
        self.marks_nodes = {n for (n, k) in self.marks}
        self.state_circuit = {s: STATE_CIRCUIT[n] for s, n in D.state_name.items()}
        self._tl = {}
        self._auth = {}
        self._stack = set()
        self._heirs_c = {}          # H4: node -> binding adoption heirs
        self.cert_ok = {}           # (file, id) -> 'ok' | reason   (shared: certs do not depend on rules)
        self.adm_hist = defaultdict(list)
        self.adm_treat = defaultdict(list)
        self.treat_by_id = {}
        self.adm_holdings = {}
        self.adm_holdings_by_node = defaultdict(list)
        self.sup_by_target = defaultdict(list)
        self.linked_treat = set()

    # ---------------------------------------------------------------- courts, rules
    def epoch(self, c, d):
        eps = self.courts.get(c)
        if not eps:
            return None
        if d == 0:
            return eps[0] if len(eps) == 1 else None
        for e in eps:
            if e.frm <= d <= e.to:
                return e
        return None

    def rule(self, system, court, name, date):
        """Court-level rows (system = -court_id) override system-level rows (SCHEMA system_rules)."""
        keys = []
        if court is not None:
            keys.append((-court, name))
        keys.append((system, name))
        for key in keys:
            rows = self.rules.get(key)
            if not rows:
                continue
            for (val, frm, to) in rows:
                if frm <= date <= to:
                    return val
        return None

    def horizontal(self, system, court, tier, date):
        """Horizontal rule for a court's own precedent (§4.1 H; F7). R23: for a court of last resort only a
        court-level row applies, or the system row when the system has no other intermediate court (D.C.:
        divisions bound, only en banc overrules, M.A.P. v. Ryan); otherwise None = H1 (may overrule itself)."""
        if tier != 'L':
            return self.rule(system, court, 'horizontal', date)
        v = self.rule(-court, None, 'horizontal', date)
        if v is not None:
            return v
        # R23 (revised, D4 triage (c)): a system-level row describes the system's intermediate courts; a court of
        # last resort is bound by its own precedent only through a court-level row (H1). The D.C. Court of
        # Appeals' divisional rule (M.A.P. v. Ryan) therefore needs a court-level row (DIFFTEST.md, data note).
        return None

    def is_scotus(self, e):
        return e.system == 0 and e.tier == 'L'

    def filter_match(self, filt, node, dom, adopter_system):
        """Adoption filter (F10, H4, §3.2). R5: 'unitB' = decision unit 2, 'unit:<n>' = unit n; 'issue:<d>' keys
        on the issue domain ('localLaw' also matches stateLaw of the adopter's system); notation filters that the
        schema cannot see (notTrialDivision, opinionAdopted, holdingApproved, judgmentAdopted, none) -> unknown."""
        if filt in ('all', '-', ''):
            return True
        u = self.D.unit[node]
        if filt == 'unitB':
            return u == 2
        if filt == 'unitA':
            return u == 1
        if filt.startswith('unit:'):
            return u == toint(filt[5:], -9)
        if filt.startswith('issue:'):
            if dom is None or dom == 'unknown':
                return None
            x = filt[6:]
            if dom == x or dom.startswith(x + ':'):
                return True
            return x == 'localLaw' and dom == 'stateLaw:%d' % adopter_system
        if filt in NOTATION_FILTERS:
            # L4 (five limits, H4): with commission.tsv the notation filters are visible: the node's notation maps to
            # exactly one filter (no row = 'none'); an unclassified notation ('other') stays unknown. Without the
            # file they are unknown, as before (R5).
            nf = self.notation_filter(node)
            return None if nf is None else nf == filt
        return None

    def notation_filter(self, node):
        """L4: the adoption filter a decision's commission notation satisfies; None = unknown (no commission.tsv, or
        a notation of unclassified wording)."""
        cm = self.D.commission
        if cm is None:
            return 'none'            # D4 reading (DEVIATIONS 63): an adoption not shown is no adoption (H4)
        n = cm.get(node)
        if n is None:
            return 'none'
        return NOTATION_FILTER.get(n, 'none')   # unclassified wording: no adoption shown (H4; D4 reading)

    def tx_promotes(self, r, ep):
        """L5 (five limits; S-TX "Supreme Court review notations", F3, §5.1 A): does an admitted writRefused row give
        a decision the precedential value of a Supreme Court of Texas opinion? Only a Texas intermediate court's
        decision; writ era (notation dated before 1 Sept 1997): "writ ref'd" (the writ of error is civil); petition
        era (from 1 Sept 1997): "pet. ref'd" when the case is shown civil (the refusing decision is of the civil
        court of last resort). A known refusing decision of any other court promotes nothing. n.r.e., denied,
        dismissed (w.o.j.) and PDR (criminal) notations add nothing."""
        D = self.D
        if ep.system == 0 or ep.tier != 'A' or D.state_name.get(ep.system) != 'Texas':
            return False
        d = r['date']
        if d <= 0:
            return False
        q = ascii_lower(norm_quote(r['cert'].quote))
        if TX_NOADD.search(q) or TX_CRIMINAL.search(q):
            return False
        writ, pet = bool(TX_WRIT_REF.search(q)), bool(TX_PET_REF.search(q))
        if writ == pet:
            return False                      # neither, or both: the notation is not identified
        B = r['by']
        civil_by = None                       # None: the refusing decision is not known
        if B is not None and B >= 0 and D.has(B):
            be = self.epoch(D.court[B], D.date[B])
            civil_by = be is not None and be.system == ep.system and be.tier == 'L' and be.lrf == 'civil'
        if civil_by is False:
            return False                      # a known refusing decision that is not the Supreme Court of Texas
        if writ:
            return d < TX_PETITION_ERA        # the writ of error was civil: civil shown by the wording
        if d < TX_PETITION_ERA:
            return False                      # "pet. ref'd" before 1997 is a criminal PDR refusal
        return civil_by is True               # petition era: civil shown only by the refusing court

    def holders(self, node, t, dom=None):
        """Who holds a decision's authority at t.
        H3: after rename/replace/absorb the successor holds it, with the deciding court's dated tier; after a
        split the old court keeps it too while it still exists. R7: where an adoption row covers the same
        (new, old) pair, the adoption row governs that inheritance instead of the succession row.
        R2-73 (DEVIATIONS 73): a split row never makes the new court hold the old court's decisions, in either run;
        only an adoption row does. Nor is the new court a court the decision "passed through" for adoption rows.
        F10/F11/§3.2: an adopter holds adopted decisions as its own (power only if adopter tier >= dated tier, R6)."""
        D = self.D
        c, d = D.court[node], D.date[node]
        ep = self.epoch(c, d)
        if ep is None:
            return None
        seen = {c}
        stack = [c]
        finals = []
        while stack:
            x = stack.pop()
            sx = [] if 'successionIgnored' in MUT else [
                (n, kind) for (n, sd, kind) in self.succ.get(x, ()) if n != x and d < sd <= t]
            # R2-73: a split passes nothing on, so a court with only split successors keeps its decisions, whether or
            # not it still has an epoch on the question date (as a court with no successor does)
            if all(k == 'split' for (_, k) in sx):
                finals.append(x)
            for (n, kind) in sx:
                if kind == 'split':
                    continue                  # R2-73: a court made by dividing another takes nothing by the division
                if (n, x) in self.adopt_pairs or (n, c) in self.adopt_pairs:
                    continue
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        out = []
        u = D.unit[node]
        for x in finals:
            if x == c:
                out.append(Holder(c, ep.tier, ep.system, ep.circuit, u, None, True, 'own'))
            else:
                xe = self.epoch(x, t)
                sysx = xe.system if xe else ep.system
                circx = xe.circuit if xe else ep.circuit
                out.append(Holder(x, ep.tier, sysx, circx, u, None, True, 'succession'))
        srcs = {c}
        frontier = [c]
        while frontier:                       # adoption sources: the court and every court it passed through
            x = frontier.pop()
            for (n, sd, kind) in self.succ.get(x, ()):
                if n != x and d < sd and n not in srcs and kind != 'split':   # R2-73
                    srcs.add(n)
                    frontier.append(n)
        for srcc in srcs:
            for (adopter, upto, filt, force) in self.adopt.get(srcc, ()):
                if d > upto:
                    continue
                ae = self.epoch(adopter, t)
                if ae is None:
                    continue
                fm = self.filter_match(filt, node, dom, ae.system)
                if fm is False:
                    continue
                cap = force if fm else UNK
                power = TIER_RANK[ae.tier] >= TIER_RANK[ep.tier]
                out.append(Holder(adopter, ae.tier, ae.system, ae.circuit, 0, cap, power, 'adoption'))
        # S-TX / F3 exception: "writ refused" / "pet. refused" gives the opinion the precedential value of an
        # opinion of the (civil) court of last resort, from the notation's date (R24, narrowed by L5: Texas civil
        # intermediate decisions only, by era and wording)
        for r in self.hist_rows(node):
            if r['kind'] == 'writRefused' and 0 < r['date'] <= t and self.tx_promotes(r, ep):
                lr = self.last_resort(ep.system, t, 'civil')
                if lr is not None:
                    out.append(Holder(lr.court, 'L', lr.system, lr.circuit, 0, None, False, 'writRefused'))
                break
        return out

    def last_resort(self, system, t, kind):
        best = None
        for c, eps in self.courts.items():
            for e in eps:
                if e.system == system and e.tier == 'L' and e.frm <= t <= e.to and e.lrf in (kind, 'all'):
                    if best is None or e.lrf == kind:
                        best = e
        return best

    def domain_of(self, issue_key):
        if not issue_key:
            return 'unknown'
        i = self.D.issues.get(issue_key)
        return i['domain'] if i else 'unknown'

    def domain_candidates(self, systems, circuits):
        c = ['federalGeneral']
        if 13 in circuits:
            c.append('federalPatent')
        for s in sorted(set(systems)):
            if s:
                c.append('stateLaw:%d' % s)
        return c

    @staticmethod
    def is_tax_court(e):
        return bool(re.search(r'Tax Court|Board of Tax Appeals', e.name))

    # ---------------------------------------------------------------- authority (§8.2 step 6)
    def rel(self, h, node, dst, dep, du, dom, t, ctx):
        D = self.D
        stier, ssys, scirc, su = h.tier, h.system, h.circuit, h.unit
        dtier, dsys = dep.tier, dep.system
        # S-TX TRAP 41.3: transferee follows transferor precedent in the transferred case
        if ctx and ctx.get('transfer_from') == h.court and stier == 'A' and dtier == 'A' and ssys == dsys:
            return ('binding', 'S-TX.41.3')
        if ssys == 0 and dsys == 0 and not (stier == 'L') and dom.startswith('stateLaw') and D.date[node] < ERIE:
            return ('persuasive', 'E1.preErieFederal')   # (c) DEVIATIONS 2: Swift-era general law, even in-circuit
        if h.court == dst and stier == dtier:          # same court (by id and dated tier, H3/§9.5)
            if stier == 'T':
                return ('persuasive', 'F13.selfNotBound')
            if stier == 'D':
                return ('persuasive', '4.4.selfNotBound')
            if stier == 'S':
                # D4 reading (five limits): a special court (the Tax Court, F12; a state special court such as the
                # Texas Commission of Appeals) follows its own precedent without being bound by a horizontal rule
                return ('persuasiveStrong', 'F12.self')
            # keyed on the precedent's date (S-MI, R9); H6: a court of last resort holds an adopted decision from
            # the adoption on, so its court-level (divisional) row is keyed on the question date (M.A.P. v. Ryan)
            hz = self.horizontal(ssys, h.court, stier, t if (h.via == 'adoption' and stier == 'L') else D.date[node])
            if hz is None:
                if stier == 'L':
                    return ('persuasiveStrong', 'H1.selfNotBound')
                return ('persuasiveStrong', 'assumeHorizontalSoft')   # (c): no row -> adheres, may overrule
            if hz == 'strong':
                return ('binding', 'F7/4.1.strong')
            if hz == 'soft':
                return ('persuasiveStrong', '4.1.soft')
            if hz == 'none':
                return ('persuasive', '4.1.none')
            if hz == 'withinUnitOnly':
                if du is None:
                    return (UNK, 'unit')
                return ('binding', '4.1.withinUnit') if su == du else ('persuasive', '4.1.otherUnit')
            return (UNK, 'horizontal.value:' + hz)
        if ssys == 0 and stier == 'L':                 # SCOTUS
            if dom.startswith('federal'):
                return ('binding', 'F1')
            # R10 (revised, D4 triage (b)): F1 binds "on federal questions only"; a SCOTUS reading of state law is
            # persuasive everywhere (lower federal courts follow the state's highest court, E1)
            return ('persuasive', 'F1.notOnStateLaw')
        if ssys != 0:                                  # state source
            if dsys == ssys:
                if stier == 'L':
                    if dtier == 'L':
                        return ('persuasive', 'H2.dualLastResort')
                    return ('binding', 'H1')
                if stier == 'A':
                    if dtier in ('T', 'D', 'S'):
                        return self.trial_scope(ssys, h.court, su, du, t)
                    return ('persuasive', '4.1.notVertical')
                if stier == 'D':
                    if dtier == 'T':
                        if du is None or su == 0 or du == 0:
                            return ('persuasive', '4.4.unitUnknown')   # (c): not shown to be the same unit
                        return ('binding', '4.4.appellateDivision') if su == du else ('persuasive', '4.4')
                    return ('persuasive', '4.4')
                return ('persuasive', '4.4.trialNotBinding')
            if dsys == 0:
                if dom == 'stateLaw:%d' % ssys:
                    if stier == 'L':
                        # (c) D4 triage: before Erie the Swift local/general split is not modelled: persuasive
                        return ('binding', 'E1') if t >= ERIE else ('persuasive', 'E1.preErie')
                    if stier == 'A':
                        return ('persuasiveStrong', 'E1.West')
                    return ('persuasive', 'E1.King')
                return ('persuasive', 'E3.stateOnFederal')
            return ('persuasive', 'X.otherSystem')       # R12
        # federal source below SCOTUS
        if dsys == 0:
            if stier == 'A':
                if scirc == 13:                          # F11(b) Federal Circuit: subject matter, not geography
                    # b2: reach binds the lower courts of circuit 13 only; another appellate court of circuit 13
                    # (the CCPA) falls through to F7.otherCircuit
                    if dep.circuit == 13 and dtier in FED_LOWER:
                        return ('binding', 'F11b.reach')
                    if dtier in FED_LOWER:
                        return ('binding', 'F11b.patent') if dom == 'federalPatent' else (
                            'persuasive', 'F11b.regionalLaw')
                    return ('persuasive', 'F7.otherCircuit')
                if self.is_tax_court(dep):               # F12 Golsen
                    v = (ctx or {}).get('venue')
                    if v is None:
                        return ('persuasive', 'F12.noVenue')   # (c): no case venue -> a national special court
                    return ('binding', 'F12') if v == scirc else ('persuasive', 'F12')
                if dtier in FED_LOWER and dep.circuit == scirc and scirc != 0:
                    if dom == 'federalPatent' and t >= FED_CIR_START:
                        return ('persuasive', 'F11b.patentExclusive')
                    if dom.startswith('stateLaw') and D.date[node] < ERIE:
                        return ('persuasive', 'E1.preErieFederal')   # (c): federal general law is not state law
                    return ('binding', 'F7.district')
                return ('persuasive', 'F7.otherCircuit')
            if stier == 'B':
                return ('persuasive', 'F13.BAP')
            return ('persuasive', 'F13')
        if dom.startswith('federal'):                    # federal source, state destination
            if stier == 'A':
                v = self.rule(dsys, None, 'stateFollowsCircuit', t)
                if v is not None:
                    sc = self.state_circuit.get(dsys)
                    if sc is None:
                        return ('persuasive', 'E3.stateCircuitUnknown')   # (c): the row cannot be placed
                    if sc == scirc:
                        return (v, 'E3.table')
            return ('persuasive', 'E3')
        if 'erieBothWays' in MUT and stier == 'A':
            return ('binding', 'MUTANT')
        return ('persuasive', 'E1.corollary')

    def trial_scope(self, system, court, su, du, t):
        v = self.rule(system, court, 'trialScope', t)    # keyed on the date of the question (R9)
        if v is None:
            return ('binding', 'assumeStatewide')        # (c): no row -> statewide, the majority rule (§4.3)
        if v == 'statewide':
            return ('binding', '4.1.V.statewide')
        if v == 'statewideChooseOnConflict':
            return ('bindingAbsentConflict', '4.1.V.chooseOnConflict')
        # (c) D4 triage: a unit that is not known is not shown to be the own unit (read as another unit)
        own = du is not None and su != 0 and du != 0 and su == du
        if v == 'ownUnitThenAny':
            return ('binding', '4.1.V.ownUnit') if own else ('bindingAbsentConflict', '4.1.V.otherUnit')
        if v == 'ownUnitOnly':
            return ('binding', '4.1.V.ownUnit') if own else ('persuasive', '4.1.V.ownUnitOnly')
        return (UNK, 'trialScope.value:' + v)

    def unpub_cap(self, node, pubkind):
        """§9.15 unpubForce : Court -> Date(precedent) -> Publication -> Force. Values are '<force>' (every
        non-published kind) or '<publication>:<force>' (that kind only); court-level rows first (R4, R8)."""
        D = self.D
        e = self.epoch(D.court[node], D.date[node])
        date = D.date[node]
        for key in ((-D.court[node], 'unpubForce'), (e.system if e else -1, 'unpubForce')):
            vals = [v for (v, frm, to) in self.rules.get(key, ()) if frm <= date <= to]
            spec = [v.split(':', 1)[1] for v in vals if v.startswith(pubkind + ':')]
            if spec:
                return (spec[0], 'F9.rule:' + pubkind)
            gen = [v for v in vals if ':' not in v]
            if gen:
                return (gen[0], 'F9.rule')
        return ('persuasive', 'F9.default')

    def decision_caps(self, node, issue_key, role, f):
        """§8.2 steps 2-3, F2, F5, F6, F9 per decision; unknown publication/form evaluated over its values."""
        D = self.D
        pub = PUB[D.pub[node]]
        form = FORM[D.form[node]]
        # R1 (revised, D4 triage (c)): an unknown publication is read as published and an unknown form as a full
        # opinion (the official reporter is the usual channel), each named in the reason, not enumerated
        pubs = [pub] if pub != 'unknown' else ['published']
        if role in ('majority', 'perCuriam'):
            # HD6: a majority part of a plurality decision binds; (c) D4 triage: an equally divided court has no
            # majority, so F5 caps whatever role the reader gave the holding
            forms = ['full'] if form in ('unknown', 'plurality') else [form]
        else:
            forms = [form] if form != 'unknown' else ['full']
        outs = []
        for p in pubs:
            for fm in forms:
                g = f
                if p in UNPUB and 'ignoreUnpublished' not in MUT:
                    g = fmin(g, self.unpub_cap(node, p))
                if fm == 'memorandum' and 'ignoreUnpublished' not in MUT:
                    g = fmin(g, ('persuasive', 'F9.memorandumForm'))   # (c) D4: a memorandum form caps at persuasive
                if fm == 'equallyDivided':
                    g = fmin(g, ('none', 'F5'))
                plural = (role == 'plurality') if role else (fm == 'plurality')
                if plural and (node, issue_key) not in self.marks:
                    g = fmin(g, ('resultOnly', 'F6'))
                if self.D.commission is not None and self.D.commission.get(node) == 'judgmentAdopted':
                    g = fmin(g, ('resultOnly', 'H4.judgmentAdopted'))   # L4: only the judgment was adopted
                outs.append(g)
        return agree(outs, 'publication/form')

    def last_epoch(self, c, t):
        """R3-80 (DEVIATIONS 80): the last epoch of court c that ended before t (None: c never sat before t)."""
        eps = [e for e in (self.courts.get(c) or ()) if e.to < t]
        return max(eps, key=lambda e: e.to) if eps else None

    def authority(self, node, issue_key, role, dst, t, dst_unit=None, ctx=None, dep_as=None):
        """Force of a decision's holding on court dst at date t, ignoring its status (§8.2 step 6 + caps).
        dep_as (R3-80): the epoch dst is asked in when it has none on t (a ceased court, asked as it last sat)."""
        D = self.D
        if not D.has(node):
            return (UNK, 'noDecision')
        d = D.date[node]
        if d == 0:
            return (UNK, 'date')
        if t < d:
            return ('none', 'notYetDecided')
        dep = self.epoch(dst, t)
        if dep is None:
            dep = dep_as
        if dep is None:
            return (UNK, 'dstEpoch')
        hs0 = self.holders(node, t)
        if not hs0:
            return (UNK, 'srcEpoch')
        du = dst_unit if dst_unit else dep.unit     # (b) D4: unit 0 = unknown -> the court's unit
        dom = self.domain_of(issue_key)
        # b1: candidate domains come from the own and succession holders and the destination; an adopter's system is
        # not a domain the issue can have at an unrelated court
        hs1 = [h for h in hs0 if h.via != 'adoption']
        oe = self.epoch(D.court[node], d)    # R2-73: the deciding court's own system stays a candidate when it is gone
        doms = [dom] if dom != 'unknown' else self.domain_candidates(
            [h.system for h in hs1] + [dep.system] + ([oe.system] if oe else []),
            [h.circuit for h in hs1] + [dep.circuit] + ([oe.circuit] if oe else []))
        res = []
        for dm in doms:
            hs = self.holders(node, t, dm)
            f = None
            for h in hs:
                r = self.rel(h, node, dst, dep, du, dm, t, ctx)
                if h.cap is not None:
                    r = fmin(r, (h.cap, 'adoption.cap'))
                f = r if f is None else fmax(f, r)
            res.append(self.decision_caps(node, issue_key, role, f))
        return agree(res, 'domain')

    def force(self, node, holding_id, dst, t, u, dst_unit=None, ctx=None):
        """force(src, holding, dst, t, u) per §8.2: status first (steps 1, 4, 5), then authority."""
        h = self.adm_holdings.get(holding_id) if holding_id not in (None, '-') else None
        issue_key = h['issue'] if h else None
        role = h['role'] if h else None
        base = self.authority(node, issue_key, role, dst, t, dst_unit, ctx)
        st, kind, by = self.status(node, holding_id, t, u)
        if st == 'negative':
            k = kind.split(':')[0]
            if kind.endswith(':partial'):
                return fmin(base, (UNK, 'status:partial:' + k))
            if k == 'depublished':
                cap = ('notCitable', 'status:depublished')
            elif k == 'reviewGranted':
                start = self._effect_start(node, holding_id, t, u)
                cap = ('notCitable', 'S-CA.reviewGranted<2016') if start and start < CA_REVIEW_2016 else (
                    'persuasive', 'S-CA.reviewGranted')
            else:
                cap = ('none', 'status:' + k)
            return fmin(base, cap)
        if st == UNK:
            return fmin(base, (UNK, 'status:' + kind))
        return base

    def _effect_start(self, node, holding_id, t, u):
        for (frm, to, pieces) in self.timeline(node, self.keyset_for(node, holding_id)):
            if frm <= t < to:
                return frm
        return None

    # ---------------------------------------------------------------- canChangeStatus (§9.23, T1, T2)
    def can_change(self, B, X, dom='unknown'):
        D = self.D
        if not D.has(B) or not D.has(X):
            return ('unknown', 'noDecision')
        bd, xd = D.date[B], D.date[X]
        if bd == 0 or xd == 0:
            return ('unknown', 'date')
        if bd < xd:
            return ('no', 'T1.earlier')
        be = self.epoch(D.court[B], bd)
        if be is None:
            return ('unknown', 'byEpoch')
        hs0 = self.holders(X, bd)
        if not hs0:
            return ('unknown', 'targetEpoch')
        hs1 = [h for h in hs0 if h.via != 'adoption']   # b1: as in authority()
        oe = self.epoch(D.court[X], xd)      # R2-73: the deciding court's own system stays a candidate when it is gone
        doms = [dom] if dom != 'unknown' else self.domain_candidates(
            [h.system for h in hs1] + [be.system] + ([oe.system] if oe else []),
            [h.circuit for h in hs1] + [be.circuit] + ([oe.circuit] if oe else []))
        res = []
        for dm in doms:
            hs = self.holders(X, bd, dm)
            best = ('no', 'T2.noPower')
            for h in hs:
                r = self.power(B, be, h, X, dm)
                if r[0] == 'yes':
                    best = r
                    break
                if r[0] == 'unknown' or (r[0] == 'no' and best[0] == 'no' and best[1].startswith('T2')):
                    best = r
            res.append(best)
        vals = {r[0] for r in res}
        if len(vals) == 1:
            return res[0]
        return ('unknown', 'ambiguous:domain')

    def bench_ok(self, B, court, bd):
        b = BENCH[self.D.bench[B]]
        if b in EN_BANC_EQUIV:
            return ('yes', 'F8.enBanc')
        if b == 'circulated':
            v = self.rule(self.epoch(court, bd).system if self.epoch(court, bd) else -1, court,
                          'circulationCountsAsEnBanc', bd)
            if v is None:
                return ('no', 'F7.circulatedAssumeNotEnBanc')     # R31 (c): no row -> not en banc
            return ('yes', 'F7.circulated') if v == '1' else ('no', 'F7.circulatedNotEnBanc')
        if b in ('panel', 'division'):
            if 'panelOverrulesPanel' in MUT:
                return ('yes', 'MUTANT')
            return ('no', 'F7.panelCannotOverrulePanel')
        return ('no', 'R31.assumePanel')     # R31 (c): an unknown bench is not shown to be en banc

    def power(self, B, be, h, X, dom):
        D = self.D
        if not h.power:
            return ('no', 'R6.adoptedFromHigher')
        bc = D.court[B]
        if self.is_scotus(be):
            if h.system == 0:
                return ('yes', 'F1')
            return ('yes', 'F1/F14') if dom.startswith('federal') else ('no', 'T2.scotusOnStateLaw')
        if bc == h.court and be.tier == h.tier:
            if h.tier in ('T', 'D'):
                return ('no', 'F13.trialNoBindingStatus')
            # H6: for a decision a court of last resort holds by adoption, the row on the treating date
            hz = self.horizontal(h.system, h.court, h.tier,
                                 D.date[B] if (h.via == 'adoption' and h.tier == 'L') else D.date[X])
            if hz is None:
                if h.tier == 'L':
                    return ('yes', 'H1.overruleOwn')
                return self.bench_ok(B, bc, D.date[B])   # R31 (c): no row -> en banc needed (as strong)
            if hz in ('soft', 'none'):
                return ('yes', '9.23.' + hz)
            if hz == 'strong':
                return self.bench_ok(B, bc, D.date[B])
            if hz == 'withinUnitOnly':
                if D.unit[B] != h.unit:
                    return ('no', 'S-FL.sisterUnit')
                return self.bench_ok(B, bc, D.date[B])
            return ('unknown', 'horizontal.value:' + hz)
        if be.system == h.system:
            if be.system != 0:
                if be.tier == 'L':
                    return ('no', 'H2.dualLastResort') if h.tier == 'L' else ('yes', 'H1')
                if be.tier == 'A' and h.tier in ('T', 'D', 'S'):   # (b) D4: a state special court is trial-level
                    return ('yes', '4.1.IACoverTrial')
                if be.tier == 'D' and h.tier == 'T':
                    if D.unit[B] == 0 or h.unit == 0:
                        return ('no', '4.4.unitUnknown')   # R31 (c): not shown to be the same unit
                    return ('yes', '4.4') if D.unit[B] == h.unit else ('no', '4.4')
                return ('no', 'T2.notHigher')
            if be.tier == 'A' and h.tier in FED_LOWER:
                if be.circuit == 13:
                    if h.circuit == 13 or dom == 'federalPatent':
                        return ('yes', 'F11b')
                    return ('no', 'F11b.regional')
                if be.circuit == h.circuit and be.circuit != 0:
                    return ('yes', 'F7.district')
            return ('no', 'T2.notHigher')
        return ('no', 'T2.crossSystem')

    # ---------------------------------------------------------------- certificates (DESIGN layer 4; R19-R22)
    def check_cert(self, cert, owners, kind, need_target, require_verb=True, target=None):
        D = self.D
        shas = {D.sha.get(o) for o in owners if o is not None and o >= 0 and D.has(o)}
        shas.discard(None)
        if not shas:
            return 'noDecision'
        if cert.sha not in shas:
            return 'shaMismatch'
        if cert.start < 0 or cert.end <= cert.start:
            return 'offsets'
        q = norm_quote(cert.quote)
        if len(q) != cert.end - cert.start:
            return 'quoteLength'
        wins = D.cert_text.get(cert.sha, ())
        # well-formed covering windows; L7 (five limits): with window_sha.tsv only hash-consistent ones are usable
        formed = [w for (s0, e0, w, hok) in wins if s0 <= cert.start and cert.end <= e0 and len(w) == e0 - s0]
        usable = [(s0, w) for (s0, e0, w, hok) in wins
                  if s0 <= cert.start and cert.end <= e0 and len(w) == e0 - s0 and hok]
        found = None
        for (s0, w) in usable:
            if norm_quote(w)[cert.start - s0:cert.end - s0] == q:   # fuzz: the window normalised too, as Lean
                found = w
                break
        if found is None:
            if not any(s0 <= cert.start and cert.end <= e0 for (s0, e0, w, hok) in wins):
                return 'noWindow'
            if formed and not usable:
                return 'windowHash'
            return 'quoteMismatch'
        ql = ascii_lower(q)    # fuzz: as Lean's toLower
        if require_verb and kind == 'other':
            return 'noVerb'                  # R28 (c): no verb names an 'other' event, so none can be certified
        if require_verb:
            verbs = VERBS.get(kind)
            if verbs and not any(v in ql for v in verbs):
                return 'noVerb'
        if require_verb and kind in NEG_TREAT and any(x in ql for x in DISQUALIFY_TREAT):
            return 'disqualified'
        if require_verb and kind in HIST_KINDS_ALL and any(x in ql for x in DISQUALIFY_HIST):
            return 'disqualified'
        if need_target:
            # R21 (revised, D4 real data): the target is named in the quote or in its covering window (the reader
            # quotes the treating sentence; the citation or caption is often next to it); citations compare as
            # lowercase letters and digits (SCHEMA cite:<normalised citation>); names as whole words of >= 3 chars
            ev = cert.tev or ''
            ctx = (q + ' ' + ' '.join(norm_quote(w) for (s0, w) in usable))   # L7: usable windows only
            ctx = ascii_lower(ctx)    # fuzz: as Lean's toLower
            if ev.startswith('cite:'):
                c = alnum(ev[5:])
                if not c or c not in alnum(ctx):
                    return 'noTarget'
                # L6 (five limits): with cite_index.tsv the citation must also resolve to the row's target (a compact
                # key indexed to >= 2 distinct nodes is ambiguous and resolves to nothing)
                if D.cite_index is not None and (target is None or D.cite_index.get(c) != target):
                    return 'noTarget'
            elif ev.startswith('name:'):
                words = set(re.findall(r'[0-9a-z]+', ctx))
                toks = [alnum(x) for x in ev[5:].split(' ')]   # fuzz: split() also split on NBSP; Lean splits on ' '
                toks = [x for x in toks if len(x) >= 3]
                if not toks or not all(x in words for x in toks):
                    return 'noTarget'
            else:
                return 'noTarget'
        if cert.part not in CERT_PARTS and not ('certAcceptsDissent' in MUT and cert.part == 'dissent'):
            return 'part'
        return 'ok'

    def check_witness(self, r, W, by_ev):
        """Round 4 (round3/implicit_schema.md): r says "X was overruled by Y" in the words of a later decision W.
        Order as Lean's Cert.checkWitness. A row that fails only date order X <= Y passes as a certificate (Lean:
        targetLater, canonical 'ok'); at_risk skips it by date."""
        D = self.D
        X, Y = r['target'], r['by']
        if not D.has(W) or r['explicit'] != 0 or r['kind'] not in NEG_TREAT:
            return 'witnessBadRow'
        res = self.check_cert(r['cert'], [W], r['kind'], True, target=X)
        if res != 'ok':
            return res
        c2 = Cert([r['cert'].sha, str(r['cert'].start), str(r['cert'].end), r['cert'].quote, by_ev, r['cert'].part])
        if self.check_cert(c2, [W], r['kind'], True, target=Y) != 'ok':
            return 'byUnresolved'
        if D.date[Y] < D.date[X]:
            return 'ok'
        if D.date[Y] != 0 and D.date[W] != 0 and D.date[W] < D.date[Y]:
            return 'witnessEarlier'
        if D.court[W] != D.court[X] and self.can_change(W, X, 'unknown')[0] != 'yes':
            return 'witnessNoStanding'
        return 'ok'

    def admit(self):
        """Run every certificate check once; build the admitted views used by status/findings/splits."""
        D = self.D
        for r in D.treatments:
            wit = D.witness.get(r['id'])
            if wit is not None and D.has(r['by']) and D.has(r['target']):
                res = self.check_witness(r, wit[0], wit[1])
            else:
                res = self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'])
            # fuzz: a row naming an unknown kind or temporal value, or a node with no decisions2 row, asserts
            # nothing (Lean: badRow); it was admitted when only the target's decision was missing, and an empty
            # temporal read as 'unknown'
            if (r['kind'] not in _TKINDS or not _temporal_ok(r['temporal_raw']) or not D.has(r['by'])
                    or not D.has(r['target'])):
                res = 'badRow'
            self.cert_ok[('treatments.tsv', r['id'])] = res
            self.treat_by_id[r['id']] = r
            if res == 'ok':
                self.adm_treat[r['target']].append(r)
        for r in D.history:
            own_text = D.sha.get(r['target']) == r['cert'].sha
            res = self.check_cert(r['cert'], [r['target'], r['by']], r['kind'], not own_text, target=r['target'])
            if r['kind'] not in _HKINDS or not D.has(r['target']):    # fuzz: as Lean's badRow
                res = 'badRow'
            self.cert_ok[('history.tsv', r['id'])] = res
            if res == 'ok':
                self.adm_hist[r['target']].append(r)
        for h in D.holdings.values():
            res = self.check_cert(h['cert'], [h['node']], None, False, require_verb=False)
            if res == 'ok' and h['role'] not in CERT_PARTS:
                res = 'role'
            self.cert_ok[('holdings.tsv', h['id'])] = res
            if res == 'ok':
                self.adm_holdings[h['id']] = h
                self.adm_holdings_by_node[h['node']].append(h)
        for s in D.supersessions:
            self.sup_by_target[s['target']].append(s)
            ev = s['evidence']
            if ev.startswith('laterCourtSays:'):
                self.linked_treat.add(ev.split(':', 1)[1])

    def share_admission(self, other):
        for a in ('cert_ok', 'adm_hist', 'adm_treat', 'treat_by_id', 'adm_holdings', 'adm_holdings_by_node',
                  'sup_by_target', 'linked_treat'):
            setattr(self, a, getattr(other, a))

    def same_case_power(self, B, X):
        """R25 (§5.1 A, T1(a), H3, F1). A same-case event acts on X's own judgment or opinion, so it is decided by
        X's court itself (withdrawal, substitution, rehearing, reinstatement: any bench), a successor of X's court,
        a court that reviews X: a higher court of X's system (in the federal system, X's own circuit, or the
        Federal Circuit, which hears appeals from every district court and the Court of Federal Claims), or SCOTUS
        (federal decisions, and state decisions on federal questions). -> 'yes' | 'no' | 'unknown' (deciding
        decision or an epoch unknown: admitted, like a row with by = -1)."""
        D = self.D
        if B is None or B < 0 or not D.has(B) or not D.has(X):
            return 'unknown'
        be, xe = self.epoch(D.court[B], D.date[B]), self.epoch(D.court[X], D.date[X])
        if be is None or xe is None:
            return 'unknown'
        if be.court == xe.court or self.is_scotus(be):
            return 'yes'
        seen, stack = {xe.court}, [xe.court]
        while stack:
            c = stack.pop()
            for (n, sd, kind) in self.succ.get(c, ()):
                if n == be.court:
                    return 'yes'
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        if be.system == 0 and be.tier == 'B' and xe.tier in ('S', 'T') and be.circuit == xe.circuit != 0:
            return 'yes'          # (b) D4: a BAP reviews the bankruptcy courts of its circuit (F13)
        if be.system == xe.system and TIER_RANK[be.tier] > TIER_RANK[xe.tier]:
            # (b) D4 real data: in the federal system only a court of appeals reviews (its own circuit's courts, or
            # the Federal Circuit any); a special court such as a bankruptcy court reviews no district court
            # b3 (real-data triage, 12 Nov): a state special court is trial-level too (a New York Surrogate's Court
            # does not review the Supreme Court, the general trial court): it reviews no court
            if (be.system != 0 and be.tier != 'S') or (
                    be.system == 0 and be.tier == 'A' and (be.circuit == 13 or be.circuit == xe.circuit != 0)):
                return 'yes'
        return 'no'

    def hist_rows(self, node):
        """Admitted same-case history of `node` (certificate passed) whose deciding court may act on it (R25)."""
        return [r for r in self.adm_hist.get(node, ()) if self.same_case_power(r['by'], node) != 'no']

    # ---------------------------------------------------------------- status (§5, §6, §7, §8.2; D5)
    def keyset_for(self, node, holding_id):
        if holding_id in (None, '-'):
            return None
        h = self.adm_holdings.get(holding_id)
        return frozenset([h['issue']]) if h else None

    @staticmethod
    def scope_applies(scope, keyset):
        """'full' | 'partial' | 'none' | 'unknownScope' | 'otherGrounds' (T1, HD4, §8.2 anonymous issue)."""
        if scope == 'all':
            return 'full'
        if scope.startswith('issues:'):
            ks = {k for k in scope[7:].split(',') if k}
            if keyset is None:
                return 'partial'
            if 'ignorePartialScope' in MUT:
                return 'full'
            if keyset <= ks:
                return 'full'
            if keyset & ks:
                return 'partial'
            return 'none'
        if scope == 'otherGrounds':
            return 'partial' if keyset is None else 'otherGrounds'
        return 'partial' if keyset is None else 'unknownScope'   # partialUnknown / unknown

    def temporal_ranges(self, temporal, date, dom):
        """TM2: conduct ranges an overruling covers: [(cfrom, cto, overrideStatus)]."""
        if 'temporalIgnored' in MUT:
            return [(0, OPEN, None)]
        if temporal == 'retroactive':
            return [(0, OPEN, None)]
        if temporal.startswith('prospectiveFrom:'):
            return [(toint(temporal.split(':', 1)[1]), OPEN, None)]
        if temporal == 'pureProspective':
            return [(next_day(date), OPEN, None)]
        # R14 (revised, D4 triage (c)): an unknown temporal scope is retroactive: Harper / Griffith for federal law,
        # and the general rule (retroactivity, e.g. New Mexico's presumption, Washington's bar on selective
        # prospectivity) for state law; a prospective overruling must say so (TM2 detection phrases)
        return [(0, OPEN, None)]

    def effects(self, node, keyset):
        D = self.D
        E = []   # [start, end, cfrom, cto, status, kind, by, dep]
        # A. same-case history (§5.1 A, F4, F8, TM3, S-CA)
        hist = sorted(self.hist_rows(node),
                      key=lambda r: (r['date'], 1 if r['kind'] in CLOSES and r['kind'] not in NEG_HIST else 0,
                                     str(r['id'])))
        for r in hist:
            k, dt = r['kind'], r['date']
            if dt == 0:
                continue
            if k in CLOSES:
                for e in E:
                    ek = e[5].split(':')
                    ek = ek[1] if ek[0] in ('unknownScope', 'otherGrounds') and len(ek) > 1 else ek[0]
                    if e[7] is None and ek in CLOSES[k] and e[0] <= dt < e[1]:   # (b) D4: unknown-scope kinds too
                        e[1] = dt
            if k not in NEG_HIST or ('vacaturIgnored' in MUT and k in ('vacated', 'withdrawn')):
                continue
            status = 'negative'
            kind = k
            if k == 'rehearingEnBancGranted':
                ce = self.epoch(D.court[node], dt)
                v = self.rule(ce.system if ce else -1, D.court[node], 'enBancGrantVacatesPanel', dt)
                if v is None:
                    status, kind = UNK, 'enBancGrantVacatesPanel.missing'
                elif v != '1':
                    continue
            if k == 'reviewGranted':
                # R16 (revised, D4 triage): S-CA's effect is read from the approved system rule reviewGrantedForce
                # (DESIGN D9), court- or system-level, keyed on the grant date: force <= notCitable -> depublished,
                # otherwise a persuasive cap (reviewPending). No row -> no effect, as cert. granted elsewhere.
                ce = self.epoch(D.court[node], D.date[node])
                v = self.rule(ce.system if ce else -1, D.court[node], 'reviewGrantedForce', dt)
                if v is None or v not in FORCE_RANK:
                    continue
                if FORCE_RANK[v] <= FORCE_RANK['notCitable']:
                    kind = 'reviewGrantedDepublished'
            app = self.scope_applies(r['scope'], keyset)
            if app == 'none':
                continue
            if app == 'partial':
                kind = kind + ':partial'
            elif app in ('unknownScope', 'otherGrounds'):
                status, kind = UNK, app + ':' + k
            E.append([dt, OPEN, 0, OPEN, status, kind, str(r['by']), None])
        # B. later-case treatments (§5.1 B, T1, T2, T3, F14, TM2)
        for r in sorted(self.adm_treat.get(node, ()), key=lambda r: (r['date'], str(r['id']))):
            k = r['kind']
            B = r['by']
            dt = r['date'] or (D.date[B] if D.has(B) else 0)
            if dt == 0:
                continue
            if k in NEG_TREAT:
                app = self.scope_applies(r['scope'], keyset)
                if app == 'none':
                    continue
                if keyset:
                    dom = self.domain_of(next(iter(keyset)))
                    pw = self.can_change(B, node, dom)
                elif r['scope'].startswith('issues:'):
                    # T1(b): power over each issue the treatment names, on that issue's domain; the anonymous
                    # issue is reached (partially) if power over some named issue is shown (D4 triage)
                    ds = {self.domain_of(x) for x in r['scope'][7:].split(',') if x}
                    dom = ds.pop() if len(ds) == 1 else 'unknown'
                    pws = [self.can_change(B, node, self.domain_of(x)) for x in r['scope'][7:].split(',') if x]
                    pw = next((p for p in pws if p[0] == 'yes'), None) or next(
                        (p for p in pws if p[0] == 'unknown'), None) or (pws[0] if pws else ('no', 'T2.noIssue'))
                else:
                    dom = 'unknown'
                    pw = self.can_change(B, node, dom)
                if pw[0] == 'no':
                    continue                 # T2: a claim, not a status change (kept for findings)
                if r['explicit'] != 1:
                    continue                 # R26 (§9.26): an inferred treatment never proves status (atRisk only)
                status, kind = 'negative', k
                if pw[0] == 'unknown':
                    status, kind = UNK, 'power:' + pw[1]
                if app == 'partial':
                    kind = kind + ':partial'   # negative or unknown: it reaches part of the decision
                elif app in ('unknownScope', 'otherGrounds'):
                    status, kind = UNK, app + ':' + k
                if r['scope'] == 'all':
                    depkeys = keyset
                elif r['scope'].startswith('issues:'):
                    ks = frozenset(x for x in r['scope'][7:].split(',') if x)
                    depkeys = ((keyset & ks) or keyset) if keyset else ks
                else:
                    depkeys = keyset
                reach = self._reach(node, B, dt)   # H4
                for (cf, ct, ov) in self.temporal_ranges(r['temporal'], dt, dom):
                    st, kd = (ov if (ov and status == 'negative') else (status, kind))
                    E.append([dt, OPEN, cf, ct, st, kd, str(B), (B, depkeys), reach])
            # R27 (c): a supersededByEnactment *treatment* is evidence, not the event (T1(d): legislation changes
            # status). Without a supersessions row joining it to a law change there is no effective date, no
            # retroactivity and no amended block (AB1), so it changes nothing; with one, that row carries it.
        # C. supersession by enactment (§7 AB1)
        E.extend(e for (_, e) in self._sup_effects(node, keyset))
        return [e for e in E if e[0] < e[1]]

    def _sup_effects(self, node, keyset):
        """§7 AB1: the effects of the supersession rows on `node` for an issue set, as [(law change, effect)]."""
        D = self.D
        E = []
        for s in self.sup_by_target.get(node, ()):
            lc = D.lawchanges.get(s['lc'])
            if lc is None:
                continue
            ev = s['evidence']
            if ev.startswith('laterCourtSays:'):
                tid = ev.split(':', 1)[1]
                if self.cert_ok.get(('treatments.tsv', tid)) != 'ok':
                    continue
            if s['issue'] not in ('-', ''):
                scope = 'issues:' + s['issue']
            else:
                blk = lc['usc']
                ks = [h['issue'] for h in self.adm_holdings_by_node.get(node, ())
                      if self._usc_match(D.issues.get(h['issue'], {}).get('usc', '-'), blk)]
                scope = ('issues:' + ','.join(sorted(set(ks)))) if ks else 'partialUnknown'
            app = self.scope_applies(scope, keyset)
            if app == 'none':
                continue
            start = lc['enacted'] or lc['effective']
            cf = lc['retro'] or lc['effective'] or lc['enacted']
            if lc['retro'] == 1:
                # R30 (SCHEMA): retroactive_to = 1 = the law governs cases pending on its effective date, whatever
                # the conduct date. Pending-ness is not in the data: approximated as asOf t >= effective, all conduct
                start, cf = lc['effective'] or lc['enacted'], 0
            if 'supersessionRetroactive' in MUT:
                cf = 0
            if start == 0:
                continue
            if s['explicit'] != 1:
                continue                     # R26: an inferred supersession never proves status (atRisk only)
            status, kind = 'negative', 'supersededByEnactment'
            if app == 'partial':
                kind = kind + ':partial'   # negative or unknown: it reaches part of the decision
            elif app in ('unknownScope', 'otherGrounds'):
                status, kind = UNK, app + ':supersededByEnactment'
            E.append((lc, [start, OPEN, cf, OPEN, status, kind, 'lc:' + s['lc'], None]))
        return E

    # ---------------------------------------------------------------- H4: status per heir after an adoption cut-off
    def _heirs(self, X):
        """H4: the courts that hold X by a binding adoption of X's own court's decisions: [(adopter, up_to)].
        Successions are not walked. Only rows whose filter is decided by the decision itself count: 'all' ('-', '')
        and 'unitB' (X's unit is 2); a row with any other filter is never an heir."""
        hs = self._heirs_c.get(X)
        if hs is None:
            D = self.D
            c, d = D.court[X], D.date[X]
            hs = self._heirs_c[X] = [
                (adopter, upto) for (adopter, upto, filt, force) in self.adopt.get(c, ())
                if d <= upto and force == 'binding' and adopter != c
                and filt in ('all', '-', '', 'unitB') and self.filter_match(filt, X, None, 0) is True]
        return hs

    def _reach(self, X, B, bd):
        """H4: which lines a treatment of X by decision B (dated bd) reaches. None = every line (ALL); else
        (reachesOrig, reached adopter courts, unreached adopter courts)."""
        heirs = self._heirs(X)
        if not heirs:
            return None
        D = self.D
        cb, cx = D.court[B], D.court[X]
        be, xe = self.epoch(cb, bd), self.epoch(cx, D.date[X])
        if be is None or xe is None or self.is_scotus(be):
            return None
        ro = (cb == cx or any(n == cb and kind != 'split' for (n, sd, kind) in self.succ.get(cx, ()))
              or (be.system == xe.system and TIER_RANK[xe.tier] < TIER_RANK[be.tier])
              or (any(a == cb for (a, _) in heirs) and self.epoch(cx, bd) is None))
        reached, unreached = set(), set()
        for (a, upto) in heirs:
            ae = self.epoch(a, bd)
            if (a == cb or (ro and bd <= upto)
                    or (ae is not None and ae.system == be.system and TIER_RANK[ae.tier] < TIER_RANK[be.tier])):
                reached.add(a)
            else:
                unreached.add(a)
        if ro and not unreached:
            return None
        return (ro, frozenset(reached), frozenset(unreached))

    # ---------------------------------------------------------------- R2-74: lines and views (DEVIATIONS 74)
    def _view(self, c, d):
        """R2-74: the view of court c asked on date d. None = the court's line is unknown (d = 0, or c has no epoch
        on d): every effect reaches it (the union status). Otherwise (epoch of c on d, d): v(a) = "c on d is in
        adopter a's line". A pure view is written as a frozenset of adopter ids (empty = `orig`, {a} = `heir a`)."""
        if d == 0:
            return None
        ce = self.epoch(c, d)
        if ce is None:
            return None
        return (ce, d)

    def _view_of(self, C):
        """R2-74: the view of a citing or treating decision: its own court on its own date."""
        D = self.D
        return self._view(D.court[C], D.date[C]) if D.has(C) else None

    def _in_view(self, view, a):
        """R2-74: v(a). For a court view: a has an epoch on the date, and the court is a, or is in a's system on a
        lower line tier and, when a is a federal court of appeals, in a's circuit. The unit plays no part."""
        if isinstance(view, frozenset):
            return a in view
        ce, t = view
        ae = self.epoch(a, t)
        return ae is not None and (ae.court == ce.court or (
            ae.system == ce.system and TIER_RANK[ce.tier] < TIER_RANK[ae.tier]
            and (not (ae.system == 0 and ae.tier == 'A') or ce.circuit == ae.circuit)))

    def _applies(self, reach, view):
        """H4 / R2-74: does an effect with this reach reach the view? reach None = all; view None = every effect."""
        if reach is None or view is None or UNION_VIEWS:
            return True
        ro, reached, unreached = reach
        return any(self._in_view(view, a) for a in reached) or (
            ro and not any(self._in_view(view, a) for a in unreached))

    def _effs(self, X, keyset):
        """Cached effects of a decision with heirs (only such a decision can have a line-limited effect)."""
        key = ('effs', X, keyset)
        effs = self._tl.get(key)
        if effs is None:
            effs = self._tl[key] = self.effects(X, keyset)
        return effs

    def _line_limited(self, X, keyset):
        """R2-74: has X an effect (for this issue set) whose reach is not `all`?"""
        return bool(self._heirs(X)) and any(len(e) >= 9 and e[8] is not None for e in self._effs(X, keyset))

    def _view_effects(self, X, keyset, view):
        """R2-74: X's effects that reach the view, or None when every effect reaches it (the union status is then
        the answer). Only a decision with heirs can have an effect that does not reach every line."""
        if view is None or not self._heirs(X):
            return None
        effs = self._effs(X, keyset)
        if all(len(e) < 9 or e[8] is None for e in effs):
            return None
        keep = [e for e in effs if len(e) < 9 or self._applies(e[8], view)]
        return None if len(keep) == len(effs) else keep

    def status_view(self, X, holding_id, t, u, view):
        """R2-74: status(X, holding, t, u) in a view: the ordinary status from only the effects that reach the view
        (same join, scope rules and dates). Evaluated at the point."""
        effs = self._view_effects(X, self.keyset_for(X, holding_id), view)
        if effs is None:
            return self.status(X, holding_id, t, u)
        return self._eval(effs, t, u)

    def line_views(self, X):
        """R2-75: the adopter ids named in a `reached` or `unreached` list of X's effects (the anonymous issue and
        each admitted holding), sorted; None when no effect of X is line-limited."""
        if not self._heirs(X):
            return None
        ads, lim = set(), False
        for ks in [None] + [frozenset([h['issue']]) for h in self.adm_holdings_by_node.get(X, ())]:
            for e in self._effs(X, ks):
                if len(e) >= 9 and e[8] is not None:
                    lim = True
                    ads |= e[8][1] | e[8][2]
        return sorted(ads) if lim else None

    def timeline_view(self, node, keyset, view):
        """R2-75: the status timeline of (node, issue set) in a pure view (the timeline of only the effects that
        reach it); the ordinary timeline when every effect reaches it."""
        effs = self._view_effects(node, keyset, view)
        if effs is None:
            return self.timeline(node, keyset)
        key = ('tlv', node, keyset, view)
        tl = self._tl.get(key)
        if tl is None:
            tl = self._tl[key] = self._segments(effs) if effs else []
        return tl

    def _cite_effects(self, C, X, keyset):
        """H4: X's effects as they apply to the citing decision C, or None when every effect applies (the global
        status is then the answer)."""
        return self._view_effects(X, keyset, self._view_of(C))

    def status_citing(self, C, X, holding_id, t, u):
        """H4: status(X, holding, t, u) as it stands for the citing decision C: only the effects that reach C's
        line. Evaluated at the point (no timeline: the filtered effect set depends on C)."""
        effs = self._cite_effects(C, X, self.keyset_for(X, holding_id))
        if effs is None:
            return self.status(X, holding_id, t, u)
        return self._eval(effs, t, u)

    @staticmethod
    def _usc_match(a, b):
        if not a or not b or a == '-' or b == '-':
            return False
        return a == b or a.startswith(b + '(') or b.startswith(a + '(')

    def timeline(self, node, keyset):
        """Status of (node, issue set) as segments [(from, to, pieces)], pieces = [(conduct_from, state)];
        state = (status, kind, by). Segments where every piece is 'none' are omitted."""
        key = (node, keyset)
        tl = self._tl.get(key)
        if tl is not None:
            return tl
        if key in self._stack:
            return None
        self._stack.add(key)
        try:
            effs = self.effects(node, keyset)
            if not effs:
                self._tl[key] = []
                return []
            segs = self._segments(effs)
            self._tl[key] = segs
            return segs
        finally:
            self._stack.discard(key)

    def _segments(self, effs):
        """The segments of a non-empty effect list (the body of `timeline`; R2-75 also runs it on the effects that
        reach one pure view)."""
        pts = set()
        for e in effs:
            pts.add(e[0])
            pts.add(e[1])
            if e[7] is not None:
                self._overruler_lapsed(e[7][0], 0)            # (b) D4: the overruler's lapse dates are
                for le in self._tl.get(('lapse', e[7][0]), ()):  # breakpoints too, even where its own
                    if le[0] > e[0]:                             # reported kind does not change
                        pts.add(le[0])
                    if le[1] > e[0]:
                        pts.add(le[1])
                dtl = self.timeline(e[7][0], e[7][1])
                if dtl:
                    for (f, t, _) in dtl:
                        if f > e[0]:
                            pts.add(f)
                        if t > e[0]:
                            pts.add(t)
        pts.discard(OPEN)
        pts = sorted(pts)
        cpts = sorted({0} | {e[2] for e in effs} | {e[3] for e in effs if e[3] < OPEN})
        segs = []
        for i, p in enumerate(pts):
            q = pts[i + 1] if i + 1 < len(pts) else OPEN
            if p >= q:
                continue
            pieces = []
            for c in cpts:
                s = self._eval(effs, p, c)
                if pieces and pieces[-1][1] == s:
                    continue
                pieces.append((c, s))
            if all(s[0] == 'none' for (_, s) in pieces):
                continue
            if segs and segs[-1][1] == p and segs[-1][2] == pieces:
                segs[-1] = (segs[-1][0], q, pieces)
            else:
                segs.append((p, q, pieces))
        return segs

    def _eval(self, effs, t, u):
        best_neg = None
        best_unk = None
        best_part = None
        for e in effs:
            if not (e[0] <= t < e[1] and e[2] <= u < e[3]):
                continue
            st, kind, by = e[4], e[5], e[6]
            if e[7] is not None and st != 'none' and 'revivalIgnored' not in MUT:
                # R15 (revised, D4 triage (c)): the overruling lapses (T3, TM3) while the overruling decision's
                # own opinion is gone on the issues it decided: withdrawn, substituted, vacated (also by an en banc
                # grant that vacates), depublished, or reversed, each over the whole of it. Revival is not
                # automatic (T3): the overruler being overruled, reviewed, partly vacated or of unknown status
                # leaves the overruling standing until a court restores the old rule.
                if self._overruler_lapsed(e[7][0], t):
                    continue
            rank = (kind.endswith(':partial'), -SEVERITY.get(kind.split(':')[0], -1), e[0],
                    KIND_POS.get(kind.split(':')[0], 99), by)   # R32: whole-decision before partial
            if st == 'negative' and kind.endswith(':partial'):
                # R32 (c): on the anonymous issue a partial negative ranks below an unknown whole-decision event
                if best_part is None or rank < best_part[0]:
                    best_part = (rank, (st, kind, by))
            elif st == 'negative':
                if best_neg is None or rank < best_neg[0]:
                    best_neg = (rank, (st, kind, by))
            elif st == UNK:
                if best_unk is None or rank < best_unk[0]:
                    best_unk = (rank, (st, kind, by))
        if best_neg:
            return best_neg[1]
        if best_unk:
            return best_unk[1]
        if best_part:
            return best_part[1]
        return ('none', '-', '-')

    def _overruler_lapsed(self, B, t):
        """R15: has decision B's opinion been withdrawn, substituted, vacated, depublished or reversed, as a whole,
        by an admitted same-case event on or before t (and not reinstated since)?"""
        key = ('lapse', B)
        effs = self._tl.get(key)
        if effs is None:
            effs = self._tl[key] = [e for e in self.effects(B, None) if e[7] is None and e[4] == 'negative'
                                    and not e[5].endswith(':partial')
                                    and e[5].split(':')[0] in LAPSE_KINDS + ('reversed',)]
        return any(e[0] <= t < e[1] for e in effs)

    def _state_at(self, node, keyset, t, u):
        tl = self.timeline(node, keyset)
        if tl is None:
            return None
        return self.lookup(tl, t, u)

    @staticmethod
    def lookup(tl, t, u):
        for (f, to, pieces) in tl:
            if f <= t < to:
                st = pieces[0][1]
                for (c, s) in pieces:
                    if c <= u:
                        st = s
                    else:
                        break
                return st
        return ('none', '-', '-')

    def status(self, node, holding_id, t, u):
        """status(holding, asOf t, conduct u) -> (negative|none|unknown, kind/reason, by)."""
        tl = self.timeline(node, self.keyset_for(node, holding_id))
        if tl is None:
            return (UNK, 'cycle', '-')
        return self.lookup(tl, t, u)

    def status_targets(self):
        D = self.D
        t = set(self.adm_hist) | set(self.adm_treat) | set(self.sup_by_target)
        return sorted(x for x in t if D.has(x))

    def status_rows(self, split_by=None):
        """Rows of every status timeline. `split_by` (the firm engine): also cut each asOf segment where the firm
        timeline changes, so that each row's firm flag holds over the whole row (D2)."""
        rows = []
        for node in self.status_targets():
            targets = [('-', '-', None)] + [(h['issue'], h['id'], frozenset([h['issue']]))
                                            for h in sorted(self.adm_holdings_by_node.get(node, ()),
                                                            key=lambda h: h['id'])]
            for (issue, hid, ks) in targets:
                tl = self.timeline(node, ks) or []
                cuts = set()
                if split_by is not None:
                    for (f2, t2, pcs2) in split_by.timeline(node, ks) or []:
                        cuts.update((f2, t2))
                        cuts.update(c for (c, _) in pcs2)
                for (f, to, pieces) in tl:
                    bounds = sorted({f, to} | {x for x in cuts if f < x < to})
                    for (f1, t1) in zip(bounds, bounds[1:]):
                        for (c, s) in pieces:
                            rows.append((node, issue, hid, f1, t1, s[0], s[1], s[2], c))
        return rows

    def line_rows(self, split_by=None):
        """R2-75 (DEVIATIONS 75): for every decision with a line-limited effect, one block of status rows per pure
        view (`orig`, then each adopter named in a reach of its effects): what status_rows would hold if only the
        effects reaching that view existed, with the view as a last element. `split_by` (the firm engine) cuts each
        segment where the firm timeline of the same view changes."""
        rows = []
        for node in self.status_targets():
            ads = self.line_views(node)
            if ads is None:
                continue
            targets = [('-', '-', None)] + [(h['issue'], h['id'], frozenset([h['issue']]))
                                            for h in sorted(self.adm_holdings_by_node.get(node, ()),
                                                            key=lambda h: h['id'])]
            for (line, view) in [('orig', frozenset())] + [(a, frozenset([a])) for a in ads]:
                for (issue, hid, ks) in targets:
                    tl = self.timeline_view(node, ks, view) or []
                    cuts = set()
                    if split_by is not None:
                        for (f2, t2, pcs2) in split_by.timeline_view(node, ks, view) or []:
                            cuts.update((f2, t2))
                            cuts.update(c for (c, _) in pcs2)
                    for (f, to, pieces) in tl:
                        bounds = sorted({f, to} | {x for x in cuts if f < x < to})
                        for (f1, t1) in zip(bounds, bounds[1:]):
                            for (c, s) in pieces:
                                rows.append((node, issue, hid, f1, t1, s[0], s[1], s[2], c, line))
        return rows

    # ---------------------------------------------------------------- splits (§9.24 / DESIGN layer 5)
    def splits(self):
        D = self.D
        by_issue = defaultdict(list)
        for h in self.adm_holdings.values():
            if h['answer'] not in ('yes', 'no'):
                continue
            iss = D.issues.get(h['issue'])
            if not iss or iss['question'] in ('', '-'):
                continue
            n = h['node']
            if not D.has(n) or D.date[n] == 0:
                continue
            if h['role'] == 'plurality' and (n, h['issue']) not in self.marks:
                continue        # F6: a plurality proposition is not a holding without a Marks row
            by_issue[h['issue']].append(h)
        out = {}
        for issue, hs in by_issue.items():
            groups = defaultdict(list)          # (court, unit, answer) -> holdings by date
            for h in hs:
                n = h['node']
                groups[(D.court[n], D.unit[n], h['answer'])].append(h)
            for g in groups.values():
                g.sort(key=lambda h: (D.date[h['node']], h['id']))
            ys = [k for k in groups if k[2] == 'yes']
            ns = [k for k in groups if k[2] == 'no']
            for gy in ys:
                for gn in ns:
                    if gy[0] == gn[0] and gy[1] == gn[1]:
                        continue                     # same court and unit: an intra-court conflict
                    best = None
                    for a in groups[gy]:
                        da = D.date[a['node']]
                        if best is not None and da >= best:
                            break
                        for b in groups[gn]:
                            date = max(da, D.date[b['node']])
                            if best is not None and date >= best:
                                break
                            if self._split_pair(a, b, issue, hs, date):
                                best = date
                                break
                    if best is None:
                        continue
                    ca, cb = gy[0], gn[0]
                    k = (issue, ca, cb, 'yes', 'no') if (ca, 'yes') <= (cb, 'no') else (issue, cb, ca, 'no', 'yes')
                    if k not in out or best < out[k]:
                        out[k] = best
        return sorted((k + (d,) for k, d in out.items()))

    def splits_at(self, date):
        """The splits that exist on `date` (the same test as `splits`, asked once, at `date`): rows
        (issue, court1, court2, answer1, answer2, date). Only holdings dated on or before `date` count."""
        D = self.D
        by_issue = defaultdict(list)
        for h in self.adm_holdings.values():
            if h['answer'] not in ('yes', 'no'):
                continue
            iss = D.issues.get(h['issue'])
            if not iss or iss['question'] in ('', '-'):
                continue
            n = h['node']
            if not D.has(n) or not (0 < D.date[n] <= date):
                continue
            if h['role'] == 'plurality' and (n, h['issue']) not in self.marks:
                continue
            by_issue[h['issue']].append(h)
        out = set()
        for issue, hs in by_issue.items():
            ys = [h for h in hs if h['answer'] == 'yes']
            ns = [h for h in hs if h['answer'] == 'no']
            for a in ys:
                for b in ns:
                    ca, cb = D.court[a['node']], D.court[b['node']]
                    if ca == cb and D.unit[a['node']] == D.unit[b['node']]:
                        continue
                    k = (issue, ca, cb, 'yes', 'no') if (ca, 'yes') <= (cb, 'no') else (issue, cb, ca, 'no', 'yes')
                    if k in out:
                        continue
                    if self._split_pair(a, b, issue, hs, date):
                        out.add(k)
        return sorted(k + (date,) for k in out)

    def _split_pair(self, a, b, issue, hs, date):
        D = self.D
        na, nb = a['node'], b['node']
        ca, cb = D.court[na], D.court[nb]
        # R2-77 (DEVIATIONS 77): each side counts only if its holding is good law in the view of its own court on
        # the date (court gone on the date: the union status)
        va, vb = self._view(ca, date), self._view(cb, date)
        if self.status_view(na, a['id'], date, date, va)[0] != 'none':
            return False
        if self.status_view(nb, b['id'], date, date, vb)[0] != 'none':
            return False
        fab = self.auth_cached(na, issue, a['role'], cb, date, D.unit[nb])
        fba = self.auth_cached(nb, issue, b['role'], ca, date, D.unit[na])

        def free(f, node, hid, view):
            # R2-77: the holding does not bind the other court: its force there is below bindingAbsentConflict under
            # every reading (as before), or its force there is known and it is not good law in that court's view.
            # An unknown force still blocks the split.
            up = upper(f)
            if up is not None and FORCE_RANK[up] < 7:
                return True
            return f[0] != UNK and self.status_view(node, hid, date, date, view)[0] != 'none'
        if not free(fab, na, a['id'], vb) or not free(fba, nb, b['id'], va):
            return False                             # one may bind the other: not a split
        return not self._resolved(hs, issue, ca, D.unit[na], cb, D.unit[nb], date, va, vb)

    def auth_cached(self, node, issue, role, dst, t, unit):
        k = (node, issue, role, dst, t, unit)
        r = self._auth.get(k)
        if r is None:
            r = self._auth[k] = self.authority(node, issue, role, dst, t, unit)
        return r

    def _resolved(self, hs, issue, ca, ua, cb, ub, date, va=None, vb=None):
        """A good-law holding on the question that binds both courts resolves the split (DESIGN layer 5).
        R2-77: it must be good law in the views of both courts on the date."""
        D = self.D
        for h in hs:
            n = h['node']
            if D.date[n] > date:
                continue
            if (self.status_view(n, h['id'], date, date, va)[0] != 'none'
                    or self.status_view(n, h['id'], date, date, vb)[0] != 'none'):
                continue
            if self.D.date[n] == 0 or TIER_RANK.get(getattr(self.epoch(D.court[n], D.date[n]), 'tier', 'T'), 0) == 0:
                continue
            f1 = self.auth_cached(n, issue, h['role'], ca, date, ua)
            f2 = self.auth_cached(n, issue, h['role'], cb, date, ub)
            if f1[0] == 'binding' and f2[0] == 'binding':
                return True
        return False

    # ---------------------------------------------------------------- conflicts (§9.24 resolver; L3)
    def _question_holdings(self, date):
        """issue -> admitted yes/no holdings on a question issue, dated 0 < d <= date, plurality holdings only with a
        Marks row (the split filter)."""
        D = self.D
        by_issue = defaultdict(list)
        for h in self.adm_holdings.values():
            if h['answer'] not in ('yes', 'no'):
                continue
            iss = D.issues.get(h['issue'])
            if not iss or iss['question'] in ('', '-'):
                continue
            n = h['node']
            if not D.has(n) or not (0 < D.date[n] <= date):
                continue
            if h['role'] == 'plurality' and (n, h['issue']) not in self.marks:
                continue
            by_issue[h['issue']].append(h)
        return by_issue

    def conflict_destinations(self, asof):
        """L3 (contract shared with the Lean): for each question issue, every (court, unit) of a decision holding on
        it, plus, for each (system, circuit) of those decisions' epochs, the first courts2.tsv row in file order with
        that system, tier T (federal: the same circuit) and an epoch covering asOf, crossed with every unit seen among
        the holding decisions (0 = no unit)."""
        D = self.D
        out = {}
        for issue, hs in self._question_holdings(asof).items():
            cu, units, sc = set(), set(), set()
            for h in hs:
                n = h['node']
                cu.add((D.court[n], D.unit[n]))
                units.add(D.unit[n])
                e = self.epoch(D.court[n], D.date[n])
                if e is not None:
                    sc.add((e.system, e.circuit))
            for (s, ci) in sorted(sc):
                for e in D.court_rows:
                    if e.system == s and e.tier == 'T' and (s != 0 or e.circuit == ci) and e.frm <= asof <= e.to:
                        for u in units:
                            cu.add((e.court, u))
                        break
            out[issue] = sorted(cu)
        return out

    def conflicts_at(self, asof, dests):
        """L3 (§9.24, §1.2 F7 conflict resolution, §4.1 V, S-CA Auto Equity): rows (issue, court, unit) where the
        destination's resolver leaves both answers permissible on asOf. Candidates are good-law holdings (status none
        on the diagonal asOf) whose force on (court, unit) is binding or bindingAbsentConflict; an unknown force that
        may reach bindingAbsentConflict leaves the destination undecided (no row). Resolver, in order: a candidate whose
        deciding court another candidate binds (and does not bind in turn) is displaced; a binding candidate displaces
        bindingAbsentConflict ones (own unit first, ownUnitThenAny); within one source court whose firstInTimeControls
        rule is 1 on asOf, the earliest controls; the answers left are the permissible set (choice)."""
        D = self.D
        quals = self._question_holdings(asof)
        out = []
        for issue in sorted(dests):
            # R2-77 (DEVIATIONS 77): the good-law holdings are those good in the view of the bound court on asOf. A
            # view is never more severe than the union status, so a holding that is good law in the union is good
            # in every view; only one with a line-limited effect can be good in some view alone.
            ks = frozenset([issue])
            pool = [(h, self.status(h['node'], h['id'], asof, asof)[0] == 'none') for h in quals.get(issue, ())]
            pool = [(h, g) for (h, g) in pool if g or self._line_limited(h['node'], ks)]
            if len({h['answer'] for (h, _) in pool}) < 2:
                continue
            for (c, u) in dests[issue]:
                if self.epoch(c, asof) is None:
                    continue
                vw = self._view(c, asof)
                good = [h for (h, g) in pool
                        if g or self.status_view(h['node'], h['id'], asof, asof, vw)[0] == 'none']
                cands, undecided = [], False
                for h in good:
                    f = self.auth_cached(h['node'], issue, h['role'], c, asof, u)
                    if f[0] == UNK:
                        up = upper(f)
                        if up is None or FORCE_RANK[up] >= 7:
                            undecided = True
                            break
                        continue
                    if FORCE_RANK[f[0]] >= 7:
                        cands.append((h, f[0]))
                if undecided or len({h['answer'] for (h, _) in cands}) < 2:
                    continue
                if self._resolve(cands, asof, issue, c) == {'yes', 'no'}:
                    out.append((issue, c, u))
        return out

    def _resolve(self, cands, asof, issue, dst=None):
        D = self.D
        de = self.epoch(dst, asof) if dst is not None else None

        def in_line(a):          # b4: the destination court is the adopter or a court below it (H4's line test)
            ae = self.epoch(a, asof)
            return de is None or (ae is not None and (ae.court == de.court or (
                ae.system == de.system and TIER_RANK[de.tier] < TIER_RANK[ae.tier]
                and (not (ae.system == 0 and ae.tier == 'A') or de.circuit == ae.circuit))))

        def binds(a, b):         # a's holding binds b's deciding court (and unit) on asOf
            nb, na = b['node'], a['node']
            if D.court[na] == D.court[nb]:
                # H3 (Kentucky 1976): a court whose tier changed does not bind its own decisions from a higher dated
                # tier (the new Court of Appeals cannot displace the old court of last resort's holdings)
                ea, eb = self.epoch(D.court[na], D.date[na]), self.epoch(D.court[nb], D.date[nb])
                if ea is not None and eb is not None and TIER_RANK[ea.tier] < TIER_RANK[eb.tier]:
                    return False
                # R4-86 (DEVIATIONS 86; S-TX-3): a decision promoted by "writ refused" has the value of the court of
                # last resort; an unpromoted decision of the same court of appeals does not displace or equal it
                def promoted(n):
                    return any(h.via == 'writRefused' for h in (self.holders(n, asof) or ()))
                if promoted(nb) and not promoted(na):
                    return False
            # D4 reading (five limits): a decision held by adoption with binding force (an adopted Commission of
            # Appeals opinion is the Supreme Court of Texas's, H4) is displaced only by a holding binding its adopter
            courts = [(D.court[nb], D.unit[nb])] + [(h.court, None) for h in (self.holders(nb, asof) or ())
                                                    if h.via == 'adoption' and h.cap == 'binding'
                                                    and in_line(h.court)]   # b4: only an adopter this court is under
            # R3-80 (DEVIATIONS 80; Bonner, 661 F.2d at 1209-11): a deciding court with no epoch on asOf has ceased.
            # It is asked as it last sat (its last epoch before asOf): a holding that bound the old court and binds
            # the adopter in whose line the bound court stands prevails over the inherited decision. Before, the
            # force on the ceased court was unknown, so nothing displaced its decisions (sweep drt9, 8 universes).
            def f_at(c, u):
                if self.epoch(c, asof) is None:
                    le = self.last_epoch(c, asof)
                    if le is None:
                        return UNK
                    return self.authority(a['node'], issue, a['role'], c, asof, u, dep_as=le)[0]
                return self.auth_cached(a['node'], issue, a['role'], c, asof, u)[0]
            return all(f_at(c, u) == 'binding' for c, u in courts)
        # vertical hierarchy (F1, H1, §4.1 V): a candidate whose court is bound by another candidate that it does not
        # bind in turn is displaced by it (SCOTUS over a state high court on federal law, a high court over its IAC)
        k = [(b, fb) for (b, fb) in cands
             if not any(a is not b and binds(a, b) and not binds(b, a) for (a, _) in cands)]
        if any(f == 'binding' for (_, f) in k):
            k = [(h, f) for (h, f) in k if f == 'binding']
        groups = defaultdict(list)
        for (h, f) in k:
            groups[D.court[h['node']]].append(h)
        answers = set()
        for c, hs in groups.items():
            if len({h['answer'] for h in hs}) > 1:
                e = self.epoch(c, D.date[hs[0]['node']])
                if self.rule(e.system if e else -1, c, 'firstInTimeControls', asof) == '1':
                    d0 = min(D.date[h['node']] for h in hs)
                    hs = [h for h in hs if D.date[h['node']] == d0]
            answers |= {h['answer'] for h in hs}
        return answers

    # ---------------------------------------------------------------- Horty binding bases (R2-78; DEVIATIONS 78)
    def horty(self, asof):
        """R2-78: rows (family, court, verdict, cases) of horty.tsv: one per distinct binding base of a family.
        A case is an admitted holding with factor rows whose decision is dated in (0, asOf]; it is live when good
        law at (asOf, asOf) in at least one pure view of its decision. The base at an examined court (c, n) is the
        live cases good in the view of c on asOf whose force at (c, n) on asOf is at least bindingAbsentConflict."""
        D = self.D
        fams = defaultdict(list)
        for hid in sorted(D.factors):
            h = self.adm_holdings.get(hid)
            if h is None:
                continue
            n = h['node']
            if not D.has(n) or not (0 < D.date[n] <= asof):
                continue
            fc = D.factor_cases.get(hid)
            if fc is not None:
                fam, outcome = fc
            elif h['answer'] in ('yes', 'no'):
                fam, outcome = h['issue'], h['answer']
            else:
                continue
            ads = self.line_views(n)
            views = [None] if ads is None else [frozenset()] + [frozenset([a]) for a in ads]
            if not any(self.status_view(n, hid, asof, asof, v)[0] == 'none' for v in views):
                continue                      # not live
            facts = frozenset((f, side) for (f, side, _) in D.factors[hid])
            reason = frozenset((f, side) for (f, side, inr) in D.factors[hid] if inr)
            fams[fam].append((hid, h, outcome, facts, reason))
        rows = []
        for fam in sorted(fams):
            cases = fams[fam]
            cu, units, sc = set(), set(), set()
            for (hid, h, _, _, _) in cases:
                n = h['node']
                cu.add((D.court[n], D.unit[n]))
                units.add(D.unit[n])
                e = self.epoch(D.court[n], D.date[n])
                if e is not None:
                    sc.add((e.system, e.circuit))
            for (s, ci) in sorted(sc):
                for e in D.court_rows:
                    if e.system == s and e.tier == 'T' and (s != 0 or e.circuit == ci) and e.frm <= asof <= e.to:
                        for u in units:
                            cu.add((e.court, u))
                        break
            if any(s == 0 for (s, _) in sc):
                for e in D.court_rows:
                    if e.system == 0 and e.tier == 'A' and 1 <= e.circuit <= 12 and e.frm <= asof <= e.to:
                        cu.add((e.court, 0))
                        break
            seen = set()
            for (c, u) in sorted(cu):
                vw = self._view(c, asof)
                base = []
                for case in cases:
                    hid, h = case[0], case[1]
                    if self.status_view(h['node'], hid, asof, asof, vw)[0] != 'none':
                        continue
                    f = self.auth_cached(h['node'], h['issue'], h['role'], c, asof, u)
                    if f[0] != UNK and FORCE_RANK[f[0]] >= 7:
                        base.append(case)
                if len(base) < 2:
                    continue
                key = ','.join(sorted(case[0] for case in base))
                if key in seen:
                    continue
                seen.add(key)
                bad = any(x[2] != y[2] and x[4] <= y[3] and y[4] <= x[3]
                          for i, x in enumerate(base) for y in base[i + 1:])
                rows.append((fam, '%d/%d' % (c, u) if u else str(c), 'inconsistent' if bad else 'consistent', key))
        return rows

    # ---------------------------------------------------------------- findings (§9.27)
    def findings(self, edges):
        D = self.D
        out = set()
        hold_issues = {n: {h['issue'] for h in hs} for n, hs in self.adm_holdings_by_node.items()}
        for (C, X) in edges:
            if not D.has(C) or not D.has(X):
                continue
            t = D.date[C]
            if t == 0 or C == X:
                continue
            for f in self._edge_findings(C, X, t, hold_issues):
                out.add(f)
            ln = self._cites_later_negated(C, X, t)
            if ln:
                out.add(('atRisk', C, X, 'citesLaterNegated:' + ln))
        # treatment-based findings
        for X, trs in self.adm_treat.items():
            for r in trs:
                C = r['by']
                if not D.has(C) or not D.has(X):
                    continue
                k = r['kind']
                t = r['date'] or D.date[C]
                if D.date[X] > D.date[C]:
                    continue             # T1: an earlier decision cannot treat a later one (a data error)
                ce = self.epoch(D.court[C], t)
                if k == 'followed' and ce is not None:
                    pub = PUB[D.pub[X]]
                    if pub in UNPUB:
                        # (c) D4 triage: the decision's own force (its status has findings of its own), below
                        # bindingAbsentConflict under every reading of an unknown attribute
                        f = self.authority(X, None, None, D.court[C], t, D.unit[C], D.extra.get(C))
                        up = upper(f)
                        if up is not None and FORCE_RANK[up] < 7:
                            out.add(('citesUnpublishedAsBinding', C, X, f[0] if f[0] != UNK else '<=' + up))
                    if FORM[D.form[X]] == 'plurality' and X not in self.marks_nodes:
                        base = self._authority_as_majority(X, D.court[C], t, D.unit[C], D.extra.get(C))
                        if base[0] == 'binding':
                            out.add(('pluralityTreatedAsBinding', C, X, 'noMarks'))
                wrow = r['id'] in D.witness     # round 4: the words are a later court's: atRisk only
                # round 4 (DEVIATIONS 84): the panel finding needs the panel's own overruling words
                own = any(v in ascii_lower(norm_quote(r['cert'].quote)) for v in PANEL_OWN_WORDS)
                if k in NEG_TREAT and own and not wrow:       # (c) a decline to follow is not a purported overruling
                    pd = self._panel_departs(C, X, r)
                    if pd:
                        out.add(('panelDepartsWithoutEnBanc', C, X, pd))
                if (k in NEG_TREAT or k == 'declinedToFollow') and not wrow and self._ignores_binding_in_unit(C, X, r):
                    out.add(('ignoresBindingInUnit', C, X, k))
        for f in self.at_risk():
            out.add(f)
        return out

    def _ignores_binding_in_unit(self, B, X, r):
        """L1 (five limits; §9.27 "a trial court departs from its own unit, ownUnit rules"; §4.1 V, §4.3, §4.4, T2): a
        trial-level court B declines to follow (or purports to overrule) a good-law decision X that binds it through
        its own unit (an intermediate court of B's unit under trialScope ownUnitThenAny / ownUnitOnly) or its own court
        (the appellate division of B's trial court and unit, §4.4), B having no power over X."""
        D = self.D
        t = r['date'] or D.date[B]
        if D.date[X] == 0 or D.date[B] < D.date[X] or t == 0:
            return False
        be = self.epoch(D.court[B], t)
        if be is None or be.system == 0 or be.tier not in ('T', 'D', 'S'):
            return False
        du = D.unit[B] or be.unit
        if not du:
            return False             # (c) unit not known: not shown to be the own unit (R31)
        if self.can_change(B, X)[0] != 'no':
            return False
        if self.status_view(X, None, t, t, self._view_of(B))[0] != 'none':   # R2-76: in the treating court's view
            return False             # only a good-law precedent is ignored
        if self.authority(X, None, None, D.court[B], t, D.unit[B], D.extra.get(B))[0] != 'binding':
            return False
        hs = self.holders(X, t) or ()
        if any(h.via == 'writRefused' for h in hs):
            return False             # it binds as the court of last resort's (S-TX-3), not through the unit rule
        for h in hs:
            if h.system != be.system or h.unit != du:
                continue
            if h.tier == 'A' and self.rule(h.system, h.court, 'trialScope', t) in ('ownUnitThenAny', 'ownUnitOnly'):
                return True
            if h.tier == 'D' and be.tier == 'T':
                return True
        return False

    def _live_negative(self, X, t):
        """Wholly negative effects on X's anonymous issue live at (t, t), lapsed overrulings excluded (cached)."""
        key = ('liveneg', X, t)
        v = self._tl.get(key)
        if v is None:
            v = self._tl[key] = [e for e in self.effects(X, None) if e[4] == 'negative'
                                 and not e[5].endswith(':partial') and e[0] <= t < e[1] and e[2] <= t < e[3]
                                 and not (e[7] is not None and self._overruler_lapsed(e[7][0], t))]
        return v

    def _live_negative_citing(self, C, X, t):
        """H4: _live_negative restricted to the effects that reach the citing decision C's line."""
        effs = self._cite_effects(C, X, None)
        if effs is None:
            return self._live_negative(X, t)
        return [e for e in effs if e[4] == 'negative'
                and not e[5].endswith(':partial') and e[0] <= t < e[1] and e[2] <= t < e[3]
                and not (e[7] is not None and self._overruler_lapsed(e[7][0], t))]

    def _cites_later_negated(self, C, X, t):
        """L2 (five limits; T1(c), §9.26, F14): atRisk citesLaterNegated. C (decided t) cites X; X's anonymous issue
        is wholly negative on asOf (on the diagonal) but not wholly negative on (t, t), and one live negative effect
        on asOf comes from a decision whose court binds C's court (force `binding` at that decision's date). A law
        change or an unknown deciding decision is not a court that binds C. -> the reported kind, or None."""
        D = self.D
        asof = getattr(self, 'asof', 20261112)
        if t >= asof:
            return None
        top = self.status_citing(C, X, None, asof, asof)   # H4: every status here is relative to C's line
        if top[0] != 'negative' or top[1].endswith(':partial'):
            return None
        now = self.status_citing(C, X, None, t, t)
        if now[0] == 'negative' and not now[1].endswith(':partial'):
            return None
        cache = self._auth
        for e in self._live_negative_citing(C, X, asof):   # H4
            by = e[6]
            if not by.isdigit():
                continue
            B = int(by)
            if B == C or not D.has(B) or D.date[B] == 0:
                continue
            k = ('bindsCiting', B, D.court[C], D.unit[C])
            f = cache.get(k)
            if f is None:
                f = cache[k] = self.authority(B, None, None, D.court[C], D.date[B], D.unit[C], D.extra.get(C))
            if f[0] == 'binding':
                return top[1].split(':')[0]
        return None

    def _authority_as_majority(self, X, dst, t, du, ctx):
        D = self.D
        saved = D.form[X]
        D.form[X] = FORM_I['full']
        try:
            return self.authority(X, None, None, dst, t, du, ctx)
        finally:
            D.form[X] = saved

    def _only_by(self, X, keyset, t, C):
        """Is every live negative effect on X (keyset) at (t, t) caused by decision C? Then C's citation of X is
        its own overruling, not a citation of overruled law (D4 triage: not just the reported representative)."""
        effs = self._cite_effects(C, X, keyset)   # H4: the effects that reach C's line
        if effs is None:
            effs = self.effects(X, keyset)
        live = [e for e in effs if e[4] == 'negative' and not e[5].endswith(':partial')
                and e[0] <= t < e[1] and e[2] <= t < e[3]
                and not (e[7] is not None and self._overruler_lapsed(e[7][0], t))]
        if not live:
            return False
        top = max(SEVERITY.get(e[5].split(':')[0], -1) for e in live)
        bys = {e[6] for e in live if SEVERITY.get(e[5].split(':')[0], -1) == top}
        return bys == {str(C)}

    def _edge_findings(self, C, X, t, hold_issues):
        D = self.D
        res = []
        top = self.status_citing(C, X, None, t, t)   # H4: every status here is relative to C's line
        if top[0] == 'negative' and top[2] == str(C) and not self._only_by(X, None, t, C):
            top = (top[0], top[1], '-')      # another decision's effect makes the same status
        sup_only = False
        if top[0] == 'negative' and top[2] != str(C) and not top[1].endswith(':partial'):
            base = top[1].split(':')[0]
            fk = self._finding_kind(base)
            if fk:
                res.append((fk, C, X, '%s:%s' % (base, top[2])))
            if base != 'supersededByEnactment':
                return res
            sup_only = True                  # H2: a wholly superseded decision: only the atRisk row below
        if True:   # D4 triage: issue-level findings whenever the whole decision is not negative (partial or unknown)
            # partial: issue-aware (HD4)
            xs = sorted(self.adm_holdings_by_node.get(X, ()), key=lambda h: h['id'])
            if not xs:
                return res
            cis = hold_issues.get(C)
            states = [(h, self.status_citing(C, X, h['id'], t, t)) for h in xs]
            # H2: the citing date is not a conduct date. A cited holding superseded on (t, t) is a low-confidence
            # risk only, and only on a holding-level match: C holds on the same issue, or on an issue whose usc
            # matches the amended block of a live explicit supersession that reaches the cited holding's issue
            for (h, s) in states:
                if not cis or s[0] != 'negative' or s[1].split(':')[0] != 'supersededByEnactment':
                    continue
                hit = h['issue'] in cis
                if not hit:
                    blocks = [lc['usc'] for (lc, e) in self._sup_effects(X, frozenset([h['issue']]))
                              if e[4] == 'negative' and e[5] == 'supersededByEnactment'
                              and e[0] <= t < e[1] and e[2] <= t < e[3]]
                    hit = any(self._usc_match(D.issues.get(k, {}).get('usc', '-'), b) for k in cis for b in blocks)
                if hit:
                    res.append(('atRisk', C, X, 'supersededConductUnknown:' + h['issue']))
            if sup_only:
                return res
            if cis:
                for (h, s) in states:
                    if h['issue'] in cis and s[0] == 'negative' and s[2] != str(C):
                        fk = self._finding_kind(s[1].split(':')[0])
                        if fk:
                            res.append((fk, C, X, '%s:%s:%s' % (s[1].split(':')[0], s[2], h['issue'])))
            elif all(s[0] == 'negative' and s[2] != str(C) for (_, s) in states):
                for (h, s) in states:
                    fk = self._finding_kind(s[1].split(':')[0])
                    if fk:
                        res.append((fk, C, X, '%s:%s:allHoldings' % (s[1].split(':')[0], s[2])))
        return res

    @staticmethod
    def _finding_kind(kind):
        if kind in FIND_OVERRULED:
            return 'citesOverruled'
        if kind in FIND_VACATED or kind == 'reversed':
            return 'citesVacated'            # R29 (c): a reversed opinion has lost force on the reversed issues
        # H2: SCHEMA has no conduct date for a citing decision, so a citation of a superseded holding is never
        # appliesSupersededHolding (see atRisk supersededConductUnknown in _edge_findings)
        return None

    def _panel_departs(self, B, X, r):
        """F7 / §9.27: a panel of a strong-horizontal court departs from binding precedent without en banc."""
        D = self.D
        bd = r['date'] or D.date[B]
        be = self.epoch(D.court[B], bd)
        hs = self.holders(X, bd)
        if be is None or not hs:
            return None
        if D.date[B] < D.date[X]:
            return None          # T1: an earlier decision cannot treat a later one (a data error, not a departure)
        if self.can_change(B, X)[0] == 'yes':
            return None          # the court has power by another route (review, adoption): not a departure
        # H3b: only a bench known to be a panel or a division departs (not unknown, not circulated, whatever the
        # circulation rule says), and only if the court had the rule on the day it departed
        if BENCH[D.bench[B]] not in ('panel', 'division'):
            return None
        if self.horizontal(be.system, D.court[B], be.tier, bd) not in ('strong', 'withinUnitOnly'):
            return None
        if be.system == 0 and be.tier == 'A' and bd < EN_BANC_STATUTE:
            return None          # H3b: no en banc procedure in the courts of appeals before 28 U.S.C. § 46(c)
        for h in hs:
            if h.court != D.court[B] or h.tier != be.tier or h.tier not in ('L', 'A', 'B', 'S') or not h.power:
                continue
            hz = self.horizontal(h.system, h.court, h.tier,
                                 bd if (h.via == 'adoption' and h.tier == 'L') else D.date[X])   # H6, as in power()
            if hz == 'withinUnitOnly' and D.unit[B] != h.unit:
                continue
            if hz not in ('strong', 'withinUnitOnly'):
                continue
            ok = self.bench_ok(B, D.court[B], bd)
            if ok[0] != 'no':
                continue
            if self.status_view(X, None, bd, bd, self._view_of(B))[0] != 'none':   # R2-76
                continue
            return '%s:%s' % (r['kind'], BENCH[D.bench[B]])
        return None

    def at_risk(self):
        D = self.D
        out = []
        for X, trs in self.adm_treat.items():
            for r in trs:
                C, k = r['by'], r['kind']
                t = r['date'] or (D.date[C] if D.has(C) else 0)
                if t == 0:
                    continue
                if D.has(C) and D.has(X) and D.date[C] < D.date[X]:
                    continue             # T1: an earlier decision cannot treat a later one (a data error, not a risk)
                st0 = self.status_view(X, None, t, t, self._view_of(C))   # R2-76: in the treating court's view
                if st0[0] == 'negative' and not st0[1].endswith(':partial'):
                    continue             # already wholly negative (a partial event leaves the rest at risk)
                if k in SOFT_TREAT:
                    out.append(('atRisk', C, X, 'soft:' + k))
                elif k in NEG_TREAT:
                    pw = self.can_change(C, X, 'unknown')
                    if pw[0] == 'no':
                        if r['id'] not in D.witness:
                            out.append(('atRisk', C, X, 'claim:' + k))
                    elif r['explicit'] != 1:
                        out.append(('atRisk', C, X, 'inferred:' + k))
        for X, sups in self.sup_by_target.items():
            for s in sups:
                ev = s['evidence']
                if ev.startswith('laterCourtSays:') and self.cert_ok.get(('treatments.tsv', ev.split(':', 1)[1])) != 'ok':
                    continue             # the court's words it rests on are not certified
                if s['explicit'] != 1 and s['lc'] in D.lawchanges:
                    out.append(('atRisk', 'lc:' + s['lc'], X, 'possiblySuperseded'))
        # F14: a later contrary holding of a court whose decisions bind the holder (abrogation candidate)
        by_issue = defaultdict(list)
        for h in self.adm_holdings.values():
            if h['answer'] in ('yes', 'no') and D.has(h['node']) and D.date[h['node']]:
                by_issue[h['issue']].append(h)
        for issue, hs in by_issue.items():
            if len({h['answer'] for h in hs}) < 2:
                continue
            ups = []                                  # candidate displacing holdings: non-trial courts only
            for y in hs:
                ye = self.epoch(D.court[y['node']], D.date[y['node']])
                if ye is not None and ye.tier != 'T':
                    ups.append(y)
            ups.sort(key=lambda h: (D.date[h['node']], h['id']))
            for x in sorted(hs, key=lambda h: h['id']):
                X = x['node']
                for y in ups:
                    Y = y['node']
                    if y['answer'] == x['answer'] or D.date[Y] <= D.date[X]:
                        continue
                    t = D.date[Y]
                    f = self.auth_cached(Y, issue, y['role'], D.court[X], t, D.unit[X])
                    if f[0] != 'binding':
                        continue
                    vw = self._view(D.court[X], t)   # R2-76: both read in the view of the holder's court on t
                    if self.status_view(X, x['id'], t, t, vw)[0] != 'none':
                        break
                    if self.status_view(Y, y['id'], t, t, vw)[0] != 'none':
                        continue
                    out.append(('atRisk', Y, X, 'contraryBinding:' + y['id']))
                    break
        return out


# ----------------------------------------------------------------------------------------------------------------
def iter_edges(edges_dir, wanted):
    """Stream citing\\tcited edge files; keep edges whose cited node is in `wanted` (string ids)."""
    if not edges_dir:
        return
    files = sorted(glob.glob(os.path.join(edges_dir, 'edges-*.tsv')))
    for fn in files:
        with open(fn, encoding='utf-8') as f:
            for line in f:
                tab = line.find('\t')
                if tab < 0:
                    continue
                cited = line[tab + 1:].rstrip('\n').split('\t', 1)[0]
                if cited in wanted:
                    yield (int(line[:tab]), int(cited))


def write_tsv(path, rows):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')


def peak_mb():
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except ImportError:
        pass
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
                        ('a', ctypes.c_size_t), ('b', ctypes.c_size_t), ('c', ctypes.c_size_t),
                        ('d', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                        ('PeakPagefileUsage', ctypes.c_size_t)]
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        k32.K32GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        k32.K32GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize / 1048576.0
    except Exception:
        return -1.0


def run(args):
    log = (lambda *a: print(*a, file=sys.stderr, flush=True))
    t0 = time.time()
    D = Data(args.data, log)
    A = Engine(D, firm=False)
    A.admit()
    A.asof = args.asof
    Fm = None
    if not args.no_firm:
        Fm = Engine(D, firm=True)
        Fm.share_admission(A)
        Fm.asof = args.asof
    os.makedirs(args.out, exist_ok=True)
    # certs
    write_tsv(os.path.join(args.out, 'certs.tsv'),
              [(f, i, r) for (f, i), r in sorted(A.cert_ok.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))])
    # status
    rows = A.status_rows(Fm)

    def firm_of(r):
        # D2: firm = the S/L-only tables give the same verdict, read at the row's first point (asOf from, conduct
        # conduct_from), as the Lean does; not row identity, which also depends on where the firm run segments
        if Fm is None:
            return 1
        node, issue, hid, f, to, st, kind, by, c = r
        ks = None if hid == '-' else frozenset([issue])
        tl = Fm.timeline(node, ks) or []
        tla = A.timeline(node, ks) or []
        p = max(f, c)           # the row's first point on the diagonal asOf = conduct, as the Lean reads firm
        return 1 if verdict(Fm.lookup(tl, p, p)) == verdict(A.lookup(tla, p, p)) else 0

    def firm_of_line(r):
        # R2-75: as firm_of, against the S/L run's status in the same pure view (the S/L run's own effects and
        # reaches; an adopter that is no heir there is in no reach list, so its view is then the S/L `orig` view)
        if Fm is None:
            return 1
        node, issue, hid, f, to, st, kind, by, c, line = r
        ks = None if hid == '-' else frozenset([issue])
        view = frozenset() if line == 'orig' else frozenset([line])
        tl = Fm.timeline_view(node, ks, view) or []
        tla = A.timeline_view(node, ks, view) or []
        p = max(f, c)
        return 1 if verdict(Fm.lookup(tl, p, p)) == verdict(A.lookup(tla, p, p)) else 0

    def verdict(x):
        # the D5 verdict a row states: none / unknown / partial / negative of a kind (not the witness row)
        st, kind = x[0], x[1]
        if st == 'negative' and not kind.endswith(':partial'):
            return ('negative', SEVERITY.get(kind.split(':')[0], -1))
        return (st if not kind.endswith(':partial') else 'partial',)
    write_tsv(os.path.join(args.out, 'status.tsv'), [r + (firm_of(r),) for r in rows])
    log('status: %d rows (%.1fs)' % (len(rows), time.time() - t0))
    # R2-75: status per line of authority (always written; empty when no decision has a line-limited effect)
    lrows = A.line_rows(Fm)
    write_tsv(os.path.join(args.out, 'status_lines.tsv'), [r[:9] + (firm_of_line(r), r[9]) for r in lrows])
    log('status_lines: %d rows (%.1fs)' % (len(lrows), time.time() - t0))
    # findings
    targets = set()
    for r in rows:
        if r[5] == 'negative':
            targets.add(str(r[0]))
    edges = list(iter_edges(args.edges, targets)) if args.edges else []
    log('edges into negative targets: %d (%.1fs)' % (len(edges), time.time() - t0))
    fa = A.findings(edges)
    ff = Fm.findings(edges) if Fm else fa
    def fkey(f):                     # D2: the finding holds with the firm tables (its detail may differ; for
        k = str(f[3]).split(':')[0]
        if f[0] == 'atRisk':
            return f[:3] + (k,)                # atRisk: its family must not differ
        if f[0] in ('citesOverruled', 'citesVacated', 'appliesSupersededHolding'):
            return f[:3] + (SEVERITY.get(k, k),)   # cites: the same kind of negative status
        return f[:3]
    fkeys = {fkey(f) for f in ff}
    write_tsv(os.path.join(args.out, 'findings.tsv'),
              [f + ((1 if fkey(f) in fkeys else 0),) for f in sorted(fa, key=lambda f: tuple(str(x) for x in f))])
    log('findings: %d (%.1fs)' % (len(fa), time.time() - t0))
    # splits
    sp = A.splits()
    write_tsv(os.path.join(args.out, 'splits.tsv'), sp)
    write_tsv(os.path.join(args.out, 'splits_asof.tsv'), A.splits_at(args.asof))
    log('splits: %d (%.1fs)' % (len(sp), time.time() - t0))
    # conflicts (L3): one destination list (from the all tables) evaluated by both rule instances; firm = the firm
    # tables give the same row
    dests = A.conflict_destinations(args.asof)
    ca = A.conflicts_at(args.asof, dests)
    cf = set(Fm.conflicts_at(args.asof, dests)) if Fm else set(ca)
    write_tsv(os.path.join(args.out, 'conflicts_asof.tsv'),
              [(i, c, u if u else '-', 'no,yes', 1 if (i, c, u) in cf else 0) for (i, c, u) in ca])
    log('conflicts: %d (%.1fs)' % (len(ca), time.time() - t0))
    # R2-78: Horty binding bases (always written; empty when there are no factor rows)
    hb = A.horty(args.asof)
    write_tsv(os.path.join(args.out, 'horty.tsv'), [r + (1,) for r in hb])
    log('horty: %d bases (%.1fs)' % (len(hb), time.time() - t0))
    stats = [('decisions', D.n_present), ('treatments', len(D.treatments)), ('history', len(D.history)),
             ('holdings', len(D.holdings)), ('status_rows', len(rows)), ('findings', len(fa)),
             ('splits', len(sp)), ('status_lines_rows', len(lrows)), ('horty_bases', len(hb)),
             ('edges_scanned_hits', len(edges)), ('seconds', round(time.time() - t0, 1)),
             ('peak_mb', round(peak_mb()))]
    cnt = defaultdict(int)
    for v in A.cert_ok.values():
        cnt['cert_' + v] += 1
    stats += sorted(cnt.items())
    write_tsv(os.path.join(args.out, 'ref_stats.tsv'), stats)
    log('done in %.1fs, peak %.0f MB' % (time.time() - t0, peak_mb()))


def engine_for(args):
    D = Data(args.data)
    E = Engine(D, firm=getattr(args, 'firm', False))
    E.admit()
    return E


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--data', required=True)
    r.add_argument('--edges')
    r.add_argument('--out', required=True)
    r.add_argument('--no-firm', action='store_true')
    r.add_argument('--asof', type=int, default=20261112, help='date of splits_asof.tsv (the Lean runner asOf)')
    f = sub.add_parser('force')
    f.add_argument('--data', required=True)
    f.add_argument('--firm', action='store_true')
    f.add_argument('--unit', type=int)
    f.add_argument('node', type=int)
    f.add_argument('holding')
    f.add_argument('dst', type=int)
    f.add_argument('t', type=int)
    f.add_argument('u', type=int)
    s = sub.add_parser('status')
    s.add_argument('--data', required=True)
    s.add_argument('--firm', action='store_true')
    s.add_argument('node', type=int)
    s.add_argument('holding')
    s.add_argument('t', type=int)
    s.add_argument('u', type=int)
    c = sub.add_parser('can')
    c.add_argument('--data', required=True)
    c.add_argument('--firm', action='store_true')
    c.add_argument('by', type=int)
    c.add_argument('target', type=int)
    c.add_argument('issue', nargs='?', default='-')
    a = ap.parse_args(argv)
    if a.cmd == 'run':
        run(a)
    elif a.cmd == 'force':
        E = engine_for(a)
        print('\t'.join(E.force(a.node, a.holding, a.dst, a.t, a.u, a.unit, E.D.extra.get(a.node))))
    elif a.cmd == 'status':
        E = engine_for(a)
        print('\t'.join(E.status(a.node, a.holding, a.t, a.u)))
    elif a.cmd == 'can':
        E = engine_for(a)
        print('\t'.join(E.can_change(a.by, a.target, E.domain_of(a.issue) if a.issue != '-' else 'unknown')))


if __name__ == '__main__':
    main()
