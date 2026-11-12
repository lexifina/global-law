import collections, random, re, subprocess, sys, json, os
sys.path.insert(0, os.path.expanduser('~/Documents/global-law-lean/lean-proofs/tools/caselaw'))
from usc_encode import blocks, norm
W = os.path.expanduser('~/Documents/us-caselaw-lean-work')
REPOS = os.path.expanduser('~/Documents/us-caselaw-repos')
random.seed(20261113)
rows = [l.rstrip('\n').split('\t') for l in open(f'{W}/usc/results/rows_out.tsv', encoding='utf-8')]
both = [r for r in rows if r[5] == '1' and r[10] == '1']
A = random.sample(both, 100)
B = random.sample(rows, 50)
vers = collections.defaultdict(list)
for i, l in enumerate(open(f'{W}/usc/versions.tsv', encoding='utf-8')):
    f = l.rstrip('\n').split('\t'); vers[f[0]].append((int(f[4]), i, f[5], f[2], f[3]))
for p in vers: vers[p].sort()
def blob(git, sha, gitdir=True):
    a = ['git', '--git-dir', git] if gitdir else ['git', '-C', git]
    return subprocess.run(a + ['cat-file', '-p', sha], capture_output=True).stdout.decode('utf-8', 'replace')
def at(path, d):
    v = [x for x in vers[path] if x[0] <= d]
    return v[-1] if v else None
def item(r, kind):
    rid, nid, date, sec, sub = r[:5]
    t, s = re.match(r'(\d+) U\.S\.C\. . (.+)', sec).groups()
    path = f'title-{t}/{s}.md'; d = int(date.replace('-', ''))
    v0, v1 = at(path, d), at(path, 20261112)
    def words(v):
        if not v or not v[2]: return '(no text: removed)'
        tx = blob(f'{W}/usc-full.git', v[2]); b = blocks(tx)
        return (b.get(sub) if sub and sub in b else tx)
    import difflib
    w0, w1 = words(v0), words(v1)
    a0, a1 = w0.split(), w1.split()
    diff = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a0, a1, autojunk=False).get_opcodes():
        if op != 'equal':
            diff.append({'then': ' '.join(a0[max(0,i1-8):i2+8]), 'now': ' '.join(a1[max(0,j1-8):j2+8])})
    repo, dpath = r[12], r[13]
    text = subprocess.run(['git', '-C', f'{REPOS}/{repo}', 'show', f'HEAD:{dpath}'], capture_output=True).stdout.decode('utf-8', 'replace')
    b0 = text.find('\n---', 3) + 4
    ms = [m.start() for m in re.finditer(r'(?<![\w.])' + re.escape(s) + r'(?![\w-])', text) if m.start() > b0
          and re.search(r'§|U\.\s?S\.\s?C|USC|[Ss]ection|[Ss]ec\.|�', text[max(0, m.start() - 30):m.start()])][:40]
    ctx = []
    for k in ms:
        if not ctx or k > ctx[-1][1]:
            ctx.append((max(0, k - 700), k + 500))
        if len(ctx) == 3: break
    context = '\n[...]\n'.join(text[a:b] for a, b in ctx) or text[:2000]
    laws = [f'{x[4]} ({x[0]})' for x in vers[path] if x[0] > d and x[3] == 'law']
    return {'id': f'{kind}{rid}', 'decision': r[11], 'decided': date, 'court_repo': repo, 'cited': f'{sec}' + (f'({sub})' if sub else ''),
            'compared': (f'subsection ({sub})' if sub and v1 and v1[2] and sub in blocks(blob(f"{W}/usc-full.git", v1[2])) else 'whole section'), 'context': context, 'words_then': w0[:3500], 'words_now': w1[:3500], 'word_changes': diff[:12],
            'laws_since': laws[:12], 'version_then_from': v0[0] if v0 else None}
out = [item(r, 'A') for r in A] + [item(r, 'B') for r in B]
random.shuffle(out)
for i in range(3):
    json.dump(out[i::3], open(f'{W}/audit/usc2_audit_in_{i}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
key={}
for n,o in enumerate(out):
    key[f'd{n+1:03d}']=o['id']; o['id']=f'd{n+1:03d}'
json.dump(key,open(f'{W}/audit/usc2_audit_key.json','w'),indent=1)
print(len(out), sum(1 for o in out if not o['context'].strip()))
