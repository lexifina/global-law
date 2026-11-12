"""Step 3: evidence per (decision, first rewriting law) pair, a score, and the dataset.

    python score.py

Reads cand_rows.tsv, feat/out_*.tsv, cache/plaw (law texts), cache/crpt (committee reports, when fetched).
Writes law_names.tsv (every case a law names), pairs.tsv (one row per decision and law, all evidence), overrides.tsv
(the candidates: pairs with evidence, within the window), lean/in.tsv (Lean input).
"""
import collections, glob, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import lawtext as LT, names as N
W = os.path.expanduser('~/Documents/us-caselaw-lean-work'); O = f'{W}/uses/overrides'
WINDOW_MONTHS = 120

rows = [l.rstrip('\n').split('\t') for l in open(f'{O}/cand_rows.tsv', encoding='utf-8')]
feat = {}
for fn in glob.glob(f'{O}/feat/out_*.tsv'):
    for l in open(fn, encoding='utf-8'):
        f = l.rstrip('\n').split('\t'); feat[f[0]] = f[1:]

# token rarity among decision names (for one-party matches)
df = collections.Counter()
seen = set()
for r in rows:
    if r[1] in seen: continue
    seen.add(r[1])
    for s in N.sides(r[15]):
        for t in set(s): df[t] += 1

# law texts: named cases, citations, override language
laws = sorted({r[8] for r in rows})
LAW = {}
with open(f'{O}/law_names.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    for lab in laws:
        t = LT.text(lab)
        if t is None:
            LAW[lab] = None; continue
        nc = LT.named_cases(t); ci = LT.cites(t)
        LAW[lab] = dict(t=t, nc=nc, ci=ci, strong=len(LT.STRONG.findall(t)), ovr=len(LT.OVR.findall(t)), rep=LT.reports(t))
        for L, R, k in nc:
            near = [c for c, j in ci if 0 <= j - k <= 200]
            fo.write(f'{lab}\t{L}\t{R}\t{near[0] if near else ""}\n')

# committee reports, when fetched: text per report id
REP = {}
for fn in glob.glob(f'{O}/cache/crpt/*.htm'):
    REP[os.path.basename(fn)[:-4]] = fn
def report_texts(lab):
    L = LAW.get(lab)
    if not L: return []
    out = []
    for h, c, n in L['rep']:
        for key in (f'CRPT-{c}{h}rpt{n}', f'CRPT-{c}{h}rpt{n}-pt1'):
            if key in REP:
                out.append((key, REP[key]))
    return out
_rt = {}
def rtext(key, fn):
    """Named cases and citations of a report, each with its passage (parsed once per report)."""
    if key not in _rt:
        import html
        t = open(fn, encoding='utf-8', errors='replace').read()
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('``', '"').replace("''", '"')
        t = re.sub(r'\s+', ' ', t)
        nc = [(A, B, k, t[max(0, k - 320):k + 320].replace('	', ' ')) for A, B, k in LT.named_cases(t)]
        ci = [(c, k, t[max(0, k - 320):k + 320].replace('	', ' ')) for c, k in LT.cites(t)]
        _rt[key] = (nc, ci)
    return _rt[key]

def snippet(t, k, w=320):
    return t[max(0, k - w):k + w].replace('\t', ' ')

pairs = collections.OrderedDict()
for r in rows:
    key = (r[1], r[8])
    pairs.setdefault(key, []).append(r)

def cites_of(r):
    return [c for c in r[18].split('|') if c and 'LEXIS' not in c and 'SCDB' not in c and 'WL' not in c]

out = []
for (nid, lab), rs in pairs.items():
    r0 = rs[0]
    name, tier, decided = r0[15], r0[3], r0[2]
    gap = min(int(r[10]) for r in rs)
    L = LAW.get(lab)
    dc = cites_of(r0)
    m = ''; lsnip = ''; near_strong = 0
    if L:
        m = N.match(name, dc, L['nc'], L['ci'], df)
        if m:
            # where the law names it
            pos = None
            if m == 'cite':
                for c in dc:
                    nc_ = N.norm_cite(c)
                    pos = next((j for cc, j in L['ci'] if cc == nc_), None)
                    if pos is not None: break
            else:
                ds = [s for s in N.sides(name) if s]
                pos = next((k for A, B, k in L['nc'] if ds and ds[0][0] in set(N.toks(A)) | set(N.toks(B))), None)
            if pos is not None:
                lsnip = snippet(L['t'], pos)
                near_strong = int(bool(LT.STRONG.search(L['t'][max(0, pos - 600):pos + 600])))
    rm = ''; rsnip = ''; rkey = ''
    for key, fn in report_texts(lab):
        nc4, ci3 = rtext(key, fn)
        nc = [(A, B, k) for A, B, k, _ in nc4]; ci = [(c, k) for c, k, _ in ci3]
        mm = N.match(name, dc, nc, ci, df)
        if mm and (not rm or mm == 'cite'):
            rm, rkey = mm, key
            if mm == 'cite':
                c0 = next(N.norm_cite(c) for c in dc if N.norm_cite(c) in {x for x, _ in ci})
                rsnip = next(sn for x, j, sn in ci3 if x == c0)
            else:
                ds = [s_ for s_ in N.sides(name) if s_]
                rsnip = next((sn for A, B, k, sn in nc4 if ds[0][0] in set(N.toks(A)) | set(N.toks(B))), '')
    # decision-text evidence: best row
    fs = [(r, feat.get(r[0])) for r in rs]
    def fv(i):
        return max((int(f[i]) for r, f in fs if f), default=-1)
    qin, qst, sh, interp, ms = fv(2), fv(3), fv(4), fv(1), fv(0)
    qtxt = next((f[9] for r, f in fs if f and f[3] != '0'), '')
    mentions = max(int(r[7]) for r in rs)
    secs = ';'.join(sorted({f'{r[4]} U.S.C. § {r[5]}' + (f'({r[6]})' if r[6] else '') for r in rs}))
    named_law = m in ('cite', 'name2', 'name1')
    named_rep = rm in ('cite', 'name2', 'name1')
    sc = 0.0
    sc += {'cite': 6, 'name2': 5, 'name1': 3}.get(m, 0)
    sc += {'cite': 3, 'name2': 3, 'name1': 1.5}.get(rm, 0) if not named_law else {'cite': 1, 'name2': 1, 'name1': .5}.get(rm, 0)
    sc += near_strong * 1.0
    sc += 0.5 if L and L['strong'] else 0
    sc += 1.5 if qst >= 1 else 0
    sc += 1.0 if sh >= 3 else (0.5 if sh >= 1 else 0)
    sc += 0.5 if interp >= 5 else 0
    sc += 1.0 if mentions >= 10 else (0.5 if mentions >= 3 else 0)
    sc += 1.0 if gap <= 36 else (0.5 if gap <= 72 else (-0.5 if gap > WINDOW_MONTHS else 0))
    sc += {'S': 1.0, 'A': 0.5}.get(tier, 0)
    textual = qst >= 1 and L is not None and L['strong'] > 0
    evidence = int(named_law or named_rep or textual)
    kind = 'law names it' if named_law else ('report names it' if named_rep else ('quoted words struck' if textual else ''))
    out.append(dict(nid=nid, decided=decided, tier=tier, name=name, cite=(dc[0] if dc else ''), repo=r0[16], path=r0[17],
                    law=lab, law_day=r0[9], title=r0[12], gap=gap, sections=secs, nrows=len(rs), mentions=mentions,
                    law_match=m, report_match=rm, report=rkey, near_strong=near_strong,
                    law_strong=(L['strong'] if L else -1), law_text=int(L is not None),
                    interp=interp, qin=qin, qstruck=qst, struck_hits=sh, quote=qtxt, evidence=evidence, kind=kind,
                    score=round(sc, 2), law_snip=lsnip, report_snip=rsnip, rids=','.join(r[0] for r in rs)))
cols = list(out[0].keys())
out.sort(key=lambda x: -x['score'])
with open(f'{O}/pairs.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    fo.write('\t'.join(cols) + '\n')
    for x in out:
        fo.write('\t'.join(str(x[c]) for c in cols) + '\n')
cand = [x for x in out if x['evidence'] and x['gap'] <= WINDOW_MONTHS]
with open(f'{O}/overrides.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    fo.write('\t'.join(cols) + '\n')
    for x in cand:
        fo.write('\t'.join(str(x[c]) for c in cols) + '\n')
# Lean input: every candidate row (citation) with its evidence flag (the pair's)
ev = {}
for x in out:
    for rid in x['rids'].split(','):
        ev[rid] = x['evidence']
os.makedirs(f'{O}/lean', exist_ok=True)
with open(f'{O}/lean/in.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    for l in open(f'{W}/usc/enc/lean_in.tsv', encoding='utf-8'):
        rid, rest = l.split('\t', 1)
        d, vs = rest.split('\t', 1)
        fo.write(f'{rid}\t{d}\t{ev.get(rid, 0)}\t{vs}')
S = collections.Counter()
for x in out:
    S['pairs'] += 1; S['pairs_' + x['tier']] += 1
    S['law_text'] += x['law_text']
    if x['gap'] <= WINDOW_MONTHS: S['pairs_in_window'] += 1
    if x['law_match']: S['law_names_' + x['law_match']] += 1
    if x['report_match']: S['report_names_' + x['report_match']] += 1
    if x['evidence'] and x['gap'] <= WINDOW_MONTHS:
        S['cand'] += 1; S['cand_' + x['tier']] += 1; S['cand_kind_' + x['kind']] += 1
json.dump(S, open(f'{O}/score_summary.json', 'w'), indent=1)
print(json.dumps(S, indent=1))
