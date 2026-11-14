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

Round 5 (caselaw-lean-2/round5/DESIGN5.md, written from that file only; REF_NOTES "Round 5"; the readings chosen
where the design is silent are in caselaw-lean-2/round5/ref/NOTES.md, numbered A-n): the presence of
treatment_class.tsv in the data directory turns round-5 mode on. Then: recognised overrulings (a later court with
power says X was overruled by Y: `unknown recognisedLater` from date(Y), the negative from date(W)),
operative-words rows (demoted to a partial scope unless the quote has a whole-case phrase and no limit phrase), one
class per status-changing row,
classes.tsv, a trailing `oclass` column on status.tsv, status_lines.tsv and findings.tsv, the finding
`atRisk ... recognisedLater`, and four more lines in ref_stats.tsv. Without that file every output is byte for byte
what this program wrote before round 5.

Round 6 (caselaw-lean-2/round6/history/DESIGN6.md §4, written from that section only; readings where it is silent
are in round6/history/REF_QUESTIONS.md, numbered Q-n): the optional table history_anchor.tsv gives a history row a
second quote, the anchor, from the text of its certificate. Such a row is checked by Engine.check_anchored (reasons
anchorMismatch, anchorNoCue, anchorDisqualified, anchorUnresolved, anchorPart, then the plain check without the
target-evidence test); a row without an anchor line is checked as before. Four more lines in ref_stats.tsv when the
table has a line. Without the file, or with an empty one, every output is byte for byte what it was.

Round 7 (caselaw-lean-2/round7/DESIGN7.md §1-3, written from that file only; readings where it is silent are in
round7/agents/ref/REF_QUESTIONS7.md, numbered Q7-n): two optional tables and one claim. joined.tsv gives a treatments
row one or two further quotes from the text of its certificate, with a relation to the main quote (`antecedent`: an
overruling stated across two sentences; `doctrineTie`: a doctrine tied to the named case); such a row is checked by
Engine.check_joined (joinedMismatch, joinedPart, joinedDisqualified, joinedRelation, joinedUnresolved, then the
row's own check without the target-evidence test). A class line with claim `doctrine` makes a doctrine row (checked
in doctrine mode, unique by label inside the table, always demoted: at most a partial scope, class `doctrine`).
history_claim.tsv claims `orderHead` (a Supreme Court order-list disposition quoted from head matter) or `setAside`
("set aside" as a vacatur cue) for a history row. Without the two tables and without a doctrine claim every output
is byte for byte what it was (round 6).
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
            'rehearingEnBancGranted': 6, 'withdrawn': 7, 'substitutedBy': 7,
            # round 5 (DESIGN5 §2.3): the most severe unknown; the kind occurs only in round-5 mode, on unknown rows
            'recognisedLater': 100}

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
import cue_table as _CUES  # noqa: E402
# round 5 (DESIGN5 §6): the six new lists of the same generated table (read from the module, never copied here)
SELF_ANNOUNCED = tuple(getattr(_CUES, 'SELF_ANNOUNCED', ()))
RECOGNISED = tuple(getattr(_CUES, 'RECOGNISED', ()))
DISQUALIFY_RECOGNISED = tuple(getattr(_CUES, 'DISQUALIFY_RECOGNISED', ()))
OPERATIVE = tuple(getattr(_CUES, 'OPERATIVE', ()))
OPERATIVE_WHOLE = tuple(getattr(_CUES, 'OPERATIVE_WHOLE', ()))
# (DESIGN5 §9, ruling of 12:50: a whole-case phrase counts only when the quote has no phrase of this list)
OPERATIVE_LIMIT = tuple(getattr(_CUES, 'OPERATIVE_LIMIT', ()))
DISQUALIFY_OPERATIVE = tuple(getattr(_CUES, 'DISQUALIFY_OPERATIVE', ()))


def _r6_list(name, key, fallback):
    """Round 6 (round6/history/DESIGN6.md §4): a list of the single cue table. Read from the generated module; when
    the module was generated before the key existed, from cue_table.json; when the table has no such key yet, the
    initial list of DESIGN6 §4 (`fallback`)."""
    v = getattr(_CUES, name, None)
    if v is None:
        try:
            import json
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cues', 'cue_table.json'),
                      encoding='utf-8') as f:
                v = json.load(f).get(key)
        except (OSError, ValueError):
            v = None
    return tuple(v) if v is not None else tuple(fallback)


# round 6 (DESIGN6 §4): the cues an anchor quote must contain, and the marks of an earlier proceeding it must not
ANCHOR = _r6_list('ANCHOR', 'anchor', (
    'court of appeals', 'court of appeal', 'circuit court', 'district court', 'court below', 'appellate division',
    'appellate court', 'appellate term', 'superior court', 'supreme court', 'court of civil appeals',
    'court of criminal appeals', 'trial court', 'certiorari', 'appeal from', 'error to', 'reported below',
    'decision below', 'opinion below', 'judgment below', 'sub nom', 'c. a.', 'rehearing', 'en banc', 'in banc',
    'panel', 'former opinion', 'prior opinion', 'original opinion', 'earlier opinion', 'previous opinion',
    'opinion of', 'opinion filed', 'opinion in this case', 'decision of this court', 'commonwealth court',
    'tax court', 'board of tax appeals', 'court of claims', 'bankruptcy'))
DISQUALIFY_ANCHOR = _r6_list('DISQUALIFY_ANCHOR', 'disqualify_anchor', (
    'former appeal', 'prior appeal', 'first appeal', 'earlier appeal', 'previous appeal', 'see also'))
ANCHOR_PARTS = ('majority', 'plurality', 'perCuriam', 'headmatter')
# round 9 (round9/DESIGN9.md §4): the part names a part_zone.tsv line may carry (the row part names; case-sensitive)
ZONE_PARTS = ('majority', 'plurality', 'perCuriam', 'concurrence', 'dissent', 'headmatter', 'other')


# round 7 (round7/DESIGN7.md §2-3): the new keys of the single cue table. Read from cue_table.json first (the source
# the generated modules come from; `order_line` is a map kind -> list and two keys are numbers, whose generated
# Python form is not fixed by the design), then from the generated module (the key upper-cased), and only when the
# table has no such key yet from the example lists of DESIGN7 (`R7_CUE_SOURCE` records which; NOTES.md says so).
R7_CUE_SOURCE = {}
_R7_JSON = None


def _r7(key, fallback):
    global _R7_JSON
    if _R7_JSON is None:
        try:
            import json
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cues', 'cue_table.json'),
                      encoding='utf-8') as f:
                _R7_JSON = json.load(f)
        except (OSError, ValueError):
            _R7_JSON = {}
    v = _R7_JSON.get(key)
    src = 'json'
    if v is None:
        v, src = getattr(_CUES, key.upper(), None), 'module'
    if v is None:
        v, src = fallback, 'design7-fallback'
    R7_CUE_SOURCE[key] = src
    if isinstance(fallback, int):
        return int(v)
    if isinstance(fallback, dict):
        return {k: tuple(x) for k, x in dict(v).items()}
    return tuple(v)


ANAPHOR = _r7('anaphor', ('those cases', 'these cases', 'that case', 'those decisions', 'these decisions',
                          'that decision', 'such cases', 'those opinions', 'those holdings', 'both cases',
                          'each of them', 'they are overruled', 'it is overruled'))
DOCTRINE_TIE = _r7('doctrine_tie', ('doctrine of', 'doctrine announced', 'doctrine established', 'rule of',
                                    'rule announced', 'rule laid down', 'announced in', 'established in',
                                    'adopted in', 'laid down in', 'the rule in', 'first announced', 'originated in'))
DOCTRINE_REJECT = _r7('doctrine_reject', ('has no place', 'is rejected', 'we reject', 'repudiate', 'abandon',
                                          'is overruled', 'no longer', 'discard', 'disapprove'))
DISQUALIFY_JOINED = _r7('disqualify_joined', ())
ORDER_LINE = _r7('order_line', {
    'certDenied': ('certiorari denied', 'petition for writ of certiorari denied'),
    'vacated': ('certiorari granted, judgment vacated', 'judgment vacated, and case remanded'),
    'reversed': ('judgment reversed',),
    'affirmed': ('judgment affirmed',),
    'reviewDismissed': ('appeal dismissed', 'certiorari dismissed', 'writ of certiorari dismissed')})
SET_ASIDE = _r7('set_aside', ('set aside', 'sets aside', 'is set aside', 'are set aside', 'be set aside'))
JOINED_GAP_MAX = _r7('joined_gap_max', 300)
ORDER_HEAD_FROM = _r7('order_head_from', 20130101)
ORDER_HEAD_KINDS = ('certDenied', 'vacated', 'reversed', 'affirmed', 'reviewDismissed')
ORDER_HEAD_MAXLEN = _r7('order_head_max_len', 400)
# round 8 (round8/DESIGN8.md §4, D8-3): bridge evidence for history rows. `bridge_cue` (kind -> list) and
# `bridge_max_len` are read from cue_table.json first (as the round-7 keys), else DESIGN8 §4's lists. A kind
# without a list fails bridgeCue (REF_QUESTIONS8.md Q8-7).
BRIDGE_CUE = _r7('bridge_cue', {
    'certDenied': ('cert. denied', 'certiorari denied', 'cert denied'),
    'vacated': ('vacated', 'judgment vacated', 'vacated and remanded'),
    'reversed': ("rev'd", 'reversed'),
    'affirmed': ("aff'd", 'affirmed'),
    'reviewDismissed': ('cert. dismissed', 'certiorari dismissed', 'appeal dismissed')})
BRIDGE_MAX_LEN = _r7('bridge_max_len', 600)
# round 8 (round8/DESIGN8.md §6, D8-12): the old circuits, for a history row with the claim `oldCircuit`:
# (acting court-of-appeals circuit, target district / bankruptcy court circuit, acting date before which it holds)
OLD_CIRCUIT = tuple(tuple(int(x) for x in t) for t in _r7('old_circuit', [[5, 11, 19811001], [8, 10, 19290301]]))
# round 8 (round8/DESIGN8.md §5, D8-5): the wider anchor cues, used only by an anchored row with the history claim
# `anchorWide` (anchor ++ anchor_wide); JSON first, else DESIGN8 §5's list
ANCHOR_WIDE = _r7('anchor_wide', ('circuit', '(ca1', '(ca2', '(ca3', '(ca4', '(ca5', '(ca6', '(ca7', '(ca8', '(ca9',
                                  '(cadc', '(cafc', 'c.a.', 'judicial court', 'court of errors', 'case below'))
# round 9 (round9/DESIGN9.md §8, D9-9): the judge-form strings `anchorWide` adds (a JSON list `anchor_wide9`, else
# DESIGN9's three; the Lean may instead extend `anchor_wide` itself: a string in both lists is harmless)
ANCHOR_WIDE9 = _r7('anchor_wide9', ('district judge', 'magistrate judge', 'trial judge'))
# round 11 (round11/DESIGN11.md §5.1, D11-4): the tribunal names an anchored row with the history claim
# `anchorTribunal` adds to the union `anchorWide` uses (a JSON list `anchor_tribunal` first, else DESIGN11's six)
ANCHOR_TRIBUNAL = _r7('anchor_tribunal', ('court of international trade', 'customs court', 'court of federal claims',
                                          'claims court', 'veterans court', 'court of veterans appeals'))
SCOTUS_COURT = 2906          # lead ruling D7-6 (8): the Supreme Court is court 2906 of the court table
JOINED_TABLES = ('treatments', 'history')
JOINED_RELS = ('antecedent', 'doctrineTie')
HCLAIMS = ('orderHead', 'setAside', 'anchorWide', 'oldCircuit',    # round 8 (DESIGN8 §5, §6)
           'trialBridge',                                           # round 10 (DESIGN10 §6, D10-8)
           'anchorTribunal')                                        # round 11 (DESIGN11 §5.1, D11-4)
# round 5 (DESIGN5 §5): the classes in their order for ties, and the claims a class-table row may make. Round 7
# (DESIGN7 §2.4): `doctrine` after `recognised` and before `atRiskWitness`, and the claim `doctrine`.
CLASS_ORDER = {'selfAnnounced': 0, 'operativeWords': 1, 'recognised': 2, 'doctrine': 3, 'atRiskWitness': 4}
CLAIMS = ('recognised', 'operativeWords', 'doctrine', 'joinedFar', 'implicitReject')   # round 9: DESIGN9 §5, §7
# round 9 (round9/DESIGN9.md §5, D9-5): a far antecedent joined quote, with the claim `joinedFar` only; JSON first
JOINED_FAR_MAX = _r7('joined_far_max', 1200)
# round 9 (round9/DESIGN9.md §7, D9-5): the cues a soft-kind row with the claim `implicitReject` adds to its kind's list
IMPLICIT_REJECT = _r7('implicit_reject', (
    'cannot agree', 'do not agree', 'unpersuaded', 'not convinced', 'wrongly decided', 'incorrectly decided',
    'erroneously decided', 'unsound', 'erroneous', 'incorrect', 'mistaken', 'undermined', 'eroded', 'discredited',
    'called into question', 'contrary to', 'depart from', 'departs from'))
# round 10 (round10/DESIGN10.md §4 + D10-5): remand bridge evidence for history rows (history_remand.tsv). JSON
# first, else DESIGN10's values (round10/agents/ref10/REF_QUESTIONS10.md Q10-7).
REMAND_COURT = _r7('remand_court', ('supreme court',))
REMAND_CUE = _r7('remand_cue', ('vacat', 'remand', 'in light of', 'further consideration'))
REMAND_QUOTE_MAX = _r7('remand_quote_max', 600)
REMAND_DOCKET_SPAN_MAX = _r7('remand_docket_span_max', 200)
REMAND_DAYS = _r7('remand_days_max', 1826)
# D10-7: the reason-case tie (c2): a span of the order's own text (<= remand_order_span_max) holding "in light of"
# (`remand_order_cue`) and compact(tie) (>= remand_tie_min characters), compact(tie) also in compact(B quote)
REMAND_ORDER_SPAN_MAX = _r7('remand_order_span_max', 300)
REMAND_ORDER_CUE = _r7('remand_order_cue', ('in light of',))
REMAND_TIE_MIN = _r7('remand_tie_min', 8)
# round 10 (round10/DESIGN10.md §6, D10-8, D10-9): the trial-judgment bridge of a history row with the claim
# `trialBridge`. JSON first, else DESIGN10's values (REF_QUESTIONS10.md Q10-14..Q10-16).
TRIAL_COURT_NAMES = _r7('trial_court_names', (
    'trial court', 'district court', 'circuit court', 'superior court', 'county court', 'court of common pleas',
    'chancery court', 'probate court', 'court below'))
INTERMEDIATE_COURT_NAMES = _r7('intermediate_court_names', (
    'court of appeal', 'appellate', 'court of special appeals', 'court of civil appeals', 'court of criminal appeals',
    'commonwealth court', 'district court of appeal'))
TBRIDGE_QUOTE_MAX = _r7('tbridge_quote_max', 600)
TBRIDGE_CUE = _r7('tbridge_cue', ('affirm',))
TBRIDGE_NEGATIVE = _r7('tbridge_negative', ('reversed', 'reverse', 'vacate', 'set aside', 'remand'))
TBRIDGE_DAYS = _r7('tbridge_days_max', 1826)
TBRIDGE_KINDS = ('reversed', 'vacated')
# D10-6 (Q10-1): the order's date "as printed", exactly two forms: "<month> <d>, <yyyy>" (full lower-case name, day
# without a leading zero) and "<abbr> <d>, <yyyy>" for the abbreviations of that month (May, June, July: full form
# only). cue_table.json `remand_months` (12 names) and `remand_months_abbr` (12 lists, one per month) first, else
# DESIGN10's values.
_MONTHS = _r7('remand_months', ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                'september', 'october', 'november', 'december'))
REMAND_MONTHS_ABBR = tuple(tuple(x) for x in _r7('remand_months_abbr', (
    ('jan.',), ('feb.',), ('mar.',), ('apr.',), (), (), (), ('aug.',), ('sept.', 'sep.'), ('oct.',), ('nov.',),
    ('dec.',))))


# round 11 (round11/DESIGN11.md §5.2, D11-5): identity-tie evidence (history_identity.tsv); JSON first, else 200
IDENTITY_SPAN_MAX = _r7('identity_span_max', 200)
IDENTITY_FORMS = ('docket', 'cite', 'date')


def date_forms(d):
    """Round 10 (D10-6): the printed forms of a yyyymmdd date; () for 0 or a non-calendar date."""
    if d <= 0:
        return ()
    try:
        x = datetime.date(d // 10000, d // 100 % 100, d % 100)
    except (ValueError, OverflowError):
        return ()
    forms = ['%s %d, %d' % (_MONTHS[x.month - 1], x.day, x.year)]
    for a in (REMAND_MONTHS_ABBR[x.month - 1] if x.month - 1 < len(REMAND_MONTHS_ABBR) else ()):
        f = '%s %d, %d' % (a, x.day, x.year)
        if f not in forms:
            forms.append(f)
    return tuple(forms)


def day_number(d):
    """Round 10 (Q10-6): proleptic Gregorian day number of a yyyymmdd date; None for 0 or a non-calendar date."""
    if d <= 0:
        return None
    try:
        return datetime.date(d // 10000, d // 100 % 100, d % 100).toordinal()
    except (ValueError, OverflowError):
        return None
# round 5 (DESIGN5 §5.1 `oclass`): "the effects that make the row's status" are those whose contribution equals the
# status, so the reference's finer event kinds are read in the status vocabulary of the Lean output: one negative
# kind per group below, and four unknown reasons. Their order (the join) is: every negative above every unknown;
# partialScope < enBancRuleUnknown < powerUnknown < recognisedLater (DESIGN5 §2.3 and §9, ruling on A-25).
STATUS_KIND = {'overruled': 'overruled', 'disapproved': 'overruled', 'recededFrom': 'overruled',
               'abrogated': 'abrogated', 'supersededByEnactment': 'superseded', 'withdrawn': 'withdrawn',
               'substitutedBy': 'withdrawn', 'vacated': 'vacated', 'rehearingEnBancGranted': 'vacated',
               'reversed': 'reversed', 'depublished': 'depublished', 'reviewGrantedDepublished': 'depublished',
               'reviewGranted': 'reviewPending'}
UNK_RANK = {'partialScope': 1, 'enBancRuleUnknown': 2, 'powerUnknown': 3, 'recognisedLater': 4}
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
        # round 5 (DESIGN5 §1, R5-1): the class table. Its presence turns round-5 mode on; absent, nothing below
        # is used and every output is round 4's. id -> (claim, field_limit, doctrine). A line that cannot be read,
        # has not exactly 5 fields, names an unknown claim or an id with no treatments row is ignored and counted;
        # a later line for an id already taken is ignored and not counted (the first line wins). NOTES.md A-1..A-3.
        self.r5 = os.path.exists(J('treatment_class.tsv'))
        self.klass = {}
        self.class_bad = 0
        if self.r5:
            ids = {r['id'] for r in self.treatments}
            for line in read_lines(J('treatment_class.tsv')):
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 5 or p[1] not in CLAIMS or p[0] not in ids:
                    self.class_bad += 1
                    continue
                if p[0] not in self.klass:
                    self.klass[p[0]] = (p[1], p[2], p[3])
        # round 6 (round6/history/DESIGN6.md §4): the optional anchor table. history id -> (a_start, a_end, a_quote,
        # a_part, src). A history row with a line here is checked by Engine.check_anchored, every other row as
        # before. Absent or empty: nothing below is used and every output is what it was. Readings where the
        # design is silent are in round6/history/REF_QUESTIONS.md (Q-n):
        #   Q-1 a line that is not valid UTF-8, has not exactly 6 fields, or whose a_start / a_end is not ASCII
        #       digits is a bad line: ignored, counted (anchor_bad_rows), and it does not take the id;
        #   Q-2 "a history row id" = the id of a history.tsv line that loads (13 fields, numeric columns), whatever
        #       its kind or nodes; a line for any other id is ignored and counted (anchor_unknown_ids);
        #   Q-3 the first good line for an id wins; a later good line for it is ignored and counted
        #       (anchor_duplicates); tests in the order bad line, unknown id, duplicate;
        #   Q-4 an anchor is keyed by id: when history.tsv has several rows with that id, each is anchored.
        self.anchor = {}
        self.anchor_bad = self.anchor_unknown = self.anchor_dup = 0
        if os.path.exists(J('history_anchor.tsv')):
            ids = {r['id'] for r in self.history}
            for line in read_lines(J('history_anchor.tsv')):
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 6 or not _NAT_RX.match(p[1]) or not _NAT_RX.match(p[2]):
                    self.anchor_bad += 1
                    BAD_ROWS['history_anchor.tsv'] += 1
                elif p[0] not in ids:
                    self.anchor_unknown += 1      # (the summary's anchor_unknown_ids)
                elif p[0] in self.anchor:
                    self.anchor_dup += 1          # (the summary's anchor_duplicates)
                else:
                    self.anchor[p[0]] = (int(p[1]), int(p[2]), p[3], p[4], p[5])
        # round 7 (round7/DESIGN7.md §1, §2.1): the optional joined table. treatments id -> [(rel, j_start, j_end,
        # j_quote, j_part, label, src)], at most two lines, in file order. Readings (REF_QUESTIONS7.md):
        #   Q7-1 a bad line (not valid UTF-8, not exactly 9 fields, j_start / j_end not ASCII digits, a `table` or
        #        `rel` outside the design's values) is ignored, counted (joined_bad_rows = the Lean's
        #        `bad_rows joined.tsv n`) and takes no id;
        #   Q7-2 tests in the order bad line, unknown id (no loaded row of the named table has it:
        #        joined_unknown_ids; lead ruling D7-6 (11): first, for both tables), history line
        #        (joined_history_ignored), a line for a witness row (a treatments id with a treatment_witness line:
        #        ignored and counted, joined_witness_ignored; D7-6 (1)), third and later line for a treatments id
        #        (joined_extra); a line with an unknown part or an empty quote is a good line that fails the check.
        self.joined = {}
        self.joined_any = False
        self.joined_bad = self.joined_unknown = self.joined_extra = self.joined_hist = self.joined_wit = 0
        if os.path.exists(J('joined.tsv')):
            tids = {r['id'] for r in self.treatments}
            hids = {r['id'] for r in self.history}
            for line in read_lines(J('joined.tsv')):
                self.joined_any = True
                p = line.split('\t') if line is not None else None
                if (p is None or len(p) != 9 or p[1] not in JOINED_TABLES or p[2] not in JOINED_RELS
                        or not _NAT_RX.match(p[3]) or not _NAT_RX.match(p[4])):
                    self.joined_bad += 1
                    BAD_ROWS['joined.tsv'] += 1
                elif p[0] not in (tids if p[1] == 'treatments' else hids):
                    self.joined_unknown += 1
                elif p[1] == 'history':
                    self.joined_hist += 1            # reserved this round (DESIGN7 §2.1, D7-2)
                elif p[0] in self.witness:
                    self.joined_wit += 1             # D7-6 (1): the row is checked as in round 6
                elif len(self.joined.get(p[0], ())) >= 2:
                    self.joined_extra += 1
                else:
                    self.joined.setdefault(p[0], []).append((p[2], int(p[3]), int(p[4]), p[5], p[6], p[7], p[8]))
        # round 7 (DESIGN7 §1, §3): the optional history claim table. history id -> set of claims. Q7-3: a bad line
        # (not UTF-8, not exactly 3 fields, an unknown claim) is counted (hclaim_bad_rows = the Lean's
        # `bad_rows history_claim.tsv n`); an id of no loaded history line is counted (hclaim_unknown_ids); a
        # second line with the same id and claim is ignored and counted (hclaim_duplicates); one id may carry both
        # claims.
        self.hclaim = {}
        self.hclaim_any = False
        self.hclaim_bad = self.hclaim_unknown = self.hclaim_dup = 0
        if os.path.exists(J('history_claim.tsv')):
            hids = {r['id'] for r in self.history}
            for line in read_lines(J('history_claim.tsv')):
                self.hclaim_any = True
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 3 or p[1] not in HCLAIMS:
                    self.hclaim_bad += 1
                    BAD_ROWS['history_claim.tsv'] += 1
                elif p[0] not in hids:
                    self.hclaim_unknown += 1
                elif p[1] in self.hclaim.get(p[0], ()):
                    self.hclaim_dup += 1
                else:
                    self.hclaim.setdefault(p[0], set()).add(p[1])
        # round 8 (round8/DESIGN8.md §4, D8-3): the optional bridge table. history id -> (w_node, b_start, b_end,
        # b_quote, src). Joined like history_anchor.tsv (REF_QUESTIONS8.md Q8-1): a bad line (not valid UTF-8, not
        # exactly 6 fields, w_node / b_start / b_end not ASCII digits) is counted (bridge_bad_rows = the Lean's
        # `bad_rows history_bridge.tsv n`) and takes no id; then an id of no loaded history line (bridge_unknown_ids);
        # then a second good line for an id (bridge_duplicates: the first line wins). Absent / empty: nothing below
        # is used and every output is round 7's.
        self.bridge = {}
        self.bridge_any = False
        self.bridge_bad = self.bridge_unknown = self.bridge_dup = 0
        if os.path.exists(J('history_bridge.tsv')):
            hids = {r['id'] for r in self.history}
            for line in read_lines(J('history_bridge.tsv')):
                self.bridge_any = True
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 6 or not all(_NAT_RX.match(p[c]) for c in (1, 2, 3)):
                    self.bridge_bad += 1
                    BAD_ROWS['history_bridge.tsv'] += 1
                elif p[0] not in hids:
                    self.bridge_unknown += 1
                elif p[0] in self.bridge:
                    self.bridge_dup += 1
                else:
                    self.bridge[p[0]] = (int(p[1]), int(p[2]), int(p[3]), p[4], p[5])
        # round 10 (round10/DESIGN10.md §4 + D10-5 + D10-7): the optional remand table. history id -> (b_node, b_start,
        # b_end, docket, bd_start, bd_end, t_start, t_end, tie, o_start, o_end). Q10-9: a bad line (not UTF-8, not
        # exactly 12 fields (D10-7), a node or
        # offset column not ASCII digits) is counted (remand_bad_rows = the Lean's `bad_rows history_remand.tsv n`)
        # and takes no id; then an id of no loaded history line (ignored, not counted); then a later good line for a
        # taken id (remand_dup_rows; the first line wins). Absent / empty: nothing below is used.
        self.remand = {}
        self.remand_any = False
        self.remand_bad = self.remand_unknown = self.remand_dup = 0
        if os.path.exists(J('history_remand.tsv')):
            hids = {r['id'] for r in self.history}
            for line in read_lines(J('history_remand.tsv')):
                self.remand_any = True
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 12 or not all(_NAT_RX.match(p[c]) for c in (1, 2, 3, 5, 6, 7, 8, 10, 11)):
                    self.remand_bad += 1
                    BAD_ROWS['history_remand.tsv'] += 1
                elif p[0] not in hids:
                    self.remand_unknown += 1
                elif p[0] in self.remand:
                    self.remand_dup += 1
                else:
                    self.remand[p[0]] = (int(p[1]), int(p[2]), int(p[3]), p[4], int(p[5]), int(p[6]), int(p[7]),
                                         int(p[8]), p[9], int(p[10]), int(p[11]))
        # round 11 (round11/DESIGN11.md §5.2, D11-5): the optional identity-tie table. history id -> (form, token,
        # d_start, d_end, t_start, t_end). A bad line (not UTF-8, not 7 fields, an unknown form, an offset not ASCII
        # digits) counts identity_bad_rows and takes no id; then an id of no history line (ignored; counted only
        # internally, REF_QUESTIONS11 Q11-6); then a later good line for a taken id (identity_dup_rows; first wins).
        self.identity = {}
        self.identity_any = False
        self.identity_bad = self.identity_unknown = self.identity_dup = 0
        if os.path.exists(J('history_identity.tsv')):
            hids = {r['id'] for r in self.history}
            for line in read_lines(J('history_identity.tsv')):
                self.identity_any = True
                p = line.split('\t') if line is not None else None
                if (p is None or len(p) != 7 or p[1] not in IDENTITY_FORMS
                        or not all(_NAT_RX.match(p[c]) for c in (3, 4, 5, 6))):
                    self.identity_bad += 1
                    BAD_ROWS['history_identity.tsv'] += 1
                elif p[0] not in hids:
                    self.identity_unknown += 1
                elif p[0] in self.identity:
                    self.identity_dup += 1
                else:
                    self.identity[p[0]] = (p[1], p[2], int(p[3]), int(p[4]), int(p[5]), int(p[6]))
        # round 10 (round10/DESIGN10.md §6, D10-8, D10-9): the optional trial-bridge table. history id -> (t_start,
        # t_end), a quote of the target T's own text. Q10-17: a bad line (not UTF-8, not 3 fields, offsets not ASCII
        # digits) counts tbridge_bad_rows and takes no id; an unknown id is ignored (not counted); a later good line
        # for a taken id counts tbridge_dup_rows. Absent / empty: nothing below is used.
        self.tbridge = {}
        self.tbridge_any = False
        self.tbridge_bad = self.tbridge_unknown = self.tbridge_dup = 0
        if os.path.exists(J('history_tbridge.tsv')):
            hids = {r['id'] for r in self.history}
            for line in read_lines(J('history_tbridge.tsv')):
                self.tbridge_any = True
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 3 or not all(_NAT_RX.match(p[c]) for c in (1, 2)):
                    self.tbridge_bad += 1
                    BAD_ROWS['history_tbridge.tsv'] += 1
                elif p[0] not in hids:
                    self.tbridge_unknown += 1
                elif p[0] in self.tbridge:
                    self.tbridge_dup += 1
                else:
                    self.tbridge[p[0]] = (int(p[1]), int(p[2]))
        # round 9 (round9/DESIGN9.md §4): the optional part-zone table. node -> [(z_start, z_end, part)], sorted.
        # Readings (round9/agents/ref9/REF_QUESTIONS9.md): Q9-6 a line that is not valid UTF-8, has not exactly 5
        # fields, or whose node / z_start / z_end is not ASCII digits is a bad line (zone_bad_rows = the Lean's
        # `bad_rows part_zone.tsv n`) and touches no node; a parsed line with z_start >= z_end or a part outside the
        # seven names poisons its node; Q9-7 two zones of a node overlap when a < d and c < b. A poisoned or
        # overlapping node loses ALL its zones (zone_bad_nodes). Absent / empty: nothing below is used.
        self.zones = {}
        self.zone_any = False
        self.zone_bad = self.zone_bad_nodes = self.zone_lines = 0
        if os.path.exists(J('part_zone.tsv')):
            raw = defaultdict(list)
            poisoned = set()
            for line in read_lines(J('part_zone.tsv')):
                self.zone_any = True
                p = line.split('\t') if line is not None else None
                if p is None or len(p) != 5 or not all(_NAT_RX.match(p[c]) for c in (0, 1, 2)):
                    self.zone_bad += 1
                    BAD_ROWS['part_zone.tsv'] += 1
                    continue
                n, zs, ze = int(p[0]), int(p[1]), int(p[2])
                if zs >= ze or p[3] not in ZONE_PARTS:
                    poisoned.add(n)
                    continue
                raw[n].append((zs, ze, p[3]))
            for n, zl in raw.items():
                if n in poisoned:
                    continue
                zl.sort()
                if any(zl[i + 1][0] < zl[i][1] for i in range(len(zl) - 1)):
                    poisoned.add(n)          # sorted by start: some pair overlaps iff some neighbour pair does
                    continue
                self.zones[n] = zl
                self.zone_lines += len(zl)
            self.zone_bad_nodes = len(poisoned)
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
        for b in self.bridge.values():
            need.add(b[0])                    # round 8: the bridge text W's sha
        for m in self.remand.values():
            need.add(m[0])                    # round 10: the remand decision B's sha
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
        # round 5 (DESIGN5): all empty and unused without the class table
        self.r5 = D.r5
        self.recog_text = {}        # shared: witness row id -> the rule-independent recognised checks pass (§2.2)
        self.recog_all = {}         # shared: row id -> okRecognised | okRecognisedUnverifiedBy, full rule set
        self.row_class = {}         # shared: row id -> class (§5), for every row of a status-changing kind
        self.demoted = set()        # shared: admitted operativeWords rows without a whole-case phrase (§3.3)
        self.op_admitted = set()    # shared: operativeWords rows whose text checks pass
        self.cert_plain = {}        # shared: operativeWords-claim row id -> its round-4 (plain) check result
        self.recog = {}             # this rule set: row id -> verdict string
        self.recog_by_target = defaultdict(list)   # this rule set: target -> [(row, W)]

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
    def check_cert(self, cert, owners, kind, need_target, require_verb=True, target=None, mode=None, hclaim=None,
                   by=None, extra_cues=(), tbridge=False):
        """mode (round 5 only; None = the round-4 check, unchanged): 'recognised' (DESIGN5 §2.2) and 'operative'
        (§3.2) replace the cue list and the disqualifier lists and resolve the target in the quote itself; round 7
        'doctrine' (DESIGN7 §2.4): the cue list `doctrine_reject`, the disqualifiers of 'operative'.
        hclaim (round 7, DESIGN7 §3; history rows only): the row's claims. `setAside` on a `vacated` row adds the
        list `set_aside` to the cue list; `orderHead` admits part `headmatter` under §3.1's conditions (acting
        decision `by`), else the reason is orderHeadNotAllowed. None or empty: the check is unchanged."""
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
        if mode is not None:
            # round 5 text mode: the cue list and the disqualifier lists of the claim, not of the kind (round 7:
            # doctrine mode, the list `doctrine_reject` and the operative disqualifiers)
            cues = RECOGNISED if mode == 'recognised' else (DOCTRINE_REJECT if mode == 'doctrine' else OPERATIVE)
            if not any(v in ql for v in cues):
                return 'noVerb'
            if any(x in ql for x in (DISQUALIFY_RECOGNISED if mode == 'recognised'
                                     else DISQUALIFY_TREAT + DISQUALIFY_OPERATIVE)):
                return 'disqualified'
        elif require_verb and kind == 'other':
            return 'noVerb'                  # R28 (c): no verb names an 'other' event, so none can be certified
        if mode is None and require_verb:
            verbs = VERBS.get(kind)
            if hclaim and 'setAside' in hclaim and kind == 'vacated':
                verbs = tuple(verbs or ()) + SET_ASIDE      # round 7 (DESIGN7 §3.2): claim-gated vacatur cue
            if extra_cues:
                verbs = tuple(verbs or ()) + tuple(extra_cues)   # round 9 (DESIGN9 §7): implicitReject
            if tbridge:
                # round 10 (DESIGN10 §6, trialBridgeD; Q10-14): the kind-cue test is replaced: a cue of the kind,
                # a trial-court name, and no intermediate-court name
                if (not verbs or not any(v in ql for v in verbs) or not any(n in ql for n in TRIAL_COURT_NAMES)
                        or any(n in ql for n in INTERMEDIATE_COURT_NAMES)):
                    return 'trialBridgeD'
            elif verbs and not any(v in ql for v in verbs):
                return 'noVerb'
        if mode is None and require_verb and kind in NEG_TREAT and any(x in ql for x in DISQUALIFY_TREAT):
            return 'disqualified'
        if mode is None and require_verb and kind in HIST_KINDS_ALL and any(x in ql for x in DISQUALIFY_HIST):
            return 'disqualified'
        if need_target:
            # R21 (revised, D4 real data): the target is named in the quote or in its covering window (the reader
            # quotes the treating sentence; the citation or caption is often next to it); citations compare as
            # lowercase letters and digits (SCHEMA cite:<normalised citation>); names as whole words of >= 3 chars
            ev = cert.tev or ''
            if mode is not None:
                ctx = q                       # round 5: named in the quote itself, not in the window
            else:
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
            if cert.part == 'headmatter' and hclaim and 'orderHead' in hclaim:
                # round 7 (DESIGN7 §3.1): the part rule admits head matter only under all the claim's conditions
                return 'ok' if self.order_head_ok(by, kind, ql) else 'orderHeadNotAllowed'
            return 'part'
        return 'ok'

    def order_head_ok(self, by, kind, ql):
        """Round 7 (DESIGN7 §3.1): may a history row with an `orderHead` claim quote its disposition from head matter?
        The acting decision is a decision of the Supreme Court of the United States (lead ruling D7-6 (8): its
        court is court 2906 and has an epoch on the decision's date), dated (decisions2; 0 fails) on or after
        `order_head_from`; the kind is one of the five order-list kinds; the normalised lower-cased quote `ql`
        contains a phrase of `order_line` for that kind and is at most 400 characters long."""
        D = self.D
        if by is None or by < 0 or not D.has(by):
            return False
        e = self.epoch(D.court[by], D.date[by])
        if e is None or e.court != SCOTUS_COURT or D.date[by] < ORDER_HEAD_FROM:
            return False
        if kind not in ORDER_HEAD_KINDS or len(ql) > ORDER_HEAD_MAXLEN:
            return False
        return any(self.order_line_hit(ql, c) for c in ORDER_LINE.get(kind, ()))

    @staticmethod
    def order_line_hit(ql, entry):
        """Round 7, lead ruling D7-9: an `order_line` entry that splits on " ... " into exactly two parts a, b means
        hasInOrder(ql, a, b): ql split on a gives at least two pieces and b occurs in the concatenation of the
        pieces after the first. Any other entry is a plain substring test."""
        parts = entry.split(' ... ')
        if len(parts) == 2:
            a, b = parts
            pieces = ql.split(a) if a else [ql]
            return len(pieces) >= 2 and b in ''.join(pieces[1:])
        return entry in ql

    @staticmethod
    def ev_resolves_in(ev, ql, target, cite_index):
        """Round 6/7: does target evidence `ev` resolve inside the lower-cased quote `ql` alone? `cite:`: the compact
        citation occurs in the compact quote and, with the citation index, the index maps it to `target`; `name:`:
        every token of 3 or more characters is a whole word (a maximal run of ASCII letters and digits) of the
        quote. Anything else, an empty citation, or a name with no such token resolves nothing (Q-7)."""
        ev = ev or ''
        if ev.startswith('cite:'):
            c = alnum(ev[5:])
            if not c or c not in alnum(ql):
                return False
            return cite_index is None or cite_index.get(c) == target
        if ev.startswith('name:'):
            words = set(re.findall(r'[0-9a-z]+', ql))
            toks = [x for x in (alnum(t) for t in ev[5:].split(' ')) if len(x) >= 3]
            return bool(toks) and all(x in words for x in toks)
        return False

    def check_joined(self, r, lines, mode, far=False, implicit=False):
        """Round 7 (round7/DESIGN7.md §2.1-2.4, `checkJoined`): a treatments row with one or two joined lines, each a
        further quote from the text of the row's own certificate with a relation to the main quote. Checks in the
        design's order, the first failure is the reason; no fall-back to the one-quote check. mode: None (plain,
        an explicit row), 'operative' (an operativeWords claim), 'doctrine' (a doctrine claim). Readings of what the
        design leaves open: REF_QUESTIONS7.md."""
        D = self.D
        cert = r['cert']
        kind = r['kind']
        wins = D.cert_text.get(cert.sha, ())
        qs = []
        # 1. joinedMismatch: every joined quote is non-empty, j_start < j_end, and the text at that offset of a
        #    usable window (well formed, covering, hash-consistent) filed under the row's own text_sha as written
        #    (Q-5 of round 6: whether that sha is the acting decision's is the main check's shaMismatch, step 6)
        for (rel, s, e, jq, jp, label, src) in lines:
            q = norm_quote(jq)
            if not q or e <= s or len(q) != e - s:
                return 'joinedMismatch'
            if not any(s0 <= s and e <= e0 and len(w) == e0 - s0 and hok and norm_quote(w)[s - s0:e - s0] == q
                       for (s0, e0, w, hok) in wins):
                return 'joinedMismatch'
            qs.append(ascii_lower(q))
        # 2. joinedPart: an opinion-of-the-court part (exact, case-sensitive; Q-10 of round 6)
        if any(l[4] not in CERT_PARTS for l in lines):
            return 'joinedPart'
        # 3. joinedDisqualified: the plain list of the row's kind (`disqualify_treat` for a status-changing kind,
        #    none for another kind) and the new list `disqualify_joined`, in every mode (lead ruling D7-6 (5): not
        #    the operative / doctrine additions)
        disq = (DISQUALIFY_TREAT if kind in NEG_TREAT else ()) + DISQUALIFY_JOINED
        if any(any(x in ql for x in disq) for ql in qs):
            return 'joinedDisqualified'
        # 4. joinedRelation
        mq = ascii_lower(norm_quote(cert.quote))
        for (rel, s, e, jq, jp, label, src), ql in zip(lines, qs):
            if rel == 'antecedent':
                # §2.2: the joined quote ends before the main quote starts, at most `joined_gap_max` characters
                # before it; the main quote has an anaphor and a cue of the row's kind (the plain list)
                if not e <= cert.start:
                    return 'joinedRelation'
                if cert.start - e > JOINED_GAP_MAX:
                    # round 9 (DESIGN9 §5): with the claim `joinedFar`, a gap up to joined_far_max on the row's own
                    # text: a usable window covering [j_end, start), no index key of another node starting there
                    # (no paragraph test: D9-7) (REF_QUESTIONS9.md Q9-12..Q9-15); the anaphor / cue tests below as §2.2
                    if not far:
                        return 'joinedRelation'
                    v = self.far_gap(cert, e, r['target'])
                    if v is not None:
                        return v
                if not any(a in mq for a in ANAPHOR):
                    return 'joinedRelation'
                if not any(v in mq for v in VERBS.get(kind, ())):
                    return 'joinedRelation'
            else:
                # §2.3: only on a doctrine row; the label D (normalised, lower-cased) has >= 2 words (pieces between
                # spaces, Q7-7) and >= 8 characters, occurs in both quotes, and the joined quote has a tie cue
                if mode != 'doctrine':
                    return 'joinedRelation'
                dl = ascii_lower(norm_quote(label))
                if len([w for w in dl.split(' ') if w]) < 2 or len(dl) < 8:
                    return 'joinedRelation'
                if dl not in mq or dl not in ql:
                    return 'joinedRelation'
                if not any(t in ql for t in DOCTRINE_TIE):
                    return 'joinedRelation'
        # 5. joinedUnresolved: the target evidence resolves inside one joined quote alone
        if not any(self.ev_resolves_in(cert.tev, ql, r['target'], D.cite_index) for ql in qs):
            return 'joinedUnresolved'
        # 6. the row's own check on its main quote, the target evidence taken as given (selfText), in its mode.
        #    Q7-8: an operativeWords claim's operativeBadRow test belongs to this step (DESIGN5 §3.2 puts it first
        #    in the operative check). Date order and authority: the status layer, as for every treatments row.
        if mode == 'operative' and (kind != 'disapproved' or r['explicit'] != 1):
            return 'operativeBadRow'
        return self.check_cert(cert, [r['by']], kind, False, target=r['target'], mode=mode,
                               extra_cues=IMPLICIT_REJECT if implicit else ())

    def far_gap(self, cert, e, target):
        """Round 9 (round9/DESIGN9.md §5, claim `joinedFar`): the tests of a joined antecedent quote ending at `e`
        more than joined_gap_max characters before the main quote starts. -> a failure reason, or None. Order (Q9-12):
        joinedFarGap (start - e > joined_far_max), joinedFarWindow (no usable window of the row's text_sha - well
        formed, covering [e, start), hash-consistent - the first in cert_text order is used), joinedFarKey (an index key that maps to a node other than the target
        starts at a compact position whose offset is in [e, start); the compact form is that of the window's text
        from e to its end, so a key may run past start; an ambiguous key is no key, D8-15; Q9-14)."""
        D = self.D
        start = cert.start
        if start - e > JOINED_FAR_MAX:
            return 'joinedFarGap'
        win = None
        for (s0, e0, w, hok) in D.cert_text.get(cert.sha, ()):
            if s0 <= e and start <= e0 and len(w) == e0 - s0 and hok:
                win = (s0, w)
                break
        if win is None:
            return 'joinedFarWindow'
        s0, w = win
        # (DESIGN9 §5 test 1, joinedFarPara, was dropped by D9-7: no paragraph test)
        if D.cite_index is None:
            return None
        self._cite_keys_of(target)          # builds the key lengths
        lens, idx = self._key_lens, D.cite_index
        tail = ascii_lower(w[e - s0:])
        comp, pos = [], []
        for i, ch in enumerate(tail):
            if '0' <= ch <= '9' or 'a' <= ch <= 'z':
                comp.append(ch)
                pos.append(e + i)
        c = ''.join(comp)
        for i in range(len(c)):
            if pos[i] >= start:
                break
            for L in lens:
                if i + L > len(c):
                    break
                v = idx.get(c[i:i + L])
                if v is not None and v != target:
                    return 'joinedFarKey'
        return None

    def check_anchored(self, r, a, hclaim=None, tbridge=False):
        """Round 6 (round6/history/DESIGN6.md §4, `checkAnchored`): a history row with a line in history_anchor.tsv.
        The anchor is a second quote from the text of the row's certificate (the same text_sha); it carries the
        target evidence, so the disposition quote's own window need not. Checks in the design's order, the first
        failure is the reason. Written from DESIGN6 §4 only; readings of what it leaves open: REF_QUESTIONS.md."""
        D = self.D
        cert = r['cert']
        a_start, a_end, a_quote, a_part = a[0], a[1], a[2], a[3]
        # 1. anchorMismatch: the anchor quote is not empty and is the text, at the stated offset, of a usable
        #    window of the same text: well formed (text length = end0 - start0), covering [a_start, a_end), and
        #    hash-consistent when window_sha.tsv is supplied (as for the main quote). Q-5: the window is looked up
        #    under the row's text_sha as written; that this sha is the sha of the target or of the acting decision
        #    is step 6's test (shaMismatch), so a row with a foreign sha fails here only if that sha has no such
        #    window.
        aq = norm_quote(a_quote)
        if a_end <= a_start or len(aq) != a_end - a_start:
            return 'anchorMismatch'
        if not any(s0 <= a_start and a_end <= e0 and len(w) == e0 - s0 and hok
                   and norm_quote(w)[a_start - s0:a_end - s0] == aq
                   for (s0, e0, w, hok) in D.cert_text.get(cert.sha, ())):
            return 'anchorMismatch'
        al = ascii_lower(aq)
        # 2. anchorNoCue: a cue of the list `anchor` in the lower-cased anchor quote (round 8, DESIGN8 §5: with the
        #    history claim `anchorWide`, of `anchor` ++ `anchor_wide`; without it the list is unchanged)
        #    (round 11, DESIGN11 §5.1: with the claim `anchorTribunal`, of `anchor` ++ `anchor_wide` ++
        #    `anchor_wide9` ++ `anchor_tribunal`; with both claims the same union; REF_QUESTIONS11 Q11-2, Q11-3)
        if hclaim and 'anchorTribunal' in hclaim:
            cues = ANCHOR + ANCHOR_WIDE + ANCHOR_WIDE9 + ANCHOR_TRIBUNAL
        elif hclaim and 'anchorWide' in hclaim:
            cues = ANCHOR + ANCHOR_WIDE + ANCHOR_WIDE9
        else:
            cues = ANCHOR
        if not any(c in al for c in cues):
            return 'anchorNoCue'
        # 3. anchorDisqualified: no mark of an earlier proceeding (list `disqualify_anchor`)
        if any(x in al for x in DISQUALIFY_ANCHOR):
            return 'anchorDisqualified'
        # 4. anchorUnresolved: the row's target evidence resolves inside the anchor quote alone (never its window).
        #    Q-6: also for a row whose certificate is from the target's own text (the plain check asks such a row
        #    for no evidence; the design makes no exception here). Evidence that is neither cite: nor name:, an
        #    empty citation, and a name with no token of 3 or more characters do not resolve (as the plain check).
        ev = cert.tev or ''
        if ev.startswith('cite:'):
            c = alnum(ev[5:])
            if not c or c not in alnum(al):
                return 'anchorUnresolved'
            if D.cite_index is not None and D.cite_index.get(c) != r['target']:
                return 'anchorUnresolved'
        elif ev.startswith('name:'):
            words = set(re.findall(r'[0-9a-z]+', al))
            toks = [x for x in (alnum(t) for t in ev[5:].split(' ')) if len(x) >= 3]
            if not toks or not all(x in words for x in toks):
                return 'anchorUnresolved'
        else:
            return 'anchorUnresolved'
        # 5. anchorPart
        if a_part not in ANCHOR_PARTS:
            return 'anchorPart'
        # 6. the plain check of the row's own certificate (the disposition quote), with the target evidence taken
        #    as given: hash, window, quote at offset, a cue of the kind, no disqualifier, part. (Date order and
        #    authority are decided in the status layer, as for every history row.)
        #    (round 7, DESIGN7 §3: a history claim changes this step's cue list or part rule, as in the plain check)
        return self.check_cert(cert, [r['target'], r['by']], r['kind'], False, target=r['target'], hclaim=hclaim,
                               by=r['by'], tbridge=tbridge)

    def check_tbridge(self, r):
        """Round 10 (round10/DESIGN10.md §6, D10-8, D10-9; Q10-15, Q10-16): after the anchored check of a
        trialBridge row passed: trialBridgeT (T's quote from history_tbridge.tsv: a usable window of T's own text,
        non-empty, <= tbridge_quote_max, holds a tbridge_cue phrase and no tbridge_negative phrase), then
        trialBridgeDate (date(T) < date(D) <= date(T) + 1,826 days, court(T) != court(D); decisions2 raw values)."""
        D = self.D
        T, Dn = r['target'], r['by']
        t = D.tbridge.get(r['id'])
        if t is None or t[1] - t[0] > TBRIDGE_QUOTE_MAX:
            return 'trialBridgeT'
        q = self.node_span(T, t[0], t[1])
        if q is None:
            return 'trialBridgeT'
        ql = ascii_lower(q)
        if not any(c in ql for c in TBRIDGE_CUE) or any(x in ql for x in TBRIDGE_NEGATIVE):
            return 'trialBridgeT'
        if Dn is None or Dn < 0 or not D.has(Dn) or not D.has(T):
            return 'trialBridgeDate'
        dt, dd = day_number(D.date[T]), day_number(D.date[Dn])
        if dt is None or dd is None or not (dt < dd <= dt + TBRIDGE_DAYS) or D.court[T] == D.court[Dn]:
            return 'trialBridgeDate'
        return 'ok'

    def _cite_keys_of(self, node):
        """Round 8: the compact keys of cite_index.tsv that the index maps to `node` (an ambiguous key, indexed to
        two or more nodes, maps to none). Built once, with the set of key lengths used by check_bridge step 6."""
        if getattr(self, '_keys_by_node', None) is None:
            m = defaultdict(list)
            for k, v in self.D.cite_index.items():
                if v is not None:
                    m[v].append(k)
            self._keys_by_node = m
            self._key_lens = sorted({len(k) for k in self.D.cite_index})
        return self._keys_by_node.get(node, ())

    def check_bridge(self, r, b, hclaim=None):
        """Round 8 (round8/DESIGN8.md §4, `checkBridge`, D8-3): a history row (O = the acting decision `by`, X = the
        target) with a line in history_bridge.tsv: a quote of a third decision W whose subsequent-history clause
        cites X, then a cue of the row's kind, then O ("X, 123 F.3d 456 (5th Cir. 2015), cert. denied, 577 U.S.
        1001"). Checks in the design's order, the first failure is the reason; no fall-back to the plain check.
        Readings of what the design leaves open: round8/agents/ref8/REF_QUESTIONS8.md (Q8-n). Positions p1, p2 and
        the position of O's citation are code-point offsets in the normalised, lower-cased quote; a compact
        citation's position is that of its first character there (Q8-4)."""
        D = self.D
        w, s, e, bq = b[0], b[1], b[2], b[3]
        q = norm_quote(bq)
        # 1. bridgeMismatch: non-empty, b_start < b_end, b_end - b_start <= bridge_max_len, and the text at that
        #    offset of a usable window (well formed, covering, hash-consistent) of W's own text (W's sha in
        #    decisions2; a W with no decisions2 row has no text: Q8-3)
        if not q or e <= s or e - s > BRIDGE_MAX_LEN or len(q) != e - s:
            return 'bridgeMismatch'
        wsha = D.sha.get(w) if D.has(w) else None
        if wsha is None or not any(s0 <= s and e <= e0 and len(win) == e0 - s0 and hok
                                   and norm_quote(win)[s - s0:e - s0] == q
                                   for (s0, e0, win, hok) in D.cert_text.get(wsha, ())):
            return 'bridgeMismatch'
        # 2. bridgeDate: date(W) >= date(O), both from decisions2; a date of 0 (or an O with no decisions2 row,
        #    by = -1 included) fails
        O = r['by']
        do = D.date[O] if (O is not None and O >= 0 and D.has(O)) else 0
        dw = D.date[w]
        if dw == 0 or do == 0 or dw < do:
            return 'bridgeDate'
        # 3. bridgeClause: one citation clause, no ';' in the normalised quote
        if ';' in q:
            return 'bridgeClause'
        ql = ascii_lower(q)
        comp, pos = [], []
        for i, ch in enumerate(ql):
            if '0' <= ch <= '9' or 'a' <= ch <= 'z':
                comp.append(ch)
                pos.append(i)
        c = ''.join(comp)
        # 4. bridgeTarget: the compact quote contains a compact citation the index maps to X; p1 = the first such
        #    (without cite_index.tsv nothing maps to X: Q8-5)
        if D.cite_index is None:
            return 'bridgeTarget'
        i1 = l1 = None                         # X's citation: compact index and length (longest key at i1)
        for k in self._cite_keys_of(r['target']):
            i = c.find(k)
            if i >= 0 and (i1 is None or i < i1 or (i == i1 and len(k) > l1)):
                i1, l1 = i, len(k)
        if i1 is None:
            return 'bridgeTarget'
        p1 = pos[i1]
        # 5. bridgeCue: after p1, a phrase of bridge_cue for the row's kind; p2 = the first such position > p1
        p2 = None
        for ph in BRIDGE_CUE.get(r['kind'], ()):
            j = ql.find(ph, p1 + 1) if ph else -1
            if j >= 0 and (p2 is None or j < p2):
                p2 = j
        if p2 is None:
            return 'bridgeCue'
        lens = self._key_lens
        idx = D.cite_index

        def keys_at(i):
            # differential run 1 (01:39, Q8-16): a compact key indexed to two or more nodes is not a key of the
            # index (the Lean drops it when the index is loaded), so it neither chains (5b) nor is a citation (6)
            return [c[i:i + L] for L in lens if i + L <= len(c) and idx.get(c[i:i + L]) is not None]
        # 5b. bridgeChain (D8-9): no index key (X's own keys included) starts between the end of X's citation
        #     (compact index i1 + l1) and p2 (Q8-13)
        for j in range(i1 + l1, len(c)):
            if pos[j] >= p2:
                break
            if keys_at(j):
                return 'bridgeChain'
        # 6. bridgeActor: the first compact citation after p2 (lead ruling D8-9 on lean8's L8-6: the first compact
        #    position after p2 at which some index key starts, taking the longest key starting there) is one the
        #    index maps to O (Q8-6, Q8-16)
        first = None
        for i in range(len(c)):
            if pos[i] <= p2:
                continue
            hits = keys_at(i)
            if hits:
                first = max(hits, key=len)
                break
        if first is None or idx[first] != O:
            return 'bridgeActor'
        # 7. the row's own check (plain, or with its history claims) with the target evidence taken as given
        #    (selfText): hash, window, quote, cue, disqualifiers, part; date order is the caller's targetLater
        #    test and authority the status layer's, as for every history row
        return self.check_cert(r['cert'], [r['target'], r['by']], r['kind'], False, target=r['target'],
                               hclaim=hclaim, by=r['by'])

    def node_span(self, node, s, e):
        """Round 10 (D10-6, Q10-2/3): the text [s, e) of `node`'s own text (its decisions2 sha), from the first
        usable window in file order (well formed, covering, hash-consistent), normalised one for one (tab / CR / LF
        -> space); None when the node has no row, the span is empty, or no usable window covers it."""
        D = self.D
        if e <= s or not D.has(node):
            return None
        sha = D.sha.get(node)
        if sha is None:
            return None
        for (s0, e0, win, hok) in D.cert_text.get(sha, ()):
            if s0 <= s and e <= e0 and len(win) == e0 - s0 and hok:
                return norm_quote(win)[s - s0:e - s0]
        return None

    def check_remand(self, r, m):
        """Round 10 (round10/DESIGN10.md §4, D10-5, D10-6; `remandBridge`): a history row (order O = `by`, target X)
        with a line of history_remand.tsv naming the remand decision B, B's quote [b_start, b_end), a docket token,
        a span of B's text and a span of X's text holding the docket. Checks in the design's order, the first
        failure is the reason; 'ok' when all pass."""
        D = self.D
        B, bs, be, docket, ds, de, ts, te, tie, os_, oe = m
        O, X = r['by'], r['target']
        # 1a. remandCourt: decisions2 raw court ids of B and X equal; a missing row fails
        if not D.has(B) or not D.has(X) or D.court[B] != D.court[X]:
            return 'remandCourt'
        # 1b. remandDate: date(O) <= date(B) <= date(O) + 1,826 calendar days, date(X) < date(O); 0 / missing /
        #     non-calendar dates fail
        if O is None or O < 0 or not D.has(O):
            return 'remandDate'
        do, db, dx = day_number(D.date[O]), day_number(D.date[B]), day_number(D.date[X])
        if do is None or db is None or dx is None or not (do <= db <= do + REMAND_DAYS) or not dx < do:
            return 'remandDate'
        # 2. remandDocket: compact(docket) >= 4 chars with a digit, inside compact(B span) and compact(X span); each
        #    span non-empty, <= remand_docket_span_max, from a usable window of that node's own text
        dk = alnum(docket)
        if len(dk) < 4 or not any('0' <= ch <= '9' for ch in dk):
            return 'remandDocket'
        if de - ds > REMAND_DOCKET_SPAN_MAX or te - ts > REMAND_DOCKET_SPAN_MAX:
            return 'remandDocket'
        bsp, tsp = self.node_span(B, ds, de), self.node_span(X, ts, te)
        if bsp is None or tsp is None or dk not in alnum(bsp) or dk not in alnum(tsp):
            return 'remandDocket'
        # 3. remandCue: B's quote (usable window, <= remand_quote_max) holds "supreme court" and a remand_cue phrase
        if be - bs > REMAND_QUOTE_MAX:
            return 'remandCue'
        q = self.node_span(B, bs, be)
        if q is None:
            return 'remandCue'
        ql = ascii_lower(q)
        if not any(c in ql for c in REMAND_COURT) or not any(c in ql for c in REMAND_CUE):
            return 'remandCue'
        # 4. remandTie (D10-7): (a) an index key mapping to O inside compact(B quote); (c) a date form of date(O)
        #    inside the lower-cased B quote; (c2) a span of O's own text (non-empty, <= remand_order_span_max, usable
        #    window) holding "in light of", and compact(tie) (>= remand_tie_min chars) inside compact(O span) and
        #    compact(B quote). Tie (b) (B's docket in B's quote) is dropped.
        cq = alnum(ql)
        if D.cite_index is not None and any(k in cq for k in self._cite_keys_of(O)):
            return 'ok'
        if any(f in ql for f in date_forms(D.date[O])):
            return 'ok'
        ck = alnum(tie)
        if len(ck) >= REMAND_TIE_MIN and ck in cq and oe - os_ <= REMAND_ORDER_SPAN_MAX:
            osp = self.node_span(O, os_, oe)
            if osp is not None:
                ol = ascii_lower(osp)
                if any(c in ol for c in REMAND_ORDER_CUE) and ck in alnum(ol):
                    return 'ok'
        return 'remandTie'

    def check_identity(self, r, m):
        """Round 11 (round11/DESIGN11.md §5.2, D11-5; `identityTie`): a history row (acting D = `by`, target T) with
        a line of history_identity.tsv: a span of D's own text and a span of T's own text (each non-empty, <=
        identity_span_max, from a usable window of that node's text, normalised one for one, ASCII lower-cased)
        hold the identity token: docket / cite: compact(token) >= 4 characters with a digit, inside both compact
        spans; date: the token is yyyymmdd = date(T) (0 / missing fails) and both spans hold a date form of it."""
        D = self.D
        form, token, ds, de, ts, te = m
        Dn, T = r['by'], r['target']
        if de - ds > IDENTITY_SPAN_MAX or te - ts > IDENTITY_SPAN_MAX:
            return 'identityTie'
        if Dn is None or Dn < 0:
            return 'identityTie'
        dsp, tsp = self.node_span(Dn, ds, de), self.node_span(T, ts, te)
        if dsp is None or tsp is None:
            return 'identityTie'
        if form in ('docket', 'cite'):
            k = alnum(token)
            if len(k) < 4 or not any('0' <= ch <= '9' for ch in k):
                return 'identityTie'
            return 'ok' if (k in alnum(dsp) and k in alnum(tsp)) else 'identityTie'
        # date (REF_QUESTIONS11 Q11-7: the token is exactly eight ASCII digits)
        if not (len(token) == 8 and _NAT_RX.match(token)) or not D.has(T) or not D.date[T]:
            return 'identityTie'
        if int(token) != D.date[T]:
            return 'identityTie'
        forms = date_forms(D.date[T])
        dl, tl = ascii_lower(dsp), ascii_lower(tsp)
        if not forms or not any(f in dl for f in forms) or not any(f in tl for f in forms):
            return 'identityTie'
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

    # ---------------------------------------------------------------- round 5 (DESIGN5 §2, §3, §5)
    def _recog_text(self, r, W, by_ev):
        """DESIGN5 §2.2, the parts of the recognised check that no rule set changes: the row is a well-formed
        witness row (witnessBadRow), the text checks pass in recognised text mode for the target evidence and for
        the by-evidence (cue of the list `recognised`, no phrase of `disqualify_recognised`, X and Y both named in
        the quote itself, a majority part), and (step 4) the two pieces of evidence differ once compacted."""
        D = self.D
        X, Y = r['target'], r['by']
        if not D.has(W) or r['explicit'] != 0 or r['kind'] not in NEG_TREAT:
            return False
        c = r['cert']
        if self.check_cert(c, [W], r['kind'], True, target=X, mode='recognised') != 'ok':
            return False
        c2 = Cert([c.sha, str(c.start), str(c.end), c.quote, by_ev, c.part])
        if self.check_cert(c2, [W], r['kind'], True, target=Y, mode='recognised') != 'ok':
            return False
        return alnum(by_ev[5:]) != alnum((c.tev or '')[5:])

    def _scope_dom(self, scope):
        """The issue domain a row's scope names: the one domain of its `issues:` keys, else unknown. (The round-4
        certificate verdicts ok / okUnverifiedBy / noAuthority of the regression outputs are can_change on this
        domain; NOTES.md A-6.)"""
        if scope.startswith('issues:'):
            ds = {self.domain_of(x) for x in scope[7:].split(',') if x}
            if len(ds) == 1:
                return ds.pop()
        return 'unknown'

    def _recog_rules(self, r, W):
        """DESIGN5 §2.2, the parts that depend on the rule set: date order X <= Y <= W with all three dates known
        (targetLater, witnessEarlier, step 3), W's power over X on every domain the issue could have (step 2; it
        implies the round-4 standing test), and Y's power over X not shown absent (noAuthority). -> the verdict
        string, or None (not recognised under this rule set: the verdict is the round-4 one)."""
        D = self.D
        X, Y = r['target'], r['by']
        dx, dy, dw = D.date[X], D.date[Y], D.date[W]
        if dx == 0 or dy == 0 or dw == 0 or dy < dx or dw < dy:
            return None
        if self.can_change(W, X, 'unknown')[0] != 'yes':
            return None
        pw = self.can_change(Y, X, self._scope_dom(r['scope']))[0]
        if pw == 'no':
            return None
        return 'okRecognised' if pw == 'yes' else 'okRecognisedUnverifiedBy'

    def _build_recog(self):
        """The rows recognised under this rule set (the text part is shared; the firm run decides its own)."""
        D = self.D
        self.recog = {}
        self.recog_by_target = defaultdict(list)
        for r in D.treatments:
            if not self.recog_text.get(r['id']):
                continue
            W = D.witness[r['id']][0]
            v = self._recog_rules(r, W)
            if v:
                self.recog[r['id']] = v
                self.recog_by_target[r['target']].append((r, W))

    def check_operative(self, r):
        """DESIGN5 §3.2: a non-witness row with an operativeWords claim. No fallback to the round-4 check."""
        if r['kind'] != 'disapproved' or r['explicit'] != 1:
            return 'operativeBadRow'
        return self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'], mode='operative')

    def _build_classes(self):
        """DESIGN5 §5: one class per treatments row of a status-changing kind, from the full rule set."""
        for r in self.D.treatments:
            if r['kind'] not in NEG_TREAT:
                continue
            if r['id'] in self.recog_all:
                c = 'recognised'
            elif r['explicit'] != 1:
                c = 'atRiskWitness'
            elif self._doctrine_claim(r):
                c = 'doctrine'       # round 7 (DESIGN7 §2.4; lead ruling D7-6 (9))
            elif any(p in ascii_lower(norm_quote(r['cert'].quote)) for p in SELF_ANNOUNCED):
                c = 'selfAnnounced'
            else:
                c = 'operativeWords'
            self.row_class[r['id']] = c

    def _doctrine_claim(self, r):
        """Round 7 (lead ruling D7-6 (9)): the row is of class `doctrine`: a class line with claim `doctrine`, kind
        `disapproved`, explicit = 1, whatever its verdict."""
        D = self.D
        return (D.r5 and r['id'] in D.klass and D.klass[r['id']][0] == 'doctrine' and r['kind'] == 'disapproved'
                and r['explicit'] == 1)

    def _plain(self, tid):
        """The round-4 certificate result of a treatments row, which is what a `laterCourtSays:<id>` supersession
        needs (DESIGN5 §9, ruling on A-21): a recognised verdict does not count, and for a row with an
        operativeWords claim it is the plain check, not the operative one. Without the class table: cert_ok."""
        v = self.cert_plain.get(tid)
        return v if v is not None else self.cert_ok.get(('treatments.tsv', tid))

    def cert_verdict(self, table, rid):
        """The verdict string of certs.tsv and classes.tsv: round 4's, or the recognised verdict (full rule set)."""
        if table == 'treatments.tsv' and rid in self.recog_all:
            return self.recog_all[rid]
        return self.cert_ok.get((table, rid))

    def zone_result(self, owner, r, jl):
        """Round 9 (round9/DESIGN9.md §4, `checkPartZone`; readings D9-4): None when the text owner `owner` (the node
        whose text the main quote is from: `by`, the witness W, or the target for a history row certified from the
        target's own text) has no kept zone; else whether the main quote [start, end) lies inside one zone
        (z_start <= start, end <= z_end) whose part equals the row's `part`, and every joined line's quote likewise
        with its `j_part` (same text owner)."""
        z = self.D.zones.get(owner)
        if not z:
            return None
        c = r['cert']
        spans = [(c.start, c.end, c.part)] + [(l[1], l[2], l[4]) for l in (jl or ())]
        return all(any(zs <= s and e <= ze and zp == p for (zs, ze, zp) in z) for (s, e, p) in spans)

    def lean_cert_passes(self, table, r):
        """Round 9 (D9-4 (2)): does the row pass the checks the Lean runner makes after the text checks, which the
        reference otherwise leaves to the status layer? (A row it fails is the Lean's `targetLater` or
        `noAuthority`, canonically a passed certificate, and is not zone-checked.) Measured against the stored
        round-8 Lean outputs (round9/agents/ref9/powercheck.py): a treatments row is `targetLater` when date(by) <
        date(target), both known (a witness row: date(Y) < date(X), as check_witness), and `noAuthority` when its
        kind changes status and can_change(by, target, scope domain) is no; a history row is `noAuthority` when
        same_case_power(by, target, claims) is no (its targetLater is the reference's own verdict already)."""
        D = self.D
        b, t = r['by'], r['target']
        if table == 'history':
            return self.same_case_power(b, t, D.hclaim.get(r['id'])) != 'no'
        if r['id'] in D.witness:
            if D.date[b] < D.date[t]:
                return False
        elif D.date[b] and D.date[t] and D.date[b] < D.date[t]:
            return False
        return r['kind'] not in NEG_TREAT or self.can_change(b, t, self._scope_dom(r['scope']))[0] != 'no'

    def zone_apply(self, res, zr, passes=True, key=None):
        """Round 9: a row whose complete round-8 verdict is `ok` (D9-4 (2): `passes` = also past the Lean's date
        order and power checks) and whose zone result is False becomes `partZone`; counts the rows that reach the
        check (zone_missing_rows: no kept zone of the text owner). D9-13: a row the Lean writes targetLater /
        noAuthority (passes False; the reference's `ok`) keeps that verdict, but when its quote fails the zone test
        it feeds no findings: `key` (table, id) goes to zone_mute and the row is not put in the admitted views."""
        if res != 'ok':
            return res
        if not passes:
            if zr is False and key is not None:
                self.zone_mute.add(key)
            return res
        return self.zone_count(zr)

    def zone_count(self, zr):
        if zr is None:
            self.zone_missing += 1
            return 'ok'
        self.zone_checked += 1
        if zr:
            return 'ok'
        self.zone_failed += 1
        return 'partZone'

    def admit(self):
        """Run every certificate check once; build the admitted views used by status/findings/splits."""
        D = self.D
        self.zone_fail = set()     # round 9: recognised rows failing the zone check (D9-4 (3))
        self.zone_missing = self.zone_checked = self.zone_failed = 0
        self.zone_mute = set()     # round 9 (D9-13): (t|h, id) of rows kept at targetLater / noAuthority whose zone fails
        self.remand_checked = self.remand_failed = 0    # round 10 (DESIGN10 §4)
        self.remand_mute = set()   # round 10 (Q10-10): (h, id) of rows kept at noAuthority whose remand check fails
        # (round 11, DESIGN11 §5.2: also those whose identity check fails)
        self.identity_checked = self.identity_failed = 0
        results = []         # [row, verdict] of every treatments row, in file order
        doctrine_rows = []   # round 7: ([row, verdict], compact labels of its doctrineTie lines) per doctrine row
        for r in D.treatments:
            wit = D.witness.get(r['id'])
            claim = D.klass[r['id']][0] if (D.r5 and r['id'] in D.klass) else None
            jl = D.joined.get(r['id'])
            if claim == 'doctrine':
                # round 7 (DESIGN7 §2.4): doctrineBadRow first; then checkJoined in doctrine mode. Lead ruling D7-6
                # (2): a doctrine claim on a witness row fails doctrineBadRow (its joined lines were ignored at
                # load, D7-6 (1)). (3): the labels are the joined lines' `label` column, compacted.
                labels = frozenset(alnum(l[5]) for l in (jl or ()) if l[0] == 'doctrineTie')
                if wit is not None or r['kind'] != 'disapproved' or r['explicit'] != 1 or not labels:
                    res = 'doctrineBadRow'
                else:
                    res = self.check_joined(r, jl, 'doctrine')
            elif claim == 'implicitReject' and r['kind'] not in SOFT_TREAT:
                res = 'implicitBadKind'            # round 9 (DESIGN9 §7; Q9-16): only a soft kind takes the claim
            elif wit is not None and D.has(r['by']) and D.has(r['target']):
                res = self.check_witness(r, wit[0], wit[1])   # (round 7: its joined lines were ignored at load)
            elif jl and wit is None:
                # round 7 (DESIGN7 §2.1): a row with joined lines; no fall-back to the one-quote check
                res = self.check_joined(r, jl, 'operative' if claim == 'operativeWords' else None,
                                        far=claim == 'joinedFar', implicit=claim == 'implicitReject')
                if claim == 'operativeWords':
                    plain = self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'])
            elif claim == 'operativeWords' and wit is None:
                res = self.check_operative(r)      # round 5: a claim on a witness row is ignored (DESIGN5 §1)
                plain = self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'])
            else:
                res = self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'],
                                      extra_cues=IMPLICIT_REJECT if claim == 'implicitReject' else ())
            # fuzz: a row naming an unknown kind or temporal value, or a node with no decisions2 row, asserts
            # nothing (Lean: badRow); it was admitted when only the target's decision was missing, and an empty
            # temporal read as 'unknown'
            if (r['kind'] not in _TKINDS or not _temporal_ok(r['temporal_raw']) or not D.has(r['by'])
                    or not D.has(r['target'])):
                res = 'badRow'
            rtext = None
            if claim == 'recognised' and wit is not None and D.has(r['by']) and D.has(r['target'])                     and res != 'badRow':
                rtext = self._recog_text(r, wit[0], wit[1])
            if D.zone_any:
                # round 9 (DESIGN9 §4, D9-4): the zone check after the complete round-8 verdict; the text owner is
                # W for a witness row, else `by`; a doctrine row after the ambiguity pass below; a row recognised
                # under the full rule set (round-8 verdict okRecognised*) is checked as such and, failing, is
                # `partZone` and not recognised; the plain check of an operativeWords row likewise (not counted)
                zr = self.zone_result(wit[0] if wit is not None else r['by'], r, jl)
                if claim == 'doctrine':
                    pass
                elif rtext and self._recog_rules(r, wit[0]) is not None:
                    if self.zone_count(zr) == 'partZone':
                        self.zone_fail.add(r['id'])
                        res = 'partZone'
                else:
                    res = self.zone_apply(res, zr, self.lean_cert_passes('treatments', r), ('t', r['id']))
                if (claim == 'operativeWords' and wit is None and plain == 'ok' and zr is False
                        and self.lean_cert_passes('treatments', r)):
                    plain = 'partZone'
            self.cert_ok[('treatments.tsv', r['id'])] = res
            self.treat_by_id[r['id']] = r
            entry = [r, res]
            results.append(entry)          # (admitted after the round-7 uniqueness pass, in this order)
            if claim == 'doctrine' and res != 'badRow':
                doctrine_rows.append((entry, labels))
            if claim is not None and res != 'badRow':
                # round 5: a recognised claim counts only on a witness row, an operativeWords claim only on a
                # non-witness row (DESIGN5 §1); a row that does not parse makes no claim
                if claim == 'recognised' and wit is not None and D.has(r['by']) and D.has(r['target']):
                    # (round 9, Q9-4: a witness row failing its zone check is not recognised)
                    self.recog_text[r['id']] = bool(rtext) and r['id'] not in self.zone_fail
                elif claim == 'operativeWords' and wit is None:
                    self.cert_plain[r['id']] = plain   # the round-4 check, for laterCourtSays (ruling on A-21)
                    if res == 'ok':
                        self.op_admitted.add(r['id'])
                        ql = ascii_lower(norm_quote(r['cert'].quote))
                        # §3.3 and §9: `whole` = a phrase of operative_whole AND no phrase of operative_limit
                        if not any(p in ql for p in OPERATIVE_WHOLE) or any(p in ql for p in OPERATIVE_LIMIT):
                            self.demoted.add(r['id'])      # not whole: the scope is demoted
        if doctrine_rows:
            # round 7 (DESIGN7 §2.4, doctrineAmbiguous): after every doctrine row is checked, a compact label that
            # two passing rows share with different targets makes every doctrine row with that label fail. Q7-11:
            # "pass" = the certificate verdict `ok` (power and date order are the status layer's, as for every
            # treatments row); a row that already failed keeps its own reason; a row's labels are those of its
            # doctrineTie lines.
            targets = defaultdict(set)
            for (entry, labels) in doctrine_rows:
                if entry[1] == 'ok':
                    for lb in labels:
                        targets[lb].add(entry[0]['target'])
            amb = {lb for lb, ts in targets.items() if len(ts) > 1}
            for (entry, labels) in doctrine_rows:
                # (differential run 1, Q7-11: the row fails; when its acting decision has no power over the target
                # the reason shown is the Lean's noAuthority, which outranks doctrineAmbiguous; either way the row
                # is not admitted)
                if entry[1] == 'ok' and labels & amb:
                    v = 'noAuthority' if self.can_change(entry[0]['by'], entry[0]['target'],
                                                         self._scope_dom(entry[0]['scope']))[0] == 'no'                         else 'doctrineAmbiguous'
                    entry[1] = v
                    self.cert_ok[('treatments.tsv', entry[0]['id'])] = v
            if D.zone_any:
                # round 9 (DESIGN9 §4, Q9-3): the zone check of a doctrine row comes after the ambiguity pass
                for (entry, labels) in doctrine_rows:
                    v = self.zone_apply(entry[1], self.zone_result(entry[0]['by'], entry[0],
                                                                   D.joined.get(entry[0]['id'])),
                                        self.lean_cert_passes('treatments', entry[0]), ('t', entry[0]['id']))
                    if v != entry[1]:
                        entry[1] = v
                        self.cert_ok[('treatments.tsv', entry[0]['id'])] = v
            for (entry, labels) in doctrine_rows:
                if entry[1] == 'ok':
                    self.demoted.add(entry[0]['id'])   # always demoted: at most a partial scope, never negative
        for (r, res) in results:
            if res == 'ok' and ('t', r['id']) not in self.zone_mute:      # (round 9, D9-13)
                self.adm_treat[r['target']].append(r)
        for r in D.history:
            anc = D.anchor.get(r['id'])
            hc = D.hclaim.get(r['id'])                 # round 7 (DESIGN7 §3): the row's history claims, if any
            brg = D.bridge.get(r['id'])
            if brg is not None:
                # round 8 (DESIGN8 §4): a row with a bridge line is checked by checkBridge, whose last step is the
                # plain check with selfText; an anchor line of the same row is not used (Q8-2)
                res = self.check_bridge(r, brg, hc)
            elif anc is not None and hc and 'trialBridge' in hc and r['kind'] in TBRIDGE_KINDS:
                # round 10 (DESIGN10 §6, D10-8, D10-9; Q10-12, Q10-13): the anchored check with trialBridgeD in the
                # cue's place, then trialBridgeT, then trialBridgeDate (a claim on any other row is ignored)
                res = self.check_anchored(r, anc, hc, tbridge=True)
                if res == 'ok':
                    res = self.check_tbridge(r)
            elif anc is not None:
                res = self.check_anchored(r, anc, hc)  # round 6 (DESIGN6 §4): a row with an anchor line
            else:
                own_text = D.sha.get(r['target']) == r['cert'].sha
                res = self.check_cert(r['cert'], [r['target'], r['by']], r['kind'], not own_text,
                                      target=r['target'], hclaim=hc, by=r['by'])
            if r['kind'] not in _HKINDS or not D.has(r['target']):    # fuzz: as Lean's badRow
                res = 'badRow'
            # round 6, lead ruling on D-1 (round6/history/REF_QUESTIONS.md section C): date order is part of the
            # check of every history row (DESIGN6 §4 step 6): a target dated after the acting decision is
            # `targetLater` (a passed text certificate, canonically) and has no effect. A date of 0 is unknown and
            # counts as ordered; so does an unknown acting decision (by = -1).
            if (res == 'ok' and r['by'] >= 0 and D.has(r['by']) and D.date[r['by']] and D.date[r['target']]
                    and D.date[r['by']] < D.date[r['target']]):
                res = 'targetLater'
            if D.zone_any:
                # round 9 (DESIGN9 §4, D9-4): the main quote only (an anchor or bridge quote is not checked); the
                # text owner is the target when the certificate is the target's own text (as the plain check's
                # own_text), else the acting decision
                owner = r['target'] if D.sha.get(r['target']) == r['cert'].sha else r['by']
                res = self.zone_apply(res, self.zone_result(owner, r, None), self.lean_cert_passes('history', r),
                                      ('h', r['id']))
            rm = D.remand.get(r['id'])
            if rm is not None and res == 'ok':
                # round 10 (DESIGN10 §4, D10-6): after the complete round-9 verdict. A row the Lean admits (power
                # not `no`) is checked and counted; a failure is its reason. A row the Lean writes noAuthority (the
                # reference's ok) keeps its verdict, is not counted, and feeds no findings when the check fails
                # (Q10-10, as D9-13).
                rr = self.check_remand(r, rm)
                if self.lean_cert_passes('history', r):
                    self.remand_checked += 1
                    if rr != 'ok':
                        self.remand_failed += 1
                        res = rr
                elif rr != 'ok':
                    self.remand_mute.add(('h', r['id']))
            idl = D.identity.get(r['id'])
            if idl is not None and res == 'ok' and ('h', r['id']) not in self.remand_mute:
                # round 11 (DESIGN11 §5.2, D11-5): after the complete round-10 verdict, as the remand check: a row
                # the Lean admits is checked and counted, a failure is its reason; a row the Lean writes
                # noAuthority keeps its verdict, is not counted, and feeds no findings when the check fails.
                ri = self.check_identity(r, idl)
                if self.lean_cert_passes('history', r):
                    self.identity_checked += 1
                    if ri != 'ok':
                        self.identity_failed += 1
                        res = ri
                elif ri != 'ok':
                    self.remand_mute.add(('h', r['id']))
            self.cert_ok[('history.tsv', r['id'])] = res
            if (res == 'ok' and ('h', r['id']) not in self.zone_mute               # (round 9, D9-13)
                    and ('h', r['id']) not in self.remand_mute):                    # (round 10, Q10-10)
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
        if D.r5:
            self._build_recog()
            self.recog_all.update(self.recog)
            self._build_classes()

    def share_admission(self, other):
        for a in ('cert_ok', 'adm_hist', 'adm_treat', 'treat_by_id', 'adm_holdings', 'adm_holdings_by_node',
                  'sup_by_target', 'linked_treat', 'recog_text', 'recog_all', 'row_class', 'demoted',
                  'op_admitted', 'cert_plain'):
            setattr(self, a, getattr(other, a))
        if self.D.r5:
            self._build_recog()     # round 5: recognition is decided per rule set (DESIGN5 §2.2)

    def same_case_power(self, B, X, claims=None):
        """R25 (§5.1 A, T1(a), H3, F1). A same-case event acts on X's own judgment or opinion, so it is decided by
        X's court itself (withdrawal, substitution, rehearing, reinstatement: any bench), a successor of X's court,
        a court that reviews X: a higher court of X's system (in the federal system, X's own circuit, or the
        Federal Circuit, which hears appeals from every district court and the Court of Federal Claims), or SCOTUS
        (federal decisions, and state decisions on federal questions). -> 'yes' | 'no' | 'unknown' (deciding
        decision or an epoch unknown: admitted, like a row with by = -1).
        claims (round 8, DESIGN8 §6): the history row's claims; with `oldCircuit` a federal court of appeals of
        circuit a also reviews a federal district (tier T) or bankruptcy (tier S) court of circuit b when the acting
        decision is dated (decisions2, 0 fails) before d, for each (a, b, d) of `old_circuit` (REF_QUESTIONS8 Q8-14).
        Without the claim the test is the round-7 one."""
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
        if (claims and 'oldCircuit' in claims and be.system == 0 and xe.system == 0 and be.tier == 'A'
                and xe.tier in ('T', 'S') and D.date[B] != 0
                and any(be.circuit == a and xe.circuit == b and D.date[B] < d for (a, b, d) in OLD_CIRCUIT)):
            return 'yes'          # round 8 (DESIGN8 §6): the old Fifth / Eighth Circuit, claim-gated
        return 'no'

    def hist_rows(self, node):
        """Admitted same-case history of `node` (certificate passed) whose deciding court may act on it (R25)."""
        return [r for r in self.adm_hist.get(node, ())
                if self.same_case_power(r['by'], node, self.D.hclaim.get(r['id'])) != 'no']

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

    def _hist_effects(self, node, keyset):
        """Part A of `effects`: the same-case history effects, before empty intervals are dropped."""
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
        return E

    def _app_power(self, r, node, keyset):
        """How a status-changing treatment row reaches an issue set of `node`, and the treating decision's power
        there: (scope_applies value, issue domain, can_change result), or None when the scope does not reach it."""
        B = r['by']
        app = self.scope_applies(r['scope'], keyset)
        if app == 'none':
            return None
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
        return app, dom, pw

    def _first_lapse(self, B, frm):
        """Round 5 (DESIGN5 §2.3 and §9, ruling on A-14): the date of the earliest lapse event of decision B dated
        on or after `frm` (whole-decision withdrawn, vacated, substituted, depublished or reversed, or an en banc
        grant that vacates under B's own court's rule; the events of R15); OPEN when there is none. An event dated
        before `frm` is ignored, even if nothing reinstated B since. An event undone on its own day (an empty
        interval) is not a lapse."""
        self._overruler_lapsed(B, 0)
        return min([e[0] for e in self._tl[('lapse', B)] if e[0] >= frm] or [OPEN])

    def _tdate(self, r):
        """The event date of a treatments row: the by-decision's decisions2 date (0 = unknown)."""
        B = r['by']
        return self.D.date[B] if self.D.has(B) else 0

    def effects(self, node, keyset):
        D = self.D
        E = self._hist_effects(node, keyset)
        # B. later-case treatments (§5.1 B, T1, T2, T3, F14, TM2)
        # DESIGN5 §9 (ruling on A-7): the event date of every treatments row is the by-decision's decisions2 date; the
        # row's own date column is never used. (Before round 5 it was used when non-zero. The two agree in every
        # universe generated before round 5 and on the real data, so no earlier output changes.)
        for r in sorted(self.adm_treat.get(node, ()), key=lambda r: (self._tdate(r), str(r['id']))):
            k = r['kind']
            B = r['by']
            dt = self._tdate(r)
            if dt == 0:
                continue
            if k in NEG_TREAT:
                ap = self._app_power(r, node, keyset)
                if ap is None:
                    continue
                app, dom, pw = ap
                if pw[0] == 'no':
                    continue                 # T2: a claim, not a status change (kept for findings)
                if r['explicit'] != 1:
                    continue                 # R26 (§9.26): an inferred treatment never proves status (atRisk only)
                if self.r5 and app == 'full' and r['id'] in self.demoted:
                    # round 5 (DESIGN5 §3.3): operative words without a whole-case phrase. The event's scope is
                    # demoted (all -> someIssue, issues ks -> someOf ks): the whole decision is reached in part,
                    # a holding in scope is reached or not, unknown which. Never a negative.
                    app = 'partial' if keyset is None else 'unknownScope'
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
                    eff = [dt, OPEN, cf, ct, st, kd, str(B), (B, depkeys), reach]
                    if self.r5:
                        eff.append(self.row_class.get(r['id']))   # element 9: the row's class (DESIGN5 §5.1)
                    E.append(eff)
            # R27 (c): a supersededByEnactment *treatment* is evidence, not the event (T1(d): legislation changes
            # status). Without a supersessions row joining it to a law change there is no effective date, no
            # retroactivity and no amended block (AB1), so it changes nothing; with one, that row carries it.
        # B2. round 5 (DESIGN5 §2.3, R5-3): a witness row recognised under this rule set. For each event an
        # explicit row by Y with the same scope would yield here (same reach of the issue set, same power test,
        # same conduct range, same lines), two effects with actor Y: e1 from date(Y), `unknown recognisedLater`
        # (power known) until Y first lapses; e2 from date(W), the negative of the row's kind, until Y or W first
        # lapses. With power unknown both are `unknown power`. No revival: the ends are fixed dates, and the
        # effects carry no dependency on Y (element 7 is None). date(Y) and date(W) are the decisions2 dates, for
        # the starts, the conduct range, the lapse search and the lines (DESIGN5 §9, ruling on A-7).
        if self.r5:
            for (r, W) in sorted(self.recog_by_target.get(node, ()), key=lambda x: (self._tdate(x[0]), str(x[0]['id']))):
                k, Y = r['kind'], r['by']
                dt = dy = D.date[Y]
                ap = self._app_power(r, node, keyset)
                if ap is None:
                    continue
                app, dom, pw = ap
                if pw[0] == 'no':
                    continue
                if pw[0] == 'yes':
                    s1, s2 = (UNK, 'recognisedLater'), ('negative', k)
                else:
                    s1 = s2 = (UNK, 'power:' + pw[1])
                if app == 'partial':
                    s1, s2 = (s1[0], s1[1] + ':partial'), (s2[0], s2[1] + ':partial')
                elif app in ('unknownScope', 'otherGrounds'):
                    s1 = s2 = (UNK, app + ':' + k)
                reach = self._reach(node, Y, dt)
                dw = D.date[W]
                end1 = self._first_lapse(Y, dy)
                end2 = min(end1, self._first_lapse(W, dw))
                for (cf, ct, ov) in self.temporal_ranges(r['temporal'], dt, dom):
                    E.append([dy, end1, cf, ct, s1[0], s1[1], str(Y), None, reach, 'recognised'])
                    E.append([dw, end2, cf, ct, s2[0], s2[1], str(Y), None, reach, 'recognised'])
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
                if self._plain(tid) != 'ok':    # (round 5: the round-4 check of the row, ruling on A-21)
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

    @staticmethod
    def _contrib(st, kind):
        """Round 5: an effect state in the status vocabulary of the Lean output (see STATUS_KIND, UNK_RANK)."""
        if st == 'negative' and not kind.endswith(':partial'):
            b = kind.split(':')[0]
            return ('neg', STATUS_KIND.get(b, b))
        if kind.endswith(':partial') or kind.startswith('unknownScope:') or kind.startswith('otherGrounds:'):
            return ('unknown', 'partialScope')
        if kind == 'recognisedLater':
            return ('unknown', 'recognisedLater')
        if kind.startswith('power:'):
            return ('unknown', 'powerUnknown')
        if kind.startswith('enBancGrantVacatesPanel'):
            return ('unknown', 'enBancRuleUnknown')
        return ('unknown', kind)

    def _with_oclass(self, s, live):
        """Round 5 (DESIGN5 §5.1): the state with a fourth element `oclass`: the least class among the live effects
        of a treatments row (explicit or recognised) whose contribution equals the status; '-' when there is none
        (good law, or a status made by same-case history or a supersession alone)."""
        if s[0] == 'none':
            return s + ('-',)
        if s[0] == 'negative' and not s[1].endswith(':partial'):
            top = self._contrib(s[0], s[1])
        else:       # no whole negative is live: the status is the most severe unknown contribution
            top = max((self._contrib(e[4], e[5]) for e in live), key=lambda c: UNK_RANK.get(c[1], 0))
        cs = [e[9] for e in live if len(e) > 9 and e[9] and self._contrib(e[4], e[5]) == top]
        return s + (min(cs, key=lambda c: CLASS_ORDER[c]) if cs else '-',)

    def _eval(self, effs, t, u):
        best_neg = None
        best_unk = None
        best_part = None
        live = [] if self.r5 else None
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
            if live is not None:
                live.append(e)
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
        res = (best_neg or best_unk or best_part or (None, ('none', '-', '-')))[1]
        return res if live is None else self._with_oclass(res, live)

    def _overruler_lapsed(self, B, t):
        """R15: has decision B's opinion been withdrawn, substituted, vacated, depublished or reversed, as a whole,
        by an admitted same-case event on or before t (and not reinstated since)?"""
        key = ('lapse', B)
        effs = self._tl.get(key)
        if effs is None:
            # (round 5: read from the history part alone, which is where every such effect comes from; a
            # recognised row on B asks for the lapse of other decisions and must not come back here)
            effs = self._tl[key] = [e for e in self._hist_effects(B, None) if e[0] < e[1] and e[7] is None
                                    and e[4] == 'negative' and not e[5].endswith(':partial')
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
        if self.r5:
            t |= set(self.recog_by_target)    # a recognised row need not pass the round-4 witness check
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
                            rows.append((node, issue, hid, f1, t1, s[0], s[1], s[2], c) + tuple(s[3:]))
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
                                rows.append((node, issue, hid, f1, t1, s[0], s[1], s[2], c, line) + tuple(s[3:]))
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
    def _f(self, kind, C, X, detail, oclass='-'):
        """A finding row. Round 5 (DESIGN5 §5.1): a fifth element `oclass`; without the class table, as before."""
        return (kind, C, X, detail, oclass) if self.r5 else (kind, C, X, detail)

    @staticmethod
    def _oc(s):
        """The oclass of a status state ('-' for a three-element state: round 4, or the cycle sentinel)."""
        return s[3] if len(s) > 3 else '-'

    def _cites_recognised_later(self, C, X, t):
        """Round 5 (DESIGN5 §2.5, R5-4): C (decided t) cites X while X, as a whole decision and in C's line, is
        `unknown recognisedLater` on (t, t), and that is not C's own doing: not every live recognisedLater effect
        has C as its actor (the test of `_only_by`, on the unknown)."""
        top = self.status_citing(C, X, None, t, t)
        if top[0] != UNK or top[1] != 'recognisedLater':
            return False
        effs = self._cite_effects(C, X, None)
        if effs is None:
            effs = self.effects(X, None)
        bys = {e[6] for e in effs if e[4] == UNK and e[5] == 'recognisedLater'
               and e[0] <= t < e[1] and e[2] <= t < e[3]}
        return bys != {str(C)}

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
                out.add(self._f('atRisk', C, X, 'citesLaterNegated:' + ln[0], ln[1]))
            if self.r5 and self._cites_recognised_later(C, X, t):
                out.add(self._f('atRisk', C, X, 'recognisedLater', 'recognised'))
        # treatment-based findings
        for X, trs in self.adm_treat.items():
            for r in trs:
                C = r['by']
                if not D.has(C) or not D.has(X):
                    continue
                k = r['kind']
                t = D.date[C]
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
                            out.add(self._f('citesUnpublishedAsBinding', C, X, f[0] if f[0] != UNK else '<=' + up))
                    if FORM[D.form[X]] == 'plurality' and X not in self.marks_nodes:
                        base = self._authority_as_majority(X, D.court[C], t, D.unit[C], D.extra.get(C))
                        if base[0] == 'binding':
                            out.add(self._f('pluralityTreatedAsBinding', C, X, 'noMarks'))
                wrow = r['id'] in D.witness     # round 4: the words are a later court's: atRisk only
                # round 4 (DEVIATIONS 84): the panel finding needs the panel's own overruling words
                own = any(v in ascii_lower(norm_quote(r['cert'].quote)) for v in PANEL_OWN_WORDS)
                if k in NEG_TREAT and own and not wrow:       # (c) a decline to follow is not a purported overruling
                    pd = self._panel_departs(C, X, r)
                    if pd:
                        out.add(self._f('panelDepartsWithoutEnBanc', C, X, pd, self.row_class.get(r['id'], '-')))
                if (k in NEG_TREAT or k == 'declinedToFollow') and not wrow and self._ignores_binding_in_unit(C, X, r):
                    out.add(self._f('ignoresBindingInUnit', C, X, k, self.row_class.get(r['id'], '-')))
        for f in self.at_risk():
            out.add(f)
        return out

    def _ignores_binding_in_unit(self, B, X, r):
        """L1 (five limits; §9.27 "a trial court departs from its own unit, ownUnit rules"; §4.1 V, §4.3, §4.4, T2): a
        trial-level court B declines to follow (or purports to overrule) a good-law decision X that binds it through
        its own unit (an intermediate court of B's unit under trialScope ownUnitThenAny / ownUnitOnly) or its own court
        (the appellate division of B's trial court and unit, §4.4), B having no power over X."""
        D = self.D
        t = D.date[B]
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
        change or an unknown deciding decision is not a court that binds C. -> (the reported kind, the oclass of
        the as-of status read: round 5), or None."""
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
                return (top[1].split(':')[0], self._oc(top))
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
            top = (top[0], top[1], '-') + tuple(top[3:])     # another decision's effect makes the same status
        sup_only = False
        if top[0] == 'negative' and top[2] != str(C) and not top[1].endswith(':partial'):
            base = top[1].split(':')[0]
            fk = self._finding_kind(base)
            if fk:
                res.append(self._f(fk, C, X, '%s:%s' % (base, top[2]), self._oc(top)))
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
                    res.append(self._f('atRisk', C, X, 'supersededConductUnknown:' + h['issue']))
            if sup_only:
                return res
            if cis:
                for (h, s) in states:
                    if h['issue'] in cis and s[0] == 'negative' and s[2] != str(C):
                        fk = self._finding_kind(s[1].split(':')[0])
                        if fk:
                            res.append(self._f(fk, C, X, '%s:%s:%s' % (s[1].split(':')[0], s[2], h['issue']),
                                               self._oc(s)))
            elif all(s[0] == 'negative' and s[2] != str(C) for (_, s) in states):
                for (h, s) in states:
                    fk = self._finding_kind(s[1].split(':')[0])
                    if fk:
                        res.append(self._f(fk, C, X, '%s:%s:allHoldings' % (s[1].split(':')[0], s[2]),
                                           self._oc(s)))
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
        bd = D.date[B]
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
                t = self._tdate(r)
                if t == 0:
                    continue
                if D.has(C) and D.has(X) and D.date[C] < D.date[X]:
                    continue             # T1: an earlier decision cannot treat a later one (a data error, not a risk)
                st0 = self.status_view(X, None, t, t, self._view_of(C))   # R2-76: in the treating court's view
                if st0[0] == 'negative' and not st0[1].endswith(':partial'):
                    continue             # already wholly negative (a partial event leaves the rest at risk)
                if k in SOFT_TREAT:
                    out.append(self._f('atRisk', C, X, 'soft:' + k))
                elif k in NEG_TREAT:
                    pw = self.can_change(C, X, 'unknown')
                    if pw[0] == 'no':
                        if r['id'] not in D.witness:
                            out.append(self._f('atRisk', C, X, 'claim:' + k, self.row_class.get(r['id'], '-')))
                    elif r['explicit'] != 1:
                        # round 5 (DESIGN5 §2.5): a row recognised under the full rule set emits no
                        # inferredRejection: its status rows carry it (recog_all is empty without the class table)
                        if r['id'] not in self.recog_all:
                            out.append(self._f('atRisk', C, X, 'inferred:' + k, self.row_class.get(r['id'], '-')))
        for X, sups in self.sup_by_target.items():
            for s in sups:
                ev = s['evidence']
                if ev.startswith('laterCourtSays:') and self._plain(ev.split(':', 1)[1]) != 'ok':
                    continue             # the court's words it rests on are not certified
                if s['explicit'] != 1 and s['lc'] in D.lawchanges:
                    out.append(self._f('atRisk', 'lc:' + s['lc'], X, 'possiblySuperseded'))
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
                    out.append(self._f('atRisk', Y, X, 'contraryBinding:' + y['id']))
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
    # (round 5: a recognised row's verdict is okRecognised / okRecognisedUnverifiedBy; cert_verdict is the round-4
    # string for every other row and for every row without the class table)
    write_tsv(os.path.join(args.out, 'certs.tsv'),
              [(f, i, A.cert_verdict(f, i) if D.r5 else r)
               for (f, i), r in sorted(A.cert_ok.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))])
    if D.r5:
        # round 5 (DESIGN5 §5.1): classes.tsv, one line per treatments row of a status-changing kind that parses:
        # id, class, claim, verdict (as in certs.tsv), field_limit, doctrine, W's node
        crows = []
        for rid in sorted(A.row_class, key=str):
            v = A.cert_verdict('treatments.tsv', rid)
            if v == 'badRow':
                continue
            c = D.klass.get(rid)
            w = D.witness.get(rid)
            crows.append((rid, A.row_class[rid], c[0] if c else '-', v, c[1] if c else '-', c[2] if c else '-',
                          w[0] if w else '-'))
        write_tsv(os.path.join(args.out, 'classes.tsv'), crows)
    # status
    rows = A.status_rows(Fm)

    def firm_of(r):
        # D2: firm = the S/L-only tables give the same verdict, read at the row's first point (asOf from, conduct
        # conduct_from), as the Lean does; not row identity, which also depends on where the firm run segments
        if Fm is None:
            return 1
        node, issue, hid, f, to, st, kind, by, c = r[:9]
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
        node, issue, hid, f, to, st, kind, by, c, line = r[:10]
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
        # (round 5, DESIGN5 §9, ruling on A-19: unchanged; `recognisedLater` is an unknown like any other here)
        return (st if not kind.endswith(':partial') else 'partial',)
    # (round 5: a row carries its oclass as a last element; it is written after firm, and after line)
    write_tsv(os.path.join(args.out, 'status.tsv'), [r[:9] + (firm_of(r),) + r[9:] for r in rows])
    log('status: %d rows (%.1fs)' % (len(rows), time.time() - t0))
    # R2-75: status per line of authority (always written; empty when no decision has a line-limited effect)
    lrows = A.line_rows(Fm)
    write_tsv(os.path.join(args.out, 'status_lines.tsv'), [r[:9] + (firm_of_line(r), r[9]) + r[10:] for r in lrows])
    log('status_lines: %d rows (%.1fs)' % (len(lrows), time.time() - t0))
    # findings
    targets = set()
    for r in rows:
        if r[5] == 'negative':
            targets.add(str(r[0]))
    if D.r5:
        # round 5: a decision under a recognised row may be `unknown recognisedLater` and never negative (Y lapsed
        # before W spoke); citations of it are read too (atRisk recognisedLater)
        targets |= {str(x) for x in A.recog_by_target} | ({str(x) for x in Fm.recog_by_target} if Fm else set())
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
    # (round 5: a finding carries its oclass as a fifth element; it is written after firm)
    write_tsv(os.path.join(args.out, 'findings.tsv'),
              [f[:4] + ((1 if fkey(f) in fkeys else 0),) + f[4:]
               for f in sorted(fa, key=lambda f: tuple(str(x) for x in f))])
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
    for (f, i), v in A.cert_ok.items():
        cnt['cert_' + (A.cert_verdict(f, i) if D.r5 else v)] += 1    # (round 5: the verdict certs.tsv shows)
    stats += sorted(cnt.items())
    if D.r5:
        # round 5 (DESIGN5 §5.1): the four extra summary lines (NOTES.md A-4 for what each counts)
        # operative_rows (ruling on A-4): the claim is admitted under the full rule set, i.e. the text checks pass
        # and the acting decision's power over the target is not shown absent (the Lean's ok / okUnverifiedBy)
        nop = sum(1 for i in A.op_admitted
                  if A.can_change(A.treat_by_id[i]['by'], A.treat_by_id[i]['target'],
                                  A._scope_dom(A.treat_by_id[i]['scope']))[0] != 'no')
        stats += [('class_rows', len(D.klass)), ('class_bad_rows', D.class_bad),
                  ('recognised_rows', len(A.recog_all)), ('operative_rows', nop)]
    if D.anchor or D.anchor_bad or D.anchor_unknown or D.anchor_dup:
        # round 6 (DESIGN6 §4): only when history_anchor.tsv has a line (absent or empty: the file is as before).
        # anchor_rows = history ids with an anchor; the other three = lines ignored, by reason (REF_QUESTIONS
        # Q-1..3, Q-11). The first three names are the Lean summary's; anchor_bad_rows is its
        # `bad_rows <tab> history_anchor.tsv <tab> n` line (diff.py maps it).
        stats += [('anchor_rows', len(D.anchor)), ('anchor_unknown_ids', D.anchor_unknown),
                  ('anchor_duplicates', D.anchor_dup), ('anchor_bad_rows', D.anchor_bad)]
    if D.joined_any:
        # round 7 (DESIGN7 §1): only when joined.tsv has a line. joined_rows = treatments ids with a kept line;
        # joined_bad_rows is the Lean's `bad_rows <tab> joined.tsv <tab> n` (diff.py maps it); Q7-2, Q7-14
        stats += [('joined_rows', len(D.joined)), ('joined_unknown_ids', D.joined_unknown),
                  ('joined_extra', D.joined_extra), ('joined_history_ignored', D.joined_hist),
                  ('joined_witness_ignored', D.joined_wit),
                  ('joined_bad_rows', D.joined_bad)]
    if D.hclaim_any:
        # round 7 (DESIGN7 §1): only when history_claim.tsv has a line; hclaim_bad_rows is the Lean's
        # `bad_rows <tab> history_claim.tsv <tab> n`; Q7-3, Q7-14
        stats += [('hclaim_rows', len(D.hclaim)), ('hclaim_unknown_ids', D.hclaim_unknown),
                  ('hclaim_duplicates', D.hclaim_dup), ('hclaim_bad_rows', D.hclaim_bad)]
        if any('anchorWide' in c for c in D.hclaim.values()):
            # round 8 (DESIGN8 §5; Q8-11): history ids with an anchorWide claim whose row is not checked by
            # checkAnchored (no anchor line, or a bridge line, which takes the row: Q8-2). Written only when some
            # line has the claim, so round-7 summaries do not move.
            stats.append(('hclaim_anchorwide_unused', sum(1 for i, c in D.hclaim.items() if 'anchorWide' in c
                                                          and (i not in D.anchor or i in D.bridge))))
        if any('anchorTribunal' in c for c in D.hclaim.values()):
            # round 11 (DESIGN11 §5.1; REF_QUESTIONS11 Q11-4): ids with the claim, and those of them whose row is
            # not checked by checkAnchored (as hclaim_anchorwide_unused). Only when some kept line has the claim.
            stats.append(('hclaim_anchortribunal', sum(1 for c in D.hclaim.values() if 'anchorTribunal' in c)))
            stats.append(('hclaim_anchortribunal_unused', sum(1 for i, c in D.hclaim.items()
                                                              if 'anchorTribunal' in c
                                                              and (i not in D.anchor or i in D.bridge))))
    if D.bridge_any:
        # round 8 (DESIGN8 §4): only when history_bridge.tsv has a line. bridge_rows = history ids with a kept line;
        # bridge_bad_rows is the Lean's `bad_rows <tab> history_bridge.tsv <tab> n` (diff.py maps it); Q8-1, Q8-9
        stats += [('bridge_rows', len(D.bridge)), ('bridge_unknown_ids', D.bridge_unknown),
                  ('bridge_duplicates', D.bridge_dup), ('bridge_bad_rows', D.bridge_bad)]
    if D.zone_any:
        # round 9 (DESIGN9 §4): only when part_zone.tsv has a line. zone_bad_rows is the Lean's `bad_rows <tab>
        # part_zone.tsv <tab> n` (diff.py maps it); the row counters count rows whose round-8 verdict is ok (Q9-9)
        stats += [('zone_nodes', len(D.zones)), ('zone_lines', D.zone_lines), ('zone_bad_nodes', D.zone_bad_nodes),
                  ('zone_bad_rows', D.zone_bad), ('zone_checked_rows', A.zone_checked),
                  ('zone_failed_rows', A.zone_failed), ('zone_missing_rows', A.zone_missing)]
    if D.tbridge_any:
        # round 10 (DESIGN10 §6, Q10-17): only when history_tbridge.tsv has a line; tbridge_bad_rows is the Lean's
        # `bad_rows <tab> history_tbridge.tsv <tab> n`
        stats += [('tbridge_lines', len(D.tbridge)), ('tbridge_dup_rows', D.tbridge_dup),
                  ('tbridge_bad_rows', D.tbridge_bad)]
    if D.remand_any:
        # round 10 (DESIGN10 §4, D10-6 / Q10-9): only when history_remand.tsv has a line. remand_bad_rows is the
        # Lean's `bad_rows <tab> history_remand.tsv <tab> n` (diff.py maps it); remand_lines = ids kept; the row
        # counters count rows the Lean admits (round-9 verdict ok, power not `no`) that reach the check
        stats += [('remand_lines', len(D.remand)), ('remand_checked_rows', A.remand_checked),
                  ('remand_failed_rows', A.remand_failed), ('remand_dup_rows', D.remand_dup),
                  ('remand_bad_rows', D.remand_bad)]
    if D.identity_any:
        # round 11 (DESIGN11 §5.2): only when history_identity.tsv has a line. identity_bad_rows is the Lean's
        # `bad_rows <tab> history_identity.tsv <tab> n` (diff.py maps it); identity_lines = ids kept
        stats += [('identity_lines', len(D.identity)), ('identity_checked_rows', A.identity_checked),
                  ('identity_failed_rows', A.identity_failed), ('identity_dup_rows', D.identity_dup),
                  ('identity_bad_rows', D.identity_bad)]
    if D.r5 and any(c[0] == 'doctrine' for c in D.klass.values()):
        # round 7 (Q7-14; names as the Lean summary's, seen in the first differential run): doctrine_rows = class
        # lines kept with the claim `doctrine`; doctrine_admitted = doctrine rows admitted under the full rule set
        # (text checks pass, power not shown absent), as operative_rows
        ndoc = sum(1 for i in A.demoted if A._doctrine_claim(A.treat_by_id[i])
                   and A.can_change(A.treat_by_id[i]['by'], A.treat_by_id[i]['target'],
                                    A._scope_dom(A.treat_by_id[i]['scope']))[0] != 'no')
        stats += [('doctrine_rows', sum(1 for c in D.klass.values() if c[0] == 'doctrine')),
                  ('doctrine_admitted', ndoc)]
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
