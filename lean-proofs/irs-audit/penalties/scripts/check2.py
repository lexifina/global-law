#!/usr/bin/env python3
"""Run 2: data2/parsed.json -> rows.tsv -> Lean classifier (8 shards in parallel) -> classified.tsv -> flags.json,
plus opinion-level tags: substantial-understatement statements on small deficiencies, the 6665(b)(1) late-return
pattern, 6751(b) outcomes (phrase match), court outcome on 6662."""
import os, re, json, subprocess, collections
from multiprocessing import Pool
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
D2 = H + '/data2'
P = json.load(open(D2 + '/parsed.json'))
NORM = {'6663(a)': '6663', '6654(a)': '6654', '6651(aX1)': '6651(a)(1)', '6651(a)(l)': '6651(a)(1)', '6651(a)(I)': '6651(a)(1)',
        '6662(c)': '6662(a)', '6662(d)': '6662(a)', '6662(e)': '6662(a)', '6662(g)': '6662(a)', '6662(b)(1)': '6662(a)', '6662(b)(2)': '6662(a)',
        '6651(f)(1)': '6651(f)', '6651(a)(2)(A)': '6651(a)(2)'}
DROP = {'6664'}


def rows_of(o):
    out = []
    for k, r in enumerate(o['recs']):
        if not r.get('pen') or r.get('deficiency') is None:
            continue
        pd = {}
        for s, v in r['pen'].items():
            if v is None or s in DROP:
                continue
            s = NORM.get(s, s)
            pd[s] = pd.get(s, 0) + v if s not in pd or pd[s] != v else v
        for a, b in (('6662', '6662(a)'),):
            if a in pd and b in pd and pd[a] == pd[b]:
                del pd[a]
        if '6662' in pd and '6662(a)' not in pd:
            pd['6662(a)'] = pd.pop('6662')
        if '6651' in pd and '6651(a)(1)' not in pd and '6651(a)(2)' not in pd:
            pd['6651(a)(1)'] = pd.pop('6651')
        if not pd:
            continue
        out.append(('%s#%d' % (o['id'], k), r['year'], r['deficiency'], pd, r))
    return out


def run_shard(i):
    env = dict(os.environ, PATH=os.path.expanduser('~/.elan/bin:') + os.environ['PATH'])
    r = subprocess.run([H + '/lean/.lake/build/bin/run', '%s/rows_%d.tsv' % (D2, i), '%s/cls_%d.tsv' % (D2, i)], cwd=H + '/lean', env=env, capture_output=True, text=True)
    return r.stdout.strip() + r.stderr.strip()


LATE = re.compile(r'(?:filed|submitted|received)[^.]{0,80}?(?:late|untimely|delinquent|after the due date)|late[- ]filed|untimely[- ]filed|delinquent(?:ly)?[- ](?:filed )?returns?|filed (?:his|her|their|its|the) [^.]{0,40}returns? (?:on|in) [A-Z][a-z]+ \d{1,2}, (?:19|20)\d\d|substitute for return|section 6020\(b\)|did not file|failed to file', re.I)


def tags(o):
    fn = D2 + '/txt/%s.txt' % o['id']
    if not os.path.exists(fn):
        return o['id'], None
    t = re.sub(r'\s+', ' ', open(fn, errors='ignore').read())
    res = {}
    if re.search(r'6751\s?\(b\)', t):
        res['6751b'] = 'mentioned'
        lost = re.search(r'(?:did not|failed to|has not|could not|didn.t|not)\s+(?:obtain|secure|show|establish|produce|introduce|offer|prove|meet|satisfy|comply)[^.]{0,160}(?:supervisory approval|section 6751\(b\)|sec\. 6751\(b\)|written approval)|(?:no|without)[^.]{0,30}(?:written )?supervisory approval[^.]{0,80}(?:was|were) (?:obtained|shown)|approval[^.]{0,60}(?:was|were) not (?:timely|obtained|personally)|(?:concedes?|conceded)[^.]{0,80}penalt[^.]{0,80}6751', t, re.I)
        met = re.search(r'(?:satisfied|met|complied with|compliance with|carried (?:his|its) burden[^.]{0,60})[^.]{0,80}(?:section|sec\.) 6751\(b\)|6751\(b\)[^.]{0,80}(?:was|were|is) (?:satisfied|met)|(?:obtained|secured|received) (?:timely )?(?:written )?supervisory approval|supervisory approval[^.]{0,80}(?:was|were) (?:timely )?(?:obtained|secured|given|received)', t, re.I)
        res['6751b'] = 'IRS failed (phrase)' if lost and not met else 'IRS met (phrase)' if met and not lost else 'both phrases' if met and lost else 'mentioned only'
    res['late'] = bool(LATE.search(t))
    su = []
    for m in re.finditer(r'[^.]{0,250}substantial understatement[^.]{0,250}\.', t, re.I):
        s = m.group(0)
        if re.search(r'\b(?:is|was|constitutes?|are|were|has|have)\b[^.]{0,60}substantial understatement|understatement[^.]{0,80}\bis substantial\b|exceeds? (?:the greater of )?\$?5,000', s, re.I) \
                and not re.search(r'not (?:a )?substantial|no substantial|does not exceed|did not exceed|if |whether|would', s, re.I):
            su.append(s.strip()[:500])
    res['su'] = su[:3]
    ACCP = r'(?:the |an |a |any )?(?:section 6662(?:\(a\))?\s+)?(?:accuracy-related |negligence )?penalt(?:y|ies)(?: under section 6662(?:\(a\))?)?'
    tail = t[len(t) // 3:]
    no = re.search(r'(?:is|are) not liable for ' + ACCP + r'|not sustain\w* (?:respondent.s )?(?:determination of )?' + ACCP + r'|respondent (?:has )?conceded? ' + ACCP, tail, re.I)
    yes = re.search(r'(?:is|are) liable for ' + ACCP + r'|sustain\w* (?:respondent.s )?(?:determination (?:of|that petitioners? (?:is|are) liable for) )?' + ACCP, tail, re.I)
    res['acc_outcome'] = 'sustained in whole or part' if yes and not no else 'not sustained / conceded' if no and not yes else 'mixed' if yes and no else 'no holding phrase'
    return o['id'], res


if __name__ == '__main__':
    rows = []; meta = {}
    for o in P:
        if o['status'] != 'parsed':
            continue
        for rid, y, d, pd, r in rows_of(o):
            pens = ';'.join('%s=%d' % (s, round(v * 100)) for s, v in pd.items())
            rows.append('%s\t%d\t%d\t%s' % (rid, y, round(d * 100), pens))
            meta[rid] = dict(id=o['id'], cite=o.get('cite'), docket=o['docket'], year=y, deficiency=d, pen=pd, decision=o['decision'],
                             title=o['title'], type=o['type'], year_filed=o['year_filed'], src=r.get('src'))
    open(D2 + '/rows.tsv', 'w').write('\n'.join(rows) + '\n')
    for i in range(8):
        open('%s/rows_%d.tsv' % (D2, i), 'w').write('\n'.join(rows[i::8]) + '\n')
    with Pool(8) as p:
        print(p.map(run_shard, range(8)))
    cls = collections.defaultdict(list); lines = []
    for i in range(8):
        for l in open('%s/cls_%d.tsv' % (D2, i)):
            rid, y, k, v = l.rstrip('\n').split('\t'); cls[rid].append((k, v)); lines.append(l)
    open(D2 + '/classified.tsv', 'w').write(''.join(lines))
    per = collections.Counter(); flags = []
    for rid, lst in cls.items():
        for k, v in lst:
            per[(k, v)] += 1
            if v.startswith('FLAG') or v.startswith('CHECK'):
                flags.append(dict(meta[rid], rid=rid, check=k, label=v))
    json.dump(flags, open(D2 + '/flags.json', 'w'), indent=0)
    json.dump({rid: dict(meta[rid], labels=cls[rid]) for rid in cls}, open(D2 + '/rowmeta.json', 'w'))
    for (k, v), n in sorted(per.items()):
        print('%-8s %6d  %s' % (k, n, v))
    print('rows', len(rows), 'flag rows', len(flags), 'flag opinions', len({f['id'] for f in flags}))
    with Pool(8) as p:
        T = dict(p.map(tags, [o for o in P if o['status'] != 'not fetched'], chunksize=50))
    json.dump(T, open(D2 + '/tags.json', 'w'))
    c = collections.Counter(v['6751b'] for v in T.values() if v and '6751b' in v)
    print('6751(b):', dict(c))
