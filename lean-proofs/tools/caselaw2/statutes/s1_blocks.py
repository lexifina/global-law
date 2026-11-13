"""Step 1: every (law, US Code block) rewrite that touches a block some decision cited before the rewrite.

For each cited block (title, section, subsection) the version vector in usc/enc/lean_in.tsv gives the block's text hash
per version of the section. A rewrite = a version made by a law whose block hash differs from the previous version's.
Kept when at least one decision citing the block was decided on or before the rewrite's in-force day.

Writes statutes/blockchanges.tsv: law, title, section, sub, inforce_day, removed (block gone), first (first rewrite after
the earliest citing decision), n_citing_before (citations decided before), version index.
"""
import collections, os
W = os.path.expanduser('~/Documents/us-caselaw-lean-work')
O = f'{W}/caselaw-lean-2/statutes'
vers = collections.defaultdict(list)
for i, l in enumerate(open(f'{W}/usc/versions.tsv', encoding='utf-8')):
    f = l.rstrip('\n').split('\t')
    vers[f[0]].append((int(f[4]), i, f[2], f[3], f[6]))
for p in vers: vers[p].sort(key=lambda v: (v[0], v[1]))
blocks = {}            # (t, s, sub) -> vs
cited = collections.defaultdict(list)   # block -> decided days
for r, li in zip(open(f'{W}/usc/enc/rows.tsv', encoding='utf-8'), open(f'{W}/usc/enc/lean_in.tsv', encoding='utf-8')):
    rid, nid, d, t, s, sub, nm = r.rstrip('\n').split('\t')
    b = (t, s, sub)
    cited[b].append(int(d))
    if b not in blocks:
        f = li.rstrip('\n').split('\t')
        blocks[b] = [tuple(map(int, x.split(','))) for x in f[2:]]
n = 0
with open(f'{O}/blockchanges.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    for b, vs in blocks.items():
        ds = sorted(cited[b])
        pv = vers[f'title-{b[0]}/{b[1]}.md']
        assert len(pv) == len(vs)
        first_done = False
        for k in range(1, len(vs)):
            if vs[k][3] == vs[k - 1][3]: continue
            day = vs[k][0]
            before = sum(1 for d in ds if d <= day)
            if before == 0: continue
            if not vs[k][1]:
                first_done = True  # an edition rewrite; the law is unknown
                continue
            removed = 1 if vs[k][3] == 0 or vs[k][2] == 0 else 0
            fo.write('\t'.join(map(str, [pv[k][3], b[0], b[1], b[2], day, removed, int(not first_done), before, k])) + '\n')
            first_done = True
            n += 1
print('blocks', len(blocks), 'law block rewrites', n)
