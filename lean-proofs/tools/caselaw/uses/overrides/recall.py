"""Recall on the gold set (Christiansen & Eskridge 2014 + Hasen 2013, decisions 1995-2011 overridden by 2011), and,
for each gold item we miss, the first step at which it falls out.

    python recall.py   -> recall.tsv, recall.json
"""
import collections, csv, json, os, re
W = os.path.expanduser('~/Documents/us-caselaw-lean-work'); O = f'{W}/uses/overrides'
csv.field_size_limit(10 ** 9)
idx = {}
for l in open(f'{W}/graph/cite_index.tsv', encoding='utf-8'):
    k, v = l.rstrip('\n').split('\t')
    if ' us ' in k: idx[k] = v
gold = list(csv.DictReader(open(f'{O}/gold/gold.tsv', encoding='utf-8'), delimiter='\t'))
rows_by_node = collections.defaultdict(list)
for l in open(f'{W}/usc/results/rows_out.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); rows_by_node[f[1]].append(f)
cand_by_node = collections.defaultdict(list)
for l in open(f'{O}/cand_rows.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); cand_by_node[f[1]].append(f)
pairs = {}
for x in csv.DictReader(open(f'{O}/pairs.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
    pairs[(x['nid'], x['law'])] = x
cand = {(x['nid'], x['law']) for x in csv.DictReader(open(f'{O}/overrides.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
allv = collections.defaultdict(list)
for l in open(f'{W}/usc/versions.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    if f[2] == 'law': allv[f[3]].append(f[0])
ranked = sorted(pairs.values(), key=lambda x: -float(x['score']))
rank = {(x['nid'], x['law']): i + 1 for i, x in enumerate(ranked)}
out = []
S = collections.Counter()
for g in gold:
    law = g['overriding_law']
    nid = idx.get(re.sub(r'\s+', ' ', g['us_cite'].lower().replace('.', '')))
    st = ''
    info = {}
    if not nid:
        st = '1 decision not in the record'
    elif not rows_by_node[nid]:
        st = '2 cites no US Code section we can read'
    elif not allv.get(law):
        st = '3 the law changed no section of the Code in our record'
    else:
        cited = {(r[3]) for r in rows_by_node[nid]}
        lawsecs = {p for p in allv[law]}
        touched = {s for s in cited if f"title-{s.split(' U.S.C. ')[0]}/{s.split('§ ')[1]}.md" in lawsecs}
        info['cited'] = len(cited); info['law_touches'] = ';'.join(sorted(touched))
        fl = {r[8] for r in cand_by_node[nid]}
        if not touched:
            st = '4 the law changed none of the sections the decision cites'
        elif law not in fl:
            # touched the section, but not first / not the cited words
            others = sorted({r[8] + ' ' + str(r[9]) for r in cand_by_node[nid] if f'{r[4]} U.S.C. § {r[5]}' in touched})
            st = '5 the law amended a cited section, but was not the first to rewrite the cited words'
            info['first_instead'] = ';'.join(others)
        else:
            p = pairs[(nid, law)]
            info.update(gap=p['gap'], law_match=p['law_match'], report_match=p['report_match'], qstruck=p['qstruck'],
                        score=p['score'], rank=rank[(nid, law)])
            if (nid, law) in cand:
                st = '0 found'
            elif int(p['gap']) > 120:
                st = '6 outside the ten-year window'
            else:
                st = '7 no evidence signal'
    S[st] += 1
    out.append(dict(decision=g['decision'], cite=g['us_cite'], law=law, status=st, node=nid or '', **info))
with open(f'{O}/recall.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    keys = ['decision', 'cite', 'law', 'status', 'node', 'cited', 'law_touches', 'first_instead', 'gap', 'law_match',
            'report_match', 'qstruck', 'score', 'rank']
    fo.write('\t'.join(keys) + '\n')
    for x in out:
        fo.write('\t'.join(str(x.get(k, '')) for k in keys) + '\n')
json.dump(dict(sorted(S.items())), open(f'{O}/recall.json', 'w'), indent=1)
print(json.dumps(dict(sorted(S.items())), indent=1))
