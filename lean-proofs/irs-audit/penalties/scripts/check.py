#!/usr/bin/env python3
"""parsed.json -> rows.tsv -> Lean classifier -> classified.tsv; plus opinion-level tags (decision form, §6751(b),
substantial-understatement statements against a deficiency of at most $5,000)."""
import os, re, json, subprocess, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
P = json.load(open(H + '/data/parsed.json'))
rows = []; meta = {}
for o in P:
    if o['status'] != 'parsed':
        continue
    for k, r in enumerate(o['recs']):
        if r.get('pen') is None or r['deficiency'] is None:
            continue
        rid = '%s#%d' % (o['id'], k)
        pd = {s: v for s, v in r['pen'].items() if v is not None}
        for a, b in (('6662', '6662(a)'), ('6651', '6651(a)(1)')):
            if a in pd and b in pd and pd[a] == pd[b]:
                del pd[a]
        if '6651' in pd and '6651(a)(1)' not in pd and '6651(a)(2)' not in pd:
            pd['6651(a)(1)'] = pd.pop('6651')
        pens = ';'.join('%s=%d' % (s, round(v * 100)) for s, v in pd.items())
        rows.append('%s\t%d\t%d\t%s' % (rid, r['year'], round(r['deficiency'] * 100), pens))
        meta[rid] = dict(o, rec=r)
open(H + '/data/rows.tsv', 'w').write('\n'.join(rows) + '\n')
env = dict(os.environ, PATH=os.path.expanduser('~/.elan/bin:') + os.environ['PATH'])
print(subprocess.run(['lake', 'exe', 'run', H + '/data/rows.tsv', H + '/data/classified.tsv'], cwd=H + '/lean', env=env,
                     capture_output=True, text=True).stdout)
cls = collections.defaultdict(list)
for l in open(H + '/data/classified.tsv'):
    rid, y, k, v = l.rstrip('\n').split('\t'); cls[rid].append((k, v))


def decision(title):
    t = (title or '').lower()
    if 'rule 155' in t: return 'Rule 155'
    if 'for respondent' in t: return 'for respondent'
    if 'for petitioner' in t: return 'for petitioner'
    if 'appropriate' in t or 'will be entered' in t: return 'other order/decision'
    return 'unstated'


summary = collections.Counter(); per_check = collections.Counter(); flags = []
for rid, lst in cls.items():
    for k, v in lst:
        lab = v.split(':')[0]
        per_check[(k, v)] += 1
        if v.startswith('FLAG') or v.startswith('CHECK'):
            m = meta[rid]
            flags.append(dict(rid=rid, cite=m.get('cite'), docket=m.get('docket'), year=m['rec']['year'], deficiency=m['rec']['deficiency'],
                              pen=m['rec']['pen'], check=k, label=v, decision=decision(m.get('title')), title=m.get('title')))
json.dump(flags, open(H + '/data/flags.json', 'w'), indent=1)
for (k, v), n in sorted(per_check.items()):
    print('%-8s %5d  %s' % (k, n, v))
print('flags', len(flags))
for f in flags:
    print(f['cite'], f['year'], f['deficiency'], f['pen'], '|', f['label'], '|', f['decision'])

# opinion-level tags from the full text
tags = collections.Counter(); su = []
for o in P:
    if o['status'] == 'duplicate':
        continue
    fn = H + '/data/txt/%s.txt' % o['id']
    if not os.path.exists(fn):
        continue
    t = re.sub(r'\s+', ' ', open(fn, errors='ignore').read())
    if re.search(r'6751\s?\(b\)', t):
        tags['mentions 6751(b)'] += 1
        if re.search(r'(?:did not|failed to|has not|could not|didn.t)\s+(?:obtain|secure|show|establish|produce|introduce|offer|prove|meet)[^.]{0,160}(?:supervisory approval|section 6751\(b\)|written approval)', t, re.I):
            tags['6751(b): IRS failed to show approval (phrase match)'] += 1
    if o['status'] == 'parsed':
        for r in o['recs']:
            if r.get('pen') and any(s.startswith('6662') for s in r['pen']) and r['deficiency'] is not None and r['deficiency'] <= 5000:
                for m in re.finditer(r'[^.]{0,250}substantial understatement[^.]{0,250}\.', t, re.I):
                    s = m.group(0)
                    if re.search(r'\b(?:is|was|constitutes?|are|were|has|have)\b[^.]{0,60}substantial understatement|understatement[^.]{0,80}\bis substantial\b|exceeds? (?:the greater of )?\$?5,000', s, re.I) \
                            and not re.search(r'not (?:a )?substantial|no substantial|does not exceed|did not exceed', s, re.I):
                        su.append(dict(id=o['id'], cite=o.get('cite'), year=r['year'], deficiency=r['deficiency'], sentence=s.strip()[:500]))
                        break
json.dump(su, open(H + '/data/su_candidates.json', 'w'), indent=1)

# coarse court outcome on the accuracy-related penalty, per opinion (phrase match; reported as such)
ACCP = r'(?:the |an |a |any )?(?:section 6662(?:\(a\))?\s+)?(?:accuracy-related |negligence )?penalt(?:y|ies)(?: under section 6662(?:\(a\))?)?'
outc = collections.Counter(); per_op = {}
for o in P:
    fn = H + '/data/txt/%s.txt' % o['id']
    if o['status'] != 'parsed' or not os.path.exists(fn):
        continue
    if not any(r.get('pen') and any(s.startswith('6662') for s in r['pen']) for r in o['recs']):
        continue
    t = re.sub(r'\s+', ' ', open(fn, errors='ignore').read())
    tail = t[len(t) // 3:]
    no = re.search(r'(?:is|are) not liable for ' + ACCP + r'|not sustain\w* (?:respondent.s )?(?:determination of )?' + ACCP + r'|respondent (?:has )?conceded? ' + ACCP, tail, re.I)
    yes = re.search(r'(?:is|are) liable for ' + ACCP + r'|sustain\w* (?:respondent.s )?(?:determination (?:of|that petitioners? (?:is|are) liable for) )?' + ACCP, tail, re.I)
    k = 'sustained in whole or part' if yes and not no else 'not sustained / conceded' if no and not yes else 'mixed (some years or petitioners)' if yes and no else 'unclear (no holding phrase found)'
    outc[k] += 1; per_op[o['id']] = k
json.dump(per_op, open(H + '/data/court_outcome.json', 'w'))
print('court outcome on 6662 (opinions with a stated 6662 amount):', dict(outc))
print(dict(tags)); print('substantial-understatement statements with deficiency <= $5,000:', len(su))
for s in su[:40]:
    print('--', s['cite'], s['year'], s['deficiency'], s['sentence'][:300])
