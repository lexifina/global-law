"""Builds the pay grid: out/annual.txt (integer euros for the Lean adapter) and out/engine_in.jsonl (engine cases)."""
import json
PASS, SMIC_M = 47100, 1801.80   # 2025: arrêté du 19 décembre 2024; décret n° 2024-951 (11,88 €/h from 1 Nov 2024)
pts = set(range(0, 8 * PASS + 1, 100)) | set(range(8 * PASS, 10 * PASS + 1, 1000))
for t in [round(12 * SMIC_M), PASS, 4 * PASS, 8 * PASS, 21621, 21622]:
    for d in [0, 1, 2, 10, 100, 1000]:
        pts |= {t - d, t + d}
pts = sorted(p for p in pts if p >= 0)
open('out/annual.txt', 'w').write('\n'.join(map(str, pts)) + '\n')
with open('out/engine_in.jsonl', 'w') as f:
    for g in pts:
        for cadre in (False, True):
            f.write(json.dumps({'g': g, 'per': 'an', 'cadre': cadre, 'variant': 'neutral'}) + '\n')
            if g % 1000 == 0 or g in (PASS, PASS + 1, 4 * PASS, 4 * PASS + 1, 8 * PASS, 8 * PASS + 1):
                f.write(json.dumps({'g': g, 'per': 'an', 'cadre': cadre, 'variant': 'default'}) + '\n')
    # monthly thresholds (cents matter): SMIC, PASS, 4 PASS, 8 PASS monthly, ± 0.01 and ± 1 €
    for t in [SMIC_M, 3925, 4 * 3925, 8 * 3925]:
        for d in [0, 0.01, 1, -0.01, -1]:
            for cadre in (False, True):
                for v in ('neutral', 'default'):
                    f.write(json.dumps({'g': round(t + d, 2), 'per': 'mois', 'cadre': cadre, 'variant': v}) + '\n')
    # every month of 2025 (and the last day), three pay levels: rates must not move within the year
    for m in range(1, 13):
        for g in (2000, 5000, 20000):
            f.write(json.dumps({'g': g, 'per': 'mois', 'cadre': True, 'variant': 'default', 'date': f'01/{m:02d}/2025'}) + '\n')
    for g in (2000, 5000, 20000):
        f.write(json.dumps({'g': g, 'per': 'mois', 'cadre': True, 'variant': 'default', 'date': '31/12/2025'}) + '\n')
print(len(pts), 'annual points')
