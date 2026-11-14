#!/usr/bin/env python3
"""gen.py - random small SCHEMA-conformant universes for differential random testing (DESIGN D4).

Each universe has courts (SCOTUS, regional circuits, the Federal Circuit, districts, the Tax Court, and state
systems with dual or changing last-resort courts, intermediate courts with units and trial courts), successions,
adoptions, dated system rules (tags S/L/U), decisions with bench/publication/form, issues, holdings, Marks rows,
treatments, same-case history, law changes and supersessions, with real decision texts so every certificate
can be checked, some deliberately broken (wrong offsets, sha, part, missing verb or target). Plus citation edges.
Round 5 (r5_layer; off with --no-r5): witness rows with treatment_witness.tsv, and treatment_class.tsv (absent in
about one universe in eight) with recognised and operativeWords claims that pass and fail each step, and bad rows.

  python gen.py --seed 1 --out DIR                 # one universe: DIR/data/*.tsv, DIR/edges/edges-00.tsv
  python gen.py --seed 1 --rounds 50 --out DIR --ref [--lean] [--diff]
        per round: generate, run precedent_ref.py, optionally run_lean.sh, and diff.py (needs --lean)
  python gen.py --big 6900000 --out DIR            # scale test: decisions2.tsv of N rows on a fixture skeleton
"""
import argparse
import hashlib
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN = 99999999
WORK = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2')

TREAT_KINDS = ['overruled'] * 6 + ['disapproved', 'recededFrom', 'abrogated'] * 2 + [
    'supersededByEnactment', 'limited', 'questioned', 'criticized', 'distinguished', 'followed', 'followed',
    'declinedToFollow']
HIST_KINDS = ['affirmed', 'reversed', 'vacated', 'vacated', 'modified', 'remanded', 'certDenied', 'reviewGranted',
              'reviewDismissed', 'depublished', 'withdrawn', 'withdrawn', 'substitutedBy',
              'rehearingEnBancGranted', 'reinstated', 'writRefused', 'other']
VERB_TEXT = {
    'overruled': 'is overruled', 'disapproved': 'is disapproved', 'recededFrom': 'we recede from it',
    'abrogated': 'has been abrogated', 'supersededByEnactment': 'was superseded by statute',
    'limited': 'is limited to its facts', 'questioned': 'is questioned', 'criticized': 'is criticized',
    'distinguished': 'is distinguished', 'followed': 'is followed as binding', 'declinedToFollow':
        'we decline to follow it', 'affirmed': 'is affirmed', 'reversed': 'is reversed', 'vacated': 'is vacated',
    'modified': 'is modified', 'remanded': 'is remanded', 'certDenied': 'certiorari denied',
    'reviewGranted': 'review granted', 'reviewDismissed': 'review dismissed', 'depublished':
        'is depublished', 'withdrawn': 'is withdrawn', 'substitutedBy': 'is substituted on rehearing',
    'rehearingEnBancGranted': 'rehearing en banc granted', 'reinstated': 'is reinstated',
    'writRefused': "writ refused", 'other': 'noted',
}
WORDS = ['Abel', 'Baker', 'Carter', 'Dalton', 'Ellis', 'Foster', 'Garcia', 'Hughes', 'Irwin', 'Jensen', 'Keller',
         'Lowry', 'Morgan', 'Nolan', 'Ortiz', 'Pruitt', 'Quinn', 'Reyes', 'Sutton', 'Tate', 'Upton', 'Vance',
         'Walsh', 'Young', 'Zeller']


def rdate(R, lo=1900, hi=2022):
    return R.randint(lo, hi) * 10000 + R.randint(1, 12) * 100 + R.randint(1, 28)


def add_days(d, n):
    import datetime
    x = datetime.date(d // 10000, d // 100 % 100, d % 100) + datetime.timedelta(days=n)
    return x.year * 10000 + x.month * 100 + x.day


def day_after(d):
    """The day after d; d itself need not be a real date (a cut-off written as `split - 1`): then the first of the
    next month."""
    try:
        return add_days(d, 1)
    except ValueError:
        y, m = d // 10000, max(1, min(12, d // 100 % 100))
        return (y + (m == 12)) * 10000 + (1 if m == 12 else m + 1) * 100 + 1


def tag(R):
    x = R.random()
    return 'S' if x < 0.6 else ('L' if x < 0.88 else 'U')


def courts(R):
    rows = []
    split = rdate(R, 1950, 1990)
    ky_change = rdate(R, 1960, 1990)
    add = lambda *a: rows.append(list(a))
    add(2906, 0, OPEN, 'Supreme Court of the United States', 0, 'L', 'all', 0, 0, 'gen', 'S')
    add(101, 0, OPEN, 'United States Court of Appeals for the First Circuit', 0, 'A', '-', 1, 0, 'gen', 'S')
    add(102, split, OPEN, 'United States Court of Appeals for the Second Circuit', 0, 'A', '-', 2, 0, 'gen', 'S')
    add(113, 19821001, OPEN, 'United States Court of Appeals for the Federal Circuit', 0, 'A', '-', 13, 0, 'gen',
        'S')
    add(201, 0, OPEN, 'United States District Court for the District of Maine', 0, 'T', '-', 1, 0, 'gen', 'S')
    add(202, 0, OPEN, 'United States District Court for the District of Vermont', 0, 'T', '-', 2, 0, 'gen', 'S')
    add(203, 0, OPEN, 'United States Court of Federal Claims', 0, 'S', '-', 13, 0, 'gen', tag(R))
    add(301, 0, OPEN, 'United States Tax Court', 0, 'S', '-', 0, 0, 'gen', 'S')
    add(401, 0, OPEN, 'Supreme Judicial Court of Maine', 20, 'L', 'all', 0, 0, 'gen', 'S')
    add(402, 0, OPEN, 'Maine Superior Court', 20, 'T', '-', 0, 1, 'gen', 'S')
    add(501, 0, OPEN, 'Supreme Court of California', 5, 'L', 'all', 0, 0, 'gen', 'S')
    add(502, 19050101, OPEN, 'California Court of Appeal', 5, 'A', '-', 0, 0, 'gen', 'S')
    add(503, 0, OPEN, 'Superior Court of California, Alpha County', 5, 'T', '-', 0, 1, 'gen', 'S')
    add(504, 0, OPEN, 'Superior Court of California, Beta County', 5, 'T', '-', 0, 2, 'gen', tag(R))
    add(505, 0, OPEN, 'Appellate Division of the Superior Court of California, Alpha County', 5, 'D', '-', 0, 1,
        'gen', 'L')
    add(601, 0, ky_change - 1, 'Court of Appeals of Kentucky', 17, 'L', 'all', 0, 0, 'gen', 'S')
    add(601, ky_change, OPEN, 'Court of Appeals of Kentucky', 17, 'A', '-', 0, 0, 'gen', 'S')
    add(602, ky_change, OPEN, 'Supreme Court of Kentucky', 17, 'L', 'all', 0, 0, 'gen', 'S')
    add(603, 0, OPEN, 'Kentucky Circuit Court', 17, 'T', '-', 0, 1, 'gen', 'S')
    add(701, 0, OPEN, 'Supreme Court of Texas', 44, 'L', 'civil', 0, 0, 'gen', 'S')
    add(702, 0, OPEN, 'Court of Criminal Appeals of Texas', 44, 'L', 'criminal', 0, 0, 'gen', 'S')
    add(703, 0, OPEN, 'Court of Appeals of Texas, First District', 44, 'A', '-', 0, 1, 'gen', 'S')
    add(704, 0, OPEN, 'Court of Appeals of Texas, Second District', 44, 'A', '-', 0, 2, 'gen', 'S')
    add(705, 0, OPEN, 'Texas District Court', 44, 'T', '-', 0, 1, 'gen', 'S')
    succ = [[601, 602, ky_change, 'replace', 'gen', 'S']]
    adopt = [[102, 101, split - 1, 'all', 'binding', 'gen', tag(R)],
             [102, 101, OPEN, 'unitB', 'binding', 'gen', tag(R)],
             [601, 601, ky_change - 1, 'all', 'binding', 'gen', 'S']]
    if R.random() < 0.5:
        adopt.append([113, 203, 19820930, 'all', 'binding', 'gen', 'L'])
    return rows, succ, adopt, split, ky_change


def system_rules(R):
    rows = []
    H = ['strong', 'soft', 'none', 'withinUnitOnly']
    TS = ['statewide', 'statewideChooseOnConflict', 'ownUnitThenAny', 'ownUnitOnly']
    F = ['binding', 'persuasive', 'citableNoWeight', 'notCitable']
    for s in (0, 5, 17, 20, 44):
        if R.random() < 0.9:
            if R.random() < 0.3:
                cut = rdate(R, 1950, 2010)
                rows.append([s, 'horizontal', R.choice(H), 0, cut - 1, 'gen', tag(R)])
                rows.append([s, 'horizontal', R.choice(H), cut, OPEN, 'gen', tag(R)])
            else:
                rows.append([s, 'horizontal', R.choice(H), 0, OPEN, 'gen', tag(R)])
        if s and R.random() < 0.85:
            rows.append([s, 'trialScope', R.choice(TS), 0, OPEN, 'gen', tag(R)])
    for c in (101, 102, 113, 502, 703, 704):
        if R.random() < 0.7:
            cut = rdate(R, 1980, 2010)
            rows.append([-c, 'unpubForce', R.choice(F), 0, cut - 1, 'gen', tag(R)])
            rows.append([-c, 'unpubForce', R.choice(F), cut, OPEN, 'gen', tag(R)])
        for rule in ('enBancGrantVacatesPanel', 'circulationCountsAsEnBanc', 'firstInTimeControls'):
            if R.random() < 0.6:
                rows.append([-c, rule, R.choice('01'), 0, OPEN, 'gen', tag(R)])
    if R.random() < 0.6:            # S-CA review granted (D9 approved rule): pre-2016 depublished, later persuasive
        cut = rdate(R, 1990, 2020)
        rows.append([R.choice([5, -502]), 'reviewGrantedForce', R.choice(['notCitable', 'none']), 0, cut - 1, 'gen',
                     tag(R)])
        rows.append([R.choice([5, -502]), 'reviewGrantedForce', 'persuasive', cut, OPEN, 'gen', tag(R)])
    if R.random() < 0.6:
        rows.append([20, 'stateFollowsCircuit', R.choice(['binding', 'persuasive']), rdate(R, 1950, 1990), OPEN,
                     'gen', 'U'])
    if R.random() < 0.3:
        rows.append([-701, 'horizontal', 'soft', 0, OPEN, 'gen', 'L'])
    return rows


SCENARIOS = [  # (by court, target court, target must predate the KY change) - pairs that exercise named rules
    (602, 601, True),    # H3: the new KY Supreme Court over the old Court of Appeals (succession)
    (601, 601, True),    # adopted predecessor decisions: the new KY CoA cannot overrule them (R6)
    (102, 101, None),    # F10: adopter circuit over adopted / non-adopted source decisions
    (101, 101, None), (102, 102, None), (502, 502, None), (703, 703, None), (704, 703, None),  # horizontal
    (2906, 501, None), (2906, 601, None), (2906, 101, None),   # F1/F14/T2 across systems
    (501, 502, None), (701, 703, None), (702, 703, None),      # H1/H2
    (113, 203, None), (101, 201, None), (102, 201, None),      # F11, F7 districts
]


def scenario_pair(R, dated, kyc):
    by, tgt, pre = R.choice(SCENARIOS)
    xs = [x for x in dated if x['court'] == tgt and (pre is None or (x['date'] < kyc) == pre)]
    bs = [x for x in dated if x['court'] == by]
    if not xs or not bs:
        return None
    a, b = R.choice(xs), R.choice(bs)
    if a['date'] > b['date']:
        a, b = b, a
    if a is b:
        return None
    return a, b


def epoch_at(crows, c, d):
    for r in crows:
        if r[0] == c and r[1] <= d <= r[2]:
            return r
    return None


def generate(seed, out, n_dec=60, legacy=False, hunt=True, lines=True, r5=True):
    """One universe. The original random stream R is consumed exactly as before the "five limits" layer was added,
    so every old seed reproduces its old universe row for row; the layer (new_layer, its own random.Random) only
    appends courts, rules, decisions (node ids >= the old count), rows and the optional files. legacy=True omits it.
    The hunt layer (hunt_layer, a third stream) appends after it in the same way; hunt=False (--no-hunt) omits it and
    reproduces the universes generated before it byte for byte. The lines layer (lines_layer, a fourth stream,
    DEVIATIONS 79) appends after the hunt layer and needs it; lines=False (--no-lines) omits it and reproduces the
    universes generated before round 2 byte for byte. The round-5 layer (r5_layer, a fifth stream, DESIGN5) appends
    after the lines layer: witness rows, treatment_witness.tsv and (in most universes) treatment_class.tsv; it
    needs the five-limits layer only. r5=False (--no-r5) omits it and reproduces the universes generated before
    round 5 byte for byte."""
    R = random.Random(seed)
    crows, succ, adopt, split, kyc = courts(R)
    srules = system_rules(R)
    court_ids = sorted({r[0] for r in crows})
    weights = {2906: 4, 101: 4, 102: 4, 113: 2, 201: 2, 202: 2, 203: 1, 301: 1, 401: 2, 402: 1, 501: 3, 502: 5,
               503: 2, 504: 2, 505: 1, 601: 4, 602: 2, 603: 1, 701: 2, 702: 2, 703: 3, 704: 3, 705: 1}
    decs = []
    while len(decs) < n_dec:
        c = R.choices(court_ids, [weights[x] for x in court_ids])[0]
        d = rdate(R)
        e = epoch_at(crows, c, d)
        if e is None:
            continue
        unit = 0
        if c in (502, 703, 704) or e[5] == 'T':
            unit = R.randint(1, 3) if c == 502 else (e[8] or R.randint(0, 2))
        if c == 101 and R.random() < 0.3:
            unit = R.choice([1, 2])
        if R.random() < 0.03:
            d = 0
        bench = R.choice(['panel'] * 4 + ['enBanc', 'division', 'limitedEnBanc', 'circulated', 'conflictPanel',
                                          'wholeCourt', 'unknown'])
        pub = R.choice(['published'] * 6 + ['unpublished', 'table', 'summaryOrder', 'memorandum', 'unknown'])
        form = R.choice(['full'] * 8 + ['perCuriam', 'summaryAffirmance', 'equallyDivided', 'certifiedAnswer',
                                        'plurality', 'plurality', 'memorandum', 'unknown'])
        decs.append({'court': c, 'date': d, 'unit': unit, 'bench': bench, 'pub': pub, 'form': form})
    decs.sort(key=lambda x: (x['date'] or 99999999))
    for i, x in enumerate(decs):
        x['node'] = i
        x['name'] = '%s v. %s' % tuple(R.sample(WORDS, 2))
        x['cite'] = '%d Rep. %d' % (R.randint(1, 900), R.randint(1, 1500))
        x['sent'] = ['%s, %s.' % (x['name'], x['cite'])]
    N = len(decs)
    dated = [x for x in decs if x['date']]
    issues = [('fed.a', 'federal question A', 'federalGeneral', '42:1983', 'Is A required?'),
              ('fed.b', 'federal question B', 'federalGeneral', '42:2000e-5(e)', 'Does B restart?'),
              ('pat.a', 'patent question', 'federalPatent', '35:101', 'Is C patentable?'),
              ('ca.a', 'California question', 'stateLaw:5', '-', 'Is D enforceable?'),
              ('ky.a', 'Kentucky question', 'stateLaw:17', '-', 'Is E allowed?'),
              ('tx.a', 'Texas question', 'stateLaw:44', '-', 'Is F allowed?'),
              ('unk.a', 'unknown-domain question', 'unknown', '-', '-')]
    ikeys = [i[0] for i in issues]

    def add_sentence(node, text):
        decs[node]['sent'].append(text)
        return (node, len(decs[node]['sent']) - 1)

    holdings, marks = [], []
    for x in decs:
        if R.random() < 0.45:
            for k in R.sample(ikeys, R.choice([1, 1, 2])):
                hid = 'h%d%s' % (x['node'], k.replace('.', ''))
                ans = R.choice(['yes', 'no'])
                role = R.choice(['majority'] * 6 + ['plurality', 'perCuriam', 'concurrence'])
                prop = 'The answer to %s is %s.' % (k, ans)
                loc = add_sentence(x['node'], 'Held: ' + prop)
                holdings.append({'id': hid, 'node': x['node'], 'issue': k, 'prop': prop, 'answer': ans,
                                 'role': role, 'loc': loc})
                if (role == 'plurality' or x['form'] == 'plurality') and R.random() < 0.4:
                    marks.append([x['node'], k, 'Narrowest', prop, 'gen', tag(R)])
    hold_by_node = {}
    for h in holdings:
        hold_by_node.setdefault(h['node'], []).append(h)
    # treatments
    treatments = []
    for i in range(int(N * 0.6)):
        if len(dated) < 2:
            break
        pair = scenario_pair(R, dated, kyc) if R.random() < 0.4 else None
        a, b = pair if pair else sorted(R.sample(dated, 2), key=lambda x: x['date'])
        if R.random() < 0.05:
            a, b = b, a     # earlier "overrules" later: must never be admitted (T1)
        B, X = b['node'], a['node']
        kind = R.choice(TREAT_KINDS)
        hk = [h['issue'] for h in hold_by_node.get(X, [])]
        sc = R.random()
        if sc < 0.55 or not hk:
            scope = R.choice(['all'] * 5 + ['partialUnknown', 'otherGrounds', 'issues:' + R.choice(ikeys)])
        else:
            scope = 'issues:' + ','.join(R.sample(hk, R.randint(1, len(hk))))
        tmp = R.random()
        temporal = 'retroactive' if tmp < 0.5 else ('unknown' if tmp < 0.8 else (
            'pureProspective' if tmp < 0.9 else 'prospectiveFrom:%d' % (b['date'] + R.randint(0, 3) * 10000)))
        explicit = 1 if R.random() < 0.85 else 0
        use_cite = R.random() < 0.5
        tev = ('cite:' + a['cite']) if use_cite else ('name:' + ' '.join(a['name'].replace('.', '').split()[::2]))
        quote = '%s, %s, %s' % (a['name'], a['cite'], VERB_TEXT[kind])
        loc = add_sentence(B, 'We hold that ' + quote + '.')
        part = R.choice(['majority'] * 9 + ['plurality', 'perCuriam', 'dissent', 'concurrence', 'unknown'])
        treatments.append({'id': 't%d' % i, 'by': B, 'target': X, 'date': b['date'], 'kind': kind,
                           'scope': scope, 'temporal': temporal, 'explicit': explicit, 'quote': quote,
                           'tev': tev, 'part': part, 'loc': loc, 'prefix': len('We hold that ')})
    # history (bias toward overruling decisions so revival is exercised)
    history = []
    overrulers = [t['by'] for t in treatments if t['kind'] in ('overruled', 'disapproved', 'recededFrom',
                                                                'abrogated')]
    for i in range(int(N * 0.35)):
        if overrulers and R.random() < 0.5:
            X = R.choice(overrulers)
        else:
            X = R.choice(dated)['node']
        if not decs[X]['date']:
            continue
        kind = R.choice(HIST_KINDS)
        d = add_days(decs[X]['date'], R.randint(0, 6 * 365))
        later = [y for y in dated if y['date'] >= decs[X]['date'] and y['node'] != X]
        by = R.choice(later)['node'] if (later and R.random() < 0.5) else -1
        hk = [h['issue'] for h in hold_by_node.get(X, [])]
        scope = R.choice(['all'] * 5 + ['unknown'] + (['issues:' + R.choice(hk)] if hk else []))
        if by >= 0:
            quote = '%s, %s, %s' % (decs[X]['name'], decs[X]['cite'], VERB_TEXT[kind])
            loc = add_sentence(by, 'The judgment in ' + quote + '.')
            prefix = len('The judgment in ')
            tev = 'cite:' + decs[X]['cite']
        else:
            quote = 'The opinion %s' % VERB_TEXT[kind]
            loc = add_sentence(X, quote + '.')
            prefix = 0
            tev = 'name:' + decs[X]['name'].split()[0]
        history.append({'id': 'y%d' % i, 'target': X, 'by': by, 'date': d, 'kind': kind, 'scope': scope,
                        'quote': quote, 'tev': tev, 'part': 'majority', 'loc': loc, 'prefix': prefix})
    # law changes and supersessions
    lawchanges, sups = [], []
    for j in range(2):
        en = rdate(R, 1950, 2022)
        eff = en + R.choice([0, 0, 10000])
        retro = R.choice([0, 0, en - R.randint(1, 3) * 10000, 1])   # 1 = cases pending on the effective date
        lawchanges.append(['lc%d' % j, 'Pub. L. %d-%d' % (R.randint(80, 118), R.randint(1, 400)),
                           R.choice(['42:1983', '42:2000e-5(e)']), en, eff, retro, 'gen'])
        cands = [h for h in holdings if h['issue'] in ('fed.a', 'fed.b') and decs[h['node']]['date']
                 and decs[h['node']]['date'] < en]
        for h in R.sample(cands, min(len(cands), 2)):
            ev = R.choice(['lawNamesDecision', 'reportNamesDecision', 'quotedWordsStruck'])
            st = [t for t in treatments if t['target'] == h['node'] and t['kind'] == 'supersededByEnactment']
            if st and R.random() < 0.5:
                ev = 'laterCourtSays:' + st[0]['id']
            sups.append(['s%d%s' % (j, h['id']), h['node'], R.choice([h['issue'], '-']), 'lc%d' % j, ev,
                         round(R.random(), 2), 1 if R.random() < 0.8 else 0, 'gen'])
    # five-limits layer (own random stream; appends only)
    L = None if legacy else new_layer(random.Random(seed * 1000003 + 977), decs, crows, adopt, srules, issues,
                                      holdings, history)
    # hunt layer (H2, H3b, H4; own random stream; appends only, after the five-limits layer)
    N1, NS1 = len(decs), len(sups)
    HL = None if (legacy or not hunt) else hunt_layer(random.Random(seed * 1000003 + 1979), decs, crows, adopt,
                                                      srules, issues, lawchanges, sups)
    # lines layer (round 2; own random stream; appends only, after the hunt layer, whose courts it uses)
    N2 = len(decs)
    LL = None if HL is None or not lines else lines_layer(random.Random(seed * 1000003 + 2026), decs, crows, succ,
                                                          adopt, srules, issues)
    # round-5 layer (DESIGN5; own random stream; appends only, after the lines layer; adds no court and no rule)
    N3 = len(decs)
    RL = None if (L is None or not r5) else r5_layer(
        random.Random(seed * 1000003 + 5005), decs, crows, issues,
        [t['id'] for t in treatments] + [t['id'] for lay in (L, HL, LL) if lay for t in lay['treatments']])
    # texts, shas, offsets
    texts, shas = {}, {}
    for x in decs:
        texts[x['node']] = ' '.join(x['sent'])
        shas[x['node']] = hashlib.sha1(texts[x['node']].encode('utf-8')).hexdigest()

    def offset(loc):
        node, idx = loc
        return sum(len(s) + 1 for s in decs[node]['sent'][:idx])

    cert_text = []

    def cert(owner, loc, quote, prefix, tev, part, corrupt):
        start = offset(loc) + prefix
        end = start + len(quote)
        sha = shas[owner]
        txt = texts[owner]
        assert txt[start:end] == quote, (txt[start:end], quote)
        s0, e0 = max(0, start - 400), min(len(txt), end + 400)
        cert_text.append([sha, s0, e0, txt[s0:e0]])
        q = quote
        if corrupt == 'offset':
            start += 1
            end += 1
        elif corrupt == 'sha':
            sha = shas[(owner + 1) % N]
        elif corrupt == 'quote':
            q = quote[:-1] + ('x' if quote[-1] != 'x' else 'y')
        elif corrupt == 'target':
            tev = 'name:Nobody'
        return [sha, start, end, q, tev, part]

    def corruption():
        x = R.random()
        return None if x < 0.85 else R.choice(['offset', 'sha', 'quote', 'target'])

    W = lambda name, rows: write(os.path.join(out, 'data', name), rows)
    os.makedirs(os.path.join(out, 'data'), exist_ok=True)
    os.makedirs(os.path.join(out, 'edges'), exist_ok=True)
    W('courts2.tsv', crows)
    W('succession.tsv', succ)
    W('adoption.tsv', adopt)
    W('system_rules.tsv', srules)
    W('decisions2.tsv', [[x['node'], x['court'], x['date'], x['unit'], x['bench'], x['pub'], x['form'],
                          shas[x['node']], 'gen'] for x in decs])
    W('issues.tsv', [list(i) + ['gen'] for i in issues])
    def hold_row(h, rng):
        return [h['id'], h['node'], h['issue'], h['prop'], h['answer'], h['role']] + cert(
            h['node'], h['loc'], 'Held: ' + h['prop'], 0, 'name:x', 'majority',
            rng.choice([None] * 9 + ['offset'])) + ['gen', 0.9]

    def treat_row(t, c):
        # (round 5: a witness row's certificate is from W's text, `owner`; every other row's from the by-decision's)
        return [t['id'], t['by'], t['target'], t['date'], t['kind'], t['scope'], t['temporal'], t['explicit']] + cert(
            t.get('owner', t['by']), t['loc'], t['quote'], t['prefix'], t['tev'], t['part'], c) + ['gen', 0.9]

    def hist_row(y, c):
        return [y['id'], y['target'], y['by'], y['date'], y['kind'], y['scope']] + cert(
            y['by'] if y['by'] >= 0 else y['target'], y['loc'], y['quote'], y['prefix'], y['tev'], y['part'],
            c) + ['gen']

    hrows = [hold_row(h, R) for h in holdings]           # the original stream, in the original order
    trows = [treat_row(t, corruption()) for t in treatments]
    yrows = [hist_row(y, corruption()) for y in history]
    if L:
        lr = L['rng']
        lcorr = lambda: None if lr.random() < 0.85 else lr.choice(['offset', 'sha', 'quote', 'target'])
        hrows += [hold_row(h, lr) for h in L['holdings']]
        trows += [treat_row(t, lcorr()) for t in L['treatments']]
        yrows += [hist_row(y, lcorr()) for y in L['history']]
        marks = marks + L['marks']
    if HL:                                               # last, so the hunt windows are the tail of cert_text
        hr = HL['rng']
        hcorr = lambda: None if hr.random() < 0.9 else hr.choice(['offset', 'sha', 'quote', 'target'])
        hrows += [hold_row(h, hr) for h in HL['holdings']]
        trows += [treat_row(t, hcorr()) for t in HL['treatments']]
    if LL:                                               # after the hunt rows: its windows are the new tail
        qr = LL['rng']
        qcorr = lambda: None if qr.random() < 0.96 else qr.choice(['offset', 'sha', 'quote', 'target'])
        hrows += [hold_row(h, _Rare(qr)) for h in LL['holdings']]
        trows += [treat_row(t, qcorr()) for t in LL['treatments']]
    if RL:                                               # after every other layer: its windows are the new tail
        vr = RL['rng']
        vcorr = lambda: None if vr.random() < 0.95 else vr.choice(['offset', 'sha', 'quote', 'target'])
        hrows += [hold_row(h, _Rare(vr)) for h in RL['holdings']]
        trows += [treat_row(t, vcorr()) for t in RL['treatments']]
        yrows += [hist_row(y, None) for y in RL['history']]
    # round 5: written by the round-5 layer only; never left over (the class table is absent in some universes)
    for name, rows in (('treatment_witness.tsv', RL['witness'] if RL else None),
                       ('treatment_class.tsv', RL['klass'] if RL else None)):
        if rows is not None:
            W(name, rows)
        elif os.path.exists(os.path.join(out, 'data', name)):
            os.remove(os.path.join(out, 'data', name))
    for name in ('factors.tsv', 'factor_cases.tsv'):     # written by the lines layer only; never left over
        if LL:
            W(name, LL[name[:-4]])
        elif os.path.exists(os.path.join(out, 'data', name)):
            os.remove(os.path.join(out, 'data', name))
    W('holdings.tsv', hrows)
    W('marks.tsv', marks)
    W('treatments.tsv', trows)
    W('history.tsv', yrows)
    # dedupe windows
    seen = set()
    ct = []
    for r in cert_text:
        k = (r[0], r[1], r[2])
        if k not in seen:
            seen.add(k)
            ct.append(r)
    W('cert_text.tsv', ct)
    W('lawchanges.tsv', lawchanges)
    W('supersessions.tsv', sups)
    extra = [[x['node'], R.choice([1, 2]), 0] for x in decs if x['court'] == 301]
    W('decisions2_extra.tsv', extra)
    # edges: cite earlier decisions, biased toward event targets
    hot = list({t['target'] for t in treatments} | {y['target'] for y in history} | {s[1] for s in sups[:NS1]})
    edges = []
    for x in dated:
        earlier = [y['node'] for y in dated if y['date'] < x['date']]
        if not earlier:
            continue
        k = R.randint(0, 4)
        pool = [h for h in hot if decs[h]['date'] and decs[h]['date'] < x['date']]
        for _ in range(k):
            y = R.choice(pool) if (pool and R.random() < 0.6) else R.choice(earlier)
            edges.append([x['node'], y])
    if L:
        edges += L['edges']
        if HL:
            edges += HL['edges']
        if LL:
            edges += LL['edges']
        if RL:
            edges += RL['edges']
        write_layer_files(L, out, decs, ct, N1, HL['rng'] if HL else None, {shas[x['node']] for x in decs[N1:N2]},
                          N2, LL['rng'] if LL else None, {shas[x['node']] for x in decs[N2:N3]},
                          N3, RL['rng'] if RL else None, {shas[x['node']] for x in decs[N3:]})
    write(os.path.join(out, 'edges', 'edges-00.tsv'), sorted({tuple(e) for e in edges}))
    return len(decs)


# ---------------------------------------------------------------------------------------------------------------
# "Five limits" layer (REF_NOTES): commission notations (H4), Texas writ/petition notations (S-TX), FL/CA units for
# conflicts, trial courts ignoring own-unit precedent, later negations of cited decisions, contrary later binding
# holdings, and the optional files cite_index.tsv / window_sha.tsv / commission.tsv. Everything is drawn from its own
# random stream and only APPENDED, so the original universe is unchanged.

TX_WORDINGS = ["writ ref'd", "writ refused", "writ ref'd n.r.e.", "writ denied", "writ dism'd w.o.j.", "pet. ref'd",
               "petition refused", "pet. denied", "pet. dism'd", "PDR ref'd", "pet. ref'd (PDR)"]
NOTATIONS = ['opinionAdopted', 'opinionApproved', 'judgmentAdopted', 'adoptedAsOpinionOfCourt', 'other']
NOTE_TEXT = {'opinionAdopted': 'Opinion adopted.', 'opinionApproved': 'Opinion approved by the Court.',
             'judgmentAdopted': 'Judgment adopted.', 'adoptedAsOpinionOfCourt': 'is adopted as the opinion of the court',
             'other': 'Opinion of the Commission of Appeals'}
HIGHER = {101: 2906, 102: 2906, 113: 2906, 201: 101, 202: 102, 502: 501, 503: 502, 504: 502, 703: 701, 704: 701,
          705: 703, 902: 901, 903: 902, 802: 801}
TRIAL_OVER = {503: (502, 505), 504: (502,), 705: (703, 704), 903: (902,), 201: (101,)}


def new_layer(G, decs, crows, adopt, srules, issues, holdings, history):
    N0 = len(decs)
    add = lambda *a: crows.append(list(a))
    add(2948, 19180101, 19451231, 'Texas Commission of Appeals', 44, 'S', '-', 0, 0, 'gen', 'S')
    add(801, 0, OPEN, 'Supreme Court of Missouri', 25, 'L', 'all', 0, 0, 'gen', 'S')
    add(802, 19720101, OPEN, 'Missouri Court of Appeals', 25, 'A', '-', 0, 0, 'gen', 'L')
    add(901, 0, OPEN, 'Supreme Court of Florida', 10, 'L', 'all', 0, 0, 'gen', 'S')
    add(902, 19570101, OPEN, 'Florida District Court of Appeal', 10, 'A', '-', 0, 0, 'gen', 'S')
    add(903, 0, OPEN, 'Florida Circuit Court', 10, 'T', '-', 0, 1, 'gen', 'S')
    for (f, force, tg) in (('opinionAdopted', 'binding', 'S'), ('holdingApproved', 'binding', 'U'),
                           ('judgmentAdopted', 'resultOnly', 'U'), ('none', 'persuasive', 'U')):
        adopt.append([701, 2948, 19451231, f, force, 'gen', tg])    # the 2927 <- 2948 rows (Texas SC here is 701)
    srules.append([10, 'horizontal', 'withinUnitOnly', 0, OPEN, 'gen', 'S'])
    srules.append([10, 'trialScope', G.choice(['ownUnitThenAny'] * 3 + ['ownUnitOnly']), 0, OPEN, 'gen',
                   G.choice('SSL')])
    srules.append([25, 'horizontal', 'soft', 0, OPEN, 'gen', 'S'])
    srules.append([25, 'trialScope', 'statewide', 0, OPEN, 'gen', 'L'])
    if G.random() < 0.4:
        srules.append([-902, 'firstInTimeControls', '1', 0, OPEN, 'gen', G.choice('SLU')])
    if G.random() < 0.5:        # make the old CA / TX trial scopes unit-dependent more often (conflicts, own unit)
        srules.append([-502, 'trialScope', G.choice(['ownUnitThenAny', 'statewideChooseOnConflict']), 0, OPEN,
                       'gen', 'L'])
    if G.random() < 0.5:
        srules.append([-703, 'trialScope', 'ownUnitOnly', 0, OPEN, 'gen', 'L'])
        srules.append([-704, 'trialScope', 'ownUnitOnly', 0, OPEN, 'gen', 'L'])
    issues.append(('fl.a', 'Florida question', 'stateLaw:10', '-', 'Is G allowed?'))
    out = {'rng': G, 'holdings': [], 'treatments': [], 'history': [], 'marks': [], 'edges': [], 'commission': []}

    def newdec(court, date, unit=0, bench=None):
        x = {'court': court, 'date': date, 'unit': unit,
             'bench': bench or G.choice(['panel'] * 5 + ['enBanc', 'unknown']),
             'pub': G.choice(['published'] * 8 + ['unpublished', 'unknown']),
             'form': G.choice(['full'] * 9 + ['perCuriam', 'plurality']), 'node': len(decs)}
        x['name'] = '%s v. %s' % tuple(G.sample(WORDS, 2))
        x['cite'] = '%d Rep. %d' % (G.randint(1, 900), G.randint(1, 1500))
        x['sent'] = ['%s, %s.' % (x['name'], x['cite'])]
        decs.append(x)
        return x

    def sentence(x, text):
        x['sent'].append(text)
        return (x['node'], len(x['sent']) - 1)

    def holding(x, issue, ans, role='majority'):
        hid = 'h%d%s' % (x['node'], issue.replace('.', ''))
        if any(h['id'] == hid for h in out['holdings']):
            return None
        prop = 'The answer to %s is %s.' % (issue, ans)
        h = {'id': hid, 'node': x['node'], 'issue': issue, 'prop': prop, 'answer': ans, 'role': role,
             'loc': sentence(x, 'Held: ' + prop)}
        out['holdings'].append(h)
        return h

    def later(d, lo=1, hi=12):
        return min(add_days(d, G.randint(lo * 365, hi * 365)), 20221228)

    def treat(b, a, kind, explicit=None, scope='all'):
        quote = '%s, %s, %s' % (a['name'], a['cite'], VERB_TEXT[kind])
        tev = ('cite:' + a['cite']) if G.random() < 0.5 else ('name:' + ' '.join(a['name'].replace('.', '').split()[::2]))
        out['treatments'].append({
            'id': 'tn%d' % len(out['treatments']), 'by': b['node'], 'target': a['node'], 'date': b['date'],
            'kind': kind, 'scope': scope, 'temporal': G.choice(['retroactive', 'retroactive', 'unknown']),
            'explicit': explicit if explicit is not None else (1 if G.random() < 0.9 else 0), 'quote': quote,
            'tev': tev, 'part': G.choice(['majority'] * 9 + ['dissent']), 'loc': sentence(b, 'We hold that ' + quote + '.'),
            'prefix': len('We hold that ')})

    old = [x for x in decs if x['date']]
    # (a) commission notations: Texas Commission of Appeals, CCA commissioners, Missouri commissioners (H4)
    for _ in range(G.randint(2, 4)):
        x = newdec(2948, rdate(G, 1918, 1945))
        if G.random() < 0.85:
            out['commission'].append((x['node'], 2948, G.choice(NOTATIONS + ['opinionAdopted'] * 2)))
        holding(x, 'tx.a', G.choice(['yes', 'no']))
    for x in [x for x in decs[:N0] if x['court'] == 702] + [newdec(702, rdate(G, 1900, 1990))]:
        if G.random() < 0.7:
            out['commission'].append((x['node'], 702, G.choice(['opinionApproved'] * 4 + ['judgmentAdopted', 'other'])))
    for _ in range(2):
        x = newdec(801, rdate(G, 1900, 1960))
        out['commission'].append((x['node'], 801, G.choice(['adoptedAsOpinionOfCourt', 'other', 'opinionAdopted',
                                                            'judgmentAdopted'])))
    for x in [x for x in decs[:N0] if x['court'] == 701]:
        if G.random() < 0.3:
            out['commission'].append((x['node'], 701, G.choice(['opinionAdopted', 'opinionApproved', 'judgmentAdopted'])))
    # (b) intra-court disagreement on question issues: FL DCAs and CA Court of Appeal units, and their trial courts
    for _ in range(G.randint(3, 6)):
        holding(newdec(902, rdate(G, 1960, 2020), G.randint(1, 3)), 'fl.a', G.choice(['yes', 'no']))
    for _ in range(G.randint(2, 4)):
        holding(newdec(502, rdate(G, 1960, 2020), G.randint(1, 3)), 'ca.a', G.choice(['yes', 'no']))
    for _ in range(G.randint(0, 2)):
        holding(newdec(703, rdate(G, 1960, 2020), 1), 'tx.a', G.choice(['yes', 'no']))
    if G.random() < 0.3:
        holding(newdec(901, rdate(G, 1990, 2022)), 'fl.a', G.choice(['yes', 'no']))
    for _ in range(G.randint(1, 2)):
        newdec(903, rdate(G, 1960, 2022), G.randint(1, 3))
    # (c) trial courts declining / purporting to overrule own-unit precedent; other claims without power
    pool = lambda courts: [x for x in decs if x['court'] in courts and x['date'] and x['date'] < 20200101]
    for _ in range(G.randint(3, 7)):
        tc = G.choice(sorted(TRIAL_OVER))
        tg = pool(TRIAL_OVER[tc])
        if not tg:
            continue
        a = G.choice(tg)
        unit = a['unit'] if (G.random() < 0.7 and a['unit']) else G.randint(1, 3)
        b = newdec(tc, later(a['date'], 0, 8), unit)
        treat(b, a, G.choice(['declinedToFollow'] * 3 + ['overruled'] * 2 + ['disapproved', 'limited', 'questioned',
                                                                               'criticized']))
    for (bc, tcs) in ((703, (701, 702)), (502, (501,)), (902, (901,)), (101, (2906,)), (703, (2948,))):
        tg = pool(tcs)
        if tg and G.random() < 0.6:
            a = G.choice(tg)
            treat(newdec(bc, later(a['date'], 0, 10), G.randint(1, 3)), a,
                  G.choice(['overruled', 'disapproved', 'limited', 'questioned', 'declinedToFollow']))
    # (d) later negation of a cited decision by a court that binds the citing court
    for _ in range(G.randint(1, 3)):
        tg = [x for x in old if x['court'] in (502, 703, 704, 902, 101, 102) and x['date'] < 20100101]
        if not tg:
            break
        a = G.choice(tg)
        hc = HIGHER[a['court']]
        bdate = later(a['date'], 3, 15)
        c = newdec(a['court'], add_days(a['date'], G.randint(30, max(31, 365 * 2))), a['unit'])
        if c['date'] >= bdate:
            continue
        out['edges'].append([c['node'], a['node']])
        b = newdec(hc, bdate, bench=G.choice(['enBanc', 'panel']))
        treat(b, a, G.choice(['overruled', 'overruled', 'disapproved', 'abrogated']), explicit=1)
    # (e) contrary later holdings by a court whose decisions bind the holder (atRisk contraryBinding)
    qh = [h for h in holdings + out['holdings'] if h['issue'] in ('fed.a', 'fed.b', 'ca.a', 'tx.a', 'fl.a')
          and decs[h['node']]['date'] and decs[h['node']]['court'] in HIGHER and decs[h['node']]['date'] < 20150101]
    for h in G.sample(qh, min(len(qh), G.randint(1, 3))):
        x = decs[h['node']]
        holding(newdec(HIGHER[x['court']], later(x['date'], 1, 15)), h['issue'], 'no' if h['answer'] == 'yes' else 'yes')
    # (f) Texas writ / petition notations, both eras, civil and criminal deciders, Texas and non-Texas targets
    tx = [x for x in old if x['court'] in (703, 704)]
    tx += [newdec(G.choice([703, 704]), rdate(G, 1993, 2001), 0) for _ in range(2)]
    other = [x for x in old if x['court'] in (502, 101, 702)]
    targets = G.sample(tx, min(len(tx), G.randint(3, 6))) + (G.sample(other, 1) if other and G.random() < 0.5 else [])
    for i, a in enumerate(targets):
        if a['node'] >= N0 and decs[a['node']]['court'] in (703, 704) and a['date'] >= 19930101:
            d = add_days(a['date'], G.randint(0, 3 * 365))
        else:
            d = later(a['date'], 0, 4)
        wording = G.choice(TX_WORDINGS)
        r = G.random()
        if r < 0.5:
            by = newdec(701, d)
        elif r < 0.75:
            by = newdec(702, d)
        else:
            by = None
        if by is None and a['node'] < N0:
            by = newdec(701, d)            # a quote in an old decision's own text would change that decision's sha
        if by is not None:
            quote = '%s, %s, %s' % (a['name'], a['cite'], wording)
            loc, prefix, tev, bn = sentence(by, 'The judgment in ' + quote + '.'), len('The judgment in '), \
                'cite:' + a['cite'], by['node']
        else:
            quote = 'The opinion %s' % wording
            loc, prefix, tev, bn = sentence(a, quote + '.'), 0, 'name:' + a['name'].split()[0], -1
        out['history'].append({'id': 'yw%d' % i, 'target': a['node'], 'by': bn, 'date': d, 'kind': 'writRefused',
                               'scope': 'all', 'quote': quote, 'tev': tev, 'part': 'majority', 'loc': loc,
                               'prefix': prefix})
    # edges from the new decisions to earlier ones
    for x in decs[N0:]:
        earlier = [y['node'] for y in decs if y['date'] and x['date'] and y['date'] < x['date']]
        for _ in range(G.randint(0, 3) if earlier else 0):
            out['edges'].append([x['node'], G.choice(earlier)])
    for x in G.sample(old, min(len(old), 8)):          # old decisions citing new earlier ones
        new_earlier = [y['node'] for y in decs[N0:] if y['date'] and y['date'] < x['date']]
        if new_earlier:
            out['edges'].append([x['node'], G.choice(new_earlier)])
    out['present'] = {'commission': G.random() < 0.85, 'cite_index': G.random() < 0.75,
                      'window_sha': G.random() < 0.67}
    return out


def write_layer_files(L, out, decs, ct, n1=None, hrng=None, hshas=(), n2=None, qrng=None, qshas=(),
                      n3=None, vrng=None, vshas=()):
    """Optional files. Decisions from n1 on and windows of texts in hshas belong to the hunt layer and draw from
    its stream (hrng), so the five-limits stream G is consumed exactly as before that layer existed. Decisions from
    n2 on and windows of texts in qshas belong to the lines layer and draw from its stream (qrng) in the same way;
    decisions from n3 on and windows of texts in vshas belong to the round-5 layer (vrng)."""
    G0 = L['rng']
    n1 = len(decs) if n1 is None else n1
    n2 = len(decs) if n2 is None else n2
    n3 = len(decs) if n3 is None else n3
    P = lambda name: os.path.join(out, 'data', name)
    if L['present']['commission']:   # (no draw)
        write(P('commission.tsv'), [[n, c, k, NOTE_TEXT[k]] for (n, c, k) in L['commission']])
    if L['present']['cite_index']:
        rows = []
        for x in decs:
            G, top = (G0, n1) if x['node'] < n1 else ((hrng, n2) if x['node'] < n2 else (
                (qrng, n3) if x['node'] < n3 else (vrng, len(decs))))
            r = G.random()
            if r < 0.85:
                rows.append([x['cite'], x['node']])
            elif r < 0.90:
                rows.append([x['cite'], G.randrange(top)])                # wrong target
            # else: missing
            if G.random() < 0.05:                                                # compact collision: ambiguous
                rows.append([x['cite'].upper().replace(' ', ''), G.randrange(top)])
        write(P('cite_index.tsv'), rows)
    if L['present']['window_sha']:
        rows = []
        for (sha, s0, e0, w) in ct:
            G = vrng if sha in vshas else (qrng if sha in qshas else (hrng if sha in hshas else G0))
            r = G.random()
            if r < 0.90:
                rows.append([sha, s0, e0, hashlib.sha1(w.encode('utf-8')).hexdigest(), 'gen'])
            elif r < 0.95:
                rows.append([sha, s0, e0, hashlib.sha1((w + 'x').encode('utf-8')).hexdigest(), 'gen'])   # corrupt
        write(P('window_sha.tsv'), rows)


# ---------------------------------------------------------------------------------------------------------------
# Hunt layer (REF_NOTES "Revisions: hunt fixes"): H4 adoption cut-offs with overrulings by the source court, the
# adopter or SCOTUS and citations from both lines; H3b departures by every bench under horizontal rules that start
# after the precedent or after the treating decision; H2 explicit supersessions cited by decisions holding on the same
# issue or the same amended block. Own random stream, appended after the five-limits layer; treatments and holdings
# sit only in new decisions (an old decision's text, and so its sha, never changes).

def hunt_layer(H, decs, crows, adopt, srules, issues, lawchanges, sups):
    add = lambda *a: crows.append(list(a))
    add(1101, 0, OPEN, 'United States Court of Appeals for the District of Columbia Circuit', 0, 'A', '-', 12, 0,
        'gen', 'S')
    add(1104, 0, OPEN, 'United States District Court for the District of Columbia', 0, 'T', '-', 12, 0, 'gen', 'S')
    add(1102, 0, OPEN, 'District of Columbia Court of Appeals', 51, 'L', 'all', 0, 0, 'gen', 'S')
    add(1103, 0, OPEN, 'Superior Court of the District of Columbia', 51, 'T', '-', 0, 1, 'gen', 'S')
    add(1001, 0, OPEN, 'Supreme Court of Ohio', 36, 'L', 'all', 0, 0, 'gen', 'S')
    add(1002, 0, OPEN, 'Court of Appeals of Ohio', 36, 'A', '-', 0, 0, 'gen', 'S')
    dc_cut = rdate(H, 1960, 1985)
    adopt.append([1102, 1101, dc_cut, 'all', 'binding', 'gen', H.choice('SSL')])
    if H.random() < 0.3:        # rows that are never heirs: a filter the decision does not decide, a weaker force
        adopt.append([1102, 1101, OPEN, H.choice(['issue:localLaw', 'unitA']), 'binding', 'gen', 'L'])
    if H.random() < 0.3:
        adopt.append([1001, 1101, dc_cut, 'all', 'persuasive', 'gen', 'L'])
    # horizontal rules with dated rows: none before d1, a binding rule from d1, something else (or nothing) from d2
    d1, d2 = rdate(H, 1940, 1980), rdate(H, 1985, 2010)
    srules.append([36, 'horizontal', H.choice(['strong', 'strong', 'withinUnitOnly']), d1, d2 - 1, 'gen',
                   H.choice('SSLU')])
    if H.random() < 0.6:
        srules.append([36, 'horizontal', H.choice(['soft', 'none', 'strong', 'withinUnitOnly']), d2, OPEN, 'gen',
                       H.choice('SLU')])
    if H.random() < 0.5:
        srules.append([-1002, 'circulationCountsAsEnBanc', H.choice('01'), 0, OPEN, 'gen', H.choice('SLU')])
    d3 = rdate(H, 1950, 2000)
    if H.random() < 0.7:
        srules.append([-1101, 'horizontal', H.choice(['strong', 'strong', 'soft']), d3, OPEN, 'gen', H.choice('SL')])
    issues.append(('fed.c', 'federal question C', 'federalGeneral', '42:2000e-5(e)(1)', 'Is the period tolled?'))
    issues.append(('fed.d', 'federal question D', 'federalGeneral', '42:1983', 'Is notice required?'))
    out = {'rng': H, 'holdings': [], 'treatments': [], 'edges': []}

    def newdec(court, date, unit=0, bench=None):
        x = {'court': court, 'date': date, 'unit': unit,
             'bench': bench or H.choice(['panel'] * 4 + ['division', 'enBanc', 'unknown', 'circulated']),
             'pub': H.choice(['published'] * 9 + ['unknown']), 'form': H.choice(['full'] * 9 + ['perCuriam']),
             'node': len(decs)}
        x['name'] = '%s v. %s' % tuple(H.sample(WORDS, 2))
        x['cite'] = '%d Rep. %d' % (H.randint(1, 900), H.randint(1, 1500))
        x['sent'] = ['%s, %s.' % (x['name'], x['cite'])]
        decs.append(x)
        return x

    def holding(x, issue, ans=None):
        hid = 'h%d%s' % (x['node'], issue.replace('.', ''))
        if any(h['id'] == hid for h in out['holdings']):
            return None
        ans = ans or H.choice(['yes', 'no'])
        prop = 'The answer to %s is %s.' % (issue, ans)
        x['sent'].append('Held: ' + prop)
        h = {'id': hid, 'node': x['node'], 'issue': issue, 'prop': prop, 'answer': ans, 'role': 'majority',
             'loc': (x['node'], len(x['sent']) - 1)}
        out['holdings'].append(h)
        return h

    def treat(b, a, kind, scope='all', explicit=1):
        quote = '%s, %s, %s' % (a['name'], a['cite'], VERB_TEXT[kind])
        tev = ('cite:' + a['cite']) if H.random() < 0.5 else (
            'name:' + ' '.join(a['name'].replace('.', '').split()[::2]))
        b['sent'].append('We hold that ' + quote + '.')
        out['treatments'].append({
            'id': 'th%d' % len(out['treatments']), 'by': b['node'], 'target': a['node'], 'date': b['date'],
            'kind': kind, 'scope': scope, 'temporal': H.choice(['retroactive', 'retroactive', 'unknown']),
            'explicit': explicit, 'quote': quote, 'tev': tev, 'part': 'majority',
            'loc': (b['node'], len(b['sent']) - 1), 'prefix': len('We hold that ')})

    def cap(d):
        return min(d, 20221228)

    def start_of(c):
        return min(r[1] for r in crows if r[0] == c)

    # H4: a decision of the source court before the cut-off, a status-changing treatment by the source court (after
    # or before the cut-off), the adopter or SCOTUS, then citations from both lines and from outside
    split = adopt[0][2] + 1
    cfgs = [(101, 102, split - 1, (101, 201), (102, 202), (502, 2906, 1101)),
            (1101, 1102, dc_cut, (1101, 1104), (1102, 1103), (101, 501, 201))]
    for (src, adopter, cut, sline, aline, outside) in cfgs:
        for _ in range(H.randint(1, 2)):
            xd = rdate(H, 1900, cut // 10000 - 1)
            x = newdec(src, xd, H.choice([0, 0, 1, 2]) if src == 101 else 0, bench='panel')
            xh = holding(x, H.choice(['fed.a', 'fed.b'])) if H.random() < 0.6 else None
            r = H.random()
            bc = src if r < 0.55 else (adopter if r < 0.9 else 2906)
            if H.random() < 0.8 or bc == adopter:
                bd = cap(add_days(max(day_after(cut), start_of(bc)), H.randint(30, 15 * 365)))
            else:
                bd = cap(add_days(xd, H.randint(30, 3 * 365)))
            b = newdec(bc, bd, x['unit'] if bc == src else 0,
                       bench=H.choice(['enBanc'] * 4 + ['wholeCourt', 'panel']))
            scope = ('issues:' + xh['issue']) if (xh and H.random() < 0.3) else 'all'
            treat(b, x, H.choice(['overruled', 'overruled', 'disapproved', 'abrogated']), scope)
            for c in sline + aline + (H.choice(outside),):
                cd = cap(add_days(max(bd, start_of(c)), H.randint(1, 10 * 365)))
                y = newdec(c, cd, H.randint(0, 2) if c in (1103,) else 0)
                out['edges'].append([y['node'], x['node']])
                if xh and H.random() < 0.5:
                    holding(y, xh['issue'])
            for c in (H.choice(sline), H.choice(aline)):       # citations before the treatment (citesLaterNegated)
                lo = max(xd, start_of(c))
                if lo < bd:
                    y = newdec(c, min(add_days(lo, H.randint(1, 5 * 365)), add_days(bd, -1)))
                    if y['date'] > xd:
                        out['edges'].append([y['node'], x['node']])
    # H3b: departures by every bench, the horizontal rule starting before / after the precedent and the treatment
    for _ in range(H.randint(3, 5)):
        x = newdec(1002, rdate(H, 1930, 2015), H.randint(0, 2))
        b = newdec(1002, cap(add_days(x['date'], H.randint(1, 30 * 365))), x['unit'] if H.random() < 0.7
                   else H.randint(0, 2), bench=H.choice(['panel', 'panel', 'division', 'unknown', 'circulated',
                                                         'enBanc']))
        treat(b, x, H.choice(['overruled', 'disapproved', 'recededFrom']))
        out['edges'].append([b['node'], x['node']])
    for _ in range(H.randint(1, 2)):
        x = newdec(1101, rdate(H, 1930, 2015))
        b = newdec(1101, cap(add_days(x['date'], H.randint(1, 30 * 365))),
                   bench=H.choice(['panel', 'division', 'unknown', 'circulated']))
        treat(b, x, H.choice(['overruled', 'disapproved']))
    # H2: an explicit supersession of a holding; citing decisions hold on the same issue, on another issue of the
    # same amended block, on an unrelated issue, or on nothing; before and after the law change
    for i in range(H.randint(2, 4)):
        if not lawchanges:
            break
        lc = H.choice(lawchanges)
        en = lc[3]
        x = newdec(H.choice([101, 2906, 1101, 501]), rdate(H, 1900, en // 10000 - 1), bench='enBanc')
        own = 'fed.a' if lc[2] == '42:1983' else 'fed.b'
        xh = holding(x, own if H.random() < 0.8 else H.choice(['fed.a', 'fed.b']))
        if H.random() < 0.3:
            holding(x, 'ca.a')
        sups.append(['sh%d' % i, x['node'], H.choice([xh['issue'], xh['issue'], '-']), lc[0],
                     H.choice(['lawNamesDecision', 'reportNamesDecision', 'quotedWordsStruck']),
                     round(H.random(), 2), 1 if H.random() < 0.85 else 0, 'gen'])
        for _ in range(H.randint(2, 4)):
            if H.random() < 0.8:
                cd = cap(add_days(max(en, lc[4]), H.randint(1, 3000)))
            else:
                cd = add_days(x['date'], H.randint(1, 300))
            y = newdec(H.choice([101, 201, 2906, 501, 1101, 1104]), cd)
            out['edges'].append([y['node'], x['node']])
            r = H.random()
            if r < 0.4:
                holding(y, xh['issue'])
            elif r < 0.7:
                holding(y, H.choice(['fed.c', 'fed.d']))
            elif r < 0.85:
                holding(y, 'ca.a')
    return out


# ---------------------------------------------------------------------------------------------------------------
# Lines layer (REF_NOTES "Revisions: round 2"; DEVIATIONS 79): status per line of authority in splits, conflicts, the
# treatment-level findings and Horty bases. Own random stream, appended after the hunt layer (whose courts 1101-1104
# and adoption 1102 <- 1101 it reuses, with 102 <- 101 of the base generator); treatments and holdings sit only in
# its own new decisions. It adds two source/adopter groups with DATED epochs, so that "the original court is gone" and
# "a decision dated outside its court's epoch" both occur: a Fifth / Eleventh Circuit pair (1201 -> 1202, district
# courts 1203 and 1204) and, in some universes, an Alabama-style division of one intermediate court into two
# (1221 -> 1222 and 1225, one trial court 1223 under both, supreme court 1224).

class _Rare:
    """A `choice` for hold_row that corrupts a certificate rarely (the layer needs its holdings admitted)."""

    def __init__(self, rng):
        self.rng = rng

    def choice(self, seq):
        return 'offset' if self.rng.random() < 0.03 else None


def lines_layer(Q, decs, crows, succ, adopt, srules, issues):
    add = lambda *a: crows.append(list(a))
    out = {'rng': Q, 'holdings': [], 'treatments': [], 'edges': [], 'factors': [], 'factor_cases': []}
    other = lambda a: 'no' if a == 'yes' else 'yes'
    # (1) dated epochs: the source court ends at the cut-off in some universes; the adopter starts the day after
    cut5 = rdate(Q, 1960, 1990)
    gone5 = Q.random() < 0.5
    # (the source court's epoch sometimes starts in 1920: its earlier decisions are dated before their court's epoch)
    add(1201, Q.choice([0, 0, 19200101]), cut5 if gone5 else OPEN,
        'United States Court of Appeals for the Fifth Circuit', 0, 'A', '-', 5, 0, 'gen', 'S')
    add(1202, day_after(cut5), OPEN, 'United States Court of Appeals for the Eleventh Circuit', 0, 'A', '-', 11, 0,
        'gen', 'S')
    add(1203, 0, OPEN, 'United States District Court for the Eastern District of Louisiana', 0, 'T', '-', 5, 0, 'gen',
        'S')
    add(1204, 0, OPEN, 'United States District Court for the Northern District of Georgia', 0, 'T', '-', 11, 0,
        'gen', 'S')
    adopt.append([1202, 1201, cut5, 'all', 'binding', 'gen', Q.choice('SSLU')])
    if gone5 and Q.random() < 0.4:      # the ended court has a successor: a replace row passes its decisions on, a
        add(1205, day_after(cut5), OPEN, 'United States Court of Appeals for the Fifth Circuit (reorganized)', 0,
            'A', '-', 5, 0, 'gen', 'S')   # split row passes nothing (DEVIATIONS 73)
        succ.append([1201, 1205, day_after(cut5), Q.choice(['replace', 'replace', 'split']), 'gen', Q.choice('SL')])
    pairs = [{'src': 101, 'ads': [102], 'cut': adopt[0][2], 'slow': 201, 'alow': 202, 'ends': False},
             {'src': 1101, 'ads': [1102], 'slow': 1104, 'alow': 1103, 'ends': False,
              'cut': next(r[2] for r in adopt if r[0] == 1102 and r[1] == 1101 and r[3] == 'all')},
             {'src': 1201, 'ads': [1202], 'cut': cut5, 'slow': 1203, 'alow': 1204, 'ends': gone5}]
    if Q.random() < 0.3:                # a divisional rule for the D.C. Court of Appeals (H6: binds it to adopted law)
        srules.append([-1102, 'horizontal', 'strong', rdate(Q, 1960, 1990), OPEN, 'gen', Q.choice('SL')])
    if Q.random() < 0.6:
        cut_a = rdate(Q, 1955, 1985)
        gone_a = Q.random() < 0.6
        add(1224, 0, OPEN, 'Supreme Court of Alabama', 61, 'L', 'all', 0, 0, 'gen', 'S')
        add(1221, 0, cut_a if gone_a else OPEN, 'Court of Appeals of Alabama', 61, 'A', '-', 0, 0, 'gen', 'S')
        add(1222, day_after(cut_a), OPEN, 'Court of Civil Appeals of Alabama', 61, 'A', '-', 0, 0, 'gen', 'S')
        add(1225, day_after(cut_a), OPEN, 'Court of Criminal Appeals of Alabama', 61, 'A', '-', 0, 0, 'gen', 'S')
        add(1223, 0, OPEN, 'Alabama Circuit Court', 61, 'T', '-', 0, 1, 'gen', 'S')
        adopt.append([1222, 1221, cut_a, 'all', 'binding', 'gen', Q.choice('UUS')])
        adopt.append([1225, 1221, cut_a, 'all', 'binding', 'gen', Q.choice('SSL')])
        if Q.random() < 0.7:
            succ.append([1221, 1222, day_after(cut_a), 'split', 'gen', 'S'])
            succ.append([1221, 1225, day_after(cut_a), 'split', 'gen', 'S'])
        if Q.random() < 0.7:
            srules.append([61, 'horizontal', Q.choice(['strong', 'strong', 'soft']), 0, OPEN, 'gen', Q.choice('SL')])
        if Q.random() < 0.4:
            srules.append([61, 'trialScope', Q.choice(['statewide', 'statewideChooseOnConflict', 'ownUnitThenAny',
                                                       'ownUnitOnly']), 0, OPEN, 'gen', 'L'])
        pairs.append({'src': 1221, 'ads': [1222, 1225], 'cut': cut_a, 'slow': 1223, 'alow': 1223, 'ends': gone_a,
                      'top': 1224})
    qissues = ['fed.a', 'fed.b', 'fed.c', 'fed.d']     # shared question issues (all federalGeneral)

    def newdec(court, date, unit=0, bench=None):
        x = {'court': court, 'date': date, 'unit': unit,
             'bench': bench or Q.choice(['panel'] * 4 + ['division', 'enBanc', 'unknown']),
             'pub': Q.choice(['published'] * 9 + ['unknown']), 'form': Q.choice(['full'] * 9 + ['perCuriam']),
             'node': len(decs)}
        x['name'] = '%s v. %s' % tuple(Q.sample(WORDS, 2))
        x['cite'] = '%d Rep. %d' % (Q.randint(1, 900), Q.randint(1, 1500))
        x['sent'] = ['%s, %s.' % (x['name'], x['cite'])]
        decs.append(x)
        return x

    def holding(x, issue, ans):
        hid = 'h%d%s' % (x['node'], issue.replace('.', ''))
        if any(h['id'] == hid for h in out['holdings']):
            return None
        prop = 'The answer to %s is %s.' % (issue, ans)
        x['sent'].append('Held: ' + prop)
        h = {'id': hid, 'node': x['node'], 'issue': issue, 'prop': prop, 'answer': ans, 'role': 'majority',
             'loc': (x['node'], len(x['sent']) - 1)}
        out['holdings'].append(h)
        return h

    def treat(b, a, kind, scope='all', explicit=1):
        quote = '%s, %s, %s' % (a['name'], a['cite'], VERB_TEXT[kind])
        tev = ('cite:' + a['cite']) if Q.random() < 0.2 else (
            'name:' + ' '.join(a['name'].replace('.', '').split()[::2]))
        b['sent'].append('We hold that ' + quote + '.')
        out['treatments'].append({
            'id': 'tq%d' % len(out['treatments']), 'by': b['node'], 'target': a['node'], 'date': b['date'],
            'kind': kind, 'scope': scope, 'temporal': Q.choice(['retroactive', 'retroactive', 'unknown']),
            'explicit': explicit, 'quote': quote, 'tev': tev, 'part': 'majority',
            'loc': (b['node'], len(b['sent']) - 1), 'prefix': len('We hold that ')})

    def cap(d):
        return min(d, 20221228)

    def start_of(c):
        return min(r[1] for r in crows if r[0] == c)

    def unit_of(c):
        return Q.randint(0, 2) if c == 1103 else (1 if c == 1223 else 0)

    en_banc = lambda: Q.choice(['enBanc'] * 3 + ['wholeCourt'])
    families = 0

    for P in pairs:
        if Q.random() < 0.2:
            continue
        src, ads, cut = P['src'], P['ads'], P['cut']
        after0 = day_after(cut)
        after = lambda lo, hi: cap(add_days(after0, Q.randint(lo, hi)))

        def before(xd):                 # a date after xd and before the cut-off (xd is at most 28 Dec of the year before)
            d = min(add_days(xd, Q.randint(30, 6 * 365)), add_days(after0, -40))
            return d if d > xd else add_days(xd, 1)

        issue = Q.choice(qissues + (['al.a'] if 'top' in P and Q.random() < 0.3 else []))
        if issue == 'al.a' and not any(i[0] == 'al.a' for i in issues):
            issues.append(('al.a', 'Alabama question', 'stateLaw:61', '-', 'Is H allowed?'))
        a1 = Q.choice(['yes', 'no'])
        mine = []                       # (decision, holding) of this cluster, for the factor rows
        # (3) yes/no holdings of the source court before the cut-off (a conflicting pair in most universes)
        xd = rdate(Q, 1900, cut // 10000 - 1)
        x1 = newdec(src, xd, Q.choice([0, 0, 0, 2]) if src == 101 else (Q.choice([0, 1, 1]) if src == 1221 else 0),
                    bench='panel')
        mine.append((x1, holding(x1, issue, a1)))
        xs = [x1]
        if Q.random() < 0.7:
            x2 = newdec(src, rdate(Q, 1900, cut // 10000 - 1), 0, bench='panel')
            mine.append((x2, holding(x2, issue, other(a1))))
            xs.append(x2)
        ans_of = {x['node']: h['answer'] for (x, h) in mine}
        # certified explicit overrulings by benches that have power: the source court after / before the cut-off,
        # an adopter, SCOTUS (and, in the divided state, its supreme court)
        who = Q.sample(['srcAfter', 'srcAfter', 'srcBefore', 'adopter', 'adopter', 'adopter', 'scotus']
                       + (['top'] if 'top' in P else []), Q.randint(1, 2))
        overruled = []
        for i, k in enumerate(who):
            x = xs[i % len(xs)] if Q.random() < 0.75 else x1
            if k == 'srcBefore':
                bc, bd = src, before(x['date'])
            elif k == 'srcAfter':
                bc, bd = src, after(30, 20 * 365)       # outside the source court's epoch when it ended at the cut-off
            elif k == 'adopter':
                bc, bd = Q.choice(ads), after(30, 20 * 365)
            elif k == 'scotus':
                bc, bd = 2906, after(30, 20 * 365)
            else:
                bc, bd = P['top'], after(30, 20 * 365)
            b = newdec(bc, bd, x['unit'] if bc == src else 0, bench=en_banc())
            treat(b, x, Q.choice(['overruled', 'overruled', 'disapproved', 'abrogated']),
                  ('issues:' + issue) if Q.random() < 0.25 else 'all')
            overruled.append((x, b))
            if Q.random() < 0.7:
                mine.append((b, holding(b, issue, other(ans_of[x['node']]))))
            out['edges'].append([b['node'], x['node']])
        # holdings after the cut-off: the source court (outside its epoch when it ended), each adopter, both lower
        # courts; each may cite the pre-cut-off decisions
        for c in [src] + ads + sorted({P['slow'], P['alow']}):
            for _ in range(Q.randint(0, 2) if c in (P['slow'], P['alow']) else 1):
                if Q.random() < 0.7:
                    y = newdec(c, after(1, 28 * 365), unit_of(c))
                    mine.append((y, holding(y, issue, Q.choice(['yes', 'no']))))
                    if Q.random() < 0.6:
                        out['edges'].append([y['node'], Q.choice(xs)['node']])
        # soft and inferred treatments, claims and panel departures by courts in each line, before and after the
        # overrulings (DEVIATIONS 76)
        for c in [src] + ads + [P['slow'], P['alow']]:
            if Q.random() < 0.55:
                x = Q.choice(xs)
                r = Q.random()
                if r < 0.45:
                    y = newdec(c, after(1, 30 * 365), unit_of(c))
                    treat(y, x, Q.choice(['limited', 'questioned', 'criticized', 'declinedToFollow']))
                elif r < 0.7:
                    y = newdec(c, after(1, 30 * 365), unit_of(c), bench=en_banc())
                    treat(y, x, 'overruled', explicit=0)
                else:
                    y = newdec(c, after(1, 30 * 365), unit_of(c), bench=Q.choice(['panel', 'panel', 'division']))
                    treat(y, x, Q.choice(['overruled', 'disapproved']))
        # a later contrary holding that binds a holder (contraryBinding): SCOTUS, after everything
        if Q.random() < 0.3 and issue != 'al.a':
            y = newdec(2906, cap(add_days(after0, Q.randint(31 * 365, 34 * 365))))
            mine.append((y, holding(y, issue, other(a1))))
        # (2) decisions dated outside their court's epoch: an adopter before it starts, as a citing decision, a
        # treating decision and a target; the ended source court after the cut-off as a target
        for a in ads:
            if start_of(a) > 19000101 and Q.random() < 0.6:
                y = newdec(a, before(x1['date']), 0, bench=en_banc())
                out['edges'].append([y['node'], x1['node']])
                r = Q.random()
                if r < 0.4:
                    treat(y, x1, 'overruled')
                elif r < 0.8:
                    mine.append((y, holding(y, issue, Q.choice(['yes', 'no']))))
                    b = newdec(Q.choice([src, a, 2906]), after(30, 10 * 365), 0, bench=en_banc())
                    treat(b, y, 'overruled')
        if P['ends'] and Q.random() < 0.7:
            y = newdec(src, after(30, 10 * 365), 0)
            mine.append((y, holding(y, issue, Q.choice(['yes', 'no']))))
            b = newdec(Q.choice(ads + [2906, src]), cap(add_days(y['date'], Q.randint(30, 5 * 365))), 0,
                       bench=en_banc())
            treat(b, y, 'overruled')
            out['edges'].append([newdec(P['slow'], cap(add_days(b['date'], Q.randint(1, 900))),
                                        unit_of(P['slow']))['node'], y['node']])
        # citing decisions in each line, after the overrulings
        last = max([b['date'] for (_, b) in overruled] + [after0])
        for c in [src, P['slow'], P['alow']] + ads:
            if Q.random() < 0.5:
                y = newdec(c, cap(add_days(last, Q.randint(1, 8 * 365))), unit_of(c))
                out['edges'].append([y['node'], Q.choice(xs)['node']])
        # (4) factor rows: the family is the holding's own issue, or a factor_cases.tsv key
        mode = Q.choice(['own', 'cases', 'cases', 'mixed'])
        families += 1
        fam = 'lines%d_%s' % (families, issue.replace('.', ''))
        pool = [(1, 'pi'), (2, 'pi'), (3, 'delta'), (4, 'delta')]
        for (x, h) in mine:
            if h is None or Q.random() > (0.95 if x in xs else 0.7):
                continue
            outcome = h['answer']
            listed = mode == 'cases' or (mode == 'mixed' and Q.random() < 0.5)
            if listed and Q.random() < 0.06:
                outcome = other(outcome)            # the family row may give another outcome than the answer
            side = 'pi' if outcome == 'yes' else 'delta'
            facts = [f for f in pool if Q.random() < 0.75]
            own = [f for f in facts if f[1] == side]
            if not own:
                own = [Q.choice([f for f in pool if f[1] == side])]
                facts = sorted(facts + own)
            reason = Q.sample(own, 1 if Q.random() < 0.8 else len(own))
            for f in facts:
                out['factors'].append([h['id'], f[0], f[1], 1 if f in reason else 0])
            if listed:
                row = lambda key, oc: [h['id'], x['node'], key, 'horty:' + key, oc, x['date'], len(facts),
                                       ','.join(str(f[0]) for f in sorted(reason)), 1, 'gen', key.split('_')[0]]
                if Q.random() < 0.08:
                    out['factor_cases'].append(row(fam + '_old', other(outcome)))   # replaced by the later row
                out['factor_cases'].append(row(fam, outcome))
                if Q.random() < 0.08:
                    out['factor_cases'].append(row(fam + '_x', 'mixed'))            # another outcome: ignored
    return out


# ---------------------------------------------------------------------------------------------------------------
# Round-5 layer (caselaw-lean-2/round5/DESIGN5.md; REF_NOTES "Round 5"). Own random stream, appended after the lines
# layer; it adds no court and no rule, and its rows sit only in its own new decisions (an old decision's text, and
# so its sha, never changes). It writes what no earlier layer wrote: witness rows (round 4: a later decision W
# says "X was overruled by Y"), treatment_witness.tsv, and treatment_class.tsv with `recognised` and
# `operativeWords` claims that pass and that fail each step of DESIGN5 §2.2 and §3.2, bad class rows, and, in about
# one universe in eight, no class table at all (round-4 mode with witness rows).

# (target court, courts of the overruling decision Y, courts of the witness W): W in the target's court of last
# resort has power; a panel of the target's own court has standing and, under a strong horizontal rule, no power;
# a lower or sister court has neither. A court that the universe does not have is skipped.
R5_CFG = [
    (2906, (2906,), (2906, 2906, 2906, 2906, 101, 501)),
    (101, (2906, 2906, 101, 101, 102), (2906, 2906, 2906, 2906, 101, 101, 201, 102)),
    (502, (501, 501, 502, 2906), (501, 501, 501, 501, 502, 503, 2906)),
    (703, (701, 702, 703, 704, 2906), (701, 701, 701, 701, 703, 705, 702)),
    (201, (101, 2906, 201), (101, 101, 2906, 2906, 201)),
    (902, (901, 901, 902, 2906), (901, 901, 901, 901, 902, 903)),
    (1002, (1001, 1001, 1002), (1001, 1001, 1001, 1002, 1002)),
]
R5_ISSUES = {0: ['fed.a', 'fed.b', 'unk.a'], 5: ['ca.a', 'fed.a', 'unk.a'], 44: ['tx.a', 'fed.a'],
             10: ['fl.a', 'fed.a'], 36: ['fed.a', 'unk.a']}
# Round-5 test quotes are built at run time from the lists of the generated cue table (cue_table.py; never copied
# here), so a change of a list changes the quotes with it. A slot is filled with one phrase of a list, stripped,
# between single spaces: {c} `recognised` (witness) or `operative`, {w} `operative_whole`, {l} `operative_limit`,
# {D} `disqualify_recognised` (witness) or `disqualify_operative`, {T} `disqualify_treat`, {s} `self_announced`.
# Each template names the case it tests, and the finished quote is checked against the lists as they stand
# (r5_layer, `fits`): a quote that is not exactly its case (a "whole" quote with a limit phrase or a disqualifier,
# a cue that is itself a whole phrase, a fixed sentence the lists no longer read that way) is drawn again.
# witness sentences: (weight, case, sentence template, quote template). {X} and {Y} are "name, cite". Cases:
# 'cue' = a recognition cue and no recognition disqualifier; 'dq' = a disqualifier; 'nocue' = no recognition cue.
R5_WITNESS = [
    (6, 'cue', 'We note {q}.', 'the {c}ing of {X} by {Y}'),
    (6, 'cue', 'As we have said, {q}.', '{X} was {c}ed by {Y}'),                 # round 4: "overruled by" disqualifies
    (3, 'cue', 'In our view {q}.', '{X} has been {c}ed by {Y}'),
    (1, 'cue', 'We recall that {q}.', '{X} was {c}ed in {Y}'),
    (1.5, 'nocue', 'It follows that {q}.', '{X} is no longer good law after {Y}'),
    (0.7, 'nocue', 'We add that {q}.', '{X} must be read in the light of {Y}'),
    (1.5, 'dq', 'We do not decide {q}.', 'on {D} the {c}ing of {X} by {Y}'),
    (1.5, 'cue', 'We turn to {X}. We recall {q}.', 'the {c}ing of that decision by {Y}'),   # X in the window
    (1.5, 'cue', 'See {Y}. It was there that {q}.', 'the {c}ing of {X} occurred'),          # Y in the window
]
# the kind a witness row states for a recognition cue (it need not agree with the cue: one row in seven does not)
R5_KIND_OF_CUE = {'overrul': 'overruled', 'abrogat': 'abrogated', 'disapprov': 'disapproved', 'reced': 'recededFrom'}
# operative sentences: (weight, case, sentence template, quote template). The case is the exact set of properties
# of the quote: c = a phrase of `operative`, w = of `operative_whole`, l = of `operative_limit`; 'd' = a
# disqualifier (`disqualify_treat` or `disqualify_operative`), whatever else; '' = no operative cue, no disqualifier.
R5_OPERATIVE = [
    (3, 'cw', 'We hold that {q}.', 'of {X} we say: {w}'),                                   # whole
    (3, 'c', 'Today {q}.', 'of {X} we say: {c}'),                                           # not whole: demoted
    (2.5, 'cwl', 'We hold that {q}.', 'of {X} we say, {l} it is contrary to this finding: {w}'),   # whole + limit
    (1.5, 'cl', 'Today {q}.', 'of {X} we say, {l} it is contrary to this finding: {c}'),
    (2, 'd', 'Today {q}.', 'of {X} and the {D} we say: {c}'),                               # the new disqualifiers
    (1, 'd', 'Today {q}.', 'of {X} and the {D} we say: {w}'),
    (1, 'd', 'Today {q}.', 'of {X} and the {T} we say: {c}'),                               # the round-4 ones
    (2, '', 'We hold that {q}.', '{X} is disapproved'),                                     # no operative cue
    (1, 'cw', 'We turn to {X}. {q}.', 'Of that decision we say: {w}'),                      # target in the window
    (1, 'c', 'We turn to {X}. {q}.', 'Of that decision we say: {c}'),
    (1, 'c', 'Today {q}.', 'of {X} we say: {c} and {s}'),                                   # and self-announced
    (1, 'cw', 'We hold that {q}.', '{X} is no longer good law'),
    (1, 'cw', 'We hold that {q}.', '{X} must be regarded as overthrown'),
    (1, 'c', 'We hold that {q}.', 'any language in {X} contrary to this finding is rejected'),
    (1, 'cwl', 'We hold that {q}.', 'in the field of public education {X} is no longer good law'),
]
R5_FIELD = ['-', '-', '-', 'in the field of public education', 'as respects interstate carriers']
R5_DOCTRINE = ['-', '-', '-', 'separate but equal', 'the rule of the earlier case']


def r5_layer(V, decs, crows, issues, old_treat_ids):
    sys.path.insert(0, HERE)
    import cue_table as cues
    # the lists as they stand in the generated table (read here, at run time; none is copied into this file)
    cue_list = lambda name: [p for p in getattr(cues, name, ()) if p.strip()]
    REC, DQ_REC = cue_list('RECOGNISED'), cue_list('DISQUALIFY_RECOGNISED')
    OPV, OPW, OPL = cue_list('OPERATIVE'), cue_list('OPERATIVE_WHOLE'), cue_list('OPERATIVE_LIMIT')
    DQ_OP, DQ_TREAT, SELF = cue_list('DISQUALIFY_OPERATIVE'), cue_list('DISQUALIFY_TREAT'), cue_list('SELF_ANNOUNCED')
    has = lambda q, phrases: any(p in q.lower() for p in phrases)
    slot = lambda phrases: V.choice(phrases).strip() if phrases else 'zzz'

    def fits(case, q, witness):
        """Is the finished quote exactly the case its template names, under the lists as they stand?"""
        if witness:
            cue, dq = has(q, REC), has(q, DQ_REC)
            return {'cue': cue and not dq, 'dq': dq, 'nocue': not cue}[case]
        props = ''.join(k for (k, ph) in (('c', OPV), ('w', OPW), ('l', OPL)) if has(q, ph))
        dq = has(q, DQ_TREAT) or has(q, DQ_OP)
        return dq if case == 'd' else (not dq and props == case)

    def draw(table, witness, **names):
        """A template and its quote, slots filled from the lists; drawn again until the quote is its case."""
        for _ in range(60):
            t = pick(table)
            c = slot(REC if witness else OPV)
            q = t[3].format(c=c, w=slot(OPW), l=slot(OPL), D=slot(DQ_REC if witness else DQ_OP),
                            T=slot(DQ_TREAT), s=slot(SELF), **names)
            if fits(t[1], q, witness):
                break
        return t, c, q

    have = {r[0] for r in crows}
    system = {r[0]: r[4] for r in crows}
    tier = {r[0]: r[5] for r in crows}
    unit0 = {r[0]: r[8] for r in crows}
    cfgs = [(x, [c for c in ys if c in have], [c for c in ws if c in have]) for (x, ys, ws) in R5_CFG if x in have]
    cfgs = [c for c in cfgs if c[1] and c[2]]
    ikeys = {i[0] for i in issues}
    out = {'rng': V, 'holdings': [], 'treatments': [], 'history': [], 'edges': [], 'witness': [], 'klass': []}
    pick = lambda table: V.choices(table, [t[0] for t in table])[0]

    def newdec(court, date, bench=None):
        u = V.randint(1, 3) if court in (502, 902) else (unit0.get(court, 0) if tier.get(court) in ('A', 'T') else 0)
        x = {'court': court, 'date': date, 'unit': u,
             'bench': bench or V.choice(['panel'] * 3 + ['enBanc'] * 3 + ['wholeCourt', 'division', 'unknown']),
             'pub': V.choice(['published'] * 9 + ['unknown']), 'form': V.choice(['full'] * 9 + ['perCuriam']),
             'node': len(decs)}
        x['name'] = '%s v. %s' % tuple(V.sample(WORDS, 2))
        x['cite'] = '%d Rep. %d' % (V.randint(1, 900), V.randint(1, 1500))
        x['sent'] = ['%s, %s.' % (x['name'], x['cite'])]
        decs.append(x)
        return x

    def sentence(x, text):
        x['sent'].append(text)
        return (x['node'], len(x['sent']) - 1)

    def holding(x, issue):
        hid = 'h%d%s' % (x['node'], issue.replace('.', ''))
        if issue not in ikeys or any(h['id'] == hid for h in out['holdings']):
            return None
        ans = V.choice(['yes', 'no'])
        prop = 'The answer to %s is %s.' % (issue, ans)
        h = {'id': hid, 'node': x['node'], 'issue': issue, 'prop': prop, 'answer': ans, 'role': 'majority',
             'loc': sentence(x, 'Held: ' + prop)}
        out['holdings'].append(h)
        return h

    def ref(x):
        return '%s, %s' % (x['name'], x['cite'])

    def evidence(x):
        return ('cite:' + x['cite']) if V.random() < 0.4 else (
            'name:' + ' '.join(x['name'].replace('.', '').split()[::2]))

    def cap(d):
        return min(d, 20221228)

    def scope_for(x):
        hk = [h['issue'] for h in out['holdings'] if h['node'] == x['node']]
        r = V.random()
        if r < 0.6:
            return 'all'
        if r < 0.85:
            return 'issues:' + (V.choice(hk) if (hk and V.random() < 0.8) else V.choice(sorted(ikeys)))
        return 'partialUnknown' if r < 0.93 else 'otherGrounds'

    def temporal_for(d):
        r = V.random()
        return 'retroactive' if r < 0.45 else ('unknown' if r < 0.85 else (
            'pureProspective' if r < 0.93 else 'prospectiveFrom:%d' % (d + V.randint(0, 3) * 10000)))

    def klass(tid, claim):
        out['klass'].append([tid, claim, V.choice(R5_FIELD), V.choice(R5_DOCTRINE), 'gen'])

    def lapse(x, lo, hi, tag):
        """A same-case event on x in its own text (by = -1), dated in [lo, hi]; sometimes reinstated later."""
        kind = V.choice(['withdrawn', 'withdrawn', 'vacated', 'vacated', 'reversed', 'depublished', 'substitutedBy',
                         'rehearingEnBancGranted'])
        hk = [h['issue'] for h in out['holdings'] if h['node'] == x['node']]
        scope = V.choice(['all'] * 8 + ['unknown'] + (['issues:' + V.choice(hk)] if hk else ['all']))
        d = cap(add_days(lo, V.randint(0, max(0, days_between(lo, hi)))))
        n = len(out['history'])

        def row(k, date):
            quote = 'The opinion %s' % VERB_TEXT[k]
            out['history'].append({'id': 'yr%d%s' % (len(out['history']), tag), 'target': x['node'], 'by': -1,
                                   'date': date, 'kind': k, 'scope': scope if k != 'reinstated' else 'all',
                                   'quote': quote, 'tev': 'name:' + x['name'].split()[0], 'part': 'majority',
                                   'loc': sentence(x, quote + '.'), 'prefix': 0})
        row(kind, d)
        if V.random() < 0.35:
            row('reinstated', cap(add_days(d, V.randint(1, 2500))))
        return n

    def citers(x, cfg, marks):
        """New decisions citing x on or around the dates in `marks` (date(Y), date(W)): before Y, on the day of Y,
        between Y and W, on the day of W, after W; some hold on one of x's issues."""
        hk = [h['issue'] for h in out['holdings'] if h['node'] == x['node']]
        lows = [c for c in ({2906: (101, 501, 201), 101: (201,), 502: (503, 504), 703: (705,), 201: (),
                             902: (903,), 1002: ()}.get(cfg[0], ())) if c in have]
        pool = [cfg[0]] * 2 + cfg[2] + lows * 3
        lo = x['date'] or 19600101
        ds = sorted(d for d in marks if d)
        pts = []
        if ds:
            y0, w0 = ds[0], ds[-1]
            if y0 > lo:
                pts.append(add_days(lo, V.randint(0, max(0, days_between(lo, y0) - 1))))       # before Y
            pts.append(y0)                                                                     # the day of Y
            if w0 > y0:
                pts.append(add_days(y0, V.randint(0, max(0, days_between(y0, w0) - 1))))       # between
                pts.append(add_days(y0, V.randint(0, max(0, days_between(y0, w0) - 1))))
            pts.append(w0)                                                                     # the day of W
            pts.append(cap(add_days(w0, V.randint(1, 4000))))                                  # after W
            pts.append(cap(add_days(w0, V.randint(1, 9000))))
        for d in V.sample(pts, min(len(pts), V.randint(2, 5))):
            c = newdec(V.choice(pool), d)
            out['edges'].append([c['node'], x['node']])
            if hk and V.random() < 0.3:
                holding(c, V.choice(hk))

    # --- witness rows (round 4), most with a recognised claim
    for i in range(V.randint(5, 9)):
        cfg = V.choice(cfgs)
        variant = V.choice(['ok'] * 16 + ['zeroX', 'zeroY', 'zeroW', 'sameEv', 'rowDate', 'rowDate', 'earlierW',
                                          'laterX'])
        xd = rdate(V, 1960, 1995)
        yd = cap(add_days(xd, V.randint(30, 12 * 365)))
        wd = yd if V.random() < 0.12 else cap(add_days(yd, V.randint(1, 12 * 365)))
        if variant == 'earlierW':
            wd = add_days(yd, -V.randint(1, 300))
        if variant == 'laterX':
            xd = add_days(yd, V.randint(1, 300))
        x = newdec(cfg[0], xd, bench=V.choice(['panel'] * 4 + ['enBanc', 'unknown']))
        for k in V.sample(R5_ISSUES.get(system[cfg[0]], ['fed.a']), V.choice([0, 1, 1, 2])):
            holding(x, k)
        y = newdec(V.choice(cfg[1]), yd)
        w = newdec(V.choice(cfg[2]), wd)
        if variant == 'sameEv':
            y['name'] = '%s v. %s' % (x['name'].split()[0], y['name'].split()[-1])
            y['sent'][0] = '%s, %s.' % (y['name'], y['cite'])
        ((_, case, stpl, _), cue, quote) = draw(R5_WITNESS, True, X=ref(x), Y=ref(y))
        kind = R5_KIND_OF_CUE.get(cue, 'overruled') if case != 'nocue' else 'overruled'
        if V.random() < 0.15:
            kind = V.choice(['overruled', 'abrogated', 'disapproved', 'recededFrom'])   # kind and cue need not agree
        sent = stpl.format(X=ref(x), Y=ref(y), q=quote)
        loc = sentence(w, sent)
        tev, bev = evidence(x), evidence(y)
        if variant == 'sameEv':
            tev = bev = 'name:' + x['name'].split()[0]
        r = V.random()
        if r < 0.05:
            bev = 'cite:1 Rep. 1'                         # the by-evidence resolves to nothing
        elif r < 0.08:
            bev = tev                                      # the same evidence for X and Y
        if variant == 'zeroX':
            x['date'] = 0
        elif variant == 'zeroY':
            y['date'] = 0
        elif variant == 'zeroW':
            w['date'] = 0
        r = V.random()
        explicit = 1 if r < 0.025 else 0                   # a witness row marked explicit: witnessBadRow
        if 0.025 <= r < 0.05:
            kind = V.choice(['limited', 'questioned'])     # not a status-changing kind: witnessBadRow
        rowdate = y['date']
        if variant == 'rowDate' and y['date']:
            # the row's date column is not Y's date: later, earlier, or 0 (never used: DESIGN5 §9, A-7)
            rowdate = V.choice([cap(add_days(y['date'], V.randint(1, 4000))), add_days(y['date'], -V.randint(1, 4000)), 0])
        tid = 'tr%d' % i
        out['treatments'].append({
            'id': tid, 'by': y['node'], 'target': x['node'], 'date': rowdate, 'kind': kind, 'scope': scope_for(x),
            'temporal': temporal_for(yd), 'explicit': explicit, 'quote': quote, 'tev': tev,
            'part': V.choice(['majority'] * 20 + ['perCuriam', 'plurality', 'dissent', 'concurrence']),
            'loc': loc, 'prefix': sent.index(quote), 'owner': w['node']})
        wn = w['node'] if V.random() < 0.975 else len(decs) + 5000 + i     # an unknown witness node
        out['witness'].append([tid, wn, bev, 'gen'])
        r = V.random()
        if r < 0.72:
            klass(tid, 'recognised')
        elif r < 0.8:
            klass(tid, 'operativeWords')                   # a claim that means nothing on a witness row
        made_tx = False
        if V.random() < 0.12 and y['date'] and x['date']:  # an explicit row by Y for the same pair
            made_tx = True
            q2 = '%s, %s' % (ref(x), VERB_TEXT['overruled'])
            out['treatments'].append({
                'id': 'tx%d' % i, 'by': y['node'], 'target': x['node'], 'date': y['date'], 'kind': 'overruled',
                'scope': V.choice(['all', 'all', 'partialUnknown']), 'temporal': 'retroactive', 'explicit': 1,
                'quote': q2, 'tev': 'cite:' + x['cite'], 'part': 'majority',
                'loc': sentence(y, 'We hold that ' + q2 + '.'), 'prefix': len('We hold that ')})
        if y['date'] and V.random() < 0.2:                 # Y lapses: between Y and W, or after W
            hi = w['date'] if (w['date'] and w['date'] > y['date'] and V.random() < 0.55) else cap(
                add_days(max(y['date'], w['date'] or 0), 3000))
            lapse(y, y['date'], hi, 'y')
        if w['date'] and V.random() < 0.14:                # W lapses
            lapse(w, w['date'], cap(add_days(w['date'], 3000)), 'w')
        if y['date'] and not made_tx and V.random() < 0.05:
            # a lapse event of Y dated BEFORE date(Y): ignored by a recognised effect (DESIGN5 §9, A-14). Only where
            # Y makes no explicit row: for those the reference's round-4 lapse test differs (NOTES.md A-14).
            lapse(y, add_days(y['date'], -900), add_days(y['date'], -1), 'p')
        if V.random() < 0.7:
            out['edges'].append([y['node'], x['node']])    # Y's own citation of X
        if V.random() < 0.7:
            out['edges'].append([w['node'], x['node']])
        out['edges'].append([w['node'], y['node']])
        citers(x, cfg, [y['date'], w['date']])
    # --- operative words (DESIGN5 §3): ordinary explicit rows, most with an operativeWords claim
    for i in range(V.randint(2, 5)):
        cfg = V.choice(cfgs)
        xd = rdate(V, 1960, 1995)
        yd = cap(add_days(xd, V.randint(30, 12 * 365)))
        x = newdec(cfg[0], xd, bench=V.choice(['panel'] * 4 + ['enBanc', 'unknown']))
        for k in V.sample(R5_ISSUES.get(system[cfg[0]], ['fed.a']), V.choice([0, 1, 1, 2])):
            holding(x, k)
        y = newdec(V.choice(cfg[1]), yd, bench=V.choice(['enBanc'] * 3 + ['wholeCourt', 'panel', 'unknown']))
        ((_, case, stpl, _), _, quote) = draw(R5_OPERATIVE, False, X=ref(x))
        sent = stpl.format(X=ref(x), q=quote)
        r = V.random()
        kind = 'disapproved' if r < 0.85 else ('overruled' if r < 0.93 else V.choice(['recededFrom', 'limited']))
        tid = 'to%d' % i
        # (DESIGN5 §9, A-7: the row's date column is never used; in one row of twelve it is not the by-decision's
        # date, and one of those in four is 0)
        rowdate = y['date'] if V.random() < 0.92 else V.choice([cap(add_days(y['date'], V.randint(1, 4000)))] * 2
                                                               + [add_days(y['date'], -V.randint(1, 4000)), 0])
        out['treatments'].append({
            'id': tid, 'by': y['node'], 'target': x['node'], 'date': rowdate, 'kind': kind, 'scope': scope_for(x),
            'temporal': temporal_for(yd), 'explicit': 1 if V.random() < 0.93 else 0, 'quote': quote,
            'tev': evidence(x), 'part': V.choice(['majority'] * 12 + ['dissent']), 'loc': sentence(y, sent),
            'prefix': sent.index(quote)})
        r = V.random()
        if r < 0.75:
            klass(tid, 'operativeWords')
        elif r < 0.82:
            klass(tid, 'recognised')                       # a claim that means nothing on a non-witness row
        if V.random() < 0.15:
            lapse(y, y['date'], cap(add_days(y['date'], 3000)), 'o')
        out['edges'].append([y['node'], x['node']])
        citers(x, cfg, [y['date'], y['date']])
    # --- claims on rows of the earlier layers, bad class rows, a shuffled table; sometimes no table at all
    for tid in V.sample(old_treat_ids, min(len(old_treat_ids), V.randint(0, 3))):
        klass(tid, V.choice(CLAIMS5))
    good = [r[0] for r in out['klass']]
    if V.random() < 0.6:
        ids = good + [t['id'] for t in out['treatments']]
        for what in V.sample(['short', 'claim', 'id', 'dup', 'dup', 'long', 'empty'], V.randint(1, 4)):
            tid = V.choice(ids)
            if what == 'short':
                out['klass'].append([tid, V.choice(CLAIMS5), '-', '-'])                       # 4 fields
            elif what == 'claim':
                out['klass'].append([tid, V.choice(['implied', 'Recognised', '']), '-', '-', 'gen'])
            elif what == 'id':
                out['klass'].append(['nosuch%d' % V.randint(0, 99), V.choice(CLAIMS5), '-', '-', 'gen'])
            elif what == 'dup' and good:                                                      # the first line wins
                g = V.choice(good)
                out['klass'].append([g, V.choice(CLAIMS5), V.choice(R5_FIELD), V.choice(R5_DOCTRINE), 'gen dup'])
            elif what == 'long':                                                              # 6 fields: bad too
                out['klass'].append([tid, V.choice(CLAIMS5), '-', '-', 'gen', 'a sixth field'])
            elif what == 'empty':
                out['klass'].append(['', V.choice(CLAIMS5), '-', '-', 'gen'])
    V.shuffle(out['klass'])
    if V.random() < 0.12:
        out['klass'] = None                                # round-4 mode: witness rows, no class table
    return out


CLAIMS5 = ['recognised', 'operativeWords']


def days_between(a, b):
    import datetime
    f = lambda d: datetime.date(d // 10000, d // 100 % 100, d % 100)
    return (f(b) - f(a)).days


def write(path, rows):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write('\t'.join(str(v) for v in r) + '\n')


def big(n, out):
    """Scale test: real-sized decisions2.tsv (n rows) on the fixture skeleton."""
    src = os.path.join(WORK, 'fixtures', 'data')
    os.makedirs(os.path.join(out, 'data'), exist_ok=True)
    for fn in os.listdir(src):
        if fn != 'decisions2.tsv':
            with open(os.path.join(src, fn), encoding='utf-8') as a, open(os.path.join(out, 'data', fn), 'w',
                                                                           encoding='utf-8', newline='\n') as b:
                b.write(a.read())
    R = random.Random(7)
    courts_ = [2906, 346, 241, 367, 268, 918, 917, 522, 524, 10000, 10001, 10002]
    with open(os.path.join(src, 'decisions2.tsv'), encoding='utf-8') as a:
        head = a.read()
    with open(os.path.join(out, 'data', 'decisions2.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(head)
        start = len(head.splitlines())
        for i in range(start, n):
            f.write('%d\t%d\t%d\t%d\tpanel\tpublished\tfull\t%040x\tgen\n' % (
                i, R.choice(courts_), rdate(R), R.randint(0, 3), R.getrandbits(160)))


def mutant_check(a, py):
    """For each deliberately broken reference variant, count rounds in which diff.py reports disagreements."""
    sys.path.insert(0, HERE)
    from precedent_ref import MUTANTS
    caught = {m: 0 for m in MUTANTS}
    for r in range(a.rounds):
        seed = a.seed + r
        d = os.path.join(a.out, 'm%04d' % seed)
        generate(seed, d, a.n, getattr(a, 'legacy', False), r5=not getattr(a, 'no_r5', False))
        args = ['--data', os.path.join(d, 'data'), '--edges', os.path.join(d, 'edges')]
        subprocess.run([py, os.path.join(HERE, 'precedent_ref.py'), 'run'] + args + ['--out', os.path.join(d, 'ref')],
                       check=True, stderr=subprocess.DEVNULL)
        for m in MUTANTS:
            env = dict(os.environ, PREF_MUTANT=m)
            o = os.path.join(d, 'mut_' + m)
            subprocess.run([py, os.path.join(HERE, 'precedent_ref.py'), 'run'] + args + ['--out', o], check=True,
                           stderr=subprocess.DEVNULL, env=env)
            p = subprocess.run([py, os.path.join(HERE, 'diff.py'), o, os.path.join(d, 'ref'), '--quiet'],
                               capture_output=True, text=True)
            caught[m] += p.returncode != 0
    for m in MUTANTS:
        print('%-26s caught in %d/%d rounds' % (m, caught[m], a.rounds))


LEAN_EXE = os.path.join(WORK, 'runner', '.lake', 'build', 'bin', 'caselaw2.exe' if os.name == 'nt' else 'caselaw2')
LEAN_HEADERS = {
    'status': 'node\tissue\tholding\tfrom\tto\tstatus\tclass\tfirm\twitness_row\tactor\tpath',
    'findings': 'finding\tciting\tcited\tissue\tdetail\tfirm\tpath',
    'certs': 'table\tid\tresult_all\tresult_firm',
    'splits': 'kind\tissue\tcourt1\tcourt2\tanswers1\tanswers2\tholdings1\tholdings2\tasOf\tfirm',
    # round 2 (DEVIATIONS 75, 78): the Lean runner always writes status_lines-00.tsv and horty-00.tsv
    'status_lines': 'node\tissue\tholding\tfrom\tto\tstatus\tclass\tfirm\twitness_row\tactor\tpath\tline',
    'horty': 'family\tcourt\tverdict\tcases\tfirm',
}
# round 5 (DESIGN5 §5.1): in round-5 mode (the data directory has treatment_class.tsv) the status, status_lines and
# findings headers gain `oclass`, and there is one more file, classes.tsv
R5_OCLASS = ('status', 'status_lines', 'findings')
CLASSES_HEADER = 'id\tclass\tclaim\tverdict\tfield_limit\tdoctrine\twitness'


def lean_headers(data_dir):
    """The header lines of the Lean runner's merged files for a data directory, as run_lean.sh writes them."""
    if not os.path.exists(os.path.join(data_dir, 'treatment_class.tsv')):
        return dict(LEAN_HEADERS)
    h = {k: v + ('\toclass' if k in R5_OCLASS else '') for k, v in LEAN_HEADERS.items()}
    h['classes'] = CLASSES_HEADER
    return h


def merge_lean(d):
    """Merge the single shard the runner wrote in d/lean as run_lean.sh merges shards: header line + body. The
    round-5 shard file is assumed to be classes-00.tsv, by the pattern of the others; when the runner wrote none,
    no classes.tsv is made and diff.py reports it as missing."""
    out = os.path.join(d, 'lean')
    for name, head in lean_headers(os.path.join(d, 'data')).items():
        src = os.path.join(out, '%s-00.tsv' % name)
        if name == 'classes' and not os.path.exists(src):
            continue
        with open(src, encoding='utf-8') as a:
            body = a.read()
        with open(os.path.join(out, name + '.tsv'), 'w', encoding='utf-8', newline='\n') as b:
            b.write(head + '\n' + body)
        os.remove(src)
    os.replace(os.path.join(out, 'summary-00.tsv'), os.path.join(out, 'summary.tsv'))


def fwd(p):
    return p.replace('\\', '/')


LEAN_PROOFS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
RUN_LEAN_SRC = 'LegalProofs/CaseLaw2/Run.lean'


def lean_env():
    return dict(os.environ, PATH=os.path.expanduser('~/.elan/bin') + os.pathsep + os.environ.get('PATH', ''))


def build_lean():
    """Build the compiled runner once (run_lean.sh does this on every call). A failure is reported, not fatal:
    run_lean falls back to the interpreter when the executable cannot be launched (e.g. blocked by Windows
    Application Control) or when CASELAW2_INTERP=1."""
    if os.environ.get('CASELAW2_INTERP') == '1':
        return
    try:
        subprocess.run(['lake', 'build', 'caselaw2'], cwd=os.path.join(WORK, 'runner'), check=True,
                       stdout=subprocess.DEVNULL, env=lean_env())
    except (OSError, subprocess.CalledProcessError) as e:
        print('warning: lake build caselaw2 failed (%s); run_lean will use the interpreter' % e, file=sys.stderr)


def _launch_lean(args):
    """The compiled runner, or `lake env lean --run Run.lean` (cwd lean-proofs) when it cannot be launched."""
    if os.environ.get('CASELAW2_INTERP') != '1':
        try:
            subprocess.run([LEAN_EXE] + args, check=True, stdout=subprocess.DEVNULL)
            return
        except OSError as e:            # PermissionError ("an Application Control policy has blocked this file")
            print('warning: %s not launchable (%s); using the interpreter' % (LEAN_EXE, e), file=sys.stderr)
    subprocess.run(['lake', 'env', 'lean', '--run', RUN_LEAN_SRC] + args, cwd=LEAN_PROOFS, check=True,
                   stdout=subprocess.DEVNULL, env=lean_env())


def run_lean(d, asof=20261112):
    """One shard of the compiled runner on universe d (the program run_lean.sh shards), merged as run_lean.sh
    merges: d/lean/{status,findings,certs,splits,summary}.tsv with header lines."""
    out = os.path.join(d, 'lean')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(d, 'data', 'decisions2.tsv'), encoding='utf-8') as f:
        nodes = 1 + max([int(l.split('\t', 1)[0]) for l in f if l.strip()] or [0])
    _launch_lean([fwd(os.path.join(d, 'data')), fwd(os.path.join(d, 'edges')), '0', '1', fwd(out), str(nodes),
                  str(asof)])
    merge_lean(d)


def one_round(job):
    """Generate, run the reference and/or the Lean, diff canonically."""
    seed, d, a = job
    n = generate(seed, d, a.n, getattr(a, 'legacy', False), not getattr(a, 'no_hunt', False),
                 not getattr(a, 'no_lines', False), not getattr(a, 'no_r5', False))
    py = sys.executable
    if a.ref:
        # (round 5: a round-4 run writes no classes.tsv; one left by an earlier run in the same directory must go)
        import shutil
        shutil.rmtree(os.path.join(d, 'ref'), ignore_errors=True)
        subprocess.run([py, os.path.join(HERE, 'precedent_ref.py'), 'run', '--data', os.path.join(d, 'data'),
                        '--edges', os.path.join(d, 'edges'), '--out', os.path.join(d, 'ref')], check=True,
                       stderr=subprocess.DEVNULL)
    if a.lean:
        run_lean(d)
    if not (a.diff and a.lean and a.ref):
        return seed, n, ''
    sys.path.insert(0, HERE)
    import diff as dmod
    D, missing = dmod.compare(os.path.join(d, 'lean'), os.path.join(d, 'ref'), dmod.load_map(a.map))
    with open(os.path.join(d, 'diff.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for r in D.rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    files = dmod.FILES + tuple(fn for fn in dmod.FILES5 if D.compared[fn])
    summ =' | '.join('%s %d/%d' % (fn, D.bad_keys[fn], D.compared[fn]) for fn in files)
    rows = [(seed,) + tuple(r) for r in D.rows]
    return seed, n, summ, rows, dict(D.compared), dict(D.bad_keys), dict(D.info)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--n', type=int, default=60, help='decisions per universe')
    ap.add_argument('--rounds', type=int, default=1)
    ap.add_argument('--out', required=True)
    ap.add_argument('--ref', action='store_true', help='run precedent_ref.py on each universe')
    ap.add_argument('--lean', action='store_true', help='run the compiled caselaw-lean-2 runner on each universe')
    ap.add_argument('--diff', action='store_true', help='diff Lean vs reference canonically (needs --lean --ref)')
    ap.add_argument('--map', help='label map for diff.py (default ref/labels.json)')
    ap.add_argument('--jobs', type=int, default=8, help='rounds in parallel (at most 16)')
    ap.add_argument('--legacy', action='store_true',
                    help='the universe as generated before the five-limits layer (old seeds, row for row)')
    ap.add_argument('--no-hunt', action='store_true',
                    help='omit the hunt layer (H2/H3b/H4 patterns): the universe as generated before it')
    ap.add_argument('--no-lines', action='store_true',
                    help='omit the lines layer (round 2, per-line status): the universe as generated before it')
    ap.add_argument('--no-r5', action='store_true',
                    help='omit the round-5 layer (witness rows, class table): the universe as generated before it')
    ap.add_argument('--keep', action='store_true', help='keep every universe (default: only disagreeing ones)')
    ap.add_argument('--quiet', action='store_true', help='no per-round lines')
    ap.add_argument('--big', type=int, help='write a scale-test universe with this many decisions')
    ap.add_argument('--mutants', action='store_true',
                    help='harness self-test: diff the reference against each PREF_MUTANT variant of itself')
    a = ap.parse_args()
    if a.big:
        big(a.big, a.out)
        return
    py = sys.executable
    if a.mutants:
        mutant_check(a, py)
        return
    if a.lean:
        build_lean()
    jobs = [(a.seed + r, os.path.join(a.out, 'r%05d' % (a.seed + r)) if a.rounds > 1 else a.out, a)
            for r in range(a.rounds)]
    import shutil
    from collections import Counter
    from multiprocessing import Pool
    buckets, keys, comp, bad, info = Counter(), {}, Counter(), Counter(), Counter()
    disagreeing = 0
    allrows = []
    with Pool(max(1, min(16, a.jobs))) as pool:
        for res in pool.imap_unordered(one_round, jobs):
            seed, n, summ = res[:3]
            if len(res) > 3:
                rows, c, b, inf = res[3], res[4], res[5], res[6]
                comp.update(c)
                bad.update(b)
                info.update(inf)
                allrows.extend(rows)
                seen = set()
                for r in rows:
                    k = (r[1], r[2], r[3])
                    if k in seen:
                        continue
                    seen.add(k)
                    buckets[k] += 1               # rounds in which this class occurs
                    keys.setdefault(k, []).append((seed, r[4], r[5], r[6]))
                if rows:
                    disagreeing += 1
                elif not a.keep and a.rounds > 1:
                    shutil.rmtree(os.path.join(a.out, 'r%05d' % seed), ignore_errors=True)
            if not a.quiet:
                print('seed %d: %d decisions  %s' % (seed, n, summ), flush=True)
    if a.diff and a.lean and a.ref:
        with open(os.path.join(a.out, 'drt_diff.tsv'), 'w', encoding='utf-8', newline='\n') as f:
            for r in sorted(allrows, key=lambda r: tuple(str(x) for x in r)):
                f.write('\t'.join(str(x) for x in r) + '\n')
        print('\n%d rounds, %d with a disagreement' % (a.rounds, disagreeing))
        for fn in ('status', 'findings', 'certs', 'splits', 'conflicts', 'lines', 'horty') + tuple(
                fn for fn in ('classes', 'summary') if comp[fn]):
            print('  %-9s %d of %d keys disagree' % (fn, bad[fn], comp[fn]))
        print('  class (file, bucket, rule): rounds   first example')
        for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]):
            print('  %-9s %-36s %-26s %5d   e.g. seed %s %s A=%s B=%s' % (k + (v,) + keys[k][0]))
        for k, v in sorted(info.items()):
            print('  info  %-60s %d' % (k, v))


if __name__ == '__main__':
    main()
