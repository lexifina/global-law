"""Print, for each flagged opinion, the determination passage and context lines that bear on the flag."""
import json, re, sys
P = json.load(open('data/parsed.json')); by = {o['id']: o for o in P}
F = json.load(open('data/flags.json'))
skip = set(sys.argv[1:])
seen = set()
for f in F:
    oid = f['rid'].split('#')[0]
    if oid in seen or f['cite'] in skip: continue
    seen.add(oid)
    t = re.sub(r'\s+', ' ', open('data/lay/%s.txt' % oid).read())
    m = re.search(r'(?:Respondent|respondent|notice|Notice|Commissioner)[^.]{0,140}?determined', t)
    print('########', f['cite'], '| docket', f['docket'], '|', f['decision'])
    print('FLAGS:', [(g['year'], g['deficiency'], g['pen'], g['label'][6:]) for g in F if g['rid'].split('#')[0] == oid])
    print('TEXT:', t[max(0, m.start() - 100):m.start() + 1100] if m else t[:800])
    full = re.sub(r'\s+', ' ', open('data/txt/%s.txt' % oid).read())
    for k in re.finditer(r'[^.]{0,200}(?:carry ?back|in the alternative|alternatively)[^.]{0,200}', full, re.I):
        print('  CTX:', k.group(0)[:400]); break
    print()
