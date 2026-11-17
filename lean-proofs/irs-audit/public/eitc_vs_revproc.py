"""EITC Assistant constantsYYYY.xml (2023-2026) vs the year's inflation Rev. Proc. (printed text lookup); misses -> public/eitc_review.tsv"""
import os, re
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); RP = {2023: '2022/2022-038', 2024: '2023/2023-034', 2025: '2024/2024-040', 2026: '2025/2025-032'}
rev = []; ok = 0
for l in open(H + '/public/facts_eitc.tsv'):
    q = l.rstrip().split(chr(9)) + ['', '', '']; f, p, vals, d = q[:4]
    m = re.search(r'constants(20\d\d)', f)
    if not m: continue
    y = int(m.group(1)); G = re.sub(r'\s+', ' ', open(H + '/src/irs-guidance/rev-proc/%s.md' % RP[y], errors='replace').read())
    for v in re.findall(r'Dollar:([0-9.]+)', vals):
        x = int(float(v))
        if x < 1000: continue
        s = '{:,}'.format(x)
        if s in G: ok += 1
        else: rev.append((y, p, s, d[:100]))
open(H + '/public/eitc_review.tsv', 'w').write(''.join('%s\t%s\t%s\t%s\n' % r for r in rev))
print('found', ok, 'review', len(rev))
