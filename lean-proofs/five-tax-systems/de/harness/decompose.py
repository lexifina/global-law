"""Attribute Lean (compat) vs GETTSIM differences: SV, Einkünfte, deductions, tariff."""
import json, sys, math
from fractions import Fraction as F
from collections import Counter
def est(x):
    x = math.floor(x)
    if x <= 12096: return 0
    if x <= 17443:
        y = F(x - 12096, 10000); return math.floor((F(93230, 100) * y + 1400) * y)
    if x <= 68480:
        z = F(x - 17443, 10000); return math.floor((F(17664, 100) * z + 2397) * z + F(101513, 100))
    if x <= 277825: return math.floor(F(42, 100) * x - F(1091192, 100))
    return math.floor(F(45, 100) * x - F(1924667, 100))
hs=[json.loads(l) for l in open(sys.argv[1])]; L=[json.loads(l) for l in open(sys.argv[2])]; G=[json.loads(l) for l in open(sys.argv[3])]
cls = Counter(); ex = {}
for h, l, g in zip(hs, L, G):
    us = l['detail']['units']
    tags = []
    lsv = sum(m[k] for u in us for m in u['members'] for k in ('RV','AV','KV','PV'))
    gsv = g['rv'] + g['av'] + g['kv'] + g['pv']
    if abs(lsv - gsv) > 0.05: tags.append('SV')
    lsum = sum(u['summeDerEinkuenfte'] for u in us); 
    if abs(lsum - g['gde']) > 0.005: tags.append('Einkuenfte')
    lab = sum(u['altersentlastungsbetrag_24a'] + u['entlastungsbetragAlleinerziehende_24b'] + u['vorsorgeaufwendungen_10'] + u['sonderausgabenOther_10b_10c'] for u in us)
    da = lab - g['abzuege']
    if abs(da) > 1.0: tags.append('Abzuege>1')
    elif abs(da) > 0.005: tags.append('AbzRound')
    # tariff on GETTSIM's own taxable income: statute
    joint = h['married'] and len(h['adults']) == 2
    lest = sum(u['tariffTax_32a'] + u['kindergeldAddedBack_2_6'] for u in us)
    if abs(lest - g['est']) > 0.5:
        if not [t for t in tags if t != 'AbzRound']:
            # same income chain; tariff or Günstigerprüfung
            kg = g['est'] - g['estMitKFB'] if any(g['kfbGuenstiger']) else 0
            tz = (2 * est(math.floor(g['zve']) // 2) if joint else est(g['zve'])) if len(us) == 1 else None
            if tz is not None and tz + kg == lest: tags.append('tariff(GETTSIM rounding/coeff)')
            else: tags.append('tariff-other')
    if not [t for t in tags if t != 'AbzRound'] and abs(lest - g['est']) <= 0.5 and abs(l['surtaxes']['Soli'] - g['soli']) > 0.011: tags.append('soli-only')
    k = '+'.join(tags) or 'equal'
    cls[k] += 1; ex.setdefault(k, []).append(h['id'])
for k, v in cls.most_common(): print(f'{v:5d} {k:45s} e.g. {ex[k][:4]}')
