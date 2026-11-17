"""Code citations in IRB guidance (rev-rul, rev-proc, notice, announcement) against Title 26 history:
(a) item still current (no later item modifies/supersedes/revokes/obsoletes it) citing a section that no longer exists;
(b) item that cites a section already repealed when the item was published (repeal commit date before publication)."""
import re, os, glob, json, subprocess, collections
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance'); U = os.path.expanduser(os.environ.get('USC_HISTORY', '~/united-states-law'))
have = {os.path.basename(f)[:-3] for f in glob.glob(U + '/title-26/*.md')}
dele = {}
def deleted(s):
    if s not in dele:
        o = subprocess.run(['git', '-C', U, 'log', '-1', '--diff-filter=D', '--format=%ad|%an', '--date=short', '--', 'title-26/%s.md' % s], capture_output=True, text=True).stdout.strip()
        dele[s] = o
    return dele[s]
items = {}; touched = set()
for f in glob.glob(G + '/*/*/*.md'):
    k = f.split('/')[-3]
    if k not in ('rev-rul', 'rev-proc', 'notice', 'announcement'): 
        t = open(f, encoding='utf-8').read(3000)
    else:
        t = open(f, encoding='utf-8').read()
    m = re.search(r'^effects: \[(.*)\]', t, re.M)
    if m:
        for e in re.findall(r'"([^"]+)"', m.group(1)):
            w = e.split()
            if w[-1] in ('modified', 'superseded', 'revoked', 'obsoleted'): touched.add(' '.join(w[:-1]))
    if k in ('rev-rul', 'rev-proc', 'notice', 'announcement'):
        it = re.search(r'^item: "([^"]+)"', t, re.M).group(1); pub = re.search(r'^published: "([^"]+)"', t, re.M).group(1)
        items[it] = (f, pub, t)
cite = re.compile(r'(?:§§? ?|\b[Ss]ections? )(\d{1,4}[A-Z]{0,2})(?=[\s(,.;:)]|$)(?![^\n]{0,40}?\b(?:of the (?:Internal Revenue Code of 1939|1939 Code|Act|Social Security|Employee Retirement|Tax Reform|Revenue Act|Public Health|Small Business)|of Public Law|of Pub\. L\.|of ERISA|of title|of the Code of 1939|of the Bankruptcy))')
A = collections.Counter(); Aex = collections.defaultdict(list); B = []; ncur = 0; ncites = 0
for it, (f, pub, t) in items.items():
    body = t.split('---', 2)[-1]
    current = it not in touched
    ncur += current
    secs = set()
    for m in cite.finditer(body):
        s = m.group(1); ncites += 1
        if s in have or s in secs: continue
        pre = body[max(0, m.start() - 45): m.start()]; post = body[m.end(): m.end() + 60]
        if 'U.S.C' in pre or re.match(r'\.\d', post) or re.search(r'repeal|former|prior to (its )?repeal|formerly', pre, re.I): continue
        if re.match(r'\s+of\s+(?!the (Internal Revenue )?Code)', post): continue
        if re.match(r'\s*(of|in) (this|Rev|Notice|Announcement|Ann)', post): continue
        secs.add(s)
        d = deleted(s)
        if not d: continue                       # never in the record (or not a Code section)
        ddate = d.split('|')[0]
        if current:
            A[s] += 1
            if len(Aex[s]) < 3: Aex[s].append((it, pub, body[max(0, m.start()-100): m.end()+80].replace('\n', ' ')))
        if ddate < pub:
            B.append((it, pub, s, d, body[max(0, m.start()-120): m.end()+80].replace('\n', ' ')))
res = dict(items=len(items), current=ncur, citations=ncites, current_citing_repealed=sum(A.values()), sections=len(A),
           by_section=A.most_common(), examples=Aex, cited_after_repeal=B)
json.dump(res, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/inventory/guidance_xref.json'), 'w'), indent=1)
print('items', len(items), 'current', ncur, 'citations', ncites)
print('current items citing a since-repealed section (item-section pairs):', sum(A.values()), 'distinct sections', len(A), A.most_common(12))
print('items citing a section repealed BEFORE the item was published:', len(B))
for b in sorted(B, key=lambda x: x[1], reverse=True)[:25]: print(b[0], b[1], 's' + b[2], b[3][:60], '|', b[4][:170])
