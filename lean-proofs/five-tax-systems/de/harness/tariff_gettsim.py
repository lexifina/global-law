"""GETTSIM's own tariff on whole-euro zvE x = 0..400 000 (single) and joint X = 0..800 000 step 2 vs Lean."""
import os
import numpy as np, gettsim, warnings
from collections import Counter
from gettsim import InputData, MainTarget, TTTargets
warnings.filterwarnings("ignore")
lean = np.array([int(l) for l in open(os.path.expanduser('~/cmp/de/runs/tariff/lean_est.txt'))])
N = len(lean)
def run(values, joint):
    n = len(values)
    if joint:
        p = np.arange(2 * n); sp = np.where(p % 2 == 0, p + 1, p - 1); ge = np.repeat(values, 2); gv = np.ones(2 * n, bool)
    else:
        p = np.arange(n); sp = -np.ones(n, int); ge = values; gv = np.zeros(n, bool)
    data = {"p_id": p, "hh_id": p // 2 if joint else p, "familie__p_id_ehepartner": sp,
            "einkommensteuer__gemeinsam_veranlagt": gv, "einkommensteuer__gesamteinkommen_y_sn": ge.astype(float)}
    tree = {"einkommensteuer": {"betrag_ohne_kinderfreibetrag_y_sn": None}}
    r = gettsim.main(main_target=MainTarget.results.df_with_nested_columns, policy_date_str="2025-07-01",
                     input_data=InputData.qname(data), tt_targets=TTTargets(tree=tree))
    v = r[r.columns[0]].to_numpy()
    return v[::2] if joint else v
xs = np.arange(N)
g = run(xs.astype(float), False)
d = np.nonzero(g != lean)[0]
zone = lambda x: 2 if x <= 17443 else 3 if x <= 68480 else 4 if x <= 277825 else 5
print('single: GETTSIM != Lean on', len(d), 'of', N, 'sign', Counter(np.sign(g[d] - lean[d]).tolist()), 'zones', Counter(zone(x) for x in d))
print('  examples', [(int(x), int(lean[x]), float(g[x])) for x in d[:6]])
X = np.arange(0, 800001)
gj = run(X.astype(float), True)
lj = 2 * lean[X // 2]
dj = np.nonzero(gj != lj)[0]
print('joint: GETTSIM != Lean (2*est(X//2)) on', len(dj), 'of', len(X), 'diff values', Counter((gj[dj] - lj[dj]).tolist()).most_common(5))
print('  odd X among them', int(np.sum(X[dj] % 2 == 1)), 'even X', int(np.sum(X[dj] % 2 == 0)))
np.savetxt(os.path.expanduser('~/cmp/de/runs/tariff/gettsim_single_diff.txt'), np.c_[d, lean[d], g[d]], fmt='%d')
