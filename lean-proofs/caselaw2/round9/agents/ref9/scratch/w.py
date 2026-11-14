import sys
sys.path.insert(0, r'~\Documents\global-law-lean\lean-proofs\tools\caselaw2\ref')
import precedent_ref as pr
for d, ids in [('r9sw1/z94016/data', ['tr0', 'tr1']), ('r9sw1p/y95009/data', ['tr6']), ('r9sw1f/x96001/data', ['tr8'])]:
    D = pr.Data(d); A = pr.Engine(D); A.admit()
    for i in ids:
        r = A.treat_by_id[i]; w = D.witness[i]
        cl = D.klass.get(i)
        print(d, i, cl and cl[0], A.cert_ok[('treatments.tsv', i)], 'rtext', A._recog_text(r, w[0], w[1]), 'rules', A._recog_rules(r, w[0]),
              'zr', A.zone_result(w[0], r, None), 'gate', A.lean_cert_passes('treatments', r), 'zones', D.zones.get(w[0]))
