"""Whole-code scan for lists a later law forgot to update.

    python -I tools/hunt/stale_lists.py            -> tools/hunt/out/stale/stale.json, stale.txt

When a public law adds a new subdivision N beside older siblings (say §23(a)(4) beside (a)(1)–(3)), every provision
elsewhere that enumerates those siblings is a place the drafters had to decide whether N belongs. This finds the
places they did not touch: provisions R, unchanged by the law that added N, which today refer to two or more of N's
older siblings and not to N. It is strongest where the same law did update another such list ("partner"), which
shows the drafters knew lists needed conforming and missed this one.

History: the united-states-law git clone (~/Documents/usc-history/clone), one commit per public law since the 2017
edition. References: the resolved references in t26.json (current text).
"""
import json, os, re, subprocess, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
REPO = os.path.expanduser('~/Documents/usc-history/clone')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'tools', 'hunt', 'out', 'stale'); os.makedirs(OUT, exist_ok=True)
P = json.load(open(os.path.expanduser('~/Documents/tax-formalization-data/out/t26.json'), encoding='utf-8'))['provisions']
PRE = '/us/usc/t26/s'
BY = {p['id']: p for p in P if p['id'].startswith(PRE)}
KIDS = defaultdict(list)
for i, p in BY.items(): KIDS[p['parent']].append(i)


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


LINE = re.compile(r'^(\s*)- \(([0-9A-Za-z]+)\)\s?(.*)$')


def parse(md, sec):
    """markdown of one section -> {id: own text}"""
    out, stack = {}, []
    cur = None
    for ln in md.split('\n'):
        m = LINE.match(ln)
        if m:
            d = len(m.group(1)) // 2
            stack = stack[:d] + [m.group(2)]
            cur = PRE + sec + '/' + '/'.join(stack)
            out[cur] = m.group(3).strip()
        elif cur and ln.strip() and not ln.startswith('#'):
            out[cur] += ' ' + ln.strip()
    return out


def targets(p):
    t = set()
    for r in p.get('rel', []) + p.get('secrefs', []):
        if r.get('historical'): continue
        if r.get('target'): t.add(r['target'])
    for r in p.get('refs', []):
        if isinstance(r, str): t.add(r)
        elif isinstance(r, dict) and r.get('target'): t.add(r['target'])
    return t


TG = {i: targets(p) for i, p in BY.items()}
RANGE = {i for i, p in BY.items() if any(r.get('range') for r in p.get('rel', []) + p.get('secrefs', []))}
commits = [l.split('|', 2) for l in git('log', '--reverse', '--format=%H|%ad|%s', '--date=short', '--', 'title-26').strip().split('\n')]
commits = [c for c in commits if not c[2].startswith('Printed text differs') and 'edition of the US Code' not in c[2] and 'end block' not in c[2]]
print(len(commits), 'law commits touching title 26', file=sys.stderr)
cands = []
BORN = {}
PASS = []
for h, date, subj in commits:
    files = [f for f in git('diff', '--name-only', h + '^', h, '--', 'title-26').split('\n') if f.endswith('.md')]
    new, changed = set(), set()
    for f in files:
        sec = os.path.basename(f)[:-3]
        a, b = parse(git('show', f'{h}^:{f}'), sec), parse(git('show', f'{h}:{f}'), sec)
        for i, t in b.items():
            if i not in a: new.add(i)
            elif a[i] != t: changed.add(i)
        if not a and b: new.add(PRE + sec)
    for i in new: BORN.setdefault(i, date)
    PASS.append((h, date, subj, new, changed))
for h, date, subj, new, changed in PASS:
    # only top-most new nodes that still exist today
    tops = [n for n in new if n in BY and BY[n]['parent'] not in new]
    for n in tops:
        par = BY[n]['parent']
        sibs = {s for s in KIDS[par] if s != n and s not in new and BY[s].get('status') == 'in-force'}
        if len(sibs) < 2: continue
        partner = [r for r in (new | changed) if r in TG and n in TG[r] and TG[r] & sibs and not r.startswith(n)]
        for r, tg in TG.items():
            if r in new or r in changed or r.startswith(n + '/') or r == n: continue
            if BORN.get(r, '0000') >= date: continue
            hit = tg & sibs
            if len(hit) < 2 and not (hit and partner): continue
            if n in tg or par in tg or any(t.startswith(n + '/') for t in tg): continue
            if any(par.startswith(t) for t in tg if t.count('/') >= 4 and t != par and par.startswith(t + '/')): continue
            cands.append(dict(law=subj.split(':')[0], date=date, new=n, new_heading=BY[n].get('heading') or '', new_text=(BY[n].get('text') or '')[:300],
                              list_at=r, list_text=(BY[r].get('heading') or '') + ' ' + (BY[r].get('text') or ''), lists=sorted(hit),
                              all_sibs=len(sibs), range=r in RANGE, partner=sorted(partner)[:4],
                              score=(3 if partner else 0) + (2 if len(hit) == len(sibs) else 0) + (1 if r.split('/')[4] == n.split('/')[4] else 0) - (2 if r in RANGE else 0)))
cands.sort(key=lambda c: (-c['score'], c['date']), reverse=False)
json.dump(cands, open(os.path.join(OUT, 'stale.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
cite = lambda i: '§' + i[len(PRE):].split('/')[0] + ''.join(f'({x})' for x in i[len(PRE):].split('/')[1:])
with open(os.path.join(OUT, 'stale.txt'), 'w', encoding='utf-8') as f:
    for c in cands:
        f.write(f"[{c['score']}] {c['date']} {c['law'][:60]}\n  NEW  {cite(c['new'])} {c['new_heading']} — {c['new_text'][:200]}\n  LIST {cite(c['list_at'])} lists {', '.join(cite(x) for x in c['lists'])}"
                f" ({len(c['lists'])} of {c['all_sibs']} older siblings){' RANGE' if c['range'] else ''}\n       {c['list_text'][:420]}\n"
                + (f"  PARTNER updated by the same law: {', '.join(cite(x) for x in c['partner'])}\n" if c['partner'] else '') + '\n')
from collections import Counter
print(len(cands), 'candidates;', Counter(c['score'] for c in cands).most_common(), Counter(c['law'][:40] for c in cands).most_common(12))
