"""Step 4: candidate (decision, law) pairs with evidence, extending the overrides work.

  A. block pairs: every law rewrite (not only the first) of a block the decision cited, within 15 years (Supreme Court,
     courts of appeals) or 10 years (other courts) of the decision. Evidence: the law names the decision
     (lawNamesDecision), a committee report on the law names it (reportNamesDecision); same matcher as the overrides work
     (reporter cite, both parties, one rare party).
  B. cite pairs: every reporter citation in a law or report that resolves to a decision node (graph/cite_index.tsv),
     decided before the law, whatever the decision cites (also before 1995). Linked to the blocks the law rewrote
     that the decision cites, else to the US Code sections amended in the law section that names it.
  C. quotedWordsStruck: the overrides candidates of that kind (first rewrite only), as they are.

    python s4_pairs.py reportlaws   -> statutes/report_laws.txt (laws whose reports to fetch)
    python s4_pairs.py              -> statutes/pairs2.tsv
"""
import collections, csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import common as C
N = C.N
csv.field_size_limit(10 ** 9)
W = C.W

def tier_repo(repo):
    if repo == 'supreme-court': return 'S'
    if re.fullmatch(r'ca\d+|cadc|cafc', repo): return 'A'
    if repo.endswith('-district') or repo in ('bankruptcy', 'tax-court', 'federal-special'): return 'F'
    return 'T'
def tier_path(path):
    c = path.split('/')[1] if '/' in path else ''
    if c == 'supreme-court-of-the-united-states': return 'S'
    if c.startswith('united-states-court-of-appeals') or c in ('court-of-appeals-for-the-federal-circuit', 'united-states-court-of-appeals-for-the-federal-circuit'): return 'A'
    if c.startswith('united-states-district-court') or c.startswith('united-states-bankruptcy') or 'tax-court' in c or 'court-of-federal-claims' in c or 'court-of-international-trade' in c: return 'F'
    return 'T'

# law rewrites per block
bc = collections.defaultdict(list)     # (t, s, sub) -> [(day, law, first)]
law_blocks = collections.defaultdict(set)
for l in open(f'{C.S}/blockchanges.tsv', encoding='utf-8'):
    law, t, s, sub, day, rem, first, nb, k = l.rstrip('\n').split('\t')
    bc[(t, s, sub)].append((int(day), law, int(first)))
    law_blocks[law].add((t, s, sub))
# decisions with citations
dec = {}                               # nid -> [day, tier, name, cite, repo, path, set(blocks)]
for r, o in zip(open(f'{W}/usc/enc/rows.tsv', encoding='utf-8'), open(f'{W}/usc/results/rows_out.tsv', encoding='utf-8')):
    rid, nid, d, t, s, sub, nm = r.rstrip('\n').split('\t')
    if nid not in dec:
        f = o.rstrip('\n').split('\t')
        dec[nid] = [int(d), tier_repo(f[12]), f[11], f[14], f[12], f[13], set()]
    dec[nid][6].add((t, s, sub))

# every reporter cite of each citing decision (nodes.tsv col 5, pipe-separated), not only the one rows_out prints
for l in open(f'{W}/graph/nodes.tsv', encoding='utf-8'):
    i = l.find('\t')
    x = dec.get(l[:i])
    if x is not None:
        f = l.rstrip('\n').split('\t')
        x.append([c for c in f[5].split('|') if c and 'LEXIS' not in c and 'SCDB' not in c and 'WL' not in c])
def window(tier): return 180 if tier in ('S', 'A') else 120
def months(d0, d1): return (d1 // 10000 - d0 // 10000) * 12 + (d1 // 100 % 100 - d0 // 100 % 100)

# block pairs
bpairs = collections.defaultdict(lambda: collections.defaultdict(list))  # nid -> law -> [(block, day, first)]
for nid, (d, tier, name, cite, repo, path, blocks, *_) in dec.items():
    for b in blocks:
        for day, law, first in bc.get(b, ()):
            if day >= d and months(d, day) <= window(tier):
                bpairs[nid][law].append((b, day, first))
laws = sorted({law for v in bpairs.values() for law in v})

if len(sys.argv) > 1 and sys.argv[1] == 'reportlaws':
    w = collections.Counter()
    for nid, v in bpairs.items():
        if dec[nid][1] in ('S', 'A'):
            for law in v: w[law] += 1 + 20 * (dec[nid][1] == 'S')
    with open(f'{C.S}/report_laws.txt', 'w', encoding='utf-8', newline='\n') as fo:
        for law, _ in w.most_common(): fo.write(law + '\n')
    print('block pairs', sum(len(v) for v in bpairs.values()), 'laws', len(laws), 'report laws', len(w))
    sys.exit()

# law and report texts: named cases and citations
LI = {json.loads(l)['law']: json.loads(l) for l in open(f'{C.S}/lawinfo.jsonl', encoding='utf-8')}
df = collections.Counter()
for nid, x in dec.items():
    for s_ in N.sides(x[2]):
        for t_ in set(s_): df[t_] += 1
LAW, REP = {}, {}
def law_parse(lab):
    if lab in LAW: return LAW[lab]
    t = C.text(lab)
    if t is None: LAW[lab] = None; return None
    nc = C.LT.named_cases(t); ci = C.LT.cites(t)
    toks = set()
    for A, B, _ in nc: toks |= set(N.toks(A)) | set(N.toks(B))
    LAW[lab] = dict(t=t, nc=nc, ci=ci, toks=toks, cset={c for c, _ in ci}, strong=len(C.LT.STRONG.findall(t)))
    return LAW[lab]
def rep_parse(key):
    if key in REP: return REP[key]
    t = C.report_text(key)
    if t is None: REP[key] = None; return None
    nc = C.LT.named_cases(t); ci = C.LT.cites(t)
    toks = set()
    for A, B, _ in nc: toks |= set(N.toks(A)) | set(N.toks(B))
    REP[key] = dict(t=t, nc=nc, ci=ci, toks=toks, cset={c for c, _ in ci})
    return REP[key]
def law_reports(lab):
    out = []
    for h, c, n in (LI.get(lab, {}).get('reports') or [])[:4]:
        key = f'CRPT-{c}{h}rpt{n}'
        x = rep_parse(key)
        if x: out.append((key, x))
    return out
def quick(name, dcites, X):
    if any(N.norm_cite(c) in X['cset'] for c in dcites): return True
    ds = [s for s in N.sides(name) if s]
    return bool(ds) and any(s[0] in X['toks'] for s in ds)
def where(X, name, dcites, m):
    if m == 'cite':
        for c in dcites:
            nc_ = N.norm_cite(c)
            pos = next((j for cc, j in X['ci'] if cc == nc_), None)
            if pos is not None: return pos
    ds = [s for s in N.sides(name) if s]
    return next((k for A, B, k in X['nc'] if ds and ds[0][0] in set(N.toks(A)) | set(N.toks(B))), None)
def snip(t, k, w=320): return t[max(0, k - w):k + w] if k is not None else ''

out = []
for nid, v in bpairs.items():
    d, tier, name, cite, repo, path = dec[nid][:6]
    dcites = sorted(set(([cite] if cite else []) + (dec[nid][7] if len(dec[nid]) > 7 else [])))
    for law, bl in v.items():
        L = law_parse(law)
        lm = rm = ''; lsn = rsn = rkey = ''; near = 0
        if L and quick(name, dcites, L):
            lm = N.match(name, dcites, L['nc'], L['ci'], df)
            if lm:
                k = where(L, name, dcites, lm); lsn = snip(L['t'], k)
                near = int(bool(k is not None and C.LT.STRONG.search(L['t'][max(0, k - 600):k + 600])))
        for key, X in law_reports(law):
            if quick(name, dcites, X):
                mm = N.match(name, dcites, X['nc'], X['ci'], df)
                if mm and (not rm or mm == 'cite'):
                    rm, rkey = mm, key; rsn = snip(X['t'], where(X, name, dcites, mm))
        if not (lm or rm): continue
        first = int(any(f for _, _, f in bl))
        out.append(dict(nid=nid, law=law, src='block', decided=d, tier=tier, name=name, cite=cite, repo=repo, path=path,
                        law_day=min(dy for _, dy, _ in bl), first=first,
                        blocks=';'.join(sorted({f'{t}:{s}' + (f'({sub})' if sub else '') for (t, s, sub), _, _ in bl})),
                        law_match=lm, report_match=rm, report=rkey, near_strong=near, law_snip=lsn, report_snip=rsn))
print('block pairs with naming evidence', len(out))

# cite pairs: reporter cites in laws / reports resolved to nodes
need = {}   # cite key -> [(law, 'law'|report key, offset)]
for lab in LI:
    L = law_parse(lab)
    if L:
        for c, k in L['ci']:
            ck = C.norm_cite_key(c.replace('U.S.', 'U.S.').replace('S.Ct.', 'S. Ct.'))
            if ck: need.setdefault(ck, []).append((lab, 'law', k))
    for key, X in law_reports(lab):
        for c, k in X['ci']:
            ck = C.norm_cite_key(c)
            if ck: need.setdefault(ck, []).append((lab, key, k))
nidof = {}
for l in open(f'{W}/graph/cite_index.tsv', encoding='utf-8'):
    k, v = l.rstrip('\n').split('\t')
    if k in need: nidof[k] = v
nodes_needed = set(nidof.values())
node = {}
for l in open(f'{W}/graph/nodes.tsv', encoding='utf-8'):
    i = l.find('\t')
    if l[:i] in nodes_needed:
        f = l.rstrip('\n').split('\t'); node[f[0]] = f
# law sections changed in the record (section level)
law_secs = collections.defaultdict(set)
for l in open(f'{W}/usc/versions.tsv', encoding='utf-8'):
    f = l.split('\t')
    if f[2] == 'law':
        m = re.match(r'title-(\w+)/(.+)\.md$', f[0])
        law_secs[f[3]].add((m.group(1), m.group(2)))
have = {(x['nid'], x['law']) for x in out}
ncite = 0
for ck, occ in need.items():
    nid = nidof.get(ck)
    if not nid or nid not in node: continue
    f = node[nid]; d = int(f[4] or 0)
    for lab, where_, k in occ:
        lday = LI[lab]['enacted'] or 0
        if not d or not lday or lday <= d: continue
        if (nid, lab) in have: continue
        have.add((nid, lab))
        # link: cited blocks the law rewrote; else US Code sections amended in the law section naming it
        blocks, how = [], ''
        if nid in dec:
            bl = [(b, dy) for b in dec[nid][6] for dy, law, _ in bc.get(b, ()) if law == lab and dy >= d]
            if bl: blocks = sorted({f'{t}:{s}' + (f'({sub})' if sub else '') for (t, s, sub), _ in bl}); how = 'citedBlock'
        if not blocks:
            X0 = LAW[lab] if where_ == 'law' else REP[where_]
            seg = X0['t'][max(0, k - 2500):k + 2500]
            near = {f'{a}:{b.replace(chr(8211), "-")}' for a, b in re.findall(r'\((\d+) U\.S\.C\. ?(\d+[\dA-Za-z]*(?:[\-–]\d+[A-Za-z]*)?)', seg)}
            near |= {f'{b}:{a.replace(chr(8211), "-")}' for a, b in re.findall(r'[Ss]ections? (\d+[\dA-Za-z]*(?:[\-–]\d+[A-Za-z]*)?)(?:\([^)]{1,6}\))* of title (\d+)', seg)}
            changed = law_secs.get(lab, set())
            blocks = sorted(u for u in near if tuple(u.split(':')) in changed)
            if blocks: how = 'nearCite'
        if not blocks and where_ == 'law':
            L = LAW[lab]
            # which law section holds offset k (offsets are in the cleaned text; locate by the section's heading words)
            secs = LI[lab]['secs']
            changed = law_secs.get(lab, set())
            pos_sec = None
            if secs:
                # cleaned-text offsets of section headings
                starts = [m.start() for m in re.finditer(r'SEC(?:TION)?\. \d+[A-Za-z]?(?:-\d+)?\. ', L['t'])]
                j = max((i for i, st in enumerate(starts) if st <= k), default=None)
                if j is not None and j < len(secs): pos_sec = secs[j]
            cand = []
            if pos_sec:
                cand = [u for u in pos_sec['usc'] if tuple(u.split(':')) in changed]
            if not cand and 0 < len(changed) <= 3:
                cand = [f'{a}:{b}' for a, b in sorted(changed)]
            if not cand and nid in dec:
                titles = {b[0] for b in dec[nid][6]}
                cand = [f'{a}:{b}' for a, b in sorted(changed) if a in titles][:5]
            blocks = cand; how = 'namingSection' if pos_sec and cand else ('smallLaw' if cand else '')
        if not blocks and where_ != 'law':
            changed = law_secs.get(lab, set())
            if nid in dec:
                titles = {b[0] for b in dec[nid][6]}
                blocks = [f'{a}:{b}' for a, b in sorted(changed) if a in titles][:5]; how = 'sameTitle' if blocks else ''
            if not blocks and 0 < len(changed) <= 3:
                blocks = [f'{a}:{b}' for a, b in sorted(changed)]; how = 'smallLaw'
        if not blocks: continue
        X = LAW[lab] if where_ == 'law' else REP[where_]
        sn = snip(X['t'], k)
        near = int(bool(C.LT.STRONG.search(X['t'][max(0, k - 600):k + 600])))
        ncite += 1
        out.append(dict(nid=nid, law=lab, src='cite:' + how, decided=d, tier=tier_path(f[2]), name=f[6], cite=f[5], repo=f[1], path=f[2],
                        law_day=lday, first=0, blocks=';'.join(blocks),
                        law_match='cite' if where_ == 'law' else '', report_match='cite' if where_ != 'law' else '',
                        report='' if where_ == 'law' else where_, near_strong=near if where_ == 'law' else 0,
                        law_snip=sn if where_ == 'law' else '', report_snip=sn if where_ != 'law' else ''))
print('cite pairs (new)', ncite)

# quoted words struck: the overrides candidates of that kind
ov = list(csv.DictReader(open(f'{C.OV}/overrides.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
for p in ov:
    if (p['nid'], p['law']) in have: continue
    secs = [re.sub(r'(\d+\w*) U\.S\.C\. § ([^ (]+)(\(.*\))?', lambda m: f'{m.group(1)}:{m.group(2)}' + (m.group(3) or ''), s) for s in p['sections'].split(';')]
    out.append(dict(nid=p['nid'], law=p['law'], src='overrides', decided=int(p['decided']), tier=p['tier'], name=p['name'], cite=p['cite'],
                    repo=p['repo'], path=p['path'], law_day=int(p['law_day']), first=1, blocks=';'.join(secs), law_match=p['law_match'], report_match=p['report_match'],
                    report=p['report'], near_strong=p['near_strong'], law_snip=p['law_snip'], report_snip=p['report_snip'], qstruck=p['qstruck'], quote=p['quote']))
qs = {(p['nid'], p['law']): p for p in ov}
for x in out:
    p = qs.get((x['nid'], x['law']))
    x['qstruck'] = p['qstruck'] if p else x.get('qstruck', '')
    x['quote'] = p['quote'] if p else x.get('quote', '')
    x['ov_kind'] = p['kind'] if p else ''
    x['ov_score'] = p['score'] if p else ''
    x['ov_audit'] = p['audit_label'] if p else ''
cols = ['nid', 'law', 'src', 'decided', 'tier', 'name', 'cite', 'repo', 'path', 'law_day', 'first', 'blocks', 'law_match', 'report_match',
        'report', 'near_strong', 'qstruck', 'quote', 'ov_kind', 'ov_score', 'ov_audit', 'law_snip', 'report_snip']
C.wtsv(f'{C.S}/pairs2.tsv', ([x[c] for c in cols] for x in out), cols)
print('pairs2', len(out), collections.Counter(x['src'].split(':')[0] for x in out))
