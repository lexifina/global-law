"""Extract AMT amounts (§55) from each year's Rev. Proc., 2013-2025."""
import re, json, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from docs import DOCS
    from extract import text, norm
D = r'\|? ?\$([\d,]+)'
out = {}
for ty in range(2013, 2026):
    for p in DOCS[ty]:
        t = norm(text(p)[0])
        i = t.find('exemption amounts under § 55(d)(1)')
        if i < 0: continue
        s = t[i:i + 1600]
        def g(pat, seg):
            m = re.search(pat, seg); return int(m.group(1).replace(',', '')) if m else None
        j = s.find('phaseout'); po = s[j:] if j > 0 else ''
        r = dict(ex_mfj=g(r'Joint Returns or Surviving Spouses ' + D, s), ex_single=g(r'Unmarried Individuals \(other than Surviving Spouses\) ' + D, s),
                 ex_mfs=g(r'Married Individuals Filing Separate Returns ' + D, s), ex_est=g(r'Estates and Trusts ' + D, s),
                 bp=g(r'and Estates and Trusts ' + D, s), bp_mfs=g(r'applies is: Married Individuals Filing Separate Returns ' + D, s),
                 po_mfj=g(r'Joint Returns or Surviving Spouses ' + D, po), po_single=g(r'Unmarried Individuals \(other than Surviving Spouses\) ' + D, po),
                 po_est=g(r'Estates and Trusts ' + D, po))
        out[ty] = dict(doc=p, v=r)
    print(ty, out.get(ty, {}).get('v'))
json.dump(out, open('amt.json', 'w'), indent=1)
