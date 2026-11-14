import sys, os
sys.path.insert(0, r'~\Documents\global-law-lean\lean-proofs\tools\caselaw2\ref')
import precedent_ref as pr
for d in sys.argv[1:]:
    D = pr.Data(os.path.join(d, 'data')); A = pr.Engine(D); A.admit()
    lc = {}
    for l in open(os.path.join(d, 'lean', 'certs.tsv'), encoding='utf-8'):
        p = l.rstrip('\n').split('\t'); lc[p[1]] = p[2:4]
    for r in D.treatments:
        w = D.witness.get(r['id']); k = D.klass.get(r['id'])
        if not w or not k or k[0] != 'recognised':
            continue
        print(os.path.basename(d), r['id'], A.cert_ok[('treatments.tsv', r['id'])], 'rtext', bool(A._recog_text(r, w[0], w[1])), 'rules', A._recog_rules(r, w[0]),
              'zr', A.zone_result(w[0], r, None), 'gate', A.lean_cert_passes('treatments', r), 'lean', lc.get(r['id']), 'dates XYW', D.date[r['target']], D.date[r['by']], D.date[w[0]])
