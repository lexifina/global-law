"""TWE (TY2026) constants vs Rev. Proc. 2025-32 (and Notice 2025-67 for retirement figures): every dollar value >= 1,000 looked up
as printed text in the guidance; values not found go to review (public/twe_review.tsv)."""
import os, re, glob, sys
REPO, RPF = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('twe', '2025/2025-032')
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
G = ''.join(open(f, errors='replace').read() for f in glob.glob(H + '/src/irs-guidance/rev-proc/%s.md' % RPF) + glob.glob(H + '/src/irs-guidance/notice/2025/2025-067.md'))
G = re.sub(r'\s+', ' ', G)
rev = []; ok = 0
for l in open(H + '/public/facts_%s.tsv' % REPO):
    q = l.rstrip().split(chr(9)) + ["", "", ""]; f, p, vals, d = q[:4]
    for v in re.findall(r'Dollar:([0-9.]+)', vals):
        x = int(float(v))
        if x < 1000: continue
        s = '{:,}'.format(x)
        if '$' + s in G or s in G: ok += 1
        else: rev.append((p, s, d[:90]))
open(H + '/public/%s_review.tsv' % REPO, 'w').write(''.join('%s\t%s\t%s\n' % r for r in rev))
print('found in guidance', ok, 'review', len(rev))
