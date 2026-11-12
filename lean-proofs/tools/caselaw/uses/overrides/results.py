"""Results: audit precision by stratum and at the top of the ranking, recall on the gold set, candidates and confirmed
overrides per Congress, and the confirmed overrides not on the gold list.

    python results.py   -> results.json, per_congress.tsv, confirmed.tsv
"""
import collections, csv, glob, json, math, os, re
O = os.path.expanduser('~/Documents/us-caselaw-lean-work/uses/overrides')
NL, TAB = chr(10), chr(9)
csv.field_size_limit(10 ** 9)
pairs = {(p['nid'], p['law']): p for p in csv.DictReader(open(f'{O}/pairs.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
# Lean decides: a pair is a candidate when Lean flags at least one of its citations (lean/out.tsv, window 10 years)
leanc = set()
for l in open(f'{O}/lean/out.tsv', encoding='utf-8'):
    f = l.rstrip(NL).split(TAB)
    if f[4] == '1': leanc.add(f[0])
cand = [p for p in pairs.values() if any(r in leanc for r in p['rids'].split(','))]
candk = {(p['nid'], p['law']) for p in cand}
py = {(p['nid'], p['law']) for p in pairs.values() if p['evidence'] == '1' and int(p['gap']) <= 120}
lab = {}       # (nid, law) -> verdict
tags = collections.defaultdict(set)
for kf in glob.glob(f'{O}/audit/key_*.json'):
    mode = kf.split('key_')[1][:-5]
    key = json.load(open(kf))
    for of in glob.glob(f'{O}/audit/out_{mode}_*.json'):
        for v in json.load(open(of, encoding='utf-8')):
            t, nid, law = key[v['id']].split('|')
            lab[(nid, law)] = v; tags[(nid, law)].add(t)
OV = ('override_express', 'override_implicit')
def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))
R = {}
# precision by evidence kind (stratum sample or census), counting each audited pair by its final kind
RAND = {'law names it': 'N', 'report names it': 'R', 'quoted words struck': 'Q'}
for kind in ('law names it', 'report names it', 'quoted words struck'):
    # only the census (N) and the random samples (R, Q) estimate a stratum's precision; top-ranked and gold items do not
    items = [lab[k] for k in lab if k in candk and pairs[k]['kind'] == kind and RAND[kind] in tags[k]]
    n = len(items); ov = sum(v['label'] in OV for v in items); ex = sum(v['label'] == 'override_express' for v in items)
    R[kind] = dict(audited=n, of=sum(1 for p in cand if p['kind'] == kind), override=ov, express=ex,
                   labels=dict(collections.Counter(v['label'] for v in items)), ci=wilson(ov, n),
                   name_check=dict(collections.Counter(v.get('name_check', '') for v in items)))
# top of the ranking
ranked = sorted(cand, key=lambda p: -float(p['score']))
for N in (10, 20, 30):
    top = [(p['nid'], p['law']) for p in ranked[:N]]
    got = [lab[k] for k in top if k in lab]
    R[f'top{N}'] = dict(audited=len(got), override=sum(v['label'] in OV for v in got), express=sum(v['label'] == 'override_express' for v in got))
base = [lab[k] for k in lab if 'B' in tags[k]]
R['baseline_non_candidates'] = dict(audited=len(base), override=sum(v['label'] in OV for v in base),
                                    labels=dict(collections.Counter(v['label'] for v in base)))
R['candidates'] = len(cand)
R['python_window_candidates'] = len(py)
R['lean_candidate_citations'] = len(leanc)
# Quoted-words stratum by court level (the sample was stratified 25 appeals/Supreme Court, 20 other courts)
for g, ts in (('SA', 'SA'), ('FT', 'FT')):
    items = [lab[k] for k in lab if k in candk and pairs[k]['kind'] == 'quoted words struck' and 'Q' in tags[k] and pairs[k]['tier'] in ts]
    R[f'quoted_{g}'] = dict(audited=len(items), override=sum(v['label'] in OV for v in items),
                            of=sum(1 for p in cand if p['kind'] == 'quoted words struck' and p['tier'] in ts),
                            ci=wilson(sum(v['label'] in OV for v in items), len(items)))
# estimated overrides among the candidates: stratum size x stratum precision
lo = hi = mid = 0.0
for kind in ('law names it', 'report names it'):
    r = R[kind]
    mid += r['of'] * r['override'] / r['audited']; lo += r['of'] * r['ci'][0]; hi += r['of'] * r['ci'][1]
for g in ('SA', 'FT'):
    r = R[f'quoted_{g}']
    mid += r['of'] * r['override'] / max(1, r['audited']); lo += r['of'] * r['ci'][0]; hi += r['of'] * r['ci'][1]
R['estimated_overrides_in_candidates'] = [round(lo), round(mid), round(hi)]
gi = [lab[k] for k in lab if 'G' in tags[k] or (k in candk and (pairs[k]['cite'], pairs[k]['law']) in {(g['us_cite'], g['overriding_law']) for g in csv.DictReader(open(f'{O}/gold/gold.tsv', encoding='utf-8'), delimiter=TAB)})]
R['auditor_on_gold'] = dict(audited=len(gi), override=sum(v['label'] in OV for v in gi), labels=dict(collections.Counter(v['label'] for v in gi)))
R['candidates_by_tier'] = dict(collections.Counter(p['tier'] for p in cand))
R['candidates_by_kind'] = dict(collections.Counter(p['kind'] for p in cand))
R['recall'] = json.load(open(f'{O}/recall.json'))
# per Congress (the law's Congress)
pc = collections.defaultdict(lambda: collections.Counter())
for p in cand:
    c = int(re.match(r'Pub\. L\. (\d+)', p['law']).group(1))
    pc[c]['candidates'] += 1; pc[c][p['kind']] += 1
    if p['tier'] == 'S': pc[c]['supreme_court'] += 1
    k = (p['nid'], p['law'])
    if k in lab and lab[k]['label'] in OV: pc[c]['confirmed'] += 1
with open(f'{O}/per_congress.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    cols = ['candidates', 'law names it', 'report names it', 'quoted words struck', 'supreme_court', 'confirmed']
    fo.write('congress\tyears\t' + '\t'.join(cols) + '\n')
    for c in sorted(pc):
        y0 = 1789 + 2 * (c - 1)
        fo.write(f'{c}\t{y0}-{y0 + 2}\t' + '\t'.join(str(pc[c][x]) for x in cols) + '\n')
# confirmed overrides, flagged when on the gold list
gold = list(csv.DictReader(open(f'{O}/gold/gold.tsv', encoding='utf-8'), delimiter='\t'))
gk = {(g['us_cite'], g['overriding_law']) for g in gold}
with open(f'{O}/confirmed.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    fo.write('label\ton_gold_list\tnew_because\tdecided\ttier\tdecision\tcite\tlaw\ttitle\tlaw_day\tmonths\tkind\tname_check\tpoint\tchange\twhy\n')
    conf = []
    for k, v in lab.items():
        if v['label'] not in OV: continue
        p = pairs[k]
        on = (p['cite'], p['law']) in gk
        why = '' if on else ('law after 2011' if int(p['law_day']) >= 20120101 else ('lower court' if p['tier'] != 'S' else 'not on the lists'))
        conf.append((p['decided'], v['label'], on, why, p, v))
    for d, l, on, why, p, v in sorted(conf, key=lambda x: x[0]):
        why = why + (' (gold check)' if 'G' in tags[(p['nid'], p['law'])] else '')
        fo.write('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ') for x in [l, int(on), why, p['decided'], p['tier'], p['name'], p['cite'], p['law'], p['title'], p['law_day'], p['gap'], p['kind'], v.get('name_check', ''), v['point'], v['change'], v['why']]) + '\n')
R['confirmed'] = len(conf)
R['confirmed_on_gold'] = sum(1 for c in conf if c[2])
R['confirmed_new'] = dict(collections.Counter(c[3] for c in conf if not c[2]))
cols = ['nid', 'decided', 'tier', 'name', 'cite', 'law', 'law_day', 'title', 'gap', 'sections', 'kind', 'score', 'law_match', 'report_match', 'report',
        'near_strong', 'law_strong', 'mentions', 'interp', 'qin', 'qstruck', 'struck_hits', 'quote', 'repo', 'path', 'law_snip', 'report_snip', 'rids']
with open(f'{O}/overrides.tsv', 'w', encoding='utf-8', newline=NL) as fo:
    fo.write(TAB.join(cols + ['on_gold_list', 'audit_label', 'audit_why']) + NL)
    gk2 = {(g['us_cite'], g['overriding_law']) for g in gold}
    for p in sorted(cand, key=lambda p: -float(p['score'])):
        k = (p['nid'], p['law']); v = lab.get(k, {})
        why = v.get('why', '').replace(TAB, ' ').replace(NL, ' ')
        fo.write(TAB.join([str(p[c]) for c in cols] + [str(int((p['cite'], p['law']) in gk2)), v.get('label', ''), why]) + NL)
json.dump(R, open(f'{O}/results.json', 'w'), indent=1)
print(json.dumps(R, indent=1))
