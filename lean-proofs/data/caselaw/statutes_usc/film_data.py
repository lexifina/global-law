import collections, json, random, re, html
random.seed(1995)
names, years = {}, {}
for l in open('versions.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    if f[2] == 'law':
        names.setdefault(f[3], html.unescape(f[6])); years.setdefault(f[3], f[4][:4])
ch = []
for l in open('versions.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    d = int(f[4])
    if f[2] == 'law' and d >= 19950104:
        ch.append([round(d // 10000 + ((d // 100) % 100 - 1) / 12, 2), int(re.match(r'title-(\d+)', f[0]).group(1))])
cit = []; S = collections.Counter(); dec = set(); decb = set(); first = collections.defaultdict(set); yr = collections.defaultdict(lambda: [0, 0])
for l in open('results/rows_out.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    a, sd = f[5] == '1', f[10] == '1'; both = a and sd
    S['rows'] += 1; S['both'] += both; dec.add(f[1])
    yr[int(f[2][:4])][0] += 1; yr[int(f[2][:4])][1] += both
    if both: decb.add(f[1]); first[f[8]].add(f[1])
    if f[4]: S['rows_sub'] += 1; S['both_sub'] += both
    if random.random() < 40000 / 1931153:
        d = f[2]
        cit.append([round(int(d[:4]) + (int(d[5:7]) - 1) / 12, 2), int(f[3].split()[0]), 2 if both else (1 if a else 0),
                    round(int(f[7][:4]) + (int(f[7][5:7]) - 1) / 12, 2) if f[7] else 0])
summ = json.load(open('results/summary.json'))
laws = sorted(first, key=lambda k: -len(first[k]))
out = dict(rows=S['rows'], both=S['both'], rows_sub=S['rows_sub'], both_sub=S['both_sub'], decisions=len(dec), decisions_both=len(decb),
           by_year={y: v for y, v in sorted(yr.items())}, laws=[[k, names.get(k, ''), years.get(k, ''), len(first[k])] for k in laws[:30]])
json.dump(out, open('results/changed_words.json', 'w'), indent=1)
json.dump({'ch': ch, 'cit': cit}, open('film_points.json', 'w'), separators=(',', ':'))
print({k: v for k, v in out.items() if k not in ('by_year', 'laws')}); print(out['laws'][:8])
