# round 3: show the conflict candidates of the reference at one bound court. usage: r3_dbg.py <universe dir> <issue> <court> [asof]
import sys, os
sys.path.insert(0, os.path.expanduser('~/caselaw2/lean-proofs/tools/caselaw2/ref'))
import precedent_ref as P
d, issue, court = sys.argv[1], sys.argv[2], int(sys.argv[3])
asof = int(sys.argv[4]) if len(sys.argv) > 4 else None
D = P.Data(os.path.join(d, 'data'), lambda *a: None)
A = P.Engine(D, firm=False); A.admit()
if asof is None:
    asof = int(open(os.path.join(d, 'lean', 'splits.tsv')).readline().split('\t')[8]) if os.path.getsize(os.path.join(d, 'lean', 'splits.tsv')) else 20251231
A.asof = asof
print('asof', asof)
quals = A._question_holdings(asof)
vw = A._view(court, asof)
print('view', vw)
cands = []
for h in quals.get(issue, ()):
    n = h['node']
    su = A.status(n, h['id'], asof, asof)
    sv = A.status_view(n, h['id'], asof, asof, vw)
    f = A.auth_cached(n, issue, h['role'], court, asof, None)
    hol = A.holders(n, asof)
    print(h['id'], 'node', n, 'court', D.court[n], D.date[n], h['answer'], 'union', su[:2], 'view', sv[:2], 'force', f[:2] if isinstance(f, tuple) else f,
          'holders', [(x.court, x.via, x.cap) for x in (hol or ())])
    if sv[0] == 'none' and f[0] != P.UNK and P.FORCE_RANK[f[0]] >= 7:
        cands.append((h, f[0]))
print('cands', [(h['id'], f) for h, f in cands])
for (a, _) in cands:
    for (b, _) in cands:
        if a is b: continue
        cs = [(D.court[b['node']], D.unit[b['node']])] + [(x.court, None) for x in (A.holders(b['node'], asof) or ()) if x.via == 'adoption' and x.cap == 'binding']
        print('  ', a['id'], '->', b['id'], [(c, A.auth_cached(a['node'], issue, a['role'], c, asof, u)[:2]) for c, u in cs])
print('resolve', A._resolve(cands, asof, issue, court))
