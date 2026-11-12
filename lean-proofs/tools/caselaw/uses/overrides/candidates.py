"""Step 1: for every (decision, cited block), the first version after the decision whose words of that block differ.
Keep it when a law made that version (the first law to rewrite exactly the cited words). Writes cand_rows.tsv."""
import collections, os, re
W = os.path.expanduser('~/Documents/us-caselaw-lean-work')
O = f'{W}/uses/overrides'
vers = collections.defaultdict(list)
for i, l in enumerate(open(f'{W}/usc/versions.tsv', encoding='utf-8')):
    f = l.rstrip('\n').split('\t')
    vers[f[0]].append((int(f[4]), i, f[2], f[3], f[6]))
for p in vers: vers[p].sort(key=lambda v: (v[0], v[1]))
def tier(repo):
    if repo == 'supreme-court': return 'S'
    if re.fullmatch(r'ca\d+|cadc|cafc', repo): return 'A'
    if repo.endswith('-district') or repo in ('bankruptcy', 'tax-court', 'federal-special'): return 'F'
    return 'T'  # state, territorial, tribal
rows = open(f'{W}/usc/enc/rows.tsv', encoding='utf-8')
lin = open(f'{W}/usc/enc/lean_in.tsv', encoding='utf-8')
rout = open(f'{W}/usc/results/rows_out.tsv', encoding='utf-8')
n = kept = edfirst = 0
with open(f'{O}/cand_rows.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    for r, li, ro in zip(rows, lin, rout):
        rid, nid, d, t, s, sub, nm = r.rstrip('\n').split('\t')
        f = li.rstrip('\n').split('\t'); o = ro.rstrip('\n').split('\t')
        assert f[0] == rid == o[0]
        d = int(d); n += 1
        vs = [tuple(map(int, x.split(','))) for x in f[2:]]
        k0 = max((k for k, v in enumerate(vs) if v[0] <= d), default=None)
        if k0 is None: continue
        s0 = vs[k0][3]
        k1 = next((k for k in range(k0 + 1, len(vs)) if vs[k][3] != s0), None)
        if k1 is None: continue
        if not vs[k1][1]: edfirst += 1; continue
        path = f'title-{t}/{s}.md'
        pv = vers[path]; assert len(pv) == len(vs) and pv[k1][0] == vs[k1][0]
        gap = (vs[k1][0] // 10000 - d // 10000) * 12 + (vs[k1][0] // 100 % 100 - d // 100 % 100)
        removed = 1 if vs[k1][3] == 0 or vs[k1][2] == 0 else 0
        kept += 1
        fo.write('\t'.join(map(str, [rid, nid, d, tier(o[12]), t, s, sub, nm, pv[k1][3], vs[k1][0], gap, removed, pv[k1][4], k0, k1, o[11], o[12], o[13], o[14]])) + '\n')
print('rows', n, 'first rewrite by law', kept, 'first rewrite by edition', edfirst)
